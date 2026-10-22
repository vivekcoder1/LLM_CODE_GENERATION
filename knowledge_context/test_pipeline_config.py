"""Credential isolation and driver-construction tests; entirely offline."""

import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline_config as config


class PipelineConfigTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "knowledge_context").mkdir()
        self.code = self.root / ".env"
        self.domain = self.root / "knowledge_context" / ".env"
        self.code.write_text(
            "NEO4J_URI=neo4j+s://code.invalid\nNEO4J_USER=code_user\n"
            "NEO4J_PASSWORD=code_secret_42\nNEO4J_DATABASE=code_db\n"
            "ANTHROPIC_API_KEY=sk-ant-test-explicit-42\nANTHROPIC_MODEL=file-model\n",
            encoding="utf-8",
        )
        self.domain.write_text(
            "NEO4J_URI=neo4j+s://domain.invalid\nNEO4J_USER=domain_user\n"
            "NEO4J_PASSWORD=domain_secret_42\nNEO4J_DATABASE=domain_db\n",
            encoding="utf-8",
        )

    def test_explicit_code_and_domain_files_do_not_mix(self):
        code = config.load_connection_config(self.code, "code", self.root)
        domain = config.load_connection_config(self.domain, "domain", self.root)
        self.assertEqual(code, {"uri": "neo4j+s://code.invalid", "user": "code_user", "password": "code_secret_42", "database": "code_db"})
        self.assertEqual(domain, {"uri": "neo4j+s://domain.invalid", "user": "domain_user", "password": "domain_secret_42", "database": "domain_db"})

    def test_inherited_values_are_ignored_and_environment_is_unchanged(self):
        with patch.dict(os.environ, {
            "NEO4J_URI": "bolt://ambient.invalid", "NEO4J_USER": "ambient",
            "NEO4J_PASSWORD": "ambient_secret", "NEO4J_DATABASE": "ambient_db",
            "ANTHROPIC_API_KEY": "ambient_key", "ANTHROPIC_MODEL": "ambient_model",
        }):
            before = copy.deepcopy(dict(os.environ))
            self.assertEqual(config.load_connection_config(self.domain, "domain", self.root)["uri"], "neo4j+s://domain.invalid")
            self.assertEqual(config.load_llm_config(self.code)["api_key"], "sk-ant-test-explicit-42")
            self.assertEqual(dict(os.environ), before)

    def test_relative_path_is_explicitly_resolved_under_root(self):
        self.assertEqual(config.load_connection_config("knowledge_context/.env", "domain", self.root)["database"], "domain_db")

    def test_missing_selected_file_never_falls_back(self):
        self.domain.unlink()
        with self.assertRaisesRegex(ValueError, "No fallback"):
            config.load_connection_config(self.domain, "domain", self.root)

    def test_missing_domain_password_never_uses_root_or_environment(self):
        self.domain.write_text("NEO4J_URI=bolt://domain.invalid\nNEO4J_USER=domain_user\n", encoding="utf-8")
        with patch.dict(os.environ, {"NEO4J_PASSWORD": "ambient_secret"}):
            with self.assertRaisesRegex(ValueError, "Missing NEO4J_PASSWORD"):
                config.load_connection_config(self.domain, "domain", self.root)

    def test_connection_interpolation_rejected_for_every_setting(self):
        for name in ("NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD", "NEO4J_DATABASE"):
            with self.subTest(name=name):
                self.domain.write_text(
                    "NEO4J_URI=bolt://domain.invalid\nNEO4J_USER=domain_user\nNEO4J_PASSWORD=secret_42\n"
                    + name + "=${AMBIENT}\n", encoding="utf-8",
                )
                with self.assertRaisesRegex(ValueError, "literal configured value"):
                    config.load_connection_config(self.domain, "domain", self.root)

    def test_placeholder_credentials_rejected_without_echoing_value(self):
        for value in ("YOUR-PASSWORD", "<secret>", "changeme", "replace_me"):
            with self.subTest(value=value):
                self.domain.write_text("NEO4J_URI=bolt://domain.invalid\nNEO4J_USER=neo4j\nNEO4J_PASSWORD=" + value, encoding="utf-8")
                with self.assertRaises(ValueError) as raised:
                    config.load_connection_config(self.domain, "domain", self.root)
                self.assertNotIn(value, str(raised.exception))

    def test_uri_with_embedded_credentials_is_rejected(self):
        self.domain.write_text("NEO4J_URI=bolt://neo4j:hidden@domain.invalid\nNEO4J_USER=neo4j\nNEO4J_PASSWORD=secret_42\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "without embedded credentials") as raised:
            config.load_connection_config(self.domain, "domain", self.root)
        self.assertNotIn("hidden", str(raised.exception))

    def test_invalid_role_and_implicit_file_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "role"):
            config.load_connection_config(self.code, "all", self.root)
        with self.assertRaisesRegex(ValueError, "explicit"):
            config.load_connection_config(None, "code", self.root)

    def test_llm_only_file_does_not_require_database_settings(self):
        self.code.write_text("ANTHROPIC_API_KEY=sk-ant-test-api-only\n", encoding="utf-8")
        self.assertEqual(config.load_llm_config(self.code), {"api_key": "sk-ant-test-api-only", "workspace_id": None, "model": config.DEFAULT_MODEL})

    def test_llm_model_precedence_and_optional_workspace(self):
        self.code.write_text(self.code.read_text() + "ANTHROPIC_WORKSPACE_ID=workspace-42\n", encoding="utf-8")
        self.assertEqual(config.load_llm_config(self.code)["model"], "file-model")
        explicit = config.load_llm_config(self.code, model="explicit-model")
        self.assertEqual(explicit["model"], "explicit-model")
        self.assertEqual(explicit["workspace_id"], "workspace-42")

    def test_llm_missing_key_does_not_use_environment(self):
        self.code.write_text("ANTHROPIC_MODEL=file-model\n", encoding="utf-8")
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "ambient_key"}):
            with self.assertRaisesRegex(ValueError, "Missing ANTHROPIC_API_KEY"):
                config.load_llm_config(self.code)

    def test_llm_interpolation_and_placeholders_rejected(self):
        for value in ("${ANTHROPIC_API_KEY}", "YOUR-API-KEY", "<api-key>", "changeme"):
            with self.subTest(value=value):
                self.code.write_text("ANTHROPIC_API_KEY=" + value, encoding="utf-8")
                with self.assertRaises(ValueError) as raised:
                    config.load_llm_config(self.code)
                self.assertNotIn(value, str(raised.exception))

    def test_llm_model_and_workspace_must_be_literal_if_provided(self):
        for name in ("ANTHROPIC_MODEL", "ANTHROPIC_WORKSPACE_ID"):
            with self.subTest(name=name):
                self.code.write_text("ANTHROPIC_API_KEY=sk-ant-test-literal\n" + name + "=${SETTING}\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "literal configured value"):
                    config.load_llm_config(self.code)

    def test_describe_connection_is_read_only_and_secret_free(self):
        values = config.load_connection_config(self.code, "code", self.root)
        values["uri"] += "?routing=hidden-query"
        description = config.describe_connection(values, self.code, "code")
        self.assertEqual(description["mode"], "READ")
        self.assertEqual(description["env_file"], str(self.code.resolve()))
        self.assertEqual(description["database"], "code_db")
        self.assertEqual(description["uri"], "neo4j+s://code.invalid")
        self.assertNotIn("password", description)
        self.assertNotIn("secret_42", json.dumps(description))
        self.assertNotIn("hidden-query", json.dumps(description))

    def test_redaction_covers_database_password_and_api_key(self):
        config.load_connection_config(self.domain, "domain", self.root)
        config.load_llm_config(self.code)
        message = config.redact_message("domain_secret_42 sk-ant-test-explicit-42 neo4j://user:hidden@host")
        self.assertNotIn("domain_secret_42", message)
        self.assertNotIn("sk-ant-test-explicit-42", message)
        self.assertNotIn("user:hidden", message)

    def test_driver_construction_is_lazy_bounded_and_does_not_create_session(self):
        factory = MagicMock()
        fake = types.SimpleNamespace(GraphDatabase=factory)
        values = config.load_connection_config(self.code, "code", self.root)
        with patch.dict(sys.modules, {"neo4j": fake}):
            driver = config.create_read_driver(values)
        factory.driver.assert_called_once_with(
            "neo4j+s://code.invalid", auth=("code_user", "code_secret_42"),
            connection_timeout=10.0, connection_acquisition_timeout=20.0,
            max_transaction_retry_time=0.0,
        )
        driver.session.assert_not_called()
        driver.verify_connectivity.assert_not_called()
        driver.execute_query.assert_not_called()

    def test_driver_constructor_error_is_redacted(self):
        factory = MagicMock()
        factory.driver.side_effect = RuntimeError("bad auth code_secret_42")
        with patch.dict(sys.modules, {"neo4j": types.SimpleNamespace(GraphDatabase=factory)}):
            with self.assertRaises(ValueError) as raised:
                config.create_read_driver({"uri": "bolt://code.invalid", "user": "neo4j", "password": "code_secret_42"})
        self.assertNotIn("code_secret_42", str(raised.exception))
        self.assertIn("[REDACTED]", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
