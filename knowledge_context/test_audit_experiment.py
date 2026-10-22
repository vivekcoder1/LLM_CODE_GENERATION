"""Offline diagnostics, output-provenance and documentation-retention tests."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

try:
    from knowledge_context.audit_experiment import LOCAL_PRIOR, build_audit, diagnose_array, write_audit
except ModuleNotFoundError:
    from audit_experiment import LOCAL_PRIOR, build_audit, diagnose_array, write_audit


HERE = Path(__file__).resolve().parent


class ExperimentAuditTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.directory = self.root / "runs" / "heat_flow" / "historical_rerun_0"
        self.directory.mkdir(parents=True)
        self.graph = json.loads((HERE / "domain_knowledge_graph.json").read_text(encoding="utf-8"))

    def save(self, array, filename="wrong_name.npy", directory=None):
        path = (directory or self.directory) / filename
        np.save(path, array)
        return path

    def run_record(self, path=None):
        record = {"run_id": "heat_historical_0", "domain": "heat_flow", "variant": "historical_rerun", "replicate": 0,
            "config_id": "config", "run_dir": str(self.directory), "artifact_provenance": "existing_outputs_rerun",
            "execution": {"status": "passed"}, "api_resolution": [], "alignment": {"generated_time_axis": 0}}
        if path:
            record["observed_artifacts"] = [{"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}]
        return record

    def manifest(self, records):
        return {"completed_utc": "2026-10-22T02:04:31+00:00", "mode": "retrieval", "runs": records}

    def build(self, records):
        return build_audit(self.manifest(records), self.graph, experiment_root=self.root, chunk_elements=2)

    def test_nan_inf_counts_first_frame_and_finite_only_range(self):
        path = self.save(np.array([[1., 2.], [np.nan, np.inf], [-np.inf, -7.]]))
        result = diagnose_array(path, chunk_elements=2)
        self.assertEqual(result["array_status"], "nonfinite")
        self.assertEqual(result["finite_count"], 3)
        self.assertEqual(result["nonfinite_count"], 3)
        self.assertEqual(result["first_nonfinite_frame"], 1)
        self.assertEqual(result["finite_min"], -7.)
        self.assertEqual(result["finite_max"], 2.)
        json.dumps(result, allow_nan=False)

    def test_fortran_array_and_nonzero_frame_axis_use_temporal_first(self):
        array = np.asfortranarray(np.ones((3, 4, 2)))
        array[2, 3, 0] = np.inf
        array[0, 1, 1] = np.nan
        result = diagnose_array(self.save(array), time_axis=1, chunk_elements=3)
        self.assertEqual(result["first_nonfinite_frame"], 1)
        self.assertEqual(result["frame_count"], 4)
        self.assertEqual(result["finite_count"], 22)

    def test_all_nonfinite_empty_scalar_and_nonnumeric_arrays(self):
        all_bad = diagnose_array(self.save(np.array([[np.nan], [np.inf]])))
        self.assertEqual(all_bad["finite_count"], 0)
        self.assertIsNone(all_bad["finite_min"])
        self.assertIsNone(all_bad["finite_max"])
        empty = diagnose_array(self.save(np.empty((0, 2))))
        self.assertEqual(empty["array_status"], "empty")
        self.assertEqual(empty["finite_count"], 0)
        scalar = diagnose_array(self.save(np.array(5)))
        self.assertEqual(scalar["finite_min"], 5)
        self.assertIsNone(scalar["frame_axis"])
        nonnumeric = diagnose_array(self.save(np.array(["alpha", "beta"])))
        self.assertEqual(nonnumeric["array_status"], "nonnumeric")

    def test_complex_ranges_are_explicit_magnitudes_and_safe_on_overflow(self):
        path = self.save(np.array([3 + 4j, 1 + 0j, complex(np.nan, 1)]))
        result = diagnose_array(path)
        self.assertEqual(result["range_basis"], "complex_magnitudes")
        self.assertEqual(result["finite_min"], 1.)
        self.assertEqual(result["finite_max"], 5.)
        self.assertEqual(result["nonfinite_count"], 1)
        maximum = np.finfo(np.float64).max
        overflowing = diagnose_array(self.save(np.array([complex(maximum, maximum)])))
        self.assertEqual(overflowing["finite_count"], 1)
        self.assertEqual(overflowing["range_omitted_count"], 1)
        self.assertIsNone(overflowing["finite_max"])
        json.dumps(overflowing, allow_nan=False)

    def test_object_pickle_and_invalid_axis_are_not_accepted(self):
        result = diagnose_array(self.save(np.array([{"secret": "never unpickle"}], dtype=object)))
        self.assertEqual(result["array_status"], "unreadable")
        axis = diagnose_array(self.save(np.ones((2, 2))), time_axis=4)
        self.assertEqual(axis["array_status"], "unreadable")
        with self.assertRaisesRegex(ValueError, "chunk_elements"):
            diagnose_array(self.directory / "missing.npy", chunk_elements=0)

    def test_wrong_output_name_remains_diagnostic_and_is_not_renamed(self):
        path = self.save(np.ones((2, 2)), "heat_flow_trj.npy")
        report = self.build([self.run_record(path)])
        row = report["tables"]["artifact_diagnostics"][0]
        self.assertFalse(row["contract_name_match"])
        self.assertEqual(row["scoring_policy"], "diagnostic_only_not_a_score")
        self.assertIsNone(row["task_component"])
        self.assertEqual(row["array_status"], "finite")
        self.assertEqual(row["hash_status"], "matched")
        self.assertTrue(path.is_file())
        self.assertFalse((self.directory / "heat_flow_temperature_trj.npy").exists())
        self.assertNotIn("rmse", row)

    def test_requested_filename_is_recognized_without_creating_a_score(self):
        path = self.save(np.ones((2, 2)), "heat_flow_temperature_trj.npy")
        row = self.build([self.run_record(path)])["tables"]["artifact_diagnostics"][0]
        self.assertTrue(row["contract_name_match"])
        self.assertEqual(row["task_component"], "main")
        self.assertEqual(row["scoring_policy"], "diagnostic_only_not_a_score")

    def test_changed_hash_and_outside_paths_are_not_loaded(self):
        path = self.save(np.ones((2, 2)))
        record = self.run_record(path)
        np.save(path, np.zeros((2, 2)))
        row = self.build([record])["tables"]["artifact_diagnostics"][0]
        self.assertEqual(row["array_status"], "changed_since_manifest")
        self.assertNotIn("finite_count", row)
        outside = self.save(np.ones((1, 1)), directory=self.root)
        row = self.build([self.run_record(outside)])["tables"]["artifact_diagnostics"][0]
        self.assertEqual(row["array_status"], "outside_isolated_run")

    def test_mapping_statuses_and_ambiguity_are_not_invented_as_exact_matches(self):
        record = self.run_record()
        record["variant"] = "combined"
        record["api_resolution"] = [
            {"quality": "exact_alias", "status": "resolved", "code_id": "a"},
            {"quality": "legacy_file_name_candidate", "status": "resolved_candidate", "code_id": "b"},
            {"quality": "ambiguous_alias", "status": "ambiguous", "code_id": None},
            {"quality": "unresolved", "status": "unresolved", "code_id": None},
            {"quality": "adapter_unavailable", "status": "unavailable", "code_id": None},
            {"quality": "exact_alias", "status": "ambiguous", "code_id": "inconsistent"},
        ]
        audit = self.build([record])
        counts = audit["tables"]["api_resolution_summary"][0]
        self.assertEqual(counts["exact_alias_count"], 1)
        self.assertEqual(counts["legacy_candidate_count"], 1)
        self.assertEqual(counts["ambiguous_count"], 2)
        self.assertEqual(counts["unavailable_count"], 1)
        self.assertEqual(counts["unresolved_count"], 1)
        self.assertEqual(sum(row["resolved_for_retrieval"] for row in audit["tables"]["api_resolution"]), 2)

    def test_aggregate_mapping_metadata_does_not_turn_unknown_counts_into_zero(self):
        record = self.run_record()
        record["api_resolution"] = {"resolved": 4}
        summary = self.build([record])["tables"]["api_resolution_summary"][0]
        self.assertEqual(summary["mapping_records_status"], "aggregate_or_invalid_format")
        self.assertIsNone(summary["mapping_count"])
        self.assertIsNone(summary["exact_alias_count"])

    def test_local_prior_provenance_and_cached_state_dependencies_remain_explicit(self):
        record = self.run_record()
        record["domain"] = "reaction_diffusion"
        tables = self.build([record])["tables"]
        self.assertEqual(tables["domain_prior_summary"][0]["evidence_origin"], LOCAL_PRIOR)
        self.assertEqual([step["order"] for step in tables["domain_update_steps"]], [0, 1, 2])
        cached_reads = [row for row in tables["domain_dependencies"] if row["relationship"] == "READS" and row["target"] == "reaction"]
        self.assertEqual(len(cached_reads), 2)
        self.assertTrue(all(row["state_version"] == 1 for row in cached_reads))
        self.assertTrue(all(row["source_sha256"] for row in tables["domain_update_steps"]))
        coverage = {row["verification_class"] for row in tables["domain_api_coverage"]}
        self.assertEqual(coverage, {"verified_local_static_definition", "unresolved_candidate_only"})
        self.assertTrue(all(row["reference_only_not_task_output_contract"] for row in tables["domain_outputs"]))

    def documentation_pair(self):
        records = []
        for variant in ("code_only", "combined"):
            directory = self.root / "runs" / "heat_flow" / (variant + "_0")
            directory.mkdir()
            text = "**Import Path:** `phi.flow.diffuse.implicit`\n" if variant == "combined" else "**Import Path:** `phi.flow.Box`\n"
            (directory / "code_context.md").write_text(text, encoding="utf-8")
            # Misleading occurrence in the combined prompt must not count as
            # baseline API documentation retained in code_context.md.
            (directory / "context.md").write_text("**Import Path:** `phi.flow.diffuse.implicit`\n", encoding="utf-8")
            record = self.run_record()
            record.update(run_id=variant + "_0", variant=variant, run_dir=str(directory),
                          metadata={"code_context_hash": hashlib.sha256(text.encode()).hexdigest()})
            if variant == "combined":
                record["api_resolution"] = [
                    {"observed_call": "diffuse.implicit", "quality": "exact_alias", "status": "resolved",
                     "code_id": "implicit", "code_import_path": "phi.flow.diffuse.implicit"},
                    {"observed_call": "missing", "quality": "unresolved", "status": "unresolved", "code_id": None},
                ]
            records.append(record)
        return records

    def test_documentation_retention_uses_literal_code_context_fields_only(self):
        tables = self.build(self.documentation_pair())["tables"]
        summary = tables["api_documentation_summary"][0]
        self.assertEqual(summary["total_bindings"], 2)
        self.assertEqual(summary["matchable_resolved_bindings"], 1)
        self.assertEqual(summary["excluded_unresolved_bindings"], 1)
        self.assertEqual(summary["combined_documented_count"], 1)
        self.assertEqual(summary["code_only_documented_count"], 0)
        unresolved = tables["api_documentation_retention"][1]
        self.assertIsNone(unresolved["combined_documented"])
        self.assertIsNone(unresolved["code_only_documented"])

    def test_changed_code_context_has_unknown_retention_not_false_absence(self):
        records = self.documentation_pair()
        (Path(records[0]["run_dir"]) / "code_context.md").write_text("changed", encoding="utf-8")
        summary = self.build(records)["tables"]["api_documentation_summary"][0]
        self.assertEqual(summary["code_only_document_status"], "code_context_changed_since_manifest")
        self.assertIsNone(summary["code_only_documented_count"])

    def test_incomplete_manifest_is_rejected_and_output_is_never_overwritten(self):
        with self.assertRaisesRegex(ValueError, "incomplete"):
            build_audit({"runs": []}, self.graph, experiment_root=self.root)
        manifest_path, graph_path = self.root / "manifest.json", self.root / "graph.json"
        manifest_path.write_text(json.dumps(self.manifest([self.run_record()])), encoding="utf-8")
        graph_path.write_text(json.dumps(self.graph), encoding="utf-8")
        paths = write_audit(manifest_path, self.root / "audit", domain_graph_path=graph_path, chunk_elements=2)
        self.assertTrue(paths["markdown"].is_file())
        self.assertGreaterEqual(len(paths), 14)
        report = json.loads(paths["json"].read_text(encoding="utf-8"))
        self.assertIn("sha256", report["sources"]["local_domain_snapshot"])
        self.assertTrue(report["limitations"])
        with self.assertRaises(FileExistsError):
            write_audit(manifest_path, self.root / "audit", domain_graph_path=graph_path)
        with self.assertRaisesRegex(ValueError, "outside simulation"):
            write_audit(manifest_path, self.directory / "audit", domain_graph_path=graph_path)


if __name__ == "__main__":
    unittest.main()
