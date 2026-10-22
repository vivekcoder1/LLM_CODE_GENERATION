"""Offline regression checks for the real code-graph pipeline integration."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("tested_kg_pipeline", ROOT / "llm-querying.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
Pipeline = module.E2ERagPipeline


class Embedder:
    def encode(self, value):
        return np.ones(3) if isinstance(value, str) else np.ones((len(value), 3))


def row(src, tgt, relationship=None):
    result = {"relationship": relationship}
    for side, node in (("src", src), ("tgt", tgt)):
        result.update({side + "_" + key: value for key, value in node.items()})
    return result


FUNCTION = {"id": "f", "type": "Function", "name": "implicit", "is_public": True,
            "import_path": "phi.flow.diffuse.implicit", "gen_desc": "Implicit diffusion step", "doc": "implicit(field, dt)"}
PARAMETER = {"id": "p", "type": "Parameter", "name": "field", "is_public": False}
TYPE = {"id": "t", "type": "Type", "name": "Field", "is_public": False}
DESCRIPTION = {"id": "d", "type": "GeneratedDescription", "name": None,
               "is_public": False, "gen_desc": "Implicit diffusion step"}


class PipelineIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.driver = MagicMock()
        self.client = MagicMock()
        self.pipeline = Pipeline(driver=self.driver, client=self.client, embed_model=Embedder(),
                                 domain_retriever=object(), database="unit", model="test-model")

    def test_injection_does_not_load_config_or_embedding_model(self):
        with patch("knowledge_context.pipeline_config.load_connection_config", side_effect=AssertionError), \
             patch("knowledge_context.pipeline_config.load_llm_config", side_effect=AssertionError):
            instance = Pipeline(driver=self.driver, client=self.client, domain_retriever=object())
        self.assertIsNone(instance.embed_model)
        self.assertEqual(self.client.mock_calls, [])

    def test_disabled_llm_blocks_even_injected_client(self):
        self.pipeline.allow_llm = False
        for operation in (lambda: self.pipeline.generate_search_blueprint("task"),
                          lambda: self.pipeline.generate_grounded_code("task", "code")):
            with self.assertRaisesRegex(RuntimeError, "disabled"):
                operation()
        self.client.messages.create.assert_not_called()

    def test_sessions_use_read_access_and_selected_database(self):
        self.pipeline._session()
        self.driver.session.assert_called_once_with(database="unit", default_access_mode="READ")

    def test_injected_resources_are_not_closed(self):
        self.pipeline.close()
        self.driver.close.assert_not_called()
        self.client.close.assert_not_called()

    def test_parameter_type_metadata_survives_filtering_and_row_order(self):
        relations = [row(FUNCTION, FUNCTION), row(PARAMETER, TYPE, "of_type"),
                     row(FUNCTION, PARAMETER, "has_parameter"), row(FUNCTION, TYPE, "returns_type")]
        retained = self.pipeline.filter_subgraph("diffusion", relations, top_k=1)
        text = self.pipeline.serialize_subgraph(retained)
        self.assertIn("field (Field)", text)
        self.assertIn("**Returns:** `Field`", text)
        self.assertEqual(len(retained), 4)

    def test_definition_with_only_description_edge_remains_available(self):
        retained = self.pipeline.filter_subgraph("diffusion", [row(FUNCTION, DESCRIPTION, "has_description")], top_k=1)
        text = self.pipeline.serialize_subgraph(retained)
        self.assertIn("[Function] implicit", text)
        self.assertIn("Implicit diffusion step", text)
        self.assertNotIn("### [GeneratedDescription]", text)

    def test_metadata_closure_is_idempotent_and_ignores_unselected_definitions(self):
        private = dict(FUNCTION, id="private", is_public=False, name="_private")
        raw = [row(FUNCTION, PARAMETER, "has_parameter"), row(PARAMETER, TYPE, "of_type"),
               row(private, DESCRIPTION, "has_description")]
        selected = [row(FUNCTION, FUNCTION)]
        result = self.pipeline.complete_code_metadata(raw, selected)
        self.assertEqual(result, self.pipeline.complete_code_metadata(raw, result))
        self.assertFalse(any(r["src_id"] == "private" for r in result))

    def test_method_description_rows_respect_owning_class_quota(self):
        owner = dict(FUNCTION, id="owner", type="Class", name="Grid")
        methods = [dict(FUNCTION, id="m" + str(i), type="Method", name="method" + str(i)) for i in range(4)]
        raw = [row(method, dict(DESCRIPTION, id="d" + str(i)), "has_description")
               for i, method in enumerate(methods)]
        raw.extend(row(owner, method, "has_method") for method in methods)
        retained = self.pipeline.filter_subgraph("grid", raw, top_k=20, max_methods_per_class=1)
        selected = {item["tgt_id"] for item in retained if item.get("tgt_type") == "Method"}
        self.assertEqual(len(selected), 1)

    def test_namespace_attribute_import_and_class_import_are_valid_patterns(self):
        cls = dict(FUNCTION, id="c", type="Class", name="CenteredGrid", import_path="phi.flow.CenteredGrid")
        text = self.pipeline.serialize_subgraph([row(FUNCTION, FUNCTION), row(cls, cls)])
        self.assertIn("from phi.flow import diffuse; diffuse.implicit(...)", text)
        self.assertIn("from phi.flow import CenteredGrid; CenteredGrid(...)", text)
        self.assertNotIn("from phi.flow.diffuse import implicit", text)

    def test_public_method_uses_initialized_instance(self):
        method = dict(FUNCTION, id="m", type="Method", name="native", import_path="phi.flow.Tensor.native")
        text = self.pipeline.serialize_subgraph([row(method, method)])
        self.assertIn("initialized `Tensor` instance", text)
        self.assertIn("instance.native(...)", text)

    def response(self, text, stop_reason="end_turn"):
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=text)], stop_reason=stop_reason,
                               usage=SimpleNamespace(input_tokens=42, output_tokens=12))

    def test_generation_prioritizes_task_and_records_usage(self):
        self.client.messages.create.return_value = self.response("```python\nx = 1\n```")
        code = self.pipeline.generate_grounded_code("CURRENT TASK", "CODE DOCS", domain_context="DOMAIN PRIOR")
        call = self.client.messages.create.call_args.kwargs
        self.assertEqual(code, "x = 1")
        self.assertIn("CURRENT TASK has authority", call["system"])
        self.assertIn("local step/initialization/helper functions", call["system"])
        self.assertIn("DOMAIN PRIOR", call["messages"][0]["content"])
        self.assertEqual(call["model"], "test-model")
        self.assertEqual(call["temperature"], 0)
        self.assertEqual(self.pipeline.last_generation_metadata["output_tokens"], 12)

    def test_truncated_generation_is_rejected(self):
        self.client.messages.create.return_value = self.response("broken =", "max_tokens")
        with self.assertRaisesRegex(ValueError, "incomplete code"):
            self.pipeline.generate_grounded_code("task", "docs")

    def test_generation_sees_unresolved_mapping_evidence(self):
        self.client.messages.create.return_value = self.response("x = 1")
        mappings = [{"observed_call": "field.laplace", "status": "unresolved", "quality": "unresolved", "code_id": None}]
        self.pipeline.generate_grounded_code("task", "docs", domain_context="recipe", api_resolution=mappings)
        prompt = self.client.messages.create.call_args.kwargs["messages"][0]["content"]
        self.assertIn("DOMAIN TO CODE API RESOLUTION EVIDENCE", prompt)
        self.assertIn('"observed_call": "field.laplace"', prompt)
        self.assertIn('"status": "unresolved"', prompt)
        self.assertIn("not runtime verification", prompt)

    def test_blueprint_errors_are_redacted_before_logging(self):
        self.client.messages.create.side_effect = ValueError("raw sensitive error")
        with patch("knowledge_context.pipeline_config.redact_message", return_value="redacted") as redact, \
             patch("builtins.print") as output:
            self.pipeline.generate_search_blueprint("task")
        redact.assert_called_once()
        self.assertEqual(self.pipeline.last_blueprint_error, "redacted")
        self.assertFalse(any("raw sensitive" in str(call) for call in output.mock_calls))


if __name__ == "__main__":
    unittest.main()
