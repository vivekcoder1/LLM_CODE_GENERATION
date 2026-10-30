# Combined knowledge graph experiment report

Fresh runs, graph/retrieval checks, and historical outcomes have separate provenance. Blank numerical values mean unmeasured. No overall quality ranking is assigned.

## Generation and execution outcomes

| run_id | domain | variant | retrieval_status | domain_status | plan_source | generation_status | execution_status | duration_s | artifact_provenance | numerical_status | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| burgers2d_code_only_0 | burgers2d | code_only | blocked |  | cached | failed | not_run |  | not_generated | not_run | Retrieval unavailable: Code retrieval indexes missing/offline: classDocEmbed, classNames, descEmbed, funcDocEmbed, functionNames |
| burgers2d_combined_0 | burgers2d | combined | blocked |  | cached | failed | not_run |  | not_generated | not_run | Retrieval unavailable: Code retrieval indexes missing/offline: classDocEmbed, classNames, descEmbed, funcDocEmbed, functionNames |
| heat_flow_code_only_0 | heat_flow | code_only | blocked |  | cached | failed | not_run |  | not_generated | not_run | Retrieval unavailable: Code retrieval indexes missing/offline: classDocEmbed, classNames, descEmbed, funcDocEmbed, functionNames |
| heat_flow_combined_0 | heat_flow | combined | blocked |  | cached | failed | not_run |  | not_generated | not_run | Retrieval unavailable: Code retrieval indexes missing/offline: classDocEmbed, classNames, descEmbed, funcDocEmbed, functionNames |
| julia_set_code_only_0 | julia_set | code_only | blocked |  | cached | failed | not_run |  | not_generated | not_run | Retrieval unavailable: Code retrieval indexes missing/offline: classDocEmbed, classNames, descEmbed, funcDocEmbed, functionNames |
| julia_set_combined_0 | julia_set | combined | blocked |  | cached | failed | not_run |  | not_generated | not_run | Retrieval unavailable: Code retrieval indexes missing/offline: classDocEmbed, classNames, descEmbed, funcDocEmbed, functionNames |
| reaction_diffusion_code_only_0 | reaction_diffusion | code_only | blocked |  | cached | failed | not_run |  | not_generated | not_run;not_run | Retrieval unavailable: Code retrieval indexes missing/offline: classDocEmbed, classNames, descEmbed, funcDocEmbed, functionNames |
| reaction_diffusion_combined_0 | reaction_diffusion | combined | blocked |  | cached | failed | not_run |  | not_generated | not_run;not_run | Retrieval unavailable: Code retrieval indexes missing/offline: classDocEmbed, classNames, descEmbed, funcDocEmbed, functionNames |

## Historical script reruns (fresh execution of existing code)

These scripts were generated earlier. Their new execution outcomes do not measure either retrieval arm's generation quality.

| run_id | domain | variant | generation_source | execution_status | duration_s | artifact_provenance | numerical_status | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| No measurements supplied |  |  |  |  |  |  |  |  |

## Generation controls and reproducibility

| run_id | config_id | model | seed | temperature | max_tokens | task_hash | code_context_hash | domain_context_hash |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| burgers2d_code_only_0 | 1ad8c65e9940 | claude-sonnet-4-6 |  | 0 | 20000 | 3e40128f9690ce73b6a4febd9e06b4f12b32b29724e02ce4181f8b1d3b22b080 |  |  |
| burgers2d_combined_0 | 1ad8c65e9940 | claude-sonnet-4-6 |  | 0 | 20000 | 3e40128f9690ce73b6a4febd9e06b4f12b32b29724e02ce4181f8b1d3b22b080 |  |  |
| heat_flow_code_only_0 | 1ad8c65e9940 | claude-sonnet-4-6 |  | 0 | 20000 | 4894e50322d00c78ab2005d7e2df51383939bb87f0bb3a6c7019d53f1ad3d4f2 |  |  |
| heat_flow_combined_0 | 1ad8c65e9940 | claude-sonnet-4-6 |  | 0 | 20000 | 4894e50322d00c78ab2005d7e2df51383939bb87f0bb3a6c7019d53f1ad3d4f2 |  |  |
| julia_set_code_only_0 | 1ad8c65e9940 | claude-sonnet-4-6 |  | 0 | 20000 | 10e0a7d9a3905b8241ffa222ab3fadcf9a580d047b1611e78bdabe187830201c |  |  |
| julia_set_combined_0 | 1ad8c65e9940 | claude-sonnet-4-6 |  | 0 | 20000 | 10e0a7d9a3905b8241ffa222ab3fadcf9a580d047b1611e78bdabe187830201c |  |  |
| reaction_diffusion_code_only_0 | 1ad8c65e9940 | claude-sonnet-4-6 |  | 0 | 20000 | 2aa75359e6b042a44fced58904c7957af95db4663795a95a8ff97f3e6c5073f5 |  |  |
| reaction_diffusion_combined_0 | 1ad8c65e9940 | claude-sonnet-4-6 |  | 0 | 20000 | 2aa75359e6b042a44fced58904c7957af95db4663795a95a8ff97f3e6c5073f5 |  |  |

## Numerical discrepancy measurements

RMSE is elementwise; mean/max L2 are per-frame norms. These values use different normalization from historical compute_l2_errors.py reports. Caveated measurements do not establish solver correctness.

| run_id | domain | variant | component | status | shape | rmse | relative_rmse | mean_l2 | max_l2 | reason | error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| burgers2d_code_only_0 | burgers2d | code_only | main | not_run |  |  |  |  |  | No successful current-run execution; outputs are not scored. |  |
| burgers2d_combined_0 | burgers2d | combined | main | not_run |  |  |  |  |  | No successful current-run execution; outputs are not scored. |  |
| heat_flow_code_only_0 | heat_flow | code_only | main | not_run |  |  |  |  |  | No successful current-run execution; outputs are not scored. |  |
| heat_flow_combined_0 | heat_flow | combined | main | not_run |  |  |  |  |  | No successful current-run execution; outputs are not scored. |  |
| julia_set_code_only_0 | julia_set | code_only | main | not_run |  |  |  |  |  | No successful current-run execution; outputs are not scored. |  |
| julia_set_combined_0 | julia_set | combined | main | not_run |  |  |  |  |  | No successful current-run execution; outputs are not scored. |  |
| reaction_diffusion_code_only_0 | reaction_diffusion | code_only | u | not_run |  |  |  |  |  | No successful current-run execution; outputs are not scored. |  |
| reaction_diffusion_code_only_0 | reaction_diffusion | code_only | v | not_run |  |  |  |  |  | No successful current-run execution; outputs are not scored. |  |
| reaction_diffusion_combined_0 | reaction_diffusion | combined | u | not_run |  |  |  |  |  | No successful current-run execution; outputs are not scored. |  |
| reaction_diffusion_combined_0 | reaction_diffusion | combined | v | not_run |  |  |  |  |  | No successful current-run execution; outputs are not scored. |  |

## Numerical provenance and interpretation

| run_id | component | expected_output | generated_path | generated_sha256 | reference_path | reference_sha256 | reference_source_sha256 | alignment_actions | caveats |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| burgers2d_code_only_0 | main | burgers2d_velocity_trj.npy |  |  | D:\Vivek\research\test_burgers2d\burgers2d_ground_truth.npy |  |  |  | ["Task initial data are Gaussian; ground-truth source uses unseeded Noise. A trajectory error measures discrepancy between these runs, not solver correctness. Matching a seed alone does not establish the same initial field."] |
| burgers2d_combined_0 | main | burgers2d_velocity_trj.npy |  |  | D:\Vivek\research\test_burgers2d\burgers2d_ground_truth.npy |  |  |  | ["Task initial data are Gaussian; ground-truth source uses unseeded Noise. A trajectory error measures discrepancy between these runs, not solver correctness. Matching a seed alone does not establish the same initial field."] |
| heat_flow_code_only_0 | main | heat_flow_temperature_trj.npy |  |  | D:\Vivek\research\test_heat_flow\heat_flow_ground_truth.npy |  |  |  | ["Task PDE specifies x-only diffusion; ground-truth code calls multidimensional diffuse.implicit with spatial conductivity. Operator agreement is unverified."] |
| heat_flow_combined_0 | main | heat_flow_temperature_trj.npy |  |  | D:\Vivek\research\test_heat_flow\heat_flow_ground_truth.npy |  |  |  | ["Task PDE specifies x-only diffusion; ground-truth code calls multidimensional diffuse.implicit with spatial conductivity. Operator agreement is unverified."] |
| julia_set_code_only_0 | main | julia_set_domain_trj.npy |  |  | D:\Vivek\research\test_julia_set\julia_set_ground_truth_trj.npy |  |  |  | [] |
| julia_set_combined_0 | main | julia_set_domain_trj.npy |  |  | D:\Vivek\research\test_julia_set\julia_set_ground_truth_trj.npy |  |  |  | [] |
| reaction_diffusion_code_only_0 | u | reaction_diffusion_u_trj.npy |  |  | D:\Vivek\research\test_reaction_diffusion\reaction_diffusion_ground_truth_u_trj.npy |  |  |  | [] |
| reaction_diffusion_code_only_0 | v | reaction_diffusion_v_trj.npy |  |  | D:\Vivek\research\test_reaction_diffusion\reaction_diffusion_ground_truth_v_trj.npy |  |  |  | [] |
| reaction_diffusion_combined_0 | u | reaction_diffusion_u_trj.npy |  |  | D:\Vivek\research\test_reaction_diffusion\reaction_diffusion_ground_truth_u_trj.npy |  |  |  | [] |
| reaction_diffusion_combined_0 | v | reaction_diffusion_v_trj.npy |  |  | D:\Vivek\research\test_reaction_diffusion\reaction_diffusion_ground_truth_v_trj.npy |  |  |  | [] |

## Paired code-only versus combined observations

Deltas are combined minus code_only. Only matched fresh-generation controls receive descriptive execution deltas; only uncaveated measurements against the same hashed reference receive component RMSE deltas.

| domain | config_id | replicate | comparison_status | code_only_execution | combined_execution | execution_delta | component_rmse_deltas | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| burgers2d | 1ad8c65e9940 | 0 | not_fresh_generation | not_run | not_run |  |  | No matched fresh generation outcomes; retrieval-only rows, existing-script reruns, and cached results do not measure context-conditioned generation. |
| heat_flow | 1ad8c65e9940 | 0 | not_fresh_generation | not_run | not_run |  |  | No matched fresh generation outcomes; retrieval-only rows, existing-script reruns, and cached results do not measure context-conditioned generation. |
| julia_set | 1ad8c65e9940 | 0 | not_fresh_generation | not_run | not_run |  |  | No matched fresh generation outcomes; retrieval-only rows, existing-script reruns, and cached results do not measure context-conditioned generation. |
| reaction_diffusion | 1ad8c65e9940 | 0 | not_fresh_generation | not_run | not_run |  |  | No matched fresh generation outcomes; retrieval-only rows, existing-script reruns, and cached results do not measure context-conditioned generation. |

## Graph construction and retrieval coverage

| measure | value |
| --- | --- |
| fresh_generations | 0 |
| graph_integrity | {"after": {"code": {"error": "Failed to DNS resolve address 50546e3c.databases.neo4j.io:7687: [Errno 11001] getaddrinfo failed", "status": "unavailable"}, "domain": {"error": "Unable to retrieve routing information", "status": "unavailable"}}, "before": {"code": {"error": "Failed to DNS resolve address 50546e3c.databases.neo4j.io:7687: [Errno 11001] getaddrinfo failed", "status": "unavailable"}, "domain": {"error": "Unable to retrieve routing information", "status": "unavailable"}}, "comparison": {"code": "unavailable", "domain": "unavailable"}, "scope": "Counts and element-ID sets only; property values and concurrent changes are not attributed."} |
| historical_reruns | 0 |
| preflight | {"graphs": {"code": {"error": "Failed to DNS resolve address 50546e3c.databases.neo4j.io:7687: [Errno 11001] getaddrinfo failed", "status": "unavailable"}, "domain": {"error": "Unable to retrieve routing information", "status": "unavailable"}}, "llm": {"available_models": ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5", "claude-fable-5-1", "claude-opus-5", "claude-sonnet-5", "claude-fable-5", "claude-opus-4-8", "claude-opus-4-7", "claude-sonnet-4-6", "claude-opus-4-6", "claude-opus-4-5-20251101", "claude-haiku-4-5-20251001", "claude-sonnet-4-5-20250929"], "model": "claude-sonnet-4-6", "status": "passed"}, "required_indexes": {"missing_or_offline": ["classDocEmbed", "classNames", "descEmbed", "funcDocEmbed", "functionNames"], "status": "blocked"}} |
| retrieval_arms | 0 |

| run_id | domain | variant | retrieval_status | domain_status | plan_source | code_nodes | domain_nodes | resolved_api_links | unresolved_api_links | context_chars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| burgers2d_code_only_0 | burgers2d | code_only | blocked |  | cached |  |  |  |  |  |
| burgers2d_combined_0 | burgers2d | combined | blocked |  | cached |  |  |  |  |  |
| heat_flow_code_only_0 | heat_flow | code_only | blocked |  | cached |  |  |  |  |  |
| heat_flow_combined_0 | heat_flow | combined | blocked |  | cached |  |  |  |  |  |
| julia_set_code_only_0 | julia_set | code_only | blocked |  | cached |  |  |  |  |  |
| julia_set_combined_0 | julia_set | combined | blocked |  | cached |  |  |  |  |  |
| reaction_diffusion_code_only_0 | reaction_diffusion | code_only | blocked |  | cached |  |  |  |  |  |
| reaction_diffusion_combined_0 | reaction_diffusion | combined | blocked |  | cached |  |  |  |  |  |

## Automated test outcomes

| name | status | tests | failures | errors | skipped | duration_s | details |
| --- | --- | --- | --- | --- | --- | --- | --- |
| test_audit_experiment.ExperimentAuditTests.test_aggregate_mapping_metadata_does_not_turn_unknown_counts_into_zero | passed | 1 | 0 | 0 | 0 | 0.077607 |  |
| test_audit_experiment.ExperimentAuditTests.test_all_nonfinite_empty_scalar_and_nonnumeric_arrays | passed | 1 | 0 | 0 | 0 | 0.184066 |  |
| test_audit_experiment.ExperimentAuditTests.test_changed_code_context_has_unknown_retention_not_false_absence | passed | 1 | 0 | 0 | 0 | 0.134053 |  |
| test_audit_experiment.ExperimentAuditTests.test_changed_hash_and_outside_paths_are_not_loaded | passed | 1 | 0 | 0 | 0 | 0.16958 |  |
| test_audit_experiment.ExperimentAuditTests.test_complex_ranges_are_explicit_magnitudes_and_safe_on_overflow | passed | 1 | 0 | 0 | 0 | 0.112425 |  |
| test_audit_experiment.ExperimentAuditTests.test_documentation_retention_uses_literal_code_context_fields_only | passed | 1 | 0 | 0 | 0 | 0.131817 |  |
| test_audit_experiment.ExperimentAuditTests.test_fortran_array_and_nonzero_frame_axis_use_temporal_first | passed | 1 | 0 | 0 | 0 | 0.060851 |  |
| test_audit_experiment.ExperimentAuditTests.test_incomplete_manifest_is_rejected_and_output_is_never_overwritten | passed | 1 | 0 | 0 | 0 | 0.368496 |  |
| test_audit_experiment.ExperimentAuditTests.test_local_prior_provenance_and_cached_state_dependencies_remain_explicit | passed | 1 | 0 | 0 | 0 | 0.068615 |  |
| test_audit_experiment.ExperimentAuditTests.test_mapping_statuses_and_ambiguity_are_not_invented_as_exact_matches | passed | 1 | 0 | 0 | 0 | 0.055792 |  |
| test_audit_experiment.ExperimentAuditTests.test_nan_inf_counts_first_frame_and_finite_only_range | passed | 1 | 0 | 0 | 0 | 0.059416 |  |
| test_audit_experiment.ExperimentAuditTests.test_object_pickle_and_invalid_axis_are_not_accepted | passed | 1 | 0 | 0 | 0 | 0.0821 |  |
| test_audit_experiment.ExperimentAuditTests.test_requested_filename_is_recognized_without_creating_a_score | passed | 1 | 0 | 0 | 0 | 0.152057 |  |
| test_audit_experiment.ExperimentAuditTests.test_wrong_output_name_remains_diagnostic_and_is_not_renamed | passed | 1 | 0 | 0 | 0 | 0.108457 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_additional_metadata_is_preserved_in_json | passed | 1 | 0 | 0 | 0 | 0.160213 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_artifacts_outside_run_directory_are_excluded | passed | 1 | 0 | 0 | 0 | 0.030424 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_axis_permutation_requires_explicit_metadata | passed | 1 | 0 | 0 | 0 | 0.057573 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_burgers_unseeded_initialization_is_caveated | passed | 1 | 0 | 0 | 0 | 0.193869 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_cached_outputs_are_excluded_even_if_execution_passed | passed | 1 | 0 | 0 | 0 | 0.025427 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_complex_magnitudes_are_preserved | passed | 1 | 0 | 0 | 0 | 0.058364 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_conventional_rmse_not_spatial_l2_norm | passed | 1 | 0 | 0 | 0 | 0.051368 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_domain_guided_code_context_changes_are_audited_as_pipeline_treatment | passed | 1 | 0 | 0 | 0 | 0.252949 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_empty_scalar_and_nonnumeric_arrays_are_rejected | passed | 1 | 0 | 0 | 0 | 0.077777 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_equal_length_conflicting_initial_frame_semantics_are_rejected | passed | 1 | 0 | 0 | 0 | 0.03497 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_execution_failure_and_generation_block_are_explicit | passed | 1 | 0 | 0 | 0 | 0.032431 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_heat_operator_mismatch_is_caveated_until_evidenced | passed | 1 | 0 | 0 | 0 | 0.172873 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_historical_rows_and_sources_remain_read_only | passed | 1 | 0 | 0 | 0 | 0.029108 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_initial_frame_is_dropped_only_with_explicit_metadata | passed | 1 | 0 | 0 | 0 | 0.025736 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_integer_subtraction_does_not_wrap | passed | 1 | 0 | 0 | 0 | 0.038564 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_matched_pair_does_not_compare_caveated_numerical_values | passed | 1 | 0 | 0 | 0 | 0.189452 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_missing_generated_artifact_is_explicit | passed | 1 | 0 | 0 | 0 | 0.019724 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_missing_reference_is_unavailable_not_zero | passed | 1 | 0 | 0 | 0 | 0.019037 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_nonfinite_arrays_are_not_scored | passed | 1 | 0 | 0 | 0 | 0.049882 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_numeric_overflow_is_not_reported_as_a_measurement | passed | 1 | 0 | 0 | 0 | 0.02201 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_pickle_object_arrays_are_rejected | passed | 1 | 0 | 0 | 0 | 0.019281 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_reference_shape_must_match_ground_truth_profile | passed | 1 | 0 | 0 | 0 | 0.015044 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_report_contains_detailed_tables_and_blank_missing_scores | passed | 1 | 0 | 0 | 0 | 0.095662 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_report_refuses_to_overwrite_any_existing_report | passed | 1 | 0 | 0 | 0 | 0.023128 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_report_serialization_is_deterministic_and_does_not_mutate_inputs | passed | 1 | 0 | 0 | 0 | 0.152354 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_rerun_can_measure_output_but_is_not_fresh_generation_pair | passed | 1 | 0 | 0 | 0 | 0.159004 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_shape_mismatch_never_broadcasts_or_truncates | passed | 1 | 0 | 0 | 0 | 0.045009 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_unmatched_generation_controls_block_claims | passed | 1 | 0 | 0 | 0 | 0.140974 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_unmeasured_context_does_not_create_efficacy_claim | passed | 1 | 0 | 0 | 0 | 0.161703 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_unsupported_domain_is_not_applicable | passed | 1 | 0 | 0 | 0 | 0.003665 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_wrong_filenames_do_not_score_accidental_old_outputs | passed | 1 | 0 | 0 | 0 | 0.024361 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_zero_reference_matching_output_is_zero_error | passed | 1 | 0 | 0 | 0 | 0.016943 |  |
| test_combined_experiment.CombinedExperimentTests.test_also_rerun_existing_is_one_historical_row_not_fake_arm_pair | passed | 1 | 0 | 0 | 0 | 0.218064 |  |
| test_combined_experiment.CombinedExperimentTests.test_ast_screen_rejects_output_escape_or_dynamic_filenames | passed | 1 | 0 | 0 | 0 | 0.011323 |  |
| test_combined_experiment.CombinedExperimentTests.test_ast_screen_rejects_sensitive_imports_and_dynamic_calls | passed | 1 | 0 | 0 | 0 | 0.012053 |  |
| test_combined_experiment.CombinedExperimentTests.test_child_environment_excludes_all_inherited_secrets | passed | 1 | 0 | 0 | 0 | 0.012934 |  |
| test_combined_experiment.CombinedExperimentTests.test_default_retrieval_makes_no_llm_calls_and_records_cached_plan | passed | 1 | 0 | 0 | 0 | 0.116606 |  |
| test_combined_experiment.CombinedExperimentTests.test_each_arm_uses_new_directory_and_saves_audit_inputs | passed | 1 | 0 | 0 | 0 | 0.129749 |  |
| test_combined_experiment.CombinedExperimentTests.test_execution_guard_blocks_sensitive_code_before_subprocess | passed | 1 | 0 | 0 | 0 | 0.024146 |  |
| test_combined_experiment.CombinedExperimentTests.test_execution_timeout_retains_partial_logs | passed | 1 | 0 | 0 | 0 | 0.052744 |  |
| test_combined_experiment.CombinedExperimentTests.test_existing_output_directory_is_never_reused | passed | 1 | 0 | 0 | 0 | 0.017471 |  |
| test_combined_experiment.CombinedExperimentTests.test_failed_selected_domain_source_does_not_silently_fall_back_to_json | passed | 1 | 0 | 0 | 0 | 0.024207 |  |
| test_combined_experiment.CombinedExperimentTests.test_generate_preflight_block_preserves_retrieval_without_generation | passed | 1 | 0 | 0 | 0 | 0.109453 |  |
| test_combined_experiment.CombinedExperimentTests.test_generate_uses_one_blueprint_per_domain_and_no_implicit_execution | passed | 1 | 0 | 0 | 0 | 0.194293 |  |
| test_combined_experiment.CombinedExperimentTests.test_generation_receives_unmodified_api_resolution_evidence_and_hash | passed | 1 | 0 | 0 | 0 | 0.334715 |  |
| test_combined_experiment.CombinedExperimentTests.test_graph_snapshot_uses_only_read_sessions_and_hashes_ids | passed | 1 | 0 | 0 | 0 | 0.035672 |  |
| test_combined_experiment.CombinedExperimentTests.test_graph_topology_comparison_detects_changed_id_sets | passed | 1 | 0 | 0 | 0 | 0.014095 |  |
| test_combined_experiment.CombinedExperimentTests.test_injected_pipeline_cannot_bypass_generation_preflight_by_default | passed | 1 | 0 | 0 | 0 | 0.217316 |  |
| test_combined_experiment.CombinedExperimentTests.test_invalid_numeric_options_are_rejected | passed | 1 | 0 | 0 | 0 | 0.044618 |  |
| test_combined_experiment.CombinedExperimentTests.test_invalid_test_results_schema_stops_before_any_pipeline_calls | passed | 1 | 0 | 0 | 0 | 0.041107 |  |
| test_combined_experiment.CombinedExperimentTests.test_missing_cached_blueprint_blocks_rows_without_llm_fallback | passed | 1 | 0 | 0 | 0 | 0.109746 |  |
| test_combined_experiment.CombinedExperimentTests.test_no_execute_flag_never_runs_existing_script | passed | 1 | 0 | 0 | 0 | 0.108553 |  |
| test_combined_experiment.CombinedExperimentTests.test_partial_retrieval_failure_keeps_successful_arm_and_manifest | passed | 1 | 0 | 0 | 0 | 0.205313 |  |
| test_combined_experiment.CombinedExperimentTests.test_per_test_results_are_loaded_hashed_and_exported | passed | 1 | 0 | 0 | 0 | 0.212947 |  |
| test_combined_experiment.CombinedExperimentTests.test_retrieval_live_setup_does_not_import_or_configure_llm_client | passed | 1 | 0 | 0 | 0 | 0.040005 |  |
| test_combined_experiment.CombinedExperimentTests.test_subprocess_receives_isolated_cwd_restricted_environment_and_timeout | passed | 1 | 0 | 0 | 0 | 0.02489 |  |
| test_combined_experiment.CombinedExperimentTests.test_unavailable_snapshot_never_claims_graph_unchanged | passed | 1 | 0 | 0 | 0 | 0.011232 |  |
| test_combined_experiment.CombinedExperimentTests.test_variants_share_immutable_blueprint_and_settings | passed | 1 | 0 | 0 | 0 | 0.111232 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_code_node_statistics_follow_serializer_definition_selection | passed | 1 | 0 | 0 | 0 | 0.005961 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_code_only_bypasses_domain_driver_and_domain_retriever | passed | 1 | 0 | 0 | 0 | 0.00809 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_combined_merges_planner_hints_and_uses_terminal_index_names | passed | 1 | 0 | 0 | 0 | 0.006662 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_driver_calls_are_read_only_explicit_and_not_closed | passed | 1 | 0 | 0 | 0 | 0.007513 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_duplicate_exact_aliases_are_not_resolved_by_filename_guess | passed | 1 | 0 | 0 | 0 | 0.009301 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_duplicate_legacy_file_candidates_remain_ambiguous | passed | 1 | 0 | 0 | 0 | 0.005522 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_exact_alias_resolution_adds_seed_and_retains_caveat | passed | 1 | 0 | 0 | 0 | 0.008348 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_invalid_variant_and_budgets_fail_before_external_calls | passed | 1 | 0 | 0 | 0 | 0.004274 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_low_scoring_required_public_api_is_pinned_before_ranked_noise | passed | 1 | 0 | 0 | 0 | 0.012023 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_metadata_settings_and_automatic_planner_are_forwarded | passed | 1 | 0 | 0 | 0 | 0.005533 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_missing_domain_uses_code_context_and_reports_status | passed | 1 | 0 | 0 | 0 | 0.004907 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_no_code_driver_produces_unavailable_resolution_without_connecting | passed | 1 | 0 | 0 | 0 | 0.005002 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_private_code_candidates_are_never_seeded | passed | 1 | 0 | 0 | 0 | 0.007383 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_private_raw_relation_cannot_be_pinned_by_id | passed | 1 | 0 | 0 | 0 | 0.008931 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_shared_blueprint_and_sane_query_caps_are_deterministic | passed | 1 | 0 | 0 | 0 | 0.006034 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_structural_metadata_completion_runs_after_pinning | passed | 1 | 0 | 0 | 0 | 0.007834 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_terminal_name_alone_cannot_resolve_wrong_file | passed | 1 | 0 | 0 | 0 | 0.006971 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_unique_file_basename_match_is_explicit_candidate | passed | 1 | 0 | 0 | 0 | 0.005643 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_builds_four_references_and_complete_provenance | passed | 1 | 0 | 0 | 0 | 0.419935 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_burgers_reads_diffused_velocity_for_advection | passed | 1 | 0 | 0 | 0 | 0.183585 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_cli_connection_overrides_selected_file_only | passed | 1 | 0 | 0 | 0 | 0.123382 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_cli_reports_underlying_neo4j_error_with_redacted_traceback | passed | 1 | 0 | 0 | 0 | 0.266599 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_cli_synchronizes_neo4j_by_default | passed | 1 | 0 | 0 | 0 | 0.214125 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_configuration_check_does_not_build_or_connect | passed | 1 | 0 | 0 | 0 | 0.048031 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_console_and_log_file_redact_passwords | passed | 1 | 0 | 0 | 0 | 0.05552 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_explicit_file_is_the_only_credentials_source | passed | 1 | 0 | 0 | 0 | 0.070225 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_export_only_does_not_load_credentials_or_connect | passed | 1 | 0 | 0 | 0 | 0.149374 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_extra_state_update_is_not_silently_omitted | passed | 1 | 0 | 0 | 0 | 0.096555 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_failed_validation_leaves_previous_export_unchanged | passed | 1 | 0 | 0 | 0 | 0.071344 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_heat_reads_coefficient_but_only_writes_temperature | passed | 1 | 0 | 0 | 0 | 0.094586 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_helper_and_parameter_dependencies_are_connected | passed | 1 | 0 | 0 | 0 | 0.083019 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_incomplete_file_blocks_cli_before_build_or_write | passed | 1 | 0 | 0 | 0 | 0.036739 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_incomplete_local_file_never_borrows_a_password | passed | 1 | 0 | 0 | 0 | 0.040095 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_interpolation_cannot_import_inherited_credentials | passed | 1 | 0 | 0 | 0 | 0.060569 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_invalid_uri_rejected_before_connecting | passed | 1 | 0 | 0 | 0 | 0.046789 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_julia_computed_output_has_no_invented_save | passed | 1 | 0 | 0 | 0 | 0.13179 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_local_file_wins_over_root_file_and_inherited_environment | passed | 1 | 0 | 0 | 0 | 0.039775 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_missing_and_empty_sources_reported_without_invented_references | passed | 1 | 0 | 0 | 0 | 0.137953 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_missing_credentials_have_actionable_error | passed | 1 | 0 | 0 | 0 | 0.039419 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_missing_dotenv_dependency_does_not_enable_environment_fallback | passed | 1 | 0 | 0 | 0 | 0.034404 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_missing_local_file_never_falls_back | passed | 1 | 0 | 0 | 0 | 0.054533 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_neo4j_batches_are_scoped_and_parameterized | passed | 1 | 0 | 0 | 0 | 0.12443 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_neo4j_logs_connection_batches_commit_and_verified_counts | passed | 1 | 0 | 0 | 0 | 0.169278 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_notes_remain_guidance | passed | 1 | 0 | 0 | 0 | 0.140233 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_npy_header_inspection_and_truncation | passed | 1 | 0 | 0 | 0 | 0.054623 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_path_escape_rejected | passed | 1 | 0 | 0 | 0 | 0.062107 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_post_commit_mismatch_does_not_report_verified_success | passed | 1 | 0 | 0 | 0 | 0.167524 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_reaction_cache_retains_old_state_dependencies | passed | 1 | 0 | 0 | 0 | 0.115666 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_reversed_recipe_is_rejected | passed | 1 | 0 | 0 | 0 | 0.067195 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_same_inputs_have_identical_graph_and_ids | passed | 1 | 0 | 0 | 0 | 0.315043 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_source_edit_invalidates_stale_step | passed | 1 | 0 | 0 | 0 | 0.069235 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_static_resolution_does_not_promote_external_candidates | passed | 1 | 0 | 0 | 0 | 0.176519 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_writer_rejects_empty_or_cross_dataset_graph | passed | 1 | 0 | 0 | 0 | 0.166916 |  |
| test_domain_retrieval.DomainRetrievalTests.test_bounded_neo4j_paths_cover_current_owned_recipe_edges | passed | 1 | 0 | 0 | 0 | 0.000319 |  |
| test_domain_retrieval.DomainRetrievalTests.test_burgers_advection_uses_already_diffused_state | passed | 1 | 0 | 0 | 0 | 0.007855 |  |
| test_domain_retrieval.DomainRetrievalTests.test_cached_reaction_is_read_at_produced_version | passed | 1 | 0 | 0 | 0 | 0.011778 |  |
| test_domain_retrieval.DomainRetrievalTests.test_dataset_isolation_filters_local_nodes_and_edges | passed | 1 | 0 | 0 | 0 | 0.023759 |  |
| test_domain_retrieval.DomainRetrievalTests.test_default_context_budget_preserves_every_recipe_step | passed | 1 | 0 | 0 | 0 | 0.094208 |  |
| test_domain_retrieval.DomainRetrievalTests.test_empty_graph_and_unknown_domain_fall_back_cleanly | passed | 1 | 0 | 0 | 0 | 0.007858 |  |
| test_domain_retrieval.DomainRetrievalTests.test_explicit_selection_does_not_follow_incoming_shared_api_edges | passed | 1 | 0 | 0 | 0 | 0.010916 |  |
| test_domain_retrieval.DomainRetrievalTests.test_helper_formulas_parameters_and_output_conventions_are_preserved | passed | 1 | 0 | 0 | 0 | 0.011755 |  |
| test_domain_retrieval.DomainRetrievalTests.test_input_snapshot_and_returned_context_are_independent | passed | 1 | 0 | 0 | 0 | 0.025872 |  |
| test_domain_retrieval.DomainRetrievalTests.test_julia_temporary_parameter_is_not_lost | passed | 1 | 0 | 0 | 0 | 0.008103 |  |
| test_domain_retrieval.DomainRetrievalTests.test_missing_or_blank_domain_does_not_infer_from_task | passed | 1 | 0 | 0 | 0 | 0.003684 |  |
| test_domain_retrieval.DomainRetrievalTests.test_neo4j_domain_cannot_change_query_structure | passed | 1 | 0 | 0 | 0 | 0.01103 |  |
| test_domain_retrieval.DomainRetrievalTests.test_neo4j_empty_result_is_clean_and_read_errors_remain_visible | passed | 1 | 0 | 0 | 0 | 0.009393 |  |
| test_domain_retrieval.DomainRetrievalTests.test_neo4j_null_projection_fields_match_local_export | passed | 1 | 0 | 0 | 0 | 0.009243 |  |
| test_domain_retrieval.DomainRetrievalTests.test_neo4j_read_uses_safe_parameterized_query_and_explicit_database | passed | 1 | 0 | 0 | 0 | 0.008803 |  |
| test_domain_retrieval.DomainRetrievalTests.test_oversized_core_is_flagged_without_cutting_json_or_steps | passed | 1 | 0 | 0 | 0 | 0.025653 |  |
| test_domain_retrieval.DomainRetrievalTests.test_public_alias_survives_missing_observed_call | passed | 1 | 0 | 0 | 0 | 0.018661 |  |
| test_domain_retrieval.DomainRetrievalTests.test_public_aliases_are_usable_code_search_hints | passed | 1 | 0 | 0 | 0 | 0.00953 |  |
| test_domain_retrieval.DomainRetrievalTests.test_reference_steps_follow_source_order_not_storage_order | passed | 1 | 0 | 0 | 0 | 0.031729 |  |
| test_domain_retrieval.DomainRetrievalTests.test_schema_and_adapter_ambiguities_fail_visibly | passed | 1 | 0 | 0 | 0 | 0.000485 |  |
| test_domain_retrieval.DomainRetrievalTests.test_task_requirements_override_reference_output_defaults | passed | 1 | 0 | 0 | 0 | 0.00989 |  |
| test_domain_retrieval.DomainRetrievalTests.test_unresolved_apis_are_candidates_without_verification_claim | passed | 1 | 0 | 0 | 0 | 0.010496 |  |
| test_domain_retrieval.DomainRetrievalTests.test_whole_program_and_save_expression_are_not_prompt_context | passed | 1 | 0 | 0 | 0 | 0.016898 |  |
| test_pipeline_config.PipelineConfigTests.test_connection_interpolation_rejected_for_every_setting | passed | 1 | 0 | 0 | 0 | 0.041371 |  |
| test_pipeline_config.PipelineConfigTests.test_describe_connection_is_read_only_and_secret_free | passed | 1 | 0 | 0 | 0 | 0.014831 |  |
| test_pipeline_config.PipelineConfigTests.test_driver_construction_is_lazy_bounded_and_does_not_create_session | passed | 1 | 0 | 0 | 0 | 0.009331 |  |
| test_pipeline_config.PipelineConfigTests.test_driver_constructor_error_is_redacted | passed | 1 | 0 | 0 | 0 | 0.004768 |  |
| test_pipeline_config.PipelineConfigTests.test_explicit_code_and_domain_files_do_not_mix | passed | 1 | 0 | 0 | 0 | 0.015708 |  |
| test_pipeline_config.PipelineConfigTests.test_inherited_values_are_ignored_and_environment_is_unchanged | passed | 1 | 0 | 0 | 0 | 0.012134 |  |
| test_pipeline_config.PipelineConfigTests.test_invalid_role_and_implicit_file_are_rejected | passed | 1 | 0 | 0 | 0 | 0.0044 |  |
| test_pipeline_config.PipelineConfigTests.test_llm_interpolation_and_placeholders_rejected | passed | 1 | 0 | 0 | 0 | 0.033485 |  |
| test_pipeline_config.PipelineConfigTests.test_llm_missing_key_does_not_use_environment | passed | 1 | 0 | 0 | 0 | 0.015008 |  |
| test_pipeline_config.PipelineConfigTests.test_llm_model_and_workspace_must_be_literal_if_provided | passed | 1 | 0 | 0 | 0 | 0.0229 |  |
| test_pipeline_config.PipelineConfigTests.test_llm_model_precedence_and_optional_workspace | passed | 1 | 0 | 0 | 0 | 0.015794 |  |
| test_pipeline_config.PipelineConfigTests.test_llm_only_file_does_not_require_database_settings | passed | 1 | 0 | 0 | 0 | 0.012331 |  |
| test_pipeline_config.PipelineConfigTests.test_missing_domain_password_never_uses_root_or_environment | passed | 1 | 0 | 0 | 0 | 0.015066 |  |
| test_pipeline_config.PipelineConfigTests.test_missing_selected_file_never_falls_back | passed | 1 | 0 | 0 | 0 | 0.005384 |  |
| test_pipeline_config.PipelineConfigTests.test_placeholder_credentials_rejected_without_echoing_value | passed | 1 | 0 | 0 | 0 | 0.043235 |  |
| test_pipeline_config.PipelineConfigTests.test_redaction_covers_database_password_and_api_key | passed | 1 | 0 | 0 | 0 | 0.012202 |  |
| test_pipeline_config.PipelineConfigTests.test_relative_path_is_explicitly_resolved_under_root | passed | 1 | 0 | 0 | 0 | 0.008644 |  |
| test_pipeline_config.PipelineConfigTests.test_uri_with_embedded_credentials_is_rejected | passed | 1 | 0 | 0 | 0 | 0.021264 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_blueprint_errors_are_redacted_before_logging | passed | 1 | 0 | 0 | 0 | 0.008173 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_definition_with_only_description_edge_remains_available | passed | 1 | 0 | 0 | 0 | 0.00055 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_disabled_llm_blocks_even_injected_client | passed | 1 | 0 | 0 | 0 | 0.000755 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_generation_prioritizes_task_and_records_usage | passed | 1 | 0 | 0 | 0 | 0.00065 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_generation_sees_unresolved_mapping_evidence | passed | 1 | 0 | 0 | 0 | 0.000684 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_injected_resources_are_not_closed | passed | 1 | 0 | 0 | 0 | 0.000356 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_injection_does_not_load_config_or_embedding_model | passed | 1 | 0 | 0 | 0 | 0.000746 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_metadata_closure_is_idempotent_and_ignores_unselected_definitions | passed | 1 | 0 | 0 | 0 | 0.000348 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_method_description_rows_respect_owning_class_quota | passed | 1 | 0 | 0 | 0 | 0.000661 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_namespace_attribute_import_and_class_import_are_valid_patterns | passed | 1 | 0 | 0 | 0 | 0.00038 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_parameter_type_metadata_survives_filtering_and_row_order | passed | 1 | 0 | 0 | 0 | 0.000771 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_public_method_uses_initialized_instance | passed | 1 | 0 | 0 | 0 | 0.0004 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_sessions_use_read_access_and_selected_database | passed | 1 | 0 | 0 | 0 | 0.001556 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_truncated_generation_is_rejected | passed | 1 | 0 | 0 | 0 | 0.001697 |  |

## Historical files (read only; not new generation results)

Historical objective/physics scores and RMSE retain their original definitions. They are not combined with fresh metrics. CSV exports contain every supplied historical row; previews below show at most 20 per source.

| path | status | rows | bytes | sha256 | provenance | error |
| --- | --- | --- | --- | --- | --- | --- |
| D:\Vivek\research\evaluation_report.csv | available | 8 | 605 | 944652f4f9b8ef61f464152c82ee4da85c81329c2c99c3bd66989988e2a3c705 | historical_read_only |  |
| D:\Vivek\research\evaluation_report.json | available | 8 | 8931 | ca6d8ab636abb9c5b9e90d5fd852152f10fc43384146c9838a5d1ee0c54d2580 | historical_read_only |  |
| D:\Vivek\research\l2summary.csv | available | 3 | 611 | ed09577aed8ab3a477743650428565b1447601ef82d6928aa173b81354fbaae7 | historical_read_only |  |
| D:\Vivek\research\optimization_runs\pruned_cross_domain\cross_domain_execution_summary.csv | available | 5 | 710 | b840c902cf21c0a38400ff82f13ac6f487abca2c1aff246c5d2aab73e6fee765 | historical_read_only |  |
| D:\Vivek\research\optimization_runs\pruned_cross_domain\cross_domain_quality_ranking.csv | available | 5 | 1203 | 897539afe49cdc19b842f8b77456dc2cbfc02049fcc9a1eea08d9acccf9b9a50 | historical_read_only |  |

### Historical: D:\Vivek\research\evaluation_report.csv

| domain | objective_score | objective_score_coverage | syntax_ok | execution_ok | duration_s | relative_rmse | physics_score | reference_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| burgers2d | 60.0 | 1.0 | True | True | 4.624 |  |  | comparison_error |
| heat_flow | 60.0 | 1.0 | True | True | 5.593 |  |  | comparison_error |
| julia_set | 100.0 | 1.0 | True | True | 1.462 | 0.0 | 1.0 | measured |
| lid_driven_cavity | 0.0 | 0.5 | True | False | 21.68 |  |  | not_applicable |
| reaction_diffusion | 100.0 | 1.0 | True | True | 5.486 | 9e-06 | 0.999991 | measured;measured |
| smoke_plume | 0.0 | 0.5 | True | False | 11.367 |  |  | not_applicable |
| structural_mechanics | 60.0 | 0.5 | True | True | 3.278 |  |  | not_applicable |
| wake_flow | 0.0 | 0.5 | True | False | 1.919 |  |  | not_applicable |

### Historical: D:\Vivek\research\evaluation_report.json

| domain | script | run | numerical | objective_score_coverage | objective_score |
| --- | --- | --- | --- | --- | --- |
| burgers2d | D:\Vivek\research\test_burgers2d\generated_burgers2d_simulation.py | {"duration_s": 4.624, "execution_ok": true, "exit_code": 0, "stderr_tail": "himl\\backend\\_backend.py:1712: RuntimeWarning: invalid value encountered in subtract\n  return a - b\nC:\\Users\\sreed\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\phiml\\backend\\_backend.py:1720: RuntimeWarning: overflow encountered in divide\n  return numerator / denominator\nC:\\Users\\sreed\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\numpy\\_core\\fromnumeric.py:86: RuntimeWarning: invalid value encountered in reduce\n  return ufunc.reduce(obj, axis, dtype, out, **passkwargs)\n", "syntax_error": "", "syntax_ok": true} | [{"error": "generated trajectory contains 501554 NaN/infinite values; first index=(13, 30, 36, 0), timestep=13", "generated_exists": true, "ground_truth_exists": true, "label": "main", "physics_score": 0.0, "status": "comparison_error"}] | 1.0 | 60.0 |
| heat_flow | D:\Vivek\research\test_heat_flow\generated_heat_flow_simulation.py | {"duration_s": 5.593, "execution_ok": true, "exit_code": 0, "stderr_tail": "pData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\phiml\\backend\\_backend.py:1712: RuntimeWarning: overflow encountered in subtract\n  return a - b\nC:\\Users\\sreed\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\phiml\\backend\\_backend.py:1712: RuntimeWarning: invalid value encountered in subtract\n  return a - b\nC:\\Users\\sreed\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\phiml\\backend\\_backend.py:1716: RuntimeWarning: invalid value encountered in multiply\n  return a * b\n", "syntax_error": "", "syntax_ok": true} | [{"error": "generated trajectory contains 209082 NaN/infinite values; first index=(16, 0, 20), timestep=16", "generated_exists": true, "ground_truth_exists": true, "label": "main", "physics_score": 0.0, "status": "comparison_error"}] | 1.0 | 60.0 |
| julia_set | D:\Vivek\research\test_julia_set\generated_julia_set_simulation.py | {"duration_s": 1.462, "execution_ok": true, "exit_code": 0, "stderr_tail": "C:\\Users\\sreed\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\phiml\\math\\_tensors.py:1229: RuntimeWarning: overflow encountered in square\n  result = op(n1, n2)\nC:\\Users\\sreed\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\phiml\\math\\_tensors.py:1229: RuntimeWarning: invalid value encountered in square\n  result = op(n1, n2)\n", "syntax_error": "", "syntax_ok": true} | [{"generated_exists": true, "ground_truth_exists": true, "label": "main", "max_l2": 0.0, "mean_l2": 0.0, "physics_score": 1.0, "relative_rmse": 0.0, "rmse": 0.0, "shape": [100, 256, 256], "status": "measured"}] | 1.0 | 100.0 |
| lid_driven_cavity | D:\Vivek\research\test_lid_driven_cavity\generated_lid_driven_cavity_simulation.py | {"duration_s": 21.68, "execution_ok": false, "exit_code": 1, "stderr_tail": "backprop and 'TensorFlow' in backend.name)  # raises ConvergenceException\n    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\sreed\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\phiml\\math\\_optimize.py\", line 209, in convergence_check\n    raise NotConverged(self)\nphiml.math._optimize.NotConverged: \\u03a6-ML CG (numpy) with preconditioner 'none' did not converge to rel_tol=1e-05, abs_tol=1e-05 within 1000 iterations. Max residual: 0.00016495059\n", "syntax_error": "", "syntax_ok": true} | [] | 0.5 | 0.0 |
| reaction_diffusion | D:\Vivek\research\test_reaction_diffusion\generated_reaction_diffusion_simulation.py | {"duration_s": 5.486, "execution_ok": true, "exit_code": 0, "stderr_tail": "D:\\Vivek\\research\\test_reaction_diffusion\\generated_reaction_diffusion_simulation.py:20: DeprecationWarning: phiml.math.length is deprecated in favor of phiml.math.norm\n  r = math.vec_length(x - center)\n", "syntax_error": "", "syntax_ok": true} | [{"generated_exists": true, "ground_truth_exists": true, "label": "u", "max_l2": 5.751848220825195e-06, "mean_l2": 3.4535277661947686e-06, "physics_score": 0.9999928776189507, "relative_rmse": 7.122431777856751e-06, "rmse": 3.7595176801983268e-06, "shape": [101, 100, 100], "status": "measured"}, {"generated_exists": true, "ground_truth_exists": true, "label": "v", "max_l2": 8.242237986666813e-06, "mean_l2": 4.572451737224804e-06, "physics_score": 0.9999888452098709, "relative_rmse": 1.1154914559902875e-05, "rmse": 4.771784218008951e-06, "shape": [101, 100, 100], "status": "measured"}] | 1.0 | 100.0 |
| smoke_plume | D:\Vivek\research\test_smoke_plume\generated_smoke_plume_simulation.py | {"duration_s": 11.367, "execution_ok": false, "exit_code": 1, "stderr_tail": "ackprop and 'TensorFlow' in backend.name)  # raises ConvergenceException\n    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\sreed\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\phiml\\math\\_optimize.py\", line 209, in convergence_check\n    raise NotConverged(self)\nphiml.math._optimize.NotConverged: \\u03a6-ML CG (numpy) with preconditioner 'none' did not converge to rel_tol=1e-05, abs_tol=1e-05 within 1000 iterations. Max residual: -1.9401796e-09\n", "syntax_error": "", "syntax_ok": true} | [] | 0.5 | 0.0 |
| structural_mechanics | D:\Vivek\research\test_structural_mechanics\generated_structural_mechanics_simulation.py | {"duration_s": 3.278, "execution_ok": true, "exit_code": 0, "stderr_tail": "", "syntax_error": "", "syntax_ok": true} | [] | 0.5 | 60.0 |
| wake_flow | D:\Vivek\research\test_wake_flow\generated_wake_flow_simulation.py | {"duration_s": 1.919, "execution_ok": false, "exit_code": 1, "stderr_tail": "Traceback (most recent call last):\n  File \"D:\\Vivek\\research\\test_wake_flow\\generated_wake_flow_simulation.py\", line 17, in <module>\n    obstacle_geometry = Cylinder(center=vec(x=20, y=50, z=2.5), radius=10, depth=5, axis='z')\n                        ^^^^^^^^\nNameError: name 'Cylinder' is not defined. Did you mean: 'cylinder'?\n", "syntax_error": "", "syntax_ok": true} | [] | 0.5 | 0.0 |

### Historical: D:\Vivek\research\l2summary.csv

| label | generated | ground_truth | mean_l2 | max_l2 | rmse |
| --- | --- | --- | --- | --- | --- |
| julia_set | test_julia_set/julia_set_trj.npy | test_julia_set\julia_set_ground_truth_trj.npy | 1551.2946792478624 | 4389.999430523881 | 1974.010298858646 |
| reaction_diffusion_u | test_reaction_diffusion/reaction_diffusion_u_trj.npy | test_reaction_diffusion\reaction_diffusion_ground_truth_u_trj.npy | 3.4535277661947686e-06 | 5.751848220825195e-06 | 3.7595176801983268e-06 |
| reaction_diffusion_v | test_reaction_diffusion/reaction_diffusion_v_trj.npy | test_reaction_diffusion\reaction_diffusion_ground_truth_v_trj.npy | 4.572451737224804e-06 | 8.242237986666813e-06 | 4.771784218008951e-06 |

### Historical: D:\Vivek\research\optimization_runs\pruned_cross_domain\cross_domain_execution_summary.csv

| rank | config_id | top_k | min_score | method_min_score | max_methods_per_class | max_nodes | fulltext_limit | description_limit | function_limit | class_limit | successful_domains | tested_domains | execution_rate | heat_flow | burgers2d | julia_set | lid_driven_cavity | reaction_diffusion | smoke_plume | wake_flow |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2b266fbc949d | 12 | 0.15 | 0.3 | 5 | 12 | 5 | 8 | 4 | 4 | 4 | 7 | 0.5714 | PASS | PASS | PASS | FAIL | PASS | FAIL | FAIL |
| 2 | 800ba81f8913 | 32 | 0.2 | 0.5 | 2 | 12 | 5 | 3 | 4 | 4 | 4 | 7 | 0.5714 | PASS | PASS | PASS | FAIL | PASS | FAIL | FAIL |
| 3 | e905e7297b5f | 12 | 0.2 | 0.5 | 5 | 12 | 5 | 5 | 2 | 2 | 4 | 7 | 0.5714 | PASS | PASS | PASS | FAIL | PASS | FAIL | FAIL |
| 4 | 3a899d129273 | 32 | 0.2 | 0.5 | 5 | 12 | 5 | 3 | 6 | 6 | 4 | 7 | 0.5714 | PASS | PASS | PASS | FAIL | PASS | FAIL | FAIL |
| 5 | c5573860ecec | 32 | 0.2 | 0.3 | 5 | 12 | 5 | 8 | 6 | 6 | 4 | 7 | 0.5714 | PASS | PASS | PASS | FAIL | PASS | FAIL | FAIL |

### Historical: D:\Vivek\research\optimization_runs\pruned_cross_domain\cross_domain_quality_ranking.csv

| rank | config_id | top_k | min_score | method_min_score | max_methods_per_class | max_nodes | fulltext_limit | description_limit | function_limit | class_limit | successful_domains | tested_domains | avg_physics_score | mean_relative_rmse | worst_relative_rmse | measured_domains | unmeasured_domains | quality_domains | julia_set_physics | reaction_diffusion_physics | julia_set_rmse | reaction_diffusion_rmse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | c5573860ecec | 32 | 0.2 | 0.3 | 5 | 12 | 5 | 8 | 6 | 6 | 4 | 7 | 0.999999 | 1e-06 | 3e-06 | julia_set;reaction_diffusion | burgers2d;heat_flow | julia_set;reaction_diffusion | 1.0 | 0.999997 | 0.0 | 3e-06 |
| 2 | 3a899d129273 | 32 | 0.2 | 0.5 | 5 | 12 | 5 | 3 | 6 | 6 | 4 | 7 | 0.999998 | 2e-06 | 5e-06 | julia_set;reaction_diffusion | burgers2d;heat_flow | julia_set;reaction_diffusion | 1.0 | 0.999996 | 0.0 | 4e-06 |
| 3 | e905e7297b5f | 12 | 0.2 | 0.5 | 5 | 12 | 5 | 5 | 2 | 2 | 4 | 7 | 0.999998 | 2e-06 | 6e-06 | julia_set;reaction_diffusion | burgers2d;heat_flow | julia_set;reaction_diffusion | 1.0 | 0.999995 | 0.0 | 5e-06 |
| 4 | 2b266fbc949d | 12 | 0.15 | 0.3 | 5 | 12 | 5 | 8 | 4 | 4 | 4 | 7 | 0.999995 | 5e-06 | 1.1e-05 | julia_set;reaction_diffusion | burgers2d;heat_flow | julia_set;reaction_diffusion | 1.0 | 0.999991 | 0.0 | 9e-06 |
| 5 | 800ba81f8913 | 32 | 0.2 | 0.5 | 2 | 12 | 5 | 3 | 4 | 4 | 4 | 7 | 0.999995 | 5e-06 | 1.1e-05 | julia_set;reaction_diffusion | burgers2d;heat_flow | julia_set;reaction_diffusion | 1.0 | 0.999991 | 0.0 | 9e-06 |

## Interpretation limits

- Fresh generation outcomes require real LLM calls; offline graph/retrieval checks do not establish generation improvement.
- Execution success is separate from numerical agreement and physical validity.
- Reference hashes identify the exact stored arrays; references were not regenerated by this report.
- Historical RMSE/objective/physics-score formulas differ from this report and are not directly comparable.
- One paired sample per domain is descriptive evidence and cannot establish statistical superiority.
