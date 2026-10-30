# Detailed integration experiment audit

API mappings come from the completed run. Recipe tables describe the selected local snapshot; they are not a fresh live-graph inspection.

## API resolution by retrieval arm

| domain | variant | retrieval_status | mapping_count | exact_alias_count | legacy_candidate_count | ambiguous_count | unresolved_count | unavailable_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| burgers2d | code_only | restored_not_requeried | 0 | 0 | 0 | 0 | 0 | 0 |
| burgers2d | combined | restored_not_requeried | 5 | 5 | 0 | 0 | 0 | 0 |
| heat_flow | code_only | restored_not_requeried | 0 | 0 | 0 | 0 | 0 | 0 |
| heat_flow | combined | restored_not_requeried | 4 | 4 | 0 | 0 | 0 | 0 |
| julia_set | code_only | restored_not_requeried | 0 | 0 | 0 | 0 | 0 | 0 |
| julia_set | combined | restored_not_requeried | 2 | 2 | 0 | 0 | 0 | 0 |
| reaction_diffusion | code_only | restored_not_requeried | 0 | 0 | 0 | 0 | 0 | 0 |
| reaction_diffusion | combined | restored_not_requeried | 3 | 2 | 0 | 0 | 1 | 0 |

## Local domain-prior coverage

| domain | status | nodes | edges | fields | parameters | helpers | ordered_steps | outputs | verified_apis | api_candidates |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| burgers2d | available | 23 | 29 | 1 | 1 | 0 | 2 | 1 | 5 | 4 |
| heat_flow | available | 25 | 34 | 2 | 4 | 0 | 1 | 1 | 4 | 4 |
| julia_set | available | 27 | 41 | 2 | 6 | 0 | 3 | 1 | 2 | 5 |
| reaction_diffusion | available | 40 | 74 | 2 | 12 | 1 | 3 | 2 | 3 | 6 |

## API documentation retention for the same resolved hints

| domain | total_bindings | matchable_resolved_bindings | excluded_unresolved_bindings | code_only_documented_count | combined_documented_count |
| --- | --- | --- | --- | --- | --- |
| burgers2d | 5 | 5 | 0 | 1 | 5 |
| heat_flow | 4 | 4 | 0 | 0 | 4 |
| julia_set | 2 | 2 | 0 | 0 | 2 |
| reaction_diffusion | 3 | 2 | 1 | 1 | 2 |

## Observed output diagnostics

| domain | variant | filename | contract_name_match | array_status | shape | dtype | finite_count | nonfinite_count | first_nonfinite_frame | finite_min | finite_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| burgers2d | code_only | burgers2d_velocity_trj.npy | True | nonfinite | [101, 64, 64, 2] | float32 | 325838 | 501554 | 13 | -1.5499860012170774e+38 | 6.583761428188549e+37 |
| burgers2d | combined | burgers2d_velocity_trj.npy | True | finite | [101, 64, 64, 2] | float32 | 827392 | 0 |  | -5.770984246034061e-10 | 0.8850861191749573 |
| heat_flow | code_only | heat_flow_temperature_trj.npy | True | nonfinite | [101, 100, 50] | float32 | 294926 | 210074 | 16 | -2.703652907482417e+38 | 1.7596375619743754e+38 |
| heat_flow | combined | heat_flow_temperature_trj.npy | True | finite | [101, 100, 50] | float32 | 505000 | 0 |  | 0.0 | 0.9890159964561462 |
| julia_set | code_only | julia_set_domain_trj.npy | True | finite | [100, 256, 256] | float64 | 6553600 | 0 |  | 0.0 | 50.0 |
| julia_set | combined | julia_set_domain_trj.npy | True | finite | [100, 256, 256] | float32 | 6553600 | 0 |  | 0.0 | 19.0 |
| reaction_diffusion | code_only | reaction_diffusion_u_trj.npy | True | finite | [101, 100, 100] | float32 | 1010000 | 0 |  | -0.9999998211860657 | 0.999984085559845 |
| reaction_diffusion | code_only | reaction_diffusion_v_trj.npy | True | finite | [101, 100, 100] | float32 | 1010000 | 0 |  | -1.7889177799224854 | 1.8555850982666016 |
| reaction_diffusion | combined | reaction_diffusion_u_trj.npy | True | finite | [101, 100, 100] | float32 | 1010000 | 0 |  | -0.9999998211860657 | 0.999984085559845 |
| reaction_diffusion | combined | reaction_diffusion_v_trj.npy | True | finite | [101, 100, 100] | float32 | 1010000 | 0 |  | -1.7889177799224854 | 1.8555850982666016 |

## Data tables

- [api_resolution.csv](api_resolution.csv) (14 rows)

- [api_resolution_summary.csv](api_resolution_summary.csv) (8 rows)

- [domain_prior_summary.csv](domain_prior_summary.csv) (4 rows)

- [domain_fields.csv](domain_fields.csv) (7 rows)

- [domain_parameters.csv](domain_parameters.csv) (23 rows)

- [domain_helpers.csv](domain_helpers.csv) (1 rows)

- [domain_update_steps.csv](domain_update_steps.csv) (9 rows)

- [domain_dependencies.csv](domain_dependencies.csv) (34 rows)

- [domain_outputs.csv](domain_outputs.csv) (5 rows)

- [domain_api_coverage.csv](domain_api_coverage.csv) (33 rows)

- [domain_guidance.csv](domain_guidance.csv) (12 rows)

- [api_documentation_retention.csv](api_documentation_retention.csv) (14 rows)

- [api_documentation_summary.csv](api_documentation_summary.csv) (4 rows)

- [artifact_diagnostics.csv](artifact_diagnostics.csv) (10 rows)

## Limitations

- API resolution records describe the completed run's metadata joins; no live graph was queried by this audit.

- Domain recipe tables come from the explicitly selected local graph snapshot. They do not prove that the live domain graph had identical content.

- Artifact diagnostics describe only manifest-reported files inside each isolated run directory. Recorded hashes are checked when available.

- Wrong-name arrays remain diagnostic observations. No file is renamed, substituted into a requested output, or awarded a task-contract score.

- Finite-only ranges omit NaN/infinite entries; a finite range does not establish stability, correctness, or agreement with a reference.

- First nonfinite frame is zero-based on the run's declared generated_time_axis (default 0). Scalar arrays have no frame axis.

- For complex arrays, finite min/max are magnitudes, as labelled. Empty and nonnumeric arrays have no numerical range.

- Historical-script reruns do not measure generation improvements from combined retrieval. This audit makes no causal improvement claim.

- API documentation retention matches only literal Import Path fields in code_context.md for the same resolved hints. It excludes unresolved hints from the matchable denominator and does not count resolution metadata in the combined prompt.

## Source hashes

```json
{
  "manifest": {
    "path": "D:\\Vivek\\research\\integration_runs\\20261028T181330_344848Z_saved_context\\manifest.json",
    "sha256": "01ae70ef48ed4e9ddd3119514cee0a41738eb5d0e881b45d85c21eb023760018"
  },
  "local_domain_snapshot": {
    "path": "D:\\Vivek\\research\\knowledge_context\\domain_knowledge_graph.json",
    "sha256": "6320d316662d8be090aafc3620d353feeb5d95130012548e30ad9db0d2b46a07",
    "evidence_origin": "local_domain_graph_snapshot_not_live_query"
  }
}
```
