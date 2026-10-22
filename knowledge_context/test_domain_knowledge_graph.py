"""Semantic and failure-mode tests; no simulation, network, or database calls."""

import copy
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import shutil
import struct
import sys
import tempfile
import types
import unittest
from unittest.mock import MagicMock, patch

from domain_knowledge_graph_creater import (
    DEFAULT_ROOT, HERE, LOGGER, KnowledgeGraphBuilder, configure_logging,
    load_neo4j_config, main, npy_header, write_neo4j,
)


class DomainGraphTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.spec = json.loads((HERE / "domain_graph_spec.json").read_text(encoding="utf-8"))
        self.spec_path = self.root / "knowledge_context" / "domain_graph_spec.json"
        self.spec_path.parent.mkdir()
        self.spec_path.write_text(json.dumps(self.spec), encoding="utf-8")
        self.config_path = self.spec_path.parent / ".env"
        self.config_path.write_text("NEO4J_URI=bolt://file.invalid\nNEO4J_USER=file_user\nNEO4J_PASSWORD=file_password\nNEO4J_DATABASE=file_db\n", encoding="utf-8")
        for profile in self.spec["references"]:
            for relative in [profile["source"], profile["note"]]:
                destination = self.root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(DEFAULT_ROOT / relative, destination)
        # Small local library fixtures exercise explicit re-export resolution.
        library = self.root / "phiflow" / "phi"
        (library / "field").mkdir(parents=True)
        (library / "field" / "__init__.py").write_text("from ._grid import CenteredGrid\n", encoding="utf-8")
        (library / "field" / "_grid.py").write_text("def CenteredGrid(*args, **kwargs):\n    pass\n", encoding="utf-8")
        (library / "physics").mkdir()
        (library / "physics" / "diffuse.py").write_text("def implicit(field, coefficient, dt):\n    pass\n", encoding="utf-8")
        self.make_header("test_julia_set/julia_set_ground_truth_trj.npy", (100, 256, 256))
        self.make_header("test_burgers2d/burgers2d_ground_truth.npy", (101, 64, 64, 2))

    def make_header(self, relative, shape):
        header = (repr({"descr": "<f4", "fortran_order": False, "shape": shape}) + "\n").encode("latin1")
        (self.root / relative).write_bytes(b"\x93NUMPY\x01\x00" + struct.pack("<H", len(header)) + header)

    def builder(self):
        return KnowledgeGraphBuilder(self.root, self.spec_path)

    def node(self, graph, suffix):
        matches = [node for node in graph["nodes"] if node["id"].endswith(suffix)]
        self.assertEqual(len(matches), 1, suffix)
        return matches[0]

    def edges(self, graph, node, relation):
        return [edge for edge in graph["edges"] if edge["source"] == node["id"] and edge["type"] == relation]

    def write_spec(self):
        self.spec_path.write_text(json.dumps(self.spec), encoding="utf-8")

    def fake_neo4j(self, graph, after=None):
        driver, session, tx = MagicMock(), MagicMock(), MagicMock()
        driver.__enter__.return_value = driver
        driver.session.return_value.__enter__.return_value = session
        session.execute_write.side_effect = lambda function: function(tx)
        counters = types.SimpleNamespace(nodes_created=0, nodes_deleted=0, relationships_created=0,
                                         relationships_deleted=0, properties_set=0, constraints_added=0)
        summary = types.SimpleNamespace(counters=counters, database="testdb",
                                        server=types.SimpleNamespace(address="example.invalid:7687", agent="Neo4j/test"))
        session.run.return_value.consume.return_value = summary
        tx.run.return_value.consume.return_value = summary
        after = after or {"nodes": len(graph["nodes"]), "edges": len(graph["edges"])}
        session.run.return_value.single.side_effect = [
            {"count": 0}, {"count": 0}, {"count": after["nodes"]}, {"count": after["edges"]},
        ]
        factory = MagicMock(return_value=driver)
        module = types.SimpleNamespace(GraphDatabase=types.SimpleNamespace(driver=factory))
        return module, factory, driver, session, tx

    def test_builds_four_references_and_complete_provenance(self):
        graph = self.builder().build()
        self.assertEqual(sum(node["label"] == "ReferenceSimulation" for node in graph["nodes"]), 4)
        ids = {node["id"] for node in graph["nodes"]}
        for row in graph["nodes"] + graph["edges"]:
            for key in ["source_path", "source_lines", "evidence_kind", "review_status"]:
                self.assertIn(key, row["properties"])
        self.assertTrue(all(edge["source"] in ids and edge["target"] in ids for edge in graph["edges"]))

    def test_burgers_reads_diffused_velocity_for_advection(self):
        graph = self.builder().build()
        diffusion = self.node(graph, "burgers2d:ground_truth:step:diffusion")
        advection = self.node(graph, "burgers2d:ground_truth:step:self_advection")
        self.assertEqual(self.edges(graph, diffusion, "READS")[0]["properties"]["state_version"], 0)
        self.assertEqual(self.edges(graph, advection, "READS")[0]["properties"]["state_version"], 1)
        self.assertEqual(self.edges(graph, diffusion, "NEXT_STEP")[0]["target"], advection["id"])

    def test_reaction_cache_retains_old_state_dependencies(self):
        graph = self.builder().build()
        cache = self.node(graph, "reaction_diffusion:ground_truth:step:cache_reaction")
        cache_reads = self.edges(graph, cache, "READS")
        self.assertEqual({edge["properties"]["variable"] for edge in cache_reads}, {"u", "v"})
        self.assertTrue(all(edge["properties"]["state_version"] == 0 for edge in cache_reads))
        update_v = self.node(graph, "reaction_diffusion:ground_truth:step:update_v")
        reads = {edge["properties"]["variable"]: edge["properties"]["state_version"] for edge in self.edges(graph, update_v, "READS")}
        self.assertEqual(reads, {"v": 0, "reaction": 1})

    def test_heat_reads_coefficient_but_only_writes_temperature(self):
        graph = self.builder().build()
        step = self.node(graph, "heat_flow:ground_truth:step:diffusion")
        self.assertEqual({edge["properties"]["variable"] for edge in self.edges(graph, step, "READS")}, {"t", "conductivity"})
        self.assertEqual(len(self.edges(graph, step, "WRITES")), 1)
        self.assertTrue(self.edges(graph, step, "WRITES")[0]["target"].endswith("field:temperature"))

    def test_julia_computed_output_has_no_invented_save(self):
        graph = self.builder().build()
        output = self.node(graph, "julia_set:ground_truth:output:count_trajectory")
        self.assertEqual(output["properties"]["save_status"], "not_explicit")
        self.assertEqual(output["properties"]["initial_frame"], "excluded_by_profile")
        self.assertEqual(self.edges(graph, output, "HAS_SAVE"), [])
        self.assertEqual(len(self.edges(graph, output, "HAS_ARTIFACT_OBSERVATION")), 1)

    def test_helper_and_parameter_dependencies_are_connected(self):
        graph = self.builder().build()
        field = self.node(graph, "reaction_diffusion:ground_truth:field:u")
        self.assertEqual(len(self.edges(graph, field, "USES_HELPER")), 1)
        helper = self.node(graph, "reaction_diffusion:ground_truth:helper:initial_condition")
        variables = {edge["properties"]["variable"] for edge in self.edges(graph, helper, "USES_PARAMETER")}
        self.assertEqual(variables, {"Lx", "Ly", "s"})

    def test_static_resolution_does_not_promote_external_candidates(self):
        graph = self.builder().build()
        codes = [node for node in graph["nodes"] if node["label"] == "CodeComponent"]
        self.assertTrue(any(node["properties"]["qualified_name"] == "phi.field._grid.CenteredGrid" for node in codes))
        self.assertFalse(any(node["properties"]["qualified_name"].startswith("numpy") for node in codes))
        self.assertTrue(any(node["label"] == "ApiCandidate" and node["properties"]["observed_call"] == "np.stack" for node in graph["nodes"]))

    def test_same_inputs_have_identical_graph_and_ids(self):
        builder = self.builder()
        self.assertEqual(builder.build(), builder.build())
        self.assertEqual(builder.build(), self.builder().build())

    def test_source_edit_invalidates_stale_step(self):
        path = self.root / self.spec["references"][0]["source"]
        path.write_text(path.read_text().replace("diffuse.implicit", "diffuse.explicit"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "matched 0 statements"):
            self.builder().build()

    def test_reversed_recipe_is_rejected(self):
        self.spec["references"][0]["steps"].reverse()
        self.write_spec()
        with self.assertRaisesRegex(ValueError, "step order"):
            self.builder().build()

    def test_extra_state_update_is_not_silently_omitted(self):
        path = self.root / self.spec["references"][0]["source"]
        path.write_text(path.read_text().replace("    return v", "    v = v * 2\n    return v"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Unconfigured statement"):
            self.builder().build()

    def test_notes_remain_guidance(self):
        graph = self.builder().build()
        notes = [node for node in graph["nodes"] if node["label"] == "Guidance"]
        self.assertEqual(len(notes), 16)
        self.assertTrue(all(node["properties"]["evidence_kind"] in {"proposed_hint", "unresolved"} for node in notes))

    def test_missing_and_empty_sources_reported_without_invented_references(self):
        empty = self.root / "test_structural_mechanics" / "structural_mechanics_ground_truth.py"
        empty.parent.mkdir()
        empty.write_text("")
        tasks = self.root / "test"
        tasks.mkdir()
        (tasks / "smoke_plume.md").write_text("A task is not a reference")
        graph = self.builder().build()
        self.assertTrue(any(item["status"] == "empty_source" for item in graph["report"]))
        self.assertIn({"domain": "smoke_plume", "status": "missing_ground_truth"}, graph["report"])
        configured = self.root / self.spec["references"][0]["source"]
        configured.write_text("")
        with self.assertRaisesRegex(ValueError, "missing or empty"):
            self.builder().build()

    def test_path_escape_rejected(self):
        self.spec["references"][0]["source"] = "../other_ground_truth.py"
        self.write_spec()
        with self.assertRaisesRegex(ValueError, "escapes project root"):
            self.builder().build()

    def test_npy_header_inspection_and_truncation(self):
        path = self.root / "test_julia_set/julia_set_ground_truth_trj.npy"
        self.assertEqual(npy_header(path)["shape"], [100, 256, 256])
        path.write_bytes(path.read_bytes()[:12])
        with self.assertRaisesRegex(ValueError, "Truncated"):
            npy_header(path)

    def test_failed_validation_leaves_previous_export_unchanged(self):
        output = self.root / "previous.json"
        output.write_text("previous graph")
        self.spec["references"][0]["steps"][0]["code"] = "v = missing(v)"
        self.write_spec()
        with redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
            status = main(["--root", str(self.root), "--spec", str(self.spec_path), "--output", str(output)])
        self.assertEqual(status, 1)
        self.assertEqual(output.read_text(), "previous graph")

    def test_neo4j_batches_are_scoped_and_parameterized(self):
        graph = self.builder().build()
        fake_module, factory, driver, session, tx = self.fake_neo4j(graph)
        with patch.dict(sys.modules, {"neo4j": fake_module}):
            write_neo4j(graph, "bolt://example.invalid", "user", "secret", "testdb")
        factory.assert_called_once_with("bolt://example.invalid", auth=("user", "secret"))
        for call in tx.run.call_args_list:
            query = call.args[0]
            self.assertNotIn("secret", query)
            self.assertIn("DomainKG", query)
            if "DELETE" in query:
                self.assertEqual(call.kwargs["dataset"], graph["dataset"])
                self.assertIn("$ids", query)
        self.assertTrue(any("MERGE" in call.args[0] for call in tx.run.call_args_list))

    def test_writer_rejects_empty_or_cross_dataset_graph(self):
        with self.assertRaisesRegex(ValueError, "empty graph"):
            write_neo4j({"nodes": []}, "", "", "")
        graph = copy.deepcopy(self.builder().build())
        graph["nodes"][0]["properties"]["dataset"] = "other"
        with self.assertRaisesRegex(ValueError, "outside its dataset"):
            write_neo4j(graph, "", "", "")

    def test_cli_synchronizes_neo4j_by_default(self):
        config = {"uri": "bolt://example.invalid", "user": "test_user", "password": "test_password", "database": "testdb"}
        errors = types.SimpleNamespace(DriverError=type("DriverError", (Exception,), {}),
                                       Neo4jError=type("Neo4jError", (Exception,), {}))
        with patch("domain_knowledge_graph_creater.load_neo4j_config", return_value=config) as settings, \
             patch("domain_knowledge_graph_creater.write_neo4j") as writer, \
             patch.dict(sys.modules, {"neo4j.exceptions": errors}), \
             redirect_stdout(io.StringIO()):
            status = main(["--root", str(self.root), "--spec", str(self.spec_path)])
        self.assertEqual(status, 0)
        settings.assert_called_once()
        writer.assert_called_once()
        self.assertEqual(writer.call_args.kwargs, config)

    def test_export_only_does_not_load_credentials_or_connect(self):
        with patch("domain_knowledge_graph_creater.load_neo4j_config") as settings, \
             patch("domain_knowledge_graph_creater.write_neo4j") as writer, \
             redirect_stdout(io.StringIO()):
            status = main(["--root", str(self.root), "--spec", str(self.spec_path), "--export-only"])
        self.assertEqual(status, 0)
        settings.assert_not_called()
        writer.assert_not_called()
        self.assertTrue((self.root / "knowledge_context/domain_knowledge_graph.json").is_file())

    def test_cli_connection_overrides_selected_file_only(self):
        environment = {"NEO4J_URI": "bolt://env.invalid", "NEO4J_USER": "env_user", "NEO4J_PASSWORD": "test_password", "NEO4J_DATABASE": "env_db"}
        with patch.dict(os.environ, environment, clear=True):
            config = load_neo4j_config(self.root, uri="bolt://override.invalid", user="override_user", database="override_db")
        self.assertEqual(config, {"uri": "bolt://override.invalid", "user": "override_user", "password": "file_password", "database": "override_db"})

    def test_missing_credentials_have_actionable_error(self):
        self.config_path.write_text("", encoding="utf-8")
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "Missing Neo4j settings.*NEO4J_URI.*NEO4J_PASSWORD"):
                load_neo4j_config(self.root)

    def test_local_file_wins_over_root_file_and_inherited_environment(self):
        (self.root / ".env").write_text("NEO4J_URI=bolt://root.invalid\nNEO4J_USER=root_user\nNEO4J_PASSWORD=root_password\n", encoding="utf-8")
        environment = {"NEO4J_URI": "bolt://inherited.invalid", "NEO4J_USER": "old_user", "NEO4J_PASSWORD": "old_password"}
        with patch.dict(os.environ, environment, clear=True):
            config = load_neo4j_config(self.root)
            self.assertEqual(dict(os.environ), environment)
        self.assertEqual(config, {"uri": "bolt://file.invalid", "user": "file_user", "password": "file_password", "database": "file_db"})

    def test_missing_local_file_never_falls_back(self):
        self.config_path.unlink()
        (self.root / ".env").write_text("NEO4J_URI=bolt://root.invalid\nNEO4J_USER=root_user\nNEO4J_PASSWORD=root_password\n", encoding="utf-8")
        with patch.dict(os.environ, {"NEO4J_URI": "bolt://env.invalid", "NEO4J_USER": "old_user", "NEO4J_PASSWORD": "old_password"}):
            with self.assertRaisesRegex(ValueError, "does not exist.*No fallback"):
                load_neo4j_config(self.root)

    def test_incomplete_local_file_never_borrows_a_password(self):
        self.config_path.write_text("NEO4J_URI=bolt://file.invalid\nNEO4J_USER=file_user\n", encoding="utf-8")
        (self.root / ".env").write_text("NEO4J_PASSWORD=root_password\n", encoding="utf-8")
        with patch.dict(os.environ, {"NEO4J_PASSWORD": "old_password"}):
            with self.assertRaisesRegex(ValueError, "Missing Neo4j settings.*NEO4J_PASSWORD"):
                load_neo4j_config(self.root)

    def test_explicit_file_is_the_only_credentials_source(self):
        alternate = self.root / "alternate.env"
        alternate.write_text("NEO4J_URI=bolt://alternate.invalid\nNEO4J_USER=alternate_user\nNEO4J_PASSWORD=alternate_password\n", encoding="utf-8")
        with patch.dict(os.environ, {"NEO4J_DATABASE": "inherited_database"}):
            config = load_neo4j_config(self.root, env_file=alternate)
        self.assertEqual(config, {"uri": "bolt://alternate.invalid", "user": "alternate_user", "password": "alternate_password", "database": None})
        alternate.write_text("NEO4J_URI=bolt://alternate.invalid\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Missing Neo4j settings.*NEO4J_USER.*NEO4J_PASSWORD"):
            load_neo4j_config(self.root, env_file=alternate)

    def test_interpolation_cannot_import_inherited_credentials(self):
        self.config_path.write_text("NEO4J_URI=${NEO4J_URI}\nNEO4J_USER=file_user\nNEO4J_PASSWORD=file_password\n", encoding="utf-8")
        with patch.dict(os.environ, {"NEO4J_URI": "bolt://inherited.invalid"}):
            with self.assertRaisesRegex(ValueError, "literal values.*interpolation is disabled"):
                load_neo4j_config(self.root)

    def test_missing_dotenv_dependency_does_not_enable_environment_fallback(self):
        with patch.dict(sys.modules, {"dotenv": None}):
            with self.assertRaisesRegex(ValueError, "requires python-dotenv.*fallback is disabled"):
                load_neo4j_config(self.root)

    def test_invalid_uri_rejected_before_connecting(self):
        for uri in ["https://host.invalid", "bolt://user:password@host.invalid", "neo4j://host.invalid:not_a_port"]:
            with self.subTest(uri=uri), self.assertRaisesRegex(ValueError, "NEO4J_URI must be a valid"):
                load_neo4j_config(self.root, uri=uri)

    def test_configuration_check_does_not_build_or_connect(self):
        console = io.StringIO()
        with patch("domain_knowledge_graph_creater.KnowledgeGraphBuilder") as builder, \
             patch("domain_knowledge_graph_creater.write_neo4j") as writer, redirect_stdout(console):
            status = main(["--root", str(self.root), "--check-config"])
        self.assertEqual(status, 0)
        builder.assert_not_called()
        writer.assert_not_called()
        self.assertIn(str(self.config_path), console.getvalue())
        self.assertIn("bolt://file.invalid", console.getvalue())
        self.assertNotIn("file_password", console.getvalue())

    def test_incomplete_file_blocks_cli_before_build_or_write(self):
        self.config_path.write_text("NEO4J_URI=bolt://file.invalid\n", encoding="utf-8")
        with patch("domain_knowledge_graph_creater.KnowledgeGraphBuilder") as builder, \
             patch("domain_knowledge_graph_creater.write_neo4j") as writer, redirect_stdout(io.StringIO()):
            status = main(["--root", str(self.root)])
        self.assertEqual(status, 1)
        builder.assert_not_called()
        writer.assert_not_called()

    def test_neo4j_logs_connection_batches_commit_and_verified_counts(self):
        graph = self.builder().build()
        fake_module, _, _, _, _ = self.fake_neo4j(graph)
        with patch.dict(sys.modules, {"neo4j": fake_module}), self.assertLogs(LOGGER, level="INFO") as logs:
            write_neo4j(graph, "bolt://uri_user:uri_password@example.invalid?secret=value", "test_user", "test_password")
        output = "\n".join(logs.output)
        for stage in ["Neo4j target", "actual database=testdb", "BEFORE", "Node batch", "Relationship batch", "COMMIT confirmed", "AFTER", "VERIFIED"]:
            self.assertIn(stage, output)
        for secret in ["uri_password", "uri_user", "test_password", "secret=value"]:
            self.assertNotIn(secret, output)

    def test_post_commit_mismatch_does_not_report_verified_success(self):
        graph = self.builder().build()
        fake_module, _, _, _, _ = self.fake_neo4j(graph, after={"nodes": 1, "edges": 0})
        with patch.dict(sys.modules, {"neo4j": fake_module}), self.assertLogs(LOGGER, level="INFO") as logs:
            with self.assertRaisesRegex(ValueError, "COMMITTED, but verification failed"):
                write_neo4j(graph, "bolt://example.invalid", "test_user", "test_password")
        self.assertNotIn("VERIFIED Neo4j", "\n".join(logs.output))

    def test_console_and_log_file_redact_passwords(self):
        console = io.StringIO()
        log_file = self.root / "diagnostics.log"
        try:
            with patch.dict(os.environ, {"NEO4J_PASSWORD": "hide_this_password"}), redirect_stdout(console):
                configure_logging(debug=True, log_file=log_file)
                LOGGER.debug("password=hide_this_password uri=neo4j+s://user:uri_password@host.invalid")
            for output in [console.getvalue(), log_file.read_text(encoding="utf-8")]:
                self.assertIn("[REDACTED]", output)
                self.assertNotIn("hide_this_password", output)
                self.assertNotIn("uri_password", output)
        finally:
            configure_logging()

    def test_cli_reports_underlying_neo4j_error_with_redacted_traceback(self):
        config = {"uri": "bolt://example.invalid", "user": "test_user", "password": "hide_this_password", "database": "testdb"}
        driver_error = type("DriverError", (Exception,), {})
        neo4j_error = type("Neo4jError", (Exception,), {})
        error = neo4j_error("authentication denied: hide_this_password")
        error.code = "Neo.ClientError.Security.Unauthorized"
        errors = types.SimpleNamespace(DriverError=driver_error, Neo4jError=neo4j_error)
        console = io.StringIO()
        with patch("domain_knowledge_graph_creater.load_neo4j_config", return_value=config), \
             patch("domain_knowledge_graph_creater.write_neo4j", side_effect=error), \
             patch.dict(sys.modules, {"neo4j.exceptions": errors}), redirect_stdout(console):
            status = main(["--root", str(self.root), "--spec", str(self.spec_path), "--debug"])
        self.assertEqual(status, 1)
        self.assertIn("authentication denied", console.getvalue())
        self.assertIn("Neo.ClientError.Security.Unauthorized", console.getvalue())
        self.assertIn("Failure traceback", console.getvalue())
        self.assertNotIn("hide_this_password", console.getvalue())


if __name__ == "__main__":
    unittest.main()
