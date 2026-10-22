"""Numerical integrity, freshness, and experiment provenance tests; entirely offline."""

import copy
import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from combined_evaluation import (  # noqa: E402
    REFERENCE_SPECS, REQUESTED_OUTPUTS, build_report, compare_trajectories,
    evaluate_run, sha256_file, write_reports,
)


class CombinedEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.run_dir = self.root / "isolated"
        self.run_dir.mkdir()
        self.generated = self.run_dir / "generated.npy"
        self.reference = self.root / "reference.npy"

    def arrays(self, generated, reference):
        np.save(self.generated, generated)
        np.save(self.reference, reference)
        return compare_trajectories(self.generated, self.reference)

    def record(self, domain="heat_flow", variant="combined"):
        spec = REFERENCE_SPECS[domain]["main"]
        ref = self.root / spec["paths"][0]
        ref.parent.mkdir(exist_ok=True)
        shape = spec["shape"]
        np.save(ref, np.ones(shape, dtype=np.float32))
        artifact = self.run_dir / REQUESTED_OUTPUTS[domain]["main"]
        np.save(artifact, np.ones(shape, dtype=np.float32))
        return {
            "run_id": variant, "domain": domain, "variant": variant, "config_id": "fixed",
            "run_dir": str(self.run_dir), "artifact_provenance": "fresh",
            "generation": {"status": "generated"},
            "execution": {"status": "passed", "execution_ok": True, "duration_s": 1.25},
            "artifacts": {"main": str(artifact)},
            "context": {"code_nodes": 12, "domain_nodes": 20},
            "metadata": {"model": "test", "seed": 1, "temperature": 0,
                         "task_hash": "task", "code_context_hash": "code", "domain_context_hash": "domain"},
        }

    def test_conventional_rmse_not_spatial_l2_norm(self):
        result = self.arrays(np.ones((3, 2, 2)) * 3, np.ones((3, 2, 2)))
        self.assertEqual(result["status"], "measured")
        self.assertEqual(result["rmse"], 2)
        self.assertEqual(result["relative_rmse"], 2)
        self.assertEqual(result["mean_l2"], 4)

    def test_integer_subtraction_does_not_wrap(self):
        result = self.arrays(np.zeros((2, 2), dtype=np.uint8), np.full((2, 2), 255, dtype=np.uint8))
        self.assertEqual(result["rmse"], 255)

    def test_complex_magnitudes_are_preserved(self):
        result = self.arrays(np.full((2, 2), 1j), np.zeros((2, 2), dtype=complex))
        self.assertEqual(result["rmse"], 1)
        self.assertIsNone(result["relative_rmse"])

    def test_zero_reference_matching_output_is_zero_error(self):
        result = self.arrays(np.zeros((2, 2)), np.zeros((2, 2)))
        self.assertEqual(result["relative_rmse"], 0)

    def test_nonfinite_arrays_are_not_scored(self):
        for value in (np.nan, np.inf):
            for bad_side in ("generated", "reference"):
                with self.subTest(value=value, bad_side=bad_side):
                    generated, reference = np.ones((2, 2)), np.ones((2, 2))
                    (generated if bad_side == "generated" else reference)[0, 0] = value
                    result = self.arrays(generated, reference)
                    self.assertEqual(result["status"], "comparison_error")
                    self.assertIsNone(result["rmse"])

    def test_pickle_object_arrays_are_rejected(self):
        result = self.arrays(np.array([[{"danger": "object"}]], dtype=object), np.ones((1, 1)))
        self.assertEqual(result["status"], "comparison_error")
        self.assertIn("allow_pickle=False", result["error"])

    def test_empty_scalar_and_nonnumeric_arrays_are_rejected(self):
        for array in (np.array([]), np.array(2), np.array([["a"]])):
            with self.subTest(shape=array.shape):
                self.assertEqual(self.arrays(array, array)["status"], "comparison_error")

    def test_shape_mismatch_never_broadcasts_or_truncates(self):
        result = self.arrays(np.ones((3, 2, 1)), np.ones((3, 2, 2)))
        self.assertEqual(result["status"], "comparison_error")
        self.assertIn("spatial/component", result["error"])
        result = self.arrays(np.ones((4, 2, 2)), np.ones((3, 2, 2)))
        self.assertEqual(result["status"], "comparison_error")

    def test_initial_frame_is_dropped_only_with_explicit_metadata(self):
        self.arrays(np.concatenate([np.full((1, 2), 99), np.ones((3, 2))]), np.ones((3, 2)))
        result = compare_trajectories(self.generated, self.reference, alignment={
            "generated_includes_initial": True, "reference_includes_initial": False,
        })
        self.assertEqual(result["rmse"], 0)
        self.assertIn("drop generated", result["alignment_actions"][0])

    def test_axis_permutation_requires_explicit_metadata(self):
        self.arrays(np.ones((3, 2, 4)), np.ones((2, 4, 3)))
        result = compare_trajectories(self.generated, self.reference, expected_shape=(3, 2, 4),
                                      alignment={"reference_time_axis": -1})
        self.assertEqual(result["status"], "measured")
        self.assertEqual(result["rmse"], 0)

    def test_equal_length_conflicting_initial_frame_semantics_are_rejected(self):
        self.arrays(np.ones((3, 2)), np.ones((3, 2)))
        result = compare_trajectories(self.generated, self.reference, alignment={
            "generated_includes_initial": False, "reference_includes_initial": True,
        })
        self.assertEqual(result["status"], "comparison_error")
        self.assertIn("timestamps", result["error"])

    def test_numeric_overflow_is_not_reported_as_a_measurement(self):
        result = self.arrays(np.full((2, 2), 1e300), np.ones((2, 2)))
        self.assertEqual(result["status"], "comparison_error")
        self.assertIsNone(result["rmse"])

    def test_reference_shape_must_match_ground_truth_profile(self):
        self.arrays(np.ones((3, 2)), np.ones((3, 2)))
        result = compare_trajectories(self.generated, self.reference, expected_shape=(4, 2))
        self.assertEqual(result["status"], "comparison_error")
        self.assertIn("source profile", result["error"])

    def test_missing_reference_is_unavailable_not_zero(self):
        record = self.record()
        (self.root / REFERENCE_SPECS["heat_flow"]["main"]["paths"][0]).unlink()
        result = evaluate_run(record, self.root)
        self.assertEqual(result["numerical_status"], "reference_unavailable")
        self.assertIsNone(result["numerical"][0]["rmse"])

    def test_unsupported_domain_is_not_applicable(self):
        result = evaluate_run({"domain": "smoke_plume"}, self.root)
        self.assertEqual(result["numerical_status"], "not_applicable")

    def test_cached_outputs_are_excluded_even_if_execution_passed(self):
        record = self.record()
        record["artifact_provenance"] = "cached"
        result = evaluate_run(record, self.root)
        self.assertEqual(result["numerical_status"], "not_current_run")

    def test_execution_failure_and_generation_block_are_explicit(self):
        record = self.record()
        record["execution"] = {"status": "not_run"}
        record["generation"] = {"status": "blocked", "error": "Missing credentials"}
        result = evaluate_run(record, self.root)
        self.assertEqual(result["numerical_status"], "not_run")
        self.assertEqual(result["generation_status"], "blocked")

    def test_artifacts_outside_run_directory_are_excluded(self):
        record = self.record()
        record["run_dir"] = str(self.root / "different_run")
        self.assertEqual(evaluate_run(record, self.root)["numerical_status"], "not_current_run")

    def test_wrong_filenames_do_not_score_accidental_old_outputs(self):
        record = self.record()
        old = Path(record["artifacts"]["main"])
        wrong = old.with_name("heat_flow_trj.npy")
        np.save(wrong, np.ones((2, 2)))
        record["artifacts"]["main"] = str(wrong)
        self.assertEqual(evaluate_run(record, self.root)["numerical_status"], "artifact_name_mismatch")

    def test_missing_generated_artifact_is_explicit(self):
        record = self.record()
        record["artifacts"] = {}
        self.assertEqual(evaluate_run(record, self.root)["numerical_status"], "generated_artifact_missing")

    def test_burgers_unseeded_initialization_is_caveated(self):
        result = evaluate_run(self.record("burgers2d"), self.root)
        self.assertEqual(result["numerical_status"], "measured_caveated")
        self.assertIn("unseeded Noise", result["caveats"][0])
        self.assertEqual(result["numerical"][0]["rmse"], 0)

    def test_heat_operator_mismatch_is_caveated_until_evidenced(self):
        record = self.record()
        self.assertEqual(evaluate_run(record, self.root)["numerical_status"], "measured_caveated")
        record["alignment"] = {"operator_matches_reference": True, "operator_evidence": "Compared 2D implicit calls"}
        self.assertEqual(evaluate_run(record, self.root)["numerical_status"], "measured")

    def test_rerun_can_measure_output_but_is_not_fresh_generation_pair(self):
        left = self.record(variant="code_only")
        right = self.record(variant="combined")
        right["artifact_provenance"] = "existing_outputs_rerun"
        report = build_report([left, right], project_root=self.root)
        self.assertEqual(report["runs"][1]["numerical_status"], "measured_caveated")
        self.assertEqual(report["paired_comparisons"][0]["comparison_status"], "not_fresh_generation")
        self.assertIsNone(report["paired_comparisons"][0]["rmse_delta"])

    def test_matched_pair_does_not_compare_caveated_numerical_values(self):
        left, right = self.record(variant="code_only"), self.record()
        report = build_report([left, right], project_root=self.root)
        pair = report["paired_comparisons"][0]
        self.assertEqual(pair["comparison_status"], "observed_pair")
        self.assertEqual(pair["execution_delta"], 0)
        self.assertEqual(pair["component_rmse_deltas"], [])

    def test_unmatched_generation_controls_block_claims(self):
        left, right = self.record(variant="code_only"), self.record()
        right["metadata"]["model"] = "different"
        pair = build_report([left, right], project_root=self.root)["paired_comparisons"][0]
        self.assertEqual(pair["comparison_status"], "unmatched_controls")
        self.assertIsNone(pair["execution_delta"])

    def test_domain_guided_code_context_changes_are_audited_as_pipeline_treatment(self):
        left, right = self.record(variant="code_only"), self.record()
        right["metadata"]["code_context_hash"] = "domain-guided-code"
        pair = build_report([left, right], project_root=self.root)["paired_comparisons"][0]
        self.assertEqual(pair["comparison_status"], "observed_pair")
        self.assertEqual(pair["combined_code_context_hash"], "domain-guided-code")

    def test_additional_metadata_is_preserved_in_json(self):
        record = self.record()
        record["metadata"]["provider_metadata"] = {"seed_supported": False}
        enriched = evaluate_run(record, self.root)
        self.assertEqual(enriched["metadata"]["provider_metadata"], {"seed_supported": False})

    def test_unmeasured_context_does_not_create_efficacy_claim(self):
        left, right = self.record(variant="code_only"), self.record()
        left["metadata"].pop("model")
        pair = build_report([left, right], project_root=self.root)["paired_comparisons"][0]
        self.assertEqual(pair["comparison_status"], "insufficient_control_metadata")

    def test_historical_rows_and_sources_remain_read_only(self):
        path = self.root / "historical.csv"
        path.write_text("domain,objective_score\nheat_flow,60.0\n", encoding="utf-8")
        before = sha256_file(path)
        report = build_report([], project_root=self.root, historical_paths=[path])
        self.assertEqual(report["historical_inventory"][0]["sha256"], before)
        self.assertEqual(report["historical_rows"][0]["data"]["objective_score"], "60.0")
        self.assertEqual(sha256_file(path), before)
        self.assertEqual(report["runs"], [])

    def test_report_contains_detailed_tables_and_blank_missing_scores(self):
        record = self.record()
        record["generation"] = {"status": "blocked", "error": "Missing credentials | safe detail"}
        record["execution"] = {"status": "not_run"}
        paths = write_reports([record], self.root / "reports", project_root=self.root,
                              tests=[{"name": "unit", "status": "passed", "tests": 3}],
                              graph_summary={"domain_nodes": 108, "api_links": 7})
        report = json.loads(paths["json"].read_text(encoding="utf-8"))
        self.assertIsNone(report["runs"][0]["numerical"][0]["rmse"])
        with paths["numerical"].open(newline="", encoding="utf-8") as handle:
            row = next(csv.DictReader(handle))
        self.assertEqual(row["rmse"], "")
        markdown = paths["markdown"].read_text(encoding="utf-8")
        self.assertIn("Missing credentials \\| safe detail", markdown)
        self.assertIn("Automated test outcomes", markdown)
        self.assertIn("Graph construction and retrieval coverage", markdown)
        self.assertIn("Historical files (read only", markdown)
        with paths["csv"].open(newline="", encoding="utf-8") as handle:
            row = next(csv.DictReader(handle))
        self.assertEqual(row["model"], "test")
        self.assertEqual(row["task_hash"], "task")
        self.assertEqual(row["generation_status"], "blocked")

    def test_report_refuses_to_overwrite_any_existing_report(self):
        output = self.root / "reports"
        output.mkdir()
        sentinel = output / "combined_evaluation.csv"
        sentinel.write_text("preserve", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            write_reports([], output, project_root=self.root)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve")
        self.assertFalse((output / "combined_evaluation.json").exists())

    def test_report_serialization_is_deterministic_and_does_not_mutate_inputs(self):
        record = self.record()
        original = copy.deepcopy(record)
        first = build_report([record], project_root=self.root)
        second = build_report([record], project_root=self.root)
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))
        self.assertEqual(record, original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
