"""Offline domain/code composition tests with injected pipeline and graph fakes."""

import copy
import unittest
from unittest.mock import MagicMock

try:
    from knowledge_context.combined_retrieval import API_READ_QUERY, retrieve_context
except ModuleNotFoundError:
    from combined_retrieval import API_READ_QUERY, retrieve_context


def hint(observed="diffuse.implicit", path="phi/physics/diffuse.py", component_type="Function"):
    return {"id": "domain:" + observed, "public_name": observed, "observed_call": observed,
            "qualified_name": "phi.physics." + observed,
            "configured_aliases": ["phi.physics." + observed], "definition_path": path,
            "component_type": component_type, "verification": "local_static_definition"}


def candidate(code_id="diffuse.py:implicit", name="implicit", import_path="phi.flow.diffuse.implicit",
              filename="diffuse.py", public=True):
    return {"id": code_id, "name": name, "component_type": "Function", "is_public_api": public,
            "import_path": import_path, "defining_files": [filename]}


def relation(code_id="diffuse.py:implicit", name="implicit", public=True):
    return {"src_id": code_id, "src_name": name, "src_type": "Function", "src_is_public": public,
            "src_import_path": "phi.flow.diffuse.implicit", "src_doc": "Implicit diffusion documentation",
            "tgt_id": code_id + "(field)", "tgt_name": "field", "tgt_type": "Parameter",
            "tgt_is_public": False, "relationship": "has_parameter"}


class CombinedRetrievalTests(unittest.TestCase):
    def pipeline(self, candidates=None, hints=None, domain_status="available"):
        pipeline = MagicMock()
        pipeline.database = "code_database"
        bundle = {
            "status": domain_status, "context": "CURATED DOMAIN RECIPE",
            "semantic_queries": ["reference implicit diffusion", "reference scalar grid"],
            "target_classes": ["CenteredGrid"], "target_functions": ["diffuse.implicit"],
            "api_hints": [hint()] if hints is None else hints,
            "statistics": {"nodes": 17},
        }
        pipeline.domain_retriever.get_domain_context.return_value = bundle
        session = pipeline.driver.session.return_value.__enter__.return_value
        tx = MagicMock()
        tx.run.return_value.data.return_value = [candidate()] if candidates is None else candidates
        session.execute_read.side_effect = lambda fn: fn(tx)
        pipeline.find_seed_nodes.return_value = ["base_seed"]
        pipeline.traverse_subgraph.return_value = [relation()]
        pipeline.filter_subgraph.return_value = [relation()]
        pipeline.serialize_subgraph.return_value = "PUBLIC API DOCS"
        pipeline.generate_search_blueprint.return_value = self.blueprint()
        return pipeline, session, tx

    @staticmethod
    def blueprint():
        return {"semantic_queries": ["base query"], "target_classes": ["Box"], "target_functions": ["math.cos"]}

    def test_combined_merges_planner_hints_and_uses_terminal_index_names(self):
        pipeline, _, _ = self.pipeline()
        base = self.blueprint()
        result = retrieve_context(pipeline, "heat_flow", "TASK", blueprint=base)
        pipeline.generate_search_blueprint.assert_not_called()
        self.assertEqual(base, self.blueprint())
        self.assertEqual(result["blueprint"]["semantic_queries"], ["base query", "reference implicit diffusion", "reference scalar grid"])
        self.assertEqual(result["blueprint"]["target_classes"], ["Box", "CenteredGrid"])
        self.assertEqual(result["blueprint"]["target_functions"], ["cos", "implicit"])
        self.assertIn("CURATED DOMAIN RECIPE", result["domain_context"])
        self.assertIn("PUBLIC API DOCS", result["code_context"])
        self.assertIn("CURRENT TASK REQUIREMENTS TAKE PRIORITY", result["context"])

    def test_exact_alias_resolution_adds_seed_and_retains_caveat(self):
        pipeline, _, tx = self.pipeline()
        result = retrieve_context(pipeline, "heat_flow", "TASK", blueprint=self.blueprint())
        record = result["api_resolution"][0]
        self.assertEqual(record["quality"], "exact_alias")
        self.assertEqual(record["code_id"], "diffuse.py:implicit")
        self.assertIn("annotations", record["namespace_caveat"])
        self.assertIn("diffuse.py:implicit", pipeline.traverse_subgraph.call_args.args[0])
        self.assertEqual(result["statistics"]["resolved_api_links"], 1)
        self.assertEqual(result["statistics"]["unresolved_api_links"], 0)
        tx.run.assert_called_once_with(API_READ_QUERY, names=["implicit"])

    def test_unique_file_basename_match_is_explicit_candidate(self):
        row = candidate(import_path="phi.flow.implicit", filename="D:\\library\\diffuse.py")
        pipeline, _, _ = self.pipeline(candidates=[row])
        result = retrieve_context(pipeline, "heat_flow", "TASK", blueprint=self.blueprint())
        record = result["api_resolution"][0]
        self.assertEqual(record["quality"], "legacy_file_name_candidate")
        self.assertEqual(record["status"], "resolved_candidate")
        self.assertIn("does not prove", record["namespace_caveat"])

    def test_duplicate_exact_aliases_are_not_resolved_by_filename_guess(self):
        rows = [candidate("a:implicit"), candidate("b:implicit", filename="other.py")]
        pipeline, _, _ = self.pipeline(candidates=rows)
        result = retrieve_context(pipeline, "heat_flow", "TASK", blueprint=self.blueprint())
        record = result["api_resolution"][0]
        self.assertIsNone(record["code_id"])
        self.assertEqual(record["quality"], "ambiguous_alias")
        self.assertEqual(record["candidate_count"], 2)
        self.assertEqual(pipeline.traverse_subgraph.call_args.args[0], ["base_seed"])

    def test_duplicate_legacy_file_candidates_remain_ambiguous(self):
        rows = [candidate("a:implicit", import_path="phi.flow.implicit"),
                candidate("b:implicit", import_path="phi.flow.implicit")]
        pipeline, _, _ = self.pipeline(candidates=rows)
        result = retrieve_context(pipeline, "heat_flow", "TASK", blueprint=self.blueprint())
        self.assertEqual(result["api_resolution"][0]["quality"], "ambiguous_legacy_file")
        self.assertEqual(result["statistics"]["unresolved_api_links"], 1)

    def test_terminal_name_alone_cannot_resolve_wrong_file(self):
        pipeline, _, _ = self.pipeline(candidates=[candidate(import_path="phi.flow.other.implicit", filename="other.py")])
        result = retrieve_context(pipeline, "heat_flow", "TASK", blueprint=self.blueprint())
        self.assertIsNone(result["api_resolution"][0]["code_id"])
        self.assertEqual(result["api_resolution"][0]["quality"], "unresolved")

    def test_private_code_candidates_are_never_seeded(self):
        pipeline, _, _ = self.pipeline(candidates=[candidate(public=False)])
        result = retrieve_context(pipeline, "heat_flow", "TASK", blueprint=self.blueprint())
        self.assertIsNone(result["api_resolution"][0]["code_id"])
        self.assertEqual(result["api_resolution"][0]["candidate_count"], 0)

    def test_low_scoring_required_public_api_is_pinned_before_ranked_noise(self):
        pipeline, _, _ = self.pipeline()
        noise = [relation("noise:" + str(i), "irrelevant") for i in range(30)]
        pipeline.traverse_subgraph.return_value = noise + [relation()]
        pipeline.filter_subgraph.return_value = noise[:24]
        result = retrieve_context(pipeline, "heat_flow", "TASK", blueprint=self.blueprint())
        serialized_rows = pipeline.serialize_subgraph.call_args.args[0]
        self.assertEqual(serialized_rows[0]["src_id"], "diffuse.py:implicit")
        self.assertEqual(len(serialized_rows), 24)
        self.assertEqual(result["statistics"]["code_nodes"], 18)
        self.assertEqual(result["statistics"]["raw_relations"], 31)

    def test_private_raw_relation_cannot_be_pinned_by_id(self):
        pipeline, _, _ = self.pipeline()
        pipeline.traverse_subgraph.return_value = [relation(public=False)]
        pipeline.filter_subgraph.return_value = []
        result = retrieve_context(pipeline, "heat_flow", "TASK", blueprint=self.blueprint())
        self.assertEqual(pipeline.serialize_subgraph.call_args.args[0], [])
        self.assertEqual(result["statistics"]["code_nodes"], 0)

    def test_code_node_statistics_follow_serializer_definition_selection(self):
        pipeline, _, _ = self.pipeline(hints=[])
        rows = [
            {"src_id": "file.py", "src_type": "File", "src_is_public": True,
             "tgt_id": "C", "tgt_type": "Class", "tgt_is_public": True, "relationship": "defines_class"},
            {"src_id": "C", "src_type": "Class", "src_is_public": True,
             "tgt_id": "C.method", "tgt_type": "Method", "tgt_is_public": True, "relationship": "has_method"},
        ]
        pipeline.traverse_subgraph.return_value = rows
        pipeline.filter_subgraph.return_value = rows
        result = retrieve_context(pipeline, "heat_flow", "TASK", variant="code_only", blueprint=self.blueprint())
        self.assertEqual(result["statistics"]["code_nodes"], 2)

    def test_code_only_bypasses_domain_driver_and_domain_retriever(self):
        pipeline, _, _ = self.pipeline()
        pipeline.domain_retriever.get_domain_context.side_effect = AssertionError("domain should not run")
        result = retrieve_context(pipeline, "heat_flow", "TASK", variant="code_only", blueprint=self.blueprint())
        pipeline.domain_retriever.get_domain_context.assert_not_called()
        pipeline.driver.session.assert_not_called()
        self.assertEqual(result["domain_status"], "disabled")
        self.assertEqual(result["domain_context"], "")
        self.assertEqual(result["api_resolution"], [])
        self.assertEqual(result["statistics"]["domain_nodes"], 0)

    def test_missing_domain_uses_code_context_and_reports_status(self):
        pipeline, _, _ = self.pipeline(hints=[], domain_status="missing_domain")
        pipeline.domain_retriever.get_domain_context.return_value.update(
            context="", semantic_queries=[], target_classes=[], target_functions=[], statistics={"nodes": 0})
        result = retrieve_context(pipeline, "unknown", "TASK", blueprint=self.blueprint())
        self.assertEqual(result["domain_status"], "missing_domain")
        self.assertEqual(result["domain_context"], "")
        self.assertIn("PUBLIC API DOCS", result["context"])
        pipeline.driver.session.assert_not_called()

    def test_no_code_driver_produces_unavailable_resolution_without_connecting(self):
        pipeline, _, _ = self.pipeline()
        pipeline.driver = None
        result = retrieve_context(pipeline, "heat_flow", "TASK", blueprint=self.blueprint())
        self.assertEqual(result["api_resolution"][0]["quality"], "adapter_unavailable")
        self.assertEqual(result["statistics"]["resolved_api_links"], 0)

    def test_shared_blueprint_and_sane_query_caps_are_deterministic(self):
        pipeline, _, _ = self.pipeline()
        base = self.blueprint()
        base["semantic_queries"] = ["q" + str(i) for i in range(50)]
        base["target_functions"] = ["f" + str(i) for i in range(50)]
        before = copy.deepcopy(base)
        result = retrieve_context(pipeline, "heat_flow", "TASK", blueprint=base)
        self.assertEqual(len(result["blueprint"]["semantic_queries"]), 12)
        self.assertEqual(len(result["blueprint"]["target_functions"]), 32)
        self.assertIn("reference implicit diffusion", result["blueprint"]["semantic_queries"])
        self.assertIn("implicit", result["blueprint"]["target_functions"])
        self.assertEqual(base, before)

    def test_structural_metadata_completion_runs_after_pinning(self):
        pipeline, _, _ = self.pipeline()
        metadata = {"src_id": "diffuse.py:implicit(field)", "src_type": "Parameter", "src_name": "field",
                    "tgt_id": "Field", "tgt_type": "Type", "tgt_name": "Field", "relationship": "of_type"}
        completed = []

        def complete(raw, selected):
            self.assertEqual(selected[0]["src_id"], "diffuse.py:implicit")
            completed.extend(selected + [metadata])
            return completed

        pipeline.complete_code_metadata = complete
        result = retrieve_context(pipeline, "heat_flow", "TASK", blueprint=self.blueprint(), settings={"top_k": 1})
        self.assertEqual(pipeline.serialize_subgraph.call_args.args[0], completed)
        self.assertEqual(result["statistics"]["filtered_relations"], 2)
        self.assertIn("API RESOLUTION EVIDENCE", result["context"])
        self.assertIn("does not prove package", result["context"])

    def test_driver_calls_are_read_only_explicit_and_not_closed(self):
        pipeline, session, _ = self.pipeline()
        retrieve_context(pipeline, "heat_flow", "TASK", blueprint=self.blueprint())
        pipeline.driver.session.assert_called_once_with(database="code_database", default_access_mode="READ")
        session.execute_write.assert_not_called()
        pipeline.driver.close.assert_not_called()
        self.assertIn("NOT n:DomainKG", API_READ_QUERY)
        self.assertIn("n.is_public_api", API_READ_QUERY)
        for mutation in ("CREATE ", "MERGE ", "DELETE ", "SET ", "REMOVE "):
            self.assertNotIn(mutation, API_READ_QUERY)

    def test_metadata_settings_and_automatic_planner_are_forwarded(self):
        pipeline, _, _ = self.pipeline()
        result = retrieve_context(pipeline, "heat_flow", "TASK", settings={"top_k": 12, "max_nodes": 8},
                                  domain_graph_sha256="snapshot_hash")
        pipeline.generate_search_blueprint.assert_called_once_with("TASK")
        self.assertEqual(pipeline.filter_subgraph.call_args.kwargs["top_k"], 12)
        self.assertEqual(pipeline.serialize_subgraph.call_args.kwargs["max_nodes"], 8)
        self.assertEqual(result["provenance"]["domain_graph_sha256"], "snapshot_hash")
        self.assertEqual(result["statistics"]["context_chars"], len(result["context"]))

    def test_invalid_variant_and_budgets_fail_before_external_calls(self):
        pipeline, _, _ = self.pipeline()
        with self.assertRaisesRegex(ValueError, "variant"):
            retrieve_context(pipeline, "heat_flow", "TASK", variant="something_else")
        with self.assertRaisesRegex(ValueError, "max_nodes"):
            retrieve_context(pipeline, "heat_flow", "TASK", settings={"max_nodes": 0})
        pipeline.find_seed_nodes.assert_not_called()


if __name__ == "__main__":
    unittest.main()
