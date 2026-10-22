"""Offline retrieval contract tests; no database, network, or model calls."""

import copy
import json
from pathlib import Path
import random
import unittest
from unittest.mock import MagicMock, patch

try:
    from knowledge_context.domain_retrieval import DOMAIN_READ_QUERY, DomainKnowledgeRetriever
except ModuleNotFoundError:
    from domain_retrieval import DOMAIN_READ_QUERY, DomainKnowledgeRetriever


HERE = Path(__file__).resolve().parent
DATASET = "ground_truth_domains"


class DomainRetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = json.loads((HERE / "domain_knowledge_graph.json").read_text(encoding="utf-8"))

    def retrieve(self, domain="reaction_diffusion", graph=None, task=""):
        return DomainKnowledgeRetriever(graph=self.graph if graph is None else graph).get_domain_context(domain, task)

    def test_reference_steps_follow_source_order_not_storage_order(self):
        graph = copy.deepcopy(self.graph)
        random.Random(19).shuffle(graph["nodes"])
        random.Random(20).shuffle(graph["edges"])
        result = self.retrieve(graph=graph)
        steps = result["knowledge"]["references"][0]["ordered_steps"]
        self.assertEqual([step["order"] for step in steps], [0, 1, 2])
        self.assertIn("cache_reaction", steps[0]["id"])
        self.assertIn("update_u", steps[1]["id"])
        self.assertIn("update_v", steps[2]["id"])
        self.assertEqual(result["context"], self.retrieve()["context"])

    def test_cached_reaction_is_read_at_produced_version(self):
        steps = self.retrieve()["knowledge"]["references"][0]["ordered_steps"]
        self.assertEqual({read["name"]: read["state_version"] for read in steps[0]["reads"]}, {"u": 0, "v": 0})
        self.assertEqual([(write["name"], write["state_version"]) for write in steps[0]["writes"]], [("reaction", 1)])
        self.assertEqual({read["name"]: read["state_version"] for read in steps[1]["reads"]}, {"u": 0, "reaction": 1})
        self.assertEqual({read["name"]: read["state_version"] for read in steps[2]["reads"]}, {"v": 0, "reaction": 1})
        self.assertNotIn("u", {read["name"] for read in steps[2]["reads"]})

    def test_julia_temporary_parameter_is_not_lost(self):
        recipe = self.retrieve("julia_set")["knowledge"]["references"][0]
        self.assertIn("c", {value["name"] for value in recipe["temporary_values"]})
        steps = recipe["ordered_steps"]
        self.assertEqual([(write["name"], write["state_version"]) for write in steps[0]["writes"]], [("c", 1)])
        self.assertIn(("c", 1), {(read["name"], read["state_version"]) for read in steps[1]["reads"]})
        self.assertIn(("complex_state", 1), {(read["name"], read["state_version"]) for read in steps[2]["reads"]})

    def test_burgers_advection_uses_already_diffused_state(self):
        steps = self.retrieve("burgers2d")["knowledge"]["references"][0]["ordered_steps"]
        self.assertEqual([step["order"] for step in steps], [0, 1])
        self.assertEqual([read["state_version"] for read in steps[0]["reads"]], [0])
        self.assertEqual([read["state_version"] for read in steps[1]["reads"]], [1])

    def test_empty_graph_and_unknown_domain_fall_back_cleanly(self):
        self.assertEqual(self.retrieve("unknown")["status"], "missing_domain")
        for graph in ({}, {"schema_version": 1, "nodes": [], "edges": []}):
            result = self.retrieve(graph=graph)
            self.assertEqual(result["status"], "missing_domain")
            self.assertEqual(result["context"], "")
            self.assertEqual(result["target_functions"], [])
            self.assertEqual(result["statistics"]["nodes"], 0)
        with patch.object(Path, "read_text", side_effect=AssertionError("implicit file read")):
            result = DomainKnowledgeRetriever().get_domain_context("heat_flow")
        self.assertEqual(result["status"], "unavailable")

    def test_missing_or_blank_domain_does_not_infer_from_task(self):
        result = self.retrieve("", task="simulate Burgers equation")
        self.assertEqual(result["status"], "missing_domain")
        self.assertEqual(result["source_mode"], "local_json")

    def test_schema_and_adapter_ambiguities_fail_visibly(self):
        with self.assertRaisesRegex(ValueError, "schema_version"):
            DomainKnowledgeRetriever(graph={"schema_version": 99})
        with self.assertRaisesRegex(ValueError, "not both"):
            DomainKnowledgeRetriever(graph={}, driver=MagicMock())
        with self.assertRaisesRegex(ValueError, "dataset"):
            DomainKnowledgeRetriever(dataset="")

    def test_dataset_isolation_filters_local_nodes_and_edges(self):
        result = DomainKnowledgeRetriever(graph=self.graph, dataset="different_dataset").get_domain_context("heat_flow")
        self.assertEqual(result["status"], "missing_domain")
        graph = copy.deepcopy(self.graph)
        extra = {"id": "other", "label": "Guidance", "properties": {"dataset": "other", "text": "FOREIGN_DATASET_SENTINEL"}}
        graph["nodes"].append(extra)
        reference = next(node for node in graph["nodes"] if node["label"] == "ReferenceSimulation" and node["properties"]["domain"] == "heat_flow")
        graph["edges"].append({"id": "bad_edge", "source": reference["id"], "target": "other", "type": "GUIDED_BY", "properties": {"dataset": DATASET}})
        self.assertNotIn("FOREIGN_DATASET_SENTINEL", self.retrieve("heat_flow", graph)["context"])

    def test_explicit_selection_does_not_follow_incoming_shared_api_edges(self):
        result = self.retrieve("heat_flow")
        self.assertEqual({recipe["domain"] for recipe in result["knowledge"]["references"]}, {"heat_flow"})
        self.assertNotIn("cache_reaction", result["context"])
        self.assertNotIn("julia_set_ground_truth.py", result["context"])

    def test_public_aliases_are_usable_code_search_hints(self):
        result = self.retrieve("heat_flow")
        self.assertIn("CenteredGrid", result["target_classes"])
        self.assertIn("diffuse.implicit", result["target_functions"])
        self.assertNotIn("implicit", result["target_functions"])
        self.assertFalse(any("._" in name for name in result["target_functions"] + result["target_classes"]))
        hints = result["knowledge"]["verified_api_hints"]
        self.assertTrue(all(hint["verification"] == "local_static_definition" for hint in hints))
        self.assertTrue(all(hint["provenance"]["source_path"] for hint in hints))

    def test_public_alias_survives_missing_observed_call(self):
        graph = copy.deepcopy(self.graph)
        for edge in graph["edges"]:
            if edge["type"] == "USES_API":
                edge["properties"].pop("observed_call", None)
        result = self.retrieve("heat_flow", graph)
        self.assertIn("diffuse.implicit", result["target_functions"])
        self.assertIn("CenteredGrid", result["target_classes"])

    def test_unresolved_apis_are_candidates_without_verification_claim(self):
        result = self.retrieve()
        candidates = result["knowledge"]["unresolved_api_candidates"]
        self.assertGreater(len(candidates), 0)
        self.assertTrue(all(candidate["status"] == "candidate_only_not_verified" for candidate in candidates))
        self.assertNotIn("np.stack", result["target_functions"])

    def test_whole_program_and_save_expression_are_not_prompt_context(self):
        graph = copy.deepcopy(self.graph)
        for node in graph["nodes"]:
            if node["label"] == "ReferenceSimulation":
                node["properties"]["source_text"] = "COMPLETE_REFERENCE_SOURCE_SENTINEL"
                node["properties"]["update_scope_source"] = "COMPLETE_UPDATE_SCOPE_SENTINEL"
            if node["label"] in ("SaveOperation", "OutputSpec"):
                node["properties"]["expression"] = "REFERENCE_SAVE_EXPRESSION_SENTINEL"
            if node["label"] == "SourceDefinition":
                node["properties"]["expression"] = "def initial_condition(x):\n    # HELPER_BODY_COMMENT_SENTINEL\n    return x * 2\n"
        result = self.retrieve(graph=graph)
        for sentinel in ("COMPLETE_REFERENCE_SOURCE_SENTINEL", "COMPLETE_UPDATE_SCOPE_SENTINEL",
                         "REFERENCE_SAVE_EXPRESSION_SENTINEL", "HELPER_BODY_COMMENT_SENTINEL"):
            self.assertNotIn(sentinel, result["context"])
        helper = result["knowledge"]["references"][0]["helpers"][0]
        self.assertEqual(helper["arguments"], ["x"])
        self.assertEqual(helper["return_expressions"], ["x * 2"])

    def test_helper_formulas_parameters_and_output_conventions_are_preserved(self):
        recipe = self.retrieve()["knowledge"]["references"][0]
        helper = recipe["helpers"][0]
        self.assertEqual(helper["name"], "initial_condition")
        self.assertTrue(helper["local_expressions"])
        self.assertTrue(helper["return_expressions"])
        self.assertIn("dt", {parameter["name"] for parameter in recipe["parameters"]})
        self.assertTrue(all(output["axis_order"] == ["time", "x", "y"] for output in recipe["outputs"]))
        self.assertTrue(all(output["initial_frame"] == "included_by_profile" for output in recipe["outputs"]))

    def test_task_requirements_override_reference_output_defaults(self):
        result = self.retrieve(task="Use dt=0.01, save new_u.npy and new_v.npy")
        knowledge = result["knowledge"]
        self.assertEqual(knowledge["task_requested_output_filenames"], ["new_u.npy", "new_v.npy"])
        self.assertIn("authoritative", knowledge["authority_policy"]["priority"])
        self.assertIn("boundaries", knowledge["authority_policy"]["conflicts"])
        self.assertTrue(knowledge["explicit_discrepancies"])
        self.assertTrue(all("filename" not in output and "expression" not in output
                            for output in knowledge["references"][0]["outputs"]))

    def test_input_snapshot_and_returned_context_are_independent(self):
        graph = copy.deepcopy(self.graph)
        retriever = DomainKnowledgeRetriever(graph=graph)
        graph["nodes"].clear()
        first = retriever.get_domain_context("heat_flow")
        expected = first["context"]
        first["knowledge"]["references"].clear()
        second = retriever.get_domain_context("heat_flow")
        self.assertEqual(second["context"], expected)

    def test_default_context_budget_preserves_every_recipe_step(self):
        for domain, step_count in (("burgers2d", 2), ("heat_flow", 1), ("julia_set", 3), ("reaction_diffusion", 3)):
            with self.subTest(domain=domain):
                result = self.retrieve(domain)
                self.assertLessEqual(len(result["context"]), 16000)
                payload = json.loads(result["context"].partition("\n")[2])
                self.assertEqual(sum(len(recipe["ordered_steps"]) for recipe in payload["references"]), step_count)
                self.assertTrue(payload["evidence_sources"])
                self.assertTrue(all(step["evidence"]["source"] in payload["evidence_sources"]
                                    for recipe in payload["references"] for step in recipe["ordered_steps"]))
                self.assertFalse(result["context_budget"]["core_exceeds_budget"])

    def test_oversized_core_is_flagged_without_cutting_json_or_steps(self):
        result = DomainKnowledgeRetriever(graph=self.graph, max_context_chars=1000).get_domain_context("reaction_diffusion")
        self.assertTrue(result["context_budget"]["core_exceeds_budget"])
        payload = json.loads(result["context"].partition("\n")[2])
        self.assertEqual(len(payload["references"][0]["ordered_steps"]), 3)
        with self.assertRaisesRegex(ValueError, "max_context_chars"):
            DomainKnowledgeRetriever(max_context_chars=1)

    def test_bounded_neo4j_paths_cover_current_owned_recipe_edges(self):
        outgoing = {}
        for edge in self.graph["edges"]:
            outgoing.setdefault(edge["source"], []).append(edge)
        for reference in (node for node in self.graph["nodes"] if node["label"] == "ReferenceSimulation"):
            distances = {reference["id"]: 0}
            frontier = [reference["id"]]
            for owner in frontier:
                for edge in outgoing.get(owner, []):
                    if edge["target"] not in distances:
                        distances[edge["target"]] = distances[owner] + 1
                        frontier.append(edge["target"])
            self.assertTrue(all(distances[owner] + 1 <= 4 for owner in distances if outgoing.get(owner)), reference["id"])

    def make_driver(self, domain="heat_flow"):
        local = self.retrieve(domain)
        selected = {node["id"] for node in self.graph["nodes"] if node["properties"].get("dataset") == DATASET}
        # A driver fixture may return the whole dataset. Client-side explicit
        # reference selection must still isolate the chosen domain.
        record = {
            "nodes": [{"id": node["id"], "labels": ["DomainKG", node["label"]], "properties": node["properties"]}
                      for node in self.graph["nodes"] if node["id"] in selected],
            "edges": copy.deepcopy(self.graph["edges"]) * 2,
        }
        driver = MagicMock()
        session = driver.session.return_value.__enter__.return_value
        tx = MagicMock()
        tx.run.return_value.single.return_value = record
        session.execute_read.side_effect = lambda fn: fn(tx)
        return driver, session, tx, local

    def test_neo4j_read_uses_safe_parameterized_query_and_explicit_database(self):
        driver, session, tx, local = self.make_driver()
        retriever = DomainKnowledgeRetriever(driver=driver, database="domain_db")
        result = retriever.get_domain_context("heat_flow")
        self.assertEqual(result["context"], local["context"])
        self.assertEqual(result["source_mode"], "neo4j")
        driver.session.assert_called_once_with(database="domain_db", default_access_mode="READ")
        tx.run.assert_called_once_with(DOMAIN_READ_QUERY, dataset=DATASET, domain="heat_flow")
        session.execute_write.assert_not_called()
        driver.close.assert_not_called()
        for forbidden in ("CREATE ", "MERGE ", "DELETE ", "SET ", "REMOVE ", "source_text", "update_scope_source"):
            self.assertNotIn(forbidden, DOMAIN_READ_QUERY)
        self.assertIn("*0..4", DOMAIN_READ_QUERY)
        self.assertIn("all(r IN relationships(path) WHERE r.dataset = $dataset)", DOMAIN_READ_QUERY)

    def test_neo4j_domain_cannot_change_query_structure(self):
        driver, _, tx, _ = self.make_driver()
        malicious = "heat_flow'}) DETACH DELETE n //"
        result = DomainKnowledgeRetriever(driver=driver).get_domain_context(malicious)
        self.assertEqual(result["status"], "missing_domain")
        self.assertEqual(tx.run.call_args.kwargs["domain"], malicious)
        self.assertNotIn(malicious, tx.run.call_args.args[0])

    def test_neo4j_null_projection_fields_match_local_export(self):
        driver, _, tx, local = self.make_driver()
        record = tx.run.return_value.single.return_value
        for node in record["nodes"]:
            node["properties"] = {"literal_json": None, "configured_aliases": None, "parameter_kind": None,
                                  "source_sha256": None, **node["properties"]}
        result = DomainKnowledgeRetriever(driver=driver).get_domain_context("heat_flow")
        self.assertEqual(result["context"], local["context"])

    def test_neo4j_empty_result_is_clean_and_read_errors_remain_visible(self):
        driver, session, tx, _ = self.make_driver()
        tx.run.return_value.single.return_value = None
        result = DomainKnowledgeRetriever(driver=driver).get_domain_context("missing")
        self.assertEqual(result["status"], "missing_domain")
        session.execute_read.side_effect = RuntimeError("read unavailable")
        with self.assertRaisesRegex(RuntimeError, "read unavailable"):
            DomainKnowledgeRetriever(driver=driver).get_domain_context("heat_flow")


if __name__ == "__main__":
    unittest.main()
