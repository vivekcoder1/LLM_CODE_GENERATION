"""Offline runner contracts: no credentials, live graph, model, or LLM calls."""

import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import MagicMock, patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_combined_experiment as runner


class FakePipeline:
    def __init__(self):
        self.calls = []
        self.blueprints = 0
        self.generations = 0
        self.generation_calls = []
        self.fail_variant = None
        self.last_generation_metadata = {"stop_reason": "end_turn", "output_tokens": 12}

    def generate_search_blueprint(self, task):
        self.blueprints += 1
        return {"semantic_queries": ["grid"], "target_classes": ["CenteredGrid"], "target_functions": []}

    def retrieve_context(self, domain, task, *, variant, blueprint, settings):
        self.calls.append({"domain": domain, "variant": variant, "blueprint": copy.deepcopy(blueprint), "settings": copy.deepcopy(settings)})
        if variant == self.fail_variant:
            raise ValueError("Synthetic retrieval failure")
        # Attempted mutation must not affect the other arm's input or manifest.
        blueprint["target_classes"].append("mutated")
        settings["top_k"] = -1
        return {"code_context": "api context " + variant, "domain_context": "recipe" if variant == "combined" else "",
                "context": "full context", "blueprint": blueprint, "domain_status": "available",
                "api_resolution": [{"observed_call": "diffuse.implicit", "status": "resolved", "quality": "exact_alias",
                                    "code_id": "implicit_1", "code_import_path": "phi.flow.diffuse.implicit",
                                    "namespace_caveat": "Annotations are not runtime verification."}],
                "statistics": {"code_nodes": 12, "domain_nodes": 20 if variant == "combined" else 0,
                               "resolved_api_links": 3, "unresolved_api_links": 1, "context_chars": 500}}

    def generate_grounded_code(self, task, context, *, max_tokens, domain_context, api_resolution=None):
        self.generations += 1
        self.generation_calls.append({"max_tokens": max_tokens, "domain_context": domain_context,
                                      "api_resolution": copy.deepcopy(api_resolution)})
        return "import numpy as np\nnp.save('heat_flow_temperature_trj.npy', np.ones((101,100,50)))\n"


class CombinedExperimentTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1])
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "test").mkdir()
        (self.root / "cache").mkdir()
        (self.root / "test_heat_flow").mkdir()
        self.task = "# Heat task\nUse grid and diffusion.\n"
        (self.root / "test/heat_flow.md").write_text(self.task, encoding="utf-8")
        digest = hashlib.sha1(self.task.encode()).hexdigest()[:12]
        self.blueprint_path = self.root / "cache" / f"heat_flow_{digest}_blueprint.json"
        self.blueprint_path.write_text(json.dumps({"semantic_queries": ["temperature"], "target_classes": ["CenteredGrid"], "target_functions": ["diffuse"]}), encoding="utf-8")
        self.script = self.root / "test_heat_flow/generated_heat_flow_simulation.py"
        self.script.write_text("import numpy as np\nnp.save('heat_flow_trj.npy', np.ones((2,2)))\n", encoding="utf-8")
        self.output = self.root / "new_experiment"
        self.pipeline = FakePipeline()

    def args(self, *extra):
        return runner.parse_args(["--project-root", str(self.root), "--output-dir", str(self.output),
                                  "--domains", "heat_flow", "--blueprint-dir", str(self.root / "cache"), *extra])

    def test_default_retrieval_makes_no_llm_calls_and_records_cached_plan(self):
        with patch.object(runner, "prepare_runtime", side_effect=AssertionError("Unexpected live runtime")):
            manifest = runner.run_experiment(self.args(), pipeline=self.pipeline)
        self.assertEqual(len(manifest["runs"]), 2)
        self.assertEqual(self.pipeline.blueprints, 0)
        self.assertEqual(self.pipeline.generations, 0)
        self.assertEqual({row["plan"]["plan_source"] for row in manifest["runs"]}, {"cached"})
        self.assertTrue(all(row["generation"]["status"] == "not_requested" for row in manifest["runs"]))
        self.assertTrue(all(row["metadata"]["model"] is None for row in manifest["runs"]))

    def test_variants_share_immutable_blueprint_and_settings(self):
        manifest = runner.run_experiment(self.args(), pipeline=self.pipeline)
        left, right = self.pipeline.calls
        self.assertEqual(left["settings"], right["settings"])
        self.assertEqual(left["blueprint"], right["blueprint"])
        self.assertEqual(manifest["settings"]["top_k"], runner.DEFAULT_SETTINGS["top_k"])
        self.assertNotIn("mutated", right["blueprint"]["target_classes"])

    def test_each_arm_uses_new_directory_and_saves_audit_inputs(self):
        manifest = runner.run_experiment(self.args(), pipeline=self.pipeline)
        directories = [Path(row["run_dir"]) for row in manifest["runs"]]
        self.assertEqual(len(set(directories)), 2)
        for row in manifest["runs"]:
            directory = Path(row["run_dir"])
            for name in ("task.md", "blueprint.json", "effective_blueprint.json", "retrieval_metadata.json", "record.json", "code_context.md", "domain_context.md", "context.md"):
                self.assertTrue((directory / name).is_file())
            self.assertIn("code_context_hash", row["metadata"])
            self.assertIn("effective_sha256", row["plan"])
        self.assertTrue(Path(manifest["reports"]["markdown"]).is_file())

    def test_existing_output_directory_is_never_reused(self):
        self.output.mkdir()
        sentinel = self.output / "preserve.txt"
        sentinel.write_text("keep", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            runner.run_experiment(self.args(), pipeline=self.pipeline)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")
        self.assertEqual(self.pipeline.calls, [])

    def test_missing_cached_blueprint_blocks_rows_without_llm_fallback(self):
        self.blueprint_path.unlink()
        manifest = runner.run_experiment(self.args(), pipeline=self.pipeline)
        self.assertEqual(self.pipeline.blueprints, 0)
        self.assertEqual(self.pipeline.calls, [])
        self.assertEqual(len(manifest["runs"]), 2)
        self.assertTrue(all(row["retrieval_status"] == "blocked" for row in manifest["runs"]))
        self.assertIn("No cached blueprint", manifest["runs"][0]["reason"])

    def test_partial_retrieval_failure_keeps_successful_arm_and_manifest(self):
        self.pipeline.fail_variant = "combined"
        manifest = runner.run_experiment(self.args(), pipeline=self.pipeline)
        self.assertEqual(manifest["runs"][0]["retrieval_status"], "passed")
        self.assertEqual(manifest["runs"][1]["retrieval_status"], "blocked")
        saved = json.loads((self.output / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(saved["runs"]), 2)
        self.assertIn("Synthetic retrieval failure", saved["runs"][1]["reason"])

    def test_also_rerun_existing_is_one_historical_row_not_fake_arm_pair(self):
        executed = []
        def fake_executor(script, **kwargs):
            executed.append(script)
            np.save(script.parent / "heat_flow_trj.npy", np.ones((2, 2)))
            return {"status": "passed", "execution_ok": True, "duration_s": .1}
        before = runner.sha256_file(self.script)
        manifest = runner.run_experiment(self.args("--also-rerun-existing", "--execute"), pipeline=self.pipeline, executor=fake_executor)
        self.assertEqual(len(manifest["runs"]), 3)
        self.assertEqual(len(executed), 1)
        historical = manifest["runs"][-1]
        self.assertEqual(historical["variant"], "historical_rerun")
        self.assertEqual(historical["generation_source"], "historical_script_rerun")
        self.assertEqual(historical["artifact_provenance"], "existing_outputs_rerun")
        self.assertEqual(historical["artifacts"], {})  # Wrong historical filename is not normalized.
        self.assertEqual(runner.sha256_file(self.script), before)
        self.assertTrue((Path(historical["run_dir"]) / "heat_flow_trj.npy").exists())
        self.assertEqual(historical["observed_artifacts"][0]["filename"], "heat_flow_trj.npy")

    def test_no_execute_flag_never_runs_existing_script(self):
        executor = MagicMock(side_effect=AssertionError("must not execute"))
        manifest = runner.run_experiment(self.args("--mode", "existing"), pipeline=self.pipeline, executor=executor)
        self.assertEqual(len(manifest["runs"]), 1)
        self.assertEqual(manifest["runs"][0]["execution"]["status"], "not_run")
        executor.assert_not_called()
        self.assertEqual(self.pipeline.calls, [])

    def test_generate_preflight_block_preserves_retrieval_without_generation(self):
        runtime = {"connections": [], "preflight": {"llm": {"status": "blocked", "error": "401"}},
                   "errors": ["LLM authentication 401"], "generation_allowed": False, "model": "test-model"}
        manifest = runner.run_experiment(self.args("--mode", "generate"), pipeline=self.pipeline, runtime=runtime)
        self.assertEqual(self.pipeline.blueprints, 0)
        self.assertEqual(self.pipeline.generations, 0)
        self.assertEqual(len(self.pipeline.calls), 2)
        self.assertTrue(all(row["generation"]["status"] == "blocked" for row in manifest["runs"]))

    def test_generate_uses_one_blueprint_per_domain_and_no_implicit_execution(self):
        runtime = {"connections": [], "preflight": {"llm": {"status": "passed", "available_models": ["test-model"]}},
                   "errors": [], "generation_allowed": True, "model": "test-model"}
        manifest = runner.run_experiment(self.args("--mode", "generate"), pipeline=self.pipeline, runtime=runtime)
        self.assertEqual(self.pipeline.blueprints, 1)
        self.assertEqual(self.pipeline.generations, 2)
        self.assertTrue(all(row["generation"]["status"] == "generated" for row in manifest["runs"]))
        self.assertTrue(all(row["execution"]["status"] == "not_run" for row in manifest["runs"]))
        self.assertTrue(all(row["generation"]["stop_reason"] == "end_turn" for row in manifest["runs"]))

    def test_generation_receives_unmodified_api_resolution_evidence_and_hash(self):
        runtime = {"connections": [], "preflight": {"llm": {"status": "passed", "available_models": ["test-model"]}},
                   "errors": [], "generation_allowed": True, "model": "test-model"}
        manifest = runner.run_experiment(self.args("--mode", "generate"), pipeline=self.pipeline, runtime=runtime)
        for record, call in zip(manifest["runs"], self.pipeline.generation_calls):
            self.assertEqual(call["api_resolution"], record["api_resolution"])
            self.assertEqual(call["api_resolution"][0]["namespace_caveat"], "Annotations are not runtime verification.")
            expected = hashlib.sha256(json.dumps(record["api_resolution"], sort_keys=True).encode("utf-8")).hexdigest()
            self.assertEqual(record["metadata"]["api_resolution_hash"], expected)

    def test_injected_pipeline_cannot_bypass_generation_preflight_by_default(self):
        manifest = runner.run_experiment(self.args("--mode", "generate"), pipeline=self.pipeline)
        self.assertEqual(self.pipeline.generations, 0)
        self.assertEqual(self.pipeline.blueprints, 0)
        self.assertTrue(all(row["generation"]["status"] == "blocked" for row in manifest["runs"]))

    def test_ast_screen_rejects_sensitive_imports_and_dynamic_calls(self):
        for source in ("import neo4j", "from os import environ", "import anthropic as a", "exec('bad')", "__import__('os')"):
            with self.subTest(source=source):
                self.assertTrue(runner.inspect_script(source))
        self.assertFalse(runner.inspect_script("from phi.flow import *\nimport numpy as np\nnp.save('output.npy', [1])"))

    def test_ast_screen_rejects_output_escape_or_dynamic_filenames(self):
        for target in ("'/outside.npy'", "'../outside.npy'", "r'C:\\outside.npy'", "name"):
            with self.subTest(target=target):
                self.assertTrue(runner.inspect_script(f"import numpy as np\nnp.save({target}, [1])"))

    def test_child_environment_excludes_all_inherited_secrets(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "secret", "NEO4J_PASSWORD": "secret", "AWS_SECRET_ACCESS_KEY": "secret", "CUSTOM_TOKEN": "secret", "PATH": "runtime"}):
            environment = runner.child_environment(self.root)
        self.assertEqual(environment["PATH"], "runtime")
        for key in ("ANTHROPIC_API_KEY", "NEO4J_PASSWORD", "AWS_SECRET_ACCESS_KEY", "CUSTOM_TOKEN"):
            self.assertNotIn(key, environment)

    def test_execution_guard_blocks_sensitive_code_before_subprocess(self):
        self.script.write_text("import os\nprint(os.environ)\n", encoding="utf-8")
        with patch.object(runner.subprocess, "run") as process:
            result = runner.execute_script(self.script, timeout=1, project_root=self.root)
        process.assert_not_called()
        self.assertEqual(result["status"], "blocked")
        self.assertIn("Forbidden import os", result["error"])

    def test_subprocess_receives_isolated_cwd_restricted_environment_and_timeout(self):
        self.script.write_text("print('ok')\n", encoding="utf-8")
        completed = types.SimpleNamespace(returncode=0, stdout="ok\n", stderr="")
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "never_pass"}), \
             patch.object(runner.subprocess, "run", return_value=completed) as process:
            result = runner.execute_script(self.script, timeout=17, project_root=self.root)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(process.call_args.kwargs["cwd"], self.script.parent)
        self.assertEqual(process.call_args.kwargs["timeout"], 17)
        self.assertNotIn("ANTHROPIC_API_KEY", process.call_args.kwargs["env"])
        self.assertEqual((self.script.parent / "stdout.txt").read_text(encoding="utf-8"), "ok\n")

    def test_execution_timeout_retains_partial_logs(self):
        self.script.write_text("print('ok')\n", encoding="utf-8")
        failure = runner.subprocess.TimeoutExpired("python", 1, output=b"partial", stderr=b"details")
        with patch.object(runner.subprocess, "run", side_effect=failure):
            result = runner.execute_script(self.script, timeout=1, project_root=self.root)
        self.assertEqual(result["status"], "timeout")
        self.assertEqual((self.script.parent / "stdout.txt").read_text(encoding="utf-8"), "partial")
        self.assertEqual((self.script.parent / "stderr.txt").read_text(encoding="utf-8"), "details")

    def test_graph_snapshot_uses_only_read_sessions_and_hashes_ids(self):
        driver = MagicMock()
        session = driver.session.return_value.__enter__.return_value
        def read(callback):
            tx = MagicMock()
            def query(text):
                if text.startswith("SHOW"):
                    return [{"name": "classNames", "state": "ONLINE", "type": "FULLTEXT"}]
                return [{"element_id": "a"}, {"element_id": "b"}]
            tx.run.side_effect = query
            return callback(tx)
        session.execute_read.side_effect = read
        snapshot = runner.graph_snapshot(driver, "selected")
        self.assertEqual(snapshot["nodes_count"], 2)
        self.assertEqual(snapshot["nodes_id_sha256"], hashlib.sha256(b"a\nb\n").hexdigest())
        for call in driver.session.call_args_list:
            self.assertEqual(call.kwargs, {"database": "selected", "default_access_mode": "READ"})
        session.execute_write.assert_not_called()

    def test_retrieval_live_setup_does_not_import_or_configure_llm_client(self):
        # Missing code credentials blocks before embeddings/pipeline creation;
        # neither models.list nor load_llm_config is touched in retrieval mode.
        import pipeline_config
        with patch.object(pipeline_config, "load_connection_config", side_effect=ValueError("missing code")), \
             patch.object(pipeline_config, "load_llm_config", side_effect=AssertionError("LLM config accessed")) as load_llm:
            pipeline, runtime = runner.prepare_runtime(self.args())
        self.assertIsNone(pipeline)
        self.assertEqual(runtime["preflight"]["llm"]["status"], "not_requested")
        load_llm.assert_not_called()

    def test_failed_selected_domain_source_does_not_silently_fall_back_to_json(self):
        import pipeline_config
        factory = MagicMock(return_value=self.pipeline)
        transformer = types.ModuleType("sentence_transformers")
        transformer.SentenceTransformer = MagicMock(return_value=object())
        def connection(path, role, root):
            if role == "domain":
                raise ValueError("Selected domain credentials are invalid")
            return {"uri": "bolt://code.invalid", "user": "code", "password": "test", "database": "selected"}
        indexes = [{"name": name, "state": "ONLINE"} for name in runner.REQUIRED_INDEXES]
        with patch.object(pipeline_config, "load_connection_config", side_effect=connection), \
             patch.object(pipeline_config, "load_llm_config", side_effect=AssertionError("Unexpected LLM configuration")), \
             patch.object(pipeline_config, "create_read_driver", return_value=MagicMock()), \
             patch.object(runner, "_snapshot_connections", return_value={"code": {"status": "available", "indexes": indexes}}), \
             patch.object(runner, "load_pipeline_class", return_value=factory), \
             patch.dict(sys.modules, {"sentence_transformers": transformer}):
            _, runtime = runner.prepare_runtime(self.args())
        options = factory.call_args.kwargs
        self.assertIsNotNone(options["domain_retriever"])
        self.assertEqual(options["domain_retriever"].source_mode, "none")
        self.assertFalse(options["allow_llm"])
        self.assertTrue(any("Selected domain credentials" in error for error in runtime["errors"]))

    def test_per_test_results_are_loaded_hashed_and_exported(self):
        results = self.root / "tests.json"
        results.write_text(json.dumps([{"name": "offline_case", "status": "passed", "tests": 1,
                                      "failures": 0, "errors": 0, "skipped": 0}]), encoding="utf-8")
        manifest = runner.run_experiment(self.args("--test-results", str(results)), pipeline=self.pipeline)
        self.assertEqual(manifest["tests"][0]["name"], "offline_case")
        self.assertEqual(manifest["test_results_source"]["sha256"], runner.sha256_file(results))
        self.assertIn("offline_case", Path(manifest["reports"]["tests"]).read_text(encoding="utf-8"))

    def test_invalid_test_results_schema_stops_before_any_pipeline_calls(self):
        results = self.root / "tests.json"
        results.write_text('{"not": "a list"}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "JSON list"):
            runner.run_experiment(self.args("--test-results", str(results)), pipeline=self.pipeline)
        self.assertEqual(self.pipeline.calls, [])

    def test_unavailable_snapshot_never_claims_graph_unchanged(self):
        snapshot = {"code": {"status": "unavailable", "error": "blocked"}}
        self.assertEqual(runner.compare_graph_snapshots(snapshot, snapshot), {"code": "unavailable"})

    def test_graph_topology_comparison_detects_changed_id_sets(self):
        before = {"code": {"status": "available", "nodes_count": 2, "relationships_count": 1,
                           "nodes_id_sha256": "nodes", "relationships_id_sha256": "rels"}}
        after = copy.deepcopy(before)
        self.assertEqual(runner.compare_graph_snapshots(before, after)["code"], "unchanged_topology_ids")
        after["code"]["nodes_id_sha256"] = "changed"
        self.assertEqual(runner.compare_graph_snapshots(before, after)["code"], "changed_topology_ids")

    def test_invalid_numeric_options_are_rejected(self):
        with self.assertRaises(SystemExit):
            runner.parse_args(["--repeats", "0"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
