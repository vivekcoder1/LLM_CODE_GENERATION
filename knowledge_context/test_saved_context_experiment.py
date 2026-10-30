"""Offline validation and generation orchestration for frozen retrieval contexts."""

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_saved_context_experiment as saved


class Generator:
    def __init__(self):
        self.calls = []
        self.failure = None
        self.last_generation_metadata = {"stop_reason": "end_turn", "input_tokens": 20, "output_tokens": 10}

    def generate_grounded_code(self, task, context, *, max_tokens, domain_context, api_resolution):
        self.calls.append({"task": task, "code_context": context, "domain_context": domain_context,
                           "api_resolution": copy.deepcopy(api_resolution), "max_tokens": max_tokens})
        if self.failure:
            raise ValueError(self.failure)
        return "print('fresh script')\n"


class SavedContextExperimentTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1])
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "test").mkdir()
        self.source_dir = self.root / "prior_snapshot"
        self.source_dir.mkdir()
        self.settings = {"top_k": 12, "max_nodes": 12}
        self.config_id = saved._canonical_hash(self.settings)[:12]
        records = []
        for domain in saved.DEFAULT_DOMAINS:
            task = "# Task " + domain + "\n"
            (self.root / "test" / (domain + ".md")).write_text(task, encoding="utf-8")
            for variant in ("code_only", "combined"):
                directory = self.source_dir / "runs" / domain / variant
                directory.mkdir(parents=True)
                code_context = "Code API " + domain
                domain_context = "Reference prior " + domain if variant == "combined" else ""
                full = code_context + "\n" + domain_context
                blueprint = {"semantic_queries": [domain], "target_classes": ["CenteredGrid"], "target_functions": []}
                for filename, value in (("task.md", task), ("code_context.md", code_context),
                                        ("domain_context.md", domain_context), ("context.md", full)):
                    (directory / filename).write_text(value, encoding="utf-8")
                (directory / "blueprint.json").write_text(json.dumps(blueprint), encoding="utf-8")
                (directory / "effective_blueprint.json").write_text(json.dumps(blueprint), encoding="utf-8")
                resolution = [{"observed_call": "diffuse.implicit", "status": "resolved_candidate", "quality": "legacy_file_name_candidate",
                               "code_id": "f1", "code_import_path": "phi.flow.diffuse.implicit", "namespace_caveat": "Not runtime verification"}] if variant == "combined" else []
                record = {"run_id": domain + "_" + variant, "domain": domain, "variant": variant,
                    "run_dir": str(directory), "retrieval_status": "passed", "config_id": self.config_id,
                    "domain_status": "available" if variant == "combined" else "disabled",
                    "context": {"context_chars": len(full), "code_nodes": 12, "domain_nodes": 20 if domain_context else 0},
                    "plan": {"effective_sha256": saved._canonical_hash(blueprint)},
                    "metadata": {"task_hash": saved._hash_text(task), "code_context_hash": saved._hash_text(code_context),
                                 "domain_context_hash": saved._hash_text(domain_context)}, "api_resolution": resolution}
                records.append(record)
        self.source = {"created_utc": "2026-10-22T02:00:00+00:00", "completed_utc": "2026-10-22T02:04:00+00:00",
                       "settings": self.settings, "config_id": self.config_id, "runs": records}
        self.manifest = self.source_dir / "manifest.json"
        self.save_source()
        self.generator = Generator()
        self.executor = MagicMock(return_value={"status": "passed", "execution_ok": True, "duration_s": .1})

    def save_source(self):
        self.manifest.write_text(json.dumps(self.source), encoding="utf-8")

    def args(self, *extra):
        return saved.parse_args(["--context-manifest", str(self.manifest), "--execute", "--project-root", str(self.root),
                                 "--output-dir", str(self.root / "new_run"), *extra])

    def test_all_eight_source_arms_validate_before_clients_exist(self):
        with patch.object(saved, "load_llm_config", side_effect=AssertionError("Credentials accessed")), \
             patch.object(saved, "load_pipeline_class", side_effect=AssertionError("Pipeline constructed")):
            result = saved.validate_source_manifest(self.manifest, self.root)
        self.assertEqual(len(result["arms"]), 8)
        self.assertEqual(result["manifest_sha256"], saved.sha256_file(self.manifest))

    def test_incomplete_manifest_is_rejected(self):
        self.source.pop("completed_utc")
        self.save_source()
        with self.assertRaisesRegex(ValueError, "completed"):
            saved.validate_source_manifest(self.manifest, self.root)

    def test_missing_or_duplicate_arms_fail_before_any_paid_call(self):
        self.source["runs"].pop()
        self.source["runs"].append(copy.deepcopy(self.source["runs"][0]))
        self.save_source()
        client = MagicMock()
        with patch.object(saved, "load_llm_config", side_effect=AssertionError("Credentials accessed")):
            with self.assertRaisesRegex(ValueError, "Missing source arm"):
                saved.run_saved_experiment(self.args(), client=client, generator=self.generator, executor=self.executor)
        self.assertEqual(self.generator.calls, [])
        client.models.list.assert_not_called()
        self.assertFalse((self.root / "new_run").exists())

    def test_tampered_code_context_is_rejected(self):
        path = Path(self.source["runs"][-1]["run_dir"]) / "code_context.md"
        path.write_text("tampered", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "code_context_hash"):
            saved.run_saved_experiment(self.args(), generator=self.generator, executor=self.executor)
        self.assertEqual(self.generator.calls, [])

    def test_changed_current_task_is_rejected(self):
        (self.root / "test/heat_flow.md").write_text("changed task", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "task_hash"):
            saved.validate_source_manifest(self.manifest, self.root)

    def test_combined_prior_requires_available_status_and_nonempty_text(self):
        record = next(row for row in self.source["runs"] if row["variant"] == "combined")
        record["domain_status"] = "unavailable"
        self.save_source()
        with self.assertRaisesRegex(ValueError, "originally available"):
            saved.validate_source_manifest(self.manifest, self.root)

    def test_paired_base_blueprints_must_match(self):
        record = self.source["runs"][1]
        path = Path(record["run_dir"]) / "blueprint.json"
        path.write_text(json.dumps({"semantic_queries": ["different"]}), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "base blueprints differ"):
            saved.validate_source_manifest(self.manifest, self.root)

    def test_effective_blueprint_hash_is_validated(self):
        path = Path(self.source["runs"][1]["run_dir"]) / "effective_blueprint.json"
        path.write_text('{"semantic_queries": ["tampered"]}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "effective blueprint"):
            saved.validate_source_manifest(self.manifest, self.root)

    def test_historical_rows_are_ignored_without_becoming_fresh_arms(self):
        self.source["runs"].append({"variant": "historical_rerun", "domain": "heat_flow"})
        self.save_source()
        self.assertEqual(len(saved.validate_source_manifest(self.manifest, self.root)["arms"]), 8)

    def test_eight_fresh_generations_preserve_snapshot_provenance_and_api_evidence(self):
        before = saved.sha256_file(self.manifest)
        with patch.object(saved, "load_llm_config", side_effect=AssertionError("Unexpected credentials")), \
             patch.object(saved, "load_pipeline_class", side_effect=AssertionError("Unexpected live pipeline")):
            result = saved.run_saved_experiment(self.args(), generator=self.generator, executor=self.executor)
        self.assertEqual(len(self.generator.calls), 8)
        self.assertEqual(self.executor.call_count, 8)
        self.assertEqual(saved.sha256_file(self.manifest), before)
        self.assertEqual(result["graph_integrity"]["status"], "not_queried")
        self.assertEqual(result["source_snapshot"]["source_completed_utc"], self.source["completed_utc"])
        self.assertEqual(len(result["reports"]), 9)
        for row, call in zip(result["runs"], self.generator.calls):
            self.assertEqual(row["retrieval_status"], "restored_not_requeried")
            self.assertEqual(row["artifact_provenance"], "fresh")
            self.assertEqual(row["generation"]["status"], "generated")
            self.assertEqual(call["api_resolution"], row["api_resolution"])
            self.assertEqual(call["code_context"], Path(row["run_dir"]).joinpath("code_context.md").read_text(encoding="utf-8"))
            self.assertEqual(row["metadata"]["api_resolution_hash"], saved._canonical_hash(row["api_resolution"]))

    def test_authentication_failure_blocks_remaining_calls_without_reroll(self):
        self.generator.failure = "Authentication error 401"
        result = saved.run_saved_experiment(self.args(), generator=self.generator, executor=self.executor)
        self.assertEqual(len(self.generator.calls), 1)
        self.assertEqual(result["runs"][0]["generation"]["status"], "failed")
        self.assertTrue(all(row["generation"]["status"] == "blocked" for row in result["runs"][1:]))
        self.executor.assert_not_called()

    def test_credit_failure_also_blocks_remaining_generations(self):
        self.generator.failure = "Your credit balance is too low"
        result = saved.run_saved_experiment(self.args(), generator=self.generator, executor=self.executor)
        self.assertEqual(len(self.generator.calls), 1)
        self.assertEqual(len(result["runs"]), 8)

    def test_isolated_generation_failure_does_not_retry_or_discard_other_results(self):
        original = self.generator.generate_grounded_code
        attempts = []
        def sometimes(*args, **kwargs):
            attempts.append(1)
            if len(attempts) == 1:
                raise ValueError("Synthetic generation failure")
            return original(*args, **kwargs)
        self.generator.generate_grounded_code = sometimes
        result = saved.run_saved_experiment(self.args(), generator=self.generator, executor=self.executor)
        self.assertEqual(len(attempts), 8)
        self.assertEqual(result["runs"][0]["generation"]["status"], "failed")
        self.assertTrue(all(row["generation"]["status"] == "generated" for row in result["runs"][1:]))

    def test_output_collision_prevents_api_or_generation_access(self):
        (self.root / "new_run").mkdir()
        client = MagicMock()
        with self.assertRaises(FileExistsError):
            saved.run_saved_experiment(self.args(), client=client, generator=self.generator, executor=self.executor)
        self.assertEqual(self.generator.calls, [])
        client.models.list.assert_not_called()

    def test_no_graph_guards_reject_accidental_reads(self):
        with self.assertRaisesRegex(RuntimeError, "forbids graph access"):
            saved.NoGraphDriver().session()
        with self.assertRaisesRegex(RuntimeError, "forbids new domain retrieval"):
            saved.NoDomainRetriever().get_domain_context("heat_flow")

    def test_test_outcomes_load_into_all_report_exports(self):
        path = self.root / "tests.json"
        path.write_text('[{"name": "unit_case", "status": "passed", "tests": 1}]', encoding="utf-8")
        result = saved.run_saved_experiment(self.args("--test-results", str(path)), generator=self.generator, executor=self.executor)
        self.assertEqual(result["tests"][0]["name"], "unit_case")
        self.assertIn("unit_case", Path(result["reports"]["tests"]).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
