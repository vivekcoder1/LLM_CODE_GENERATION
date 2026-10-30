# Combined knowledge graph experiment report

Fresh runs, graph/retrieval checks, and historical outcomes have separate provenance. Blank numerical values mean unmeasured. No overall quality ranking is assigned.

## Generation and execution outcomes

| run_id | domain | variant | retrieval_status | domain_status | plan_source | generation_status | execution_status | duration_s | artifact_provenance | numerical_status | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| burgers2d_code_only_0 | burgers2d | code_only | restored_not_requeried | disabled | saved_retrieval_snapshot | generated | passed | 18.248828 | fresh | comparison_error |  |
| burgers2d_combined_0 | burgers2d | combined | restored_not_requeried | available | saved_retrieval_snapshot | generated | passed | 32.313646 | fresh | measured_caveated |  |
| heat_flow_code_only_0 | heat_flow | code_only | restored_not_requeried | disabled | saved_retrieval_snapshot | generated | passed | 9.978705 | fresh | comparison_error |  |
| heat_flow_combined_0 | heat_flow | combined | restored_not_requeried | available | saved_retrieval_snapshot | generated | passed | 36.898029 | fresh | measured_caveated |  |
| julia_set_code_only_0 | julia_set | code_only | restored_not_requeried | disabled | saved_retrieval_snapshot | generated | passed | 9.631615 | fresh | measured |  |
| julia_set_combined_0 | julia_set | combined | restored_not_requeried | available | saved_retrieval_snapshot | generated | passed | 2.429867 | fresh | measured |  |
| reaction_diffusion_code_only_0 | reaction_diffusion | code_only | restored_not_requeried | disabled | saved_retrieval_snapshot | generated | passed | 3.30246 | fresh | measured;measured |  |
| reaction_diffusion_combined_0 | reaction_diffusion | combined | restored_not_requeried | available | saved_retrieval_snapshot | generated | passed | 3.714028 | fresh | measured;measured |  |

## Historical script reruns (fresh execution of existing code)

These scripts were generated earlier. Their new execution outcomes do not measure either retrieval arm's generation quality.

| run_id | domain | variant | generation_source | execution_status | duration_s | artifact_provenance | numerical_status | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| No measurements supplied |  |  |  |  |  |  |  |  |

## Generation controls and reproducibility

| run_id | config_id | model | seed | temperature | max_tokens | task_hash | code_context_hash | domain_context_hash |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| burgers2d_code_only_0 | 1ad8c65e9940 | claude-sonnet-4-6 |  | 0 | 20000 | 3e40128f9690ce73b6a4febd9e06b4f12b32b29724e02ce4181f8b1d3b22b080 | fe15cfb996aa62ca95bbeeb799ef51ce2c797ae63b77a14f07e0e9337608a1c8 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| burgers2d_combined_0 | 1ad8c65e9940 | claude-sonnet-4-6 |  | 0 | 20000 | 3e40128f9690ce73b6a4febd9e06b4f12b32b29724e02ce4181f8b1d3b22b080 | b0d361ce7bd3cfc3c93970d741e8eb86730f2338aba7f15531b783bdd363ec18 | 05bed0fe71d27efbaa0824b7f738ff56a5ef653a135465c117d5c9eb9eb19420 |
| heat_flow_code_only_0 | 1ad8c65e9940 | claude-sonnet-4-6 |  | 0 | 20000 | 4894e50322d00c78ab2005d7e2df51383939bb87f0bb3a6c7019d53f1ad3d4f2 | 8624f05113f00e150fbb31a9b4daa31e4504c827066f422f1a5432ff5c7b9b64 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| heat_flow_combined_0 | 1ad8c65e9940 | claude-sonnet-4-6 |  | 0 | 20000 | 4894e50322d00c78ab2005d7e2df51383939bb87f0bb3a6c7019d53f1ad3d4f2 | f938eb4ff0cce9bd8fe13fd573361e14bc54fd705570feb7fda50e4b2197e6fd | 557f3526b70513a4da594ecffd955d831a03e9eaa2023a670e70112a605f7f78 |
| julia_set_code_only_0 | 1ad8c65e9940 | claude-sonnet-4-6 |  | 0 | 20000 | 10e0a7d9a3905b8241ffa222ab3fadcf9a580d047b1611e78bdabe187830201c | 22712a6bf04f16c9c5365b9cae981cd59c8f9bf1fb597abac732673fd0195285 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| julia_set_combined_0 | 1ad8c65e9940 | claude-sonnet-4-6 |  | 0 | 20000 | 10e0a7d9a3905b8241ffa222ab3fadcf9a580d047b1611e78bdabe187830201c | d01b3cfb07c322c735023145fd5eb116ad621987c1d86c66198e0f1c7e26ec17 | 187b87fdcf8eb6ee477f3b731b0286fa5176edd64f1eacfb09b5195bc876b1b7 |
| reaction_diffusion_code_only_0 | 1ad8c65e9940 | claude-sonnet-4-6 |  | 0 | 20000 | 2aa75359e6b042a44fced58904c7957af95db4663795a95a8ff97f3e6c5073f5 | e62b88aa2ff4749316e4c5fb28e799d1713fc5ac83be1913b2fbc609edf1bc67 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| reaction_diffusion_combined_0 | 1ad8c65e9940 | claude-sonnet-4-6 |  | 0 | 20000 | 2aa75359e6b042a44fced58904c7957af95db4663795a95a8ff97f3e6c5073f5 | a24e23d24acd1354b1c2c8ca89928924c53f2863af062e0480093ee5050ba466 | e58e8921e42b9eb52e2f025ec6aac5527db596d73d3eefeeeb4d29becc73d052 |

## Numerical discrepancy measurements

RMSE is elementwise; mean/max L2 are per-frame norms. These values use different normalization from historical compute_l2_errors.py reports. Caveated measurements do not establish solver correctness.

| run_id | domain | variant | component | status | shape | rmse | relative_rmse | mean_l2 | max_l2 | reason | error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| burgers2d_code_only_0 | burgers2d | code_only | main | comparison_error |  |  |  |  |  |  | trajectory contains 501554 NaN/infinite values |
| burgers2d_combined_0 | burgers2d | combined | main | measured_caveated | [101, 64, 64, 2] | 0.3798066919711809 | 0.9961133520880253 | 28.96117467116306 | 90.59910879976493 |  |  |
| heat_flow_code_only_0 | heat_flow | code_only | main | comparison_error |  |  |  |  |  |  | trajectory contains 210074 NaN/infinite values |
| heat_flow_combined_0 | heat_flow | combined | main | measured_caveated | [101, 100, 50] | 2.082628732015258e-06 | 5.54557562481197e-06 | 0.00011932525720124538 | 0.00029229282933294145 |  |  |
| julia_set_code_only_0 | julia_set | code_only | main | measured | [100, 256, 256] | 7.519814523885068 | 4.823887539800515 | 1475.367018881357 | 4372.596253943417 |  |  |
| julia_set_combined_0 | julia_set | combined | main | measured | [100, 256, 256] | 0.0 | 0.0 | 0.0 | 0.0 |  |  |
| reaction_diffusion_code_only_0 | reaction_diffusion | code_only | u | measured | [101, 100, 100] | 3.7222935701477625e-08 | 7.051910545897388e-08 | 3.430974720414595e-06 | 5.494953462598701e-06 |  |  |
| reaction_diffusion_code_only_0 | reaction_diffusion | code_only | v | measured | [101, 100, 100] | 4.713715222466051e-08 | 1.1019166615607521e-07 | 4.5187180732744745e-06 | 7.983700342973225e-06 |  |  |
| reaction_diffusion_combined_0 | reaction_diffusion | combined | u | measured | [101, 100, 100] | 0.0 | 0.0 | 0.0 | 0.0 |  |  |
| reaction_diffusion_combined_0 | reaction_diffusion | combined | v | measured | [101, 100, 100] | 0.0 | 0.0 | 0.0 | 0.0 |  |  |

## Numerical provenance and interpretation

| run_id | component | expected_output | generated_path | generated_sha256 | reference_path | reference_sha256 | reference_source_sha256 | alignment_actions | caveats |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| burgers2d_code_only_0 | main | burgers2d_velocity_trj.npy | D:\Vivek\research\integration_runs\20261028T181330_344848Z_saved_context\runs\burgers2d\code_only_0\burgers2d_velocity_trj.npy | 5d63e09130e27474fac843f0b37bca81c61da5a6ae8dad4a3d1a7d448426fdf0 | D:\Vivek\research\test_burgers2d\burgers2d_ground_truth.npy | 45c8f507aa93861cb6cb5571e092d11e93a764ef322cd2944799f30caea5084c | f578b6acf3536ce62fea0f6696ab2938f11d2e63f7ede910f0b358f3ebd11c51 |  | ["Task initial data are Gaussian; ground-truth source uses unseeded Noise. A trajectory error measures discrepancy between these runs, not solver correctness. Matching a seed alone does not establish the same initial field."] |
| burgers2d_combined_0 | main | burgers2d_velocity_trj.npy | D:\Vivek\research\integration_runs\20261028T181330_344848Z_saved_context\runs\burgers2d\combined_0\burgers2d_velocity_trj.npy | de004807cd10faffe9c4d64be48249ac4a8a0dde9a96ef6f4ae3d4d5b773b0aa | D:\Vivek\research\test_burgers2d\burgers2d_ground_truth.npy | 45c8f507aa93861cb6cb5571e092d11e93a764ef322cd2944799f30caea5084c | f578b6acf3536ce62fea0f6696ab2938f11d2e63f7ede910f0b358f3ebd11c51 | [] | ["Task initial data are Gaussian; ground-truth source uses unseeded Noise. A trajectory error measures discrepancy between these runs, not solver correctness. Matching a seed alone does not establish the same initial field."] |
| heat_flow_code_only_0 | main | heat_flow_temperature_trj.npy | D:\Vivek\research\integration_runs\20261028T181330_344848Z_saved_context\runs\heat_flow\code_only_0\heat_flow_temperature_trj.npy | cf13272b3bd22805f53265235caa9e9a5a85372d3fc9d64da952cdc0f440f9d1 | D:\Vivek\research\test_heat_flow\heat_flow_ground_truth.npy | 7758259a8d8736e2cf766acc09436749360f51fc9427b9ad77bc0ef8238be288 | 39611a4534bacc8e961de6cb36e7e1b6a2d80ee0343e48f52adce89c8d4334f2 |  | ["Task PDE specifies x-only diffusion; ground-truth code calls multidimensional diffuse.implicit with spatial conductivity. Operator agreement is unverified."] |
| heat_flow_combined_0 | main | heat_flow_temperature_trj.npy | D:\Vivek\research\integration_runs\20261028T181330_344848Z_saved_context\runs\heat_flow\combined_0\heat_flow_temperature_trj.npy | dfea1bcee2952381b5917a254c767f04f634be9c8cdc421fa047b3aad3c5633c | D:\Vivek\research\test_heat_flow\heat_flow_ground_truth.npy | 7758259a8d8736e2cf766acc09436749360f51fc9427b9ad77bc0ef8238be288 | 39611a4534bacc8e961de6cb36e7e1b6a2d80ee0343e48f52adce89c8d4334f2 | [] | ["Task PDE specifies x-only diffusion; ground-truth code calls multidimensional diffuse.implicit with spatial conductivity. Operator agreement is unverified."] |
| julia_set_code_only_0 | main | julia_set_domain_trj.npy | D:\Vivek\research\integration_runs\20261028T181330_344848Z_saved_context\runs\julia_set\code_only_0\julia_set_domain_trj.npy | c883269d1348ebcf99a98716174a639b7d83a64104cb7c240e6e05467bc78e48 | D:\Vivek\research\test_julia_set\julia_set_ground_truth_trj.npy | d8986a5d23f0f668bc284c180ed24a628bbfdf906709fce9251acb318809fca0 | 622e2498f5b4b99e0df490ab25d28a26f1ee2dc1f0b2fef1afc1e593fe84d098 | [] | [] |
| julia_set_combined_0 | main | julia_set_domain_trj.npy | D:\Vivek\research\integration_runs\20261028T181330_344848Z_saved_context\runs\julia_set\combined_0\julia_set_domain_trj.npy | d8986a5d23f0f668bc284c180ed24a628bbfdf906709fce9251acb318809fca0 | D:\Vivek\research\test_julia_set\julia_set_ground_truth_trj.npy | d8986a5d23f0f668bc284c180ed24a628bbfdf906709fce9251acb318809fca0 | 622e2498f5b4b99e0df490ab25d28a26f1ee2dc1f0b2fef1afc1e593fe84d098 | [] | [] |
| reaction_diffusion_code_only_0 | u | reaction_diffusion_u_trj.npy | D:\Vivek\research\integration_runs\20261028T181330_344848Z_saved_context\runs\reaction_diffusion\code_only_0\reaction_diffusion_u_trj.npy | f53d7880c21f01875ef1eb605b034c87aeb8cfa95335072b2fb645efe50cc049 | D:\Vivek\research\test_reaction_diffusion\reaction_diffusion_ground_truth_u_trj.npy | 031c9fa2b47db15a669c9e12191d5987f20706ce668106e209f2b91432d8fd07 | ca81049a1ff4f524113c086e1ba863d4c831242529373ba1250ffcacf6f166f9 | [] | [] |
| reaction_diffusion_code_only_0 | v | reaction_diffusion_v_trj.npy | D:\Vivek\research\integration_runs\20261028T181330_344848Z_saved_context\runs\reaction_diffusion\code_only_0\reaction_diffusion_v_trj.npy | 624dcaf7dcc428d4a1ecfa425f4f2c0225acce0d5a30d3c9aef286f09d72b712 | D:\Vivek\research\test_reaction_diffusion\reaction_diffusion_ground_truth_v_trj.npy | 246398cc9ac3d33e7c1d99f21ebf1f48502a496e92abb5909a329221fa5c4b72 | ca81049a1ff4f524113c086e1ba863d4c831242529373ba1250ffcacf6f166f9 | [] | [] |
| reaction_diffusion_combined_0 | u | reaction_diffusion_u_trj.npy | D:\Vivek\research\integration_runs\20261028T181330_344848Z_saved_context\runs\reaction_diffusion\combined_0\reaction_diffusion_u_trj.npy | 031c9fa2b47db15a669c9e12191d5987f20706ce668106e209f2b91432d8fd07 | D:\Vivek\research\test_reaction_diffusion\reaction_diffusion_ground_truth_u_trj.npy | 031c9fa2b47db15a669c9e12191d5987f20706ce668106e209f2b91432d8fd07 | ca81049a1ff4f524113c086e1ba863d4c831242529373ba1250ffcacf6f166f9 | [] | [] |
| reaction_diffusion_combined_0 | v | reaction_diffusion_v_trj.npy | D:\Vivek\research\integration_runs\20261028T181330_344848Z_saved_context\runs\reaction_diffusion\combined_0\reaction_diffusion_v_trj.npy | 246398cc9ac3d33e7c1d99f21ebf1f48502a496e92abb5909a329221fa5c4b72 | D:\Vivek\research\test_reaction_diffusion\reaction_diffusion_ground_truth_v_trj.npy | 246398cc9ac3d33e7c1d99f21ebf1f48502a496e92abb5909a329221fa5c4b72 | ca81049a1ff4f524113c086e1ba863d4c831242529373ba1250ffcacf6f166f9 | [] | [] |

## Paired code-only versus combined observations

Deltas are combined minus code_only. Only matched fresh-generation controls receive descriptive execution deltas; only uncaveated measurements against the same hashed reference receive component RMSE deltas.

| domain | config_id | replicate | comparison_status | code_only_execution | combined_execution | execution_delta | component_rmse_deltas | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| burgers2d | 1ad8c65e9940 | 0 | observed_pair | passed | passed | 0 | [] | Descriptive comparison of complete code-only versus domain-guided retrieval pipelines; no significance or general improvement claim. Provider seed absent; stochastic generation is uncontrolled. |
| heat_flow | 1ad8c65e9940 | 0 | observed_pair | passed | passed | 0 | [] | Descriptive comparison of complete code-only versus domain-guided retrieval pipelines; no significance or general improvement claim. Provider seed absent; stochastic generation is uncontrolled. |
| julia_set | 1ad8c65e9940 | 0 | observed_pair | passed | passed | 0 | [{"component": "main", "rmse_delta": -7.519814523885068}] | Descriptive comparison of complete code-only versus domain-guided retrieval pipelines; no significance or general improvement claim. Provider seed absent; stochastic generation is uncontrolled. |
| reaction_diffusion | 1ad8c65e9940 | 0 | observed_pair | passed | passed | 0 | [{"component": "u", "rmse_delta": -3.7222935701477625e-08}, {"component": "v", "rmse_delta": -4.713715222466051e-08}] | Descriptive comparison of complete code-only versus domain-guided retrieval pipelines; no significance or general improvement claim. Provider seed absent; stochastic generation is uncontrolled. |

## Graph construction and retrieval coverage

| measure | value |
| --- | --- |
| context_origin | saved_retrieval_snapshot |
| live_graph_status | not_queried |
| model_preflight | {"available_models": ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5", "claude-fable-5-1", "claude-opus-5", "claude-sonnet-5", "claude-fable-5", "claude-opus-4-8", "claude-opus-4-7", "claude-sonnet-4-6", "claude-opus-4-6", "claude-opus-4-5-20251101", "claude-haiku-4-5-20251001", "claude-sonnet-4-5-20250929"], "model": "claude-sonnet-4-6", "status": "passed"} |
| source_snapshot | {"config_id": "1ad8c65e9940", "manifest_path": "D:\\Vivek\\research\\integration_runs\\20261022T020018_419755Z\\manifest.json", "manifest_sha256": "f29e6cdfebdae1f218392201c2bbddc6eace2fd5a2dabf63258c1503e792809f", "settings": {"class_limit": 6, "description_limit": 8, "fulltext_limit": 5, "function_limit": 6, "max_methods_per_class": 5, "max_nodes": 12, "max_semantic_queries": 12, "max_target_classes": 24, "max_target_functions": 32, "method_min_score": 0.3, "min_score": 0.2, "private_penalty": 0.15, "public_boost": 0.2, "top_k": 32}, "source_completed_utc": "2026-10-22T02:04:31.638761+00:00", "source_created_utc": "2026-10-22T02:00:18.421755+00:00"} |

| run_id | domain | variant | retrieval_status | domain_status | plan_source | code_nodes | domain_nodes | resolved_api_links | unresolved_api_links | context_chars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| burgers2d_code_only_0 | burgers2d | code_only | restored_not_requeried | disabled | saved_retrieval_snapshot | 12 | 0 | 0 | 0 | 15496 |
| burgers2d_combined_0 | burgers2d | combined | restored_not_requeried | available | saved_retrieval_snapshot | 12 | 23 | 5 | 0 | 23033 |
| heat_flow_code_only_0 | heat_flow | code_only | restored_not_requeried | disabled | saved_retrieval_snapshot | 12 | 0 | 0 | 0 | 9688 |
| heat_flow_combined_0 | heat_flow | combined | restored_not_requeried | available | saved_retrieval_snapshot | 12 | 25 | 4 | 0 | 22432 |
| julia_set_code_only_0 | julia_set | code_only | restored_not_requeried | disabled | saved_retrieval_snapshot | 12 | 0 | 0 | 0 | 12196 |
| julia_set_combined_0 | julia_set | combined | restored_not_requeried | available | saved_retrieval_snapshot | 12 | 27 | 2 | 0 | 21347 |
| reaction_diffusion_code_only_0 | reaction_diffusion | code_only | restored_not_requeried | disabled | saved_retrieval_snapshot | 12 | 0 | 0 | 0 | 16155 |
| reaction_diffusion_combined_0 | reaction_diffusion | combined | restored_not_requeried | available | saved_retrieval_snapshot | 12 | 40 | 2 | 1 | 25198 |

## Automated test outcomes

| name | status | tests | failures | errors | skipped | duration_s | details |
| --- | --- | --- | --- | --- | --- | --- | --- |
| test_audit_experiment.ExperimentAuditTests.test_aggregate_mapping_metadata_does_not_turn_unknown_counts_into_zero | passed | 1 | 0 | 0 | 0 | 0.032056 |  |
| test_audit_experiment.ExperimentAuditTests.test_all_nonfinite_empty_scalar_and_nonnumeric_arrays | passed | 1 | 0 | 0 | 0 | 0.074852 |  |
| test_audit_experiment.ExperimentAuditTests.test_changed_code_context_has_unknown_retention_not_false_absence | passed | 1 | 0 | 0 | 0 | 0.078729 |  |
| test_audit_experiment.ExperimentAuditTests.test_changed_hash_and_outside_paths_are_not_loaded | passed | 1 | 0 | 0 | 0 | 0.082838 |  |
| test_audit_experiment.ExperimentAuditTests.test_complex_ranges_are_explicit_magnitudes_and_safe_on_overflow | passed | 1 | 0 | 0 | 0 | 0.039997 |  |
| test_audit_experiment.ExperimentAuditTests.test_documentation_retention_uses_literal_code_context_fields_only | passed | 1 | 0 | 0 | 0 | 0.063763 |  |
| test_audit_experiment.ExperimentAuditTests.test_fortran_array_and_nonzero_frame_axis_use_temporal_first | passed | 1 | 0 | 0 | 0 | 0.034063 |  |
| test_audit_experiment.ExperimentAuditTests.test_incomplete_manifest_is_rejected_and_output_is_never_overwritten | passed | 1 | 0 | 0 | 0 | 0.158613 |  |
| test_audit_experiment.ExperimentAuditTests.test_local_prior_provenance_and_cached_state_dependencies_remain_explicit | passed | 1 | 0 | 0 | 0 | 0.027828 |  |
| test_audit_experiment.ExperimentAuditTests.test_mapping_statuses_and_ambiguity_are_not_invented_as_exact_matches | passed | 1 | 0 | 0 | 0 | 0.031679 |  |
| test_audit_experiment.ExperimentAuditTests.test_nan_inf_counts_first_frame_and_finite_only_range | passed | 1 | 0 | 0 | 0 | 0.033427 |  |
| test_audit_experiment.ExperimentAuditTests.test_object_pickle_and_invalid_axis_are_not_accepted | passed | 1 | 0 | 0 | 0 | 0.026884 |  |
| test_audit_experiment.ExperimentAuditTests.test_requested_filename_is_recognized_without_creating_a_score | passed | 1 | 0 | 0 | 0 | 0.043175 |  |
| test_audit_experiment.ExperimentAuditTests.test_wrong_output_name_remains_diagnostic_and_is_not_renamed | passed | 1 | 0 | 0 | 0 | 0.047401 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_additional_metadata_is_preserved_in_json | passed | 1 | 0 | 0 | 0 | 0.106563 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_artifacts_outside_run_directory_are_excluded | passed | 1 | 0 | 0 | 0 | 0.023188 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_axis_permutation_requires_explicit_metadata | passed | 1 | 0 | 0 | 0 | 0.032256 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_burgers_unseeded_initialization_is_caveated | passed | 1 | 0 | 0 | 0 | 0.124283 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_cached_outputs_are_excluded_even_if_execution_passed | passed | 1 | 0 | 0 | 0 | 0.018684 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_complex_magnitudes_are_preserved | passed | 1 | 0 | 0 | 0 | 0.027431 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_conventional_rmse_not_spatial_l2_norm | passed | 1 | 0 | 0 | 0 | 0.014861 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_domain_guided_code_context_changes_are_audited_as_pipeline_treatment | passed | 1 | 0 | 0 | 0 | 0.193509 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_empty_npy_files_return_comparison_error_instead_of_aborting_report | passed | 1 | 0 | 0 | 0 | 0.021541 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_empty_scalar_and_nonnumeric_arrays_are_rejected | passed | 1 | 0 | 0 | 0 | 0.030451 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_equal_length_conflicting_initial_frame_semantics_are_rejected | passed | 1 | 0 | 0 | 0 | 0.017874 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_execution_failure_and_generation_block_are_explicit | passed | 1 | 0 | 0 | 0 | 0.019075 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_heat_operator_mismatch_is_caveated_until_evidenced | passed | 1 | 0 | 0 | 0 | 0.153684 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_historical_rows_and_sources_remain_read_only | passed | 1 | 0 | 0 | 0 | 0.014795 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_initial_frame_is_dropped_only_with_explicit_metadata | passed | 1 | 0 | 0 | 0 | 0.018649 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_integer_subtraction_does_not_wrap | passed | 1 | 0 | 0 | 0 | 0.018282 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_matched_pair_does_not_compare_caveated_numerical_values | passed | 1 | 0 | 0 | 0 | 0.208278 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_missing_generated_artifact_is_explicit | passed | 1 | 0 | 0 | 0 | 0.022844 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_missing_reference_is_unavailable_not_zero | passed | 1 | 0 | 0 | 0 | 0.023173 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_nonfinite_arrays_are_not_scored | passed | 1 | 0 | 0 | 0 | 0.041866 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_numeric_overflow_is_not_reported_as_a_measurement | passed | 1 | 0 | 0 | 0 | 0.016616 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_pickle_object_arrays_are_rejected | passed | 1 | 0 | 0 | 0 | 0.012549 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_reference_shape_must_match_ground_truth_profile | passed | 1 | 0 | 0 | 0 | 0.019561 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_report_contains_detailed_tables_and_blank_missing_scores | passed | 1 | 0 | 0 | 0 | 0.139447 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_report_refuses_to_overwrite_any_existing_report | passed | 1 | 0 | 0 | 0 | 0.015955 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_report_serialization_is_deterministic_and_does_not_mutate_inputs | passed | 1 | 0 | 0 | 0 | 0.158849 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_rerun_can_measure_output_but_is_not_fresh_generation_pair | passed | 1 | 0 | 0 | 0 | 0.168914 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_shape_mismatch_never_broadcasts_or_truncates | passed | 1 | 0 | 0 | 0 | 0.021769 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_unmatched_generation_controls_block_claims | passed | 1 | 0 | 0 | 0 | 0.160747 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_unmeasured_context_does_not_create_efficacy_claim | passed | 1 | 0 | 0 | 0 | 0.156269 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_unsupported_domain_is_not_applicable | passed | 1 | 0 | 0 | 0 | 0.003555 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_wrong_filenames_do_not_score_accidental_old_outputs | passed | 1 | 0 | 0 | 0 | 0.021867 |  |
| test_combined_evaluation.CombinedEvaluationTests.test_zero_reference_matching_output_is_zero_error | passed | 1 | 0 | 0 | 0 | 0.014305 |  |
| test_combined_experiment.CombinedExperimentTests.test_also_rerun_existing_is_one_historical_row_not_fake_arm_pair | passed | 1 | 0 | 0 | 0 | 0.151125 |  |
| test_combined_experiment.CombinedExperimentTests.test_ast_screen_rejects_output_escape_or_dynamic_filenames | passed | 1 | 0 | 0 | 0 | 0.009992 |  |
| test_combined_experiment.CombinedExperimentTests.test_ast_screen_rejects_sensitive_imports_and_dynamic_calls | passed | 1 | 0 | 0 | 0 | 0.009495 |  |
| test_combined_experiment.CombinedExperimentTests.test_child_environment_excludes_all_inherited_secrets | passed | 1 | 0 | 0 | 0 | 0.014303 |  |
| test_combined_experiment.CombinedExperimentTests.test_combined_generation_rejects_empty_available_domain_context | passed | 1 | 0 | 0 | 0 | 0.104769 |  |
| test_combined_experiment.CombinedExperimentTests.test_combined_generation_requires_available_domain | passed | 1 | 0 | 0 | 0 | 0.103829 |  |
| test_combined_experiment.CombinedExperimentTests.test_default_retrieval_makes_no_llm_calls_and_records_cached_plan | passed | 1 | 0 | 0 | 0 | 0.109244 |  |
| test_combined_experiment.CombinedExperimentTests.test_each_arm_uses_new_directory_and_saves_audit_inputs | passed | 1 | 0 | 0 | 0 | 0.121541 |  |
| test_combined_experiment.CombinedExperimentTests.test_execution_guard_blocks_sensitive_code_before_subprocess | passed | 1 | 0 | 0 | 0 | 0.015616 |  |
| test_combined_experiment.CombinedExperimentTests.test_execution_timeout_retains_partial_logs | passed | 1 | 0 | 0 | 0 | 0.022352 |  |
| test_combined_experiment.CombinedExperimentTests.test_existing_output_directory_is_never_reused | passed | 1 | 0 | 0 | 0 | 0.018814 |  |
| test_combined_experiment.CombinedExperimentTests.test_failed_selected_domain_source_does_not_silently_fall_back_to_json | passed | 1 | 0 | 0 | 0 | 0.023387 |  |
| test_combined_experiment.CombinedExperimentTests.test_generate_preflight_block_preserves_retrieval_without_generation | passed | 1 | 0 | 0 | 0 | 0.112048 |  |
| test_combined_experiment.CombinedExperimentTests.test_generate_uses_one_blueprint_per_domain_and_no_implicit_execution | passed | 1 | 0 | 0 | 0 | 0.134488 |  |
| test_combined_experiment.CombinedExperimentTests.test_generation_receives_unmodified_api_resolution_evidence_and_hash | passed | 1 | 0 | 0 | 0 | 0.126331 |  |
| test_combined_experiment.CombinedExperimentTests.test_graph_snapshot_uses_only_read_sessions_and_hashes_ids | passed | 1 | 0 | 0 | 0 | 0.02553 |  |
| test_combined_experiment.CombinedExperimentTests.test_graph_topology_comparison_detects_changed_id_sets | passed | 1 | 0 | 0 | 0 | 0.01336 |  |
| test_combined_experiment.CombinedExperimentTests.test_injected_pipeline_cannot_bypass_generation_preflight_by_default | passed | 1 | 0 | 0 | 0 | 0.146607 |  |
| test_combined_experiment.CombinedExperimentTests.test_invalid_numeric_options_are_rejected | passed | 1 | 0 | 0 | 0 | 0.024544 |  |
| test_combined_experiment.CombinedExperimentTests.test_invalid_test_results_schema_stops_before_any_pipeline_calls | passed | 1 | 0 | 0 | 0 | 0.045225 |  |
| test_combined_experiment.CombinedExperimentTests.test_missing_cached_blueprint_blocks_rows_without_llm_fallback | passed | 1 | 0 | 0 | 0 | 0.113059 |  |
| test_combined_experiment.CombinedExperimentTests.test_no_execute_flag_never_runs_existing_script | passed | 1 | 0 | 0 | 0 | 0.086228 |  |
| test_combined_experiment.CombinedExperimentTests.test_partial_retrieval_failure_keeps_successful_arm_and_manifest | passed | 1 | 0 | 0 | 0 | 0.183883 |  |
| test_combined_experiment.CombinedExperimentTests.test_per_test_results_are_loaded_hashed_and_exported | passed | 1 | 0 | 0 | 0 | 0.140422 |  |
| test_combined_experiment.CombinedExperimentTests.test_retrieval_live_setup_does_not_import_or_configure_llm_client | passed | 1 | 0 | 0 | 0 | 0.02094 |  |
| test_combined_experiment.CombinedExperimentTests.test_subprocess_receives_isolated_cwd_restricted_environment_and_timeout | passed | 1 | 0 | 0 | 0 | 0.026648 |  |
| test_combined_experiment.CombinedExperimentTests.test_unavailable_snapshot_never_claims_graph_unchanged | passed | 1 | 0 | 0 | 0 | 0.009696 |  |
| test_combined_experiment.CombinedExperimentTests.test_variants_share_immutable_blueprint_and_settings | passed | 1 | 0 | 0 | 0 | 0.113923 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_code_node_statistics_follow_serializer_definition_selection | passed | 1 | 0 | 0 | 0 | 0.005441 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_code_only_bypasses_domain_driver_and_domain_retriever | passed | 1 | 0 | 0 | 0 | 0.006672 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_combined_merges_planner_hints_and_uses_terminal_index_names | passed | 1 | 0 | 0 | 0 | 0.00633 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_driver_calls_are_read_only_explicit_and_not_closed | passed | 1 | 0 | 0 | 0 | 0.01209 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_duplicate_exact_aliases_are_not_resolved_by_filename_guess | passed | 1 | 0 | 0 | 0 | 0.007283 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_duplicate_legacy_file_candidates_remain_ambiguous | passed | 1 | 0 | 0 | 0 | 0.007403 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_exact_alias_resolution_adds_seed_and_retains_caveat | passed | 1 | 0 | 0 | 0 | 0.005606 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_invalid_variant_and_budgets_fail_before_external_calls | passed | 1 | 0 | 0 | 0 | 0.006598 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_low_scoring_required_public_api_is_pinned_before_ranked_noise | passed | 1 | 0 | 0 | 0 | 0.010628 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_metadata_settings_and_automatic_planner_are_forwarded | passed | 1 | 0 | 0 | 0 | 0.007839 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_missing_domain_uses_code_context_and_reports_status | passed | 1 | 0 | 0 | 0 | 0.005652 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_no_code_driver_produces_unavailable_resolution_without_connecting | passed | 1 | 0 | 0 | 0 | 0.006109 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_private_code_candidates_are_never_seeded | passed | 1 | 0 | 0 | 0 | 0.006563 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_private_raw_relation_cannot_be_pinned_by_id | passed | 1 | 0 | 0 | 0 | 0.01163 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_shared_blueprint_and_sane_query_caps_are_deterministic | passed | 1 | 0 | 0 | 0 | 0.00736 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_structural_metadata_completion_runs_after_pinning | passed | 1 | 0 | 0 | 0 | 0.006334 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_terminal_name_alone_cannot_resolve_wrong_file | passed | 1 | 0 | 0 | 0 | 0.006977 |  |
| test_combined_retrieval.CombinedRetrievalTests.test_unique_file_basename_match_is_explicit_candidate | passed | 1 | 0 | 0 | 0 | 0.011663 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_builds_four_references_and_complete_provenance | passed | 1 | 0 | 0 | 0 | 0.295389 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_burgers_reads_diffused_velocity_for_advection | passed | 1 | 0 | 0 | 0 | 0.197648 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_cli_connection_overrides_selected_file_only | passed | 1 | 0 | 0 | 0 | 0.108467 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_cli_reports_underlying_neo4j_error_with_redacted_traceback | passed | 1 | 0 | 0 | 0 | 0.227186 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_cli_synchronizes_neo4j_by_default | passed | 1 | 0 | 0 | 0 | 0.224272 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_configuration_check_does_not_build_or_connect | passed | 1 | 0 | 0 | 0 | 0.074738 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_console_and_log_file_redact_passwords | passed | 1 | 0 | 0 | 0 | 0.082108 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_explicit_file_is_the_only_credentials_source | passed | 1 | 0 | 0 | 0 | 0.095516 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_export_only_does_not_load_credentials_or_connect | passed | 1 | 0 | 0 | 0 | 0.250809 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_extra_state_update_is_not_silently_omitted | passed | 1 | 0 | 0 | 0 | 0.110516 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_failed_validation_leaves_previous_export_unchanged | passed | 1 | 0 | 0 | 0 | 0.139617 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_heat_reads_coefficient_but_only_writes_temperature | passed | 1 | 0 | 0 | 0 | 0.177588 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_helper_and_parameter_dependencies_are_connected | passed | 1 | 0 | 0 | 0 | 0.184368 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_incomplete_file_blocks_cli_before_build_or_write | passed | 1 | 0 | 0 | 0 | 0.068615 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_incomplete_local_file_never_borrows_a_password | passed | 1 | 0 | 0 | 0 | 0.067061 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_interpolation_cannot_import_inherited_credentials | passed | 1 | 0 | 0 | 0 | 0.065889 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_invalid_uri_rejected_before_connecting | passed | 1 | 0 | 0 | 0 | 0.055993 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_julia_computed_output_has_no_invented_save | passed | 1 | 0 | 0 | 0 | 0.16294 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_local_file_wins_over_root_file_and_inherited_environment | passed | 1 | 0 | 0 | 0 | 0.074414 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_missing_and_empty_sources_reported_without_invented_references | passed | 1 | 0 | 0 | 0 | 0.234417 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_missing_credentials_have_actionable_error | passed | 1 | 0 | 0 | 0 | 0.058938 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_missing_dotenv_dependency_does_not_enable_environment_fallback | passed | 1 | 0 | 0 | 0 | 0.056486 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_missing_local_file_never_falls_back | passed | 1 | 0 | 0 | 0 | 0.060821 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_neo4j_batches_are_scoped_and_parameterized | passed | 1 | 0 | 0 | 0 | 0.173626 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_neo4j_logs_connection_batches_commit_and_verified_counts | passed | 1 | 0 | 0 | 0 | 0.185474 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_notes_remain_guidance | passed | 1 | 0 | 0 | 0 | 0.168221 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_npy_header_inspection_and_truncation | passed | 1 | 0 | 0 | 0 | 0.073712 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_path_escape_rejected | passed | 1 | 0 | 0 | 0 | 0.069034 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_post_commit_mismatch_does_not_report_verified_success | passed | 1 | 0 | 0 | 0 | 0.185803 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_reaction_cache_retains_old_state_dependencies | passed | 1 | 0 | 0 | 0 | 0.156266 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_reversed_recipe_is_rejected | passed | 1 | 0 | 0 | 0 | 0.078888 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_same_inputs_have_identical_graph_and_ids | passed | 1 | 0 | 0 | 0 | 0.475061 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_source_edit_invalidates_stale_step | passed | 1 | 0 | 0 | 0 | 0.098471 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_static_resolution_does_not_promote_external_candidates | passed | 1 | 0 | 0 | 0 | 0.16724 |  |
| test_domain_knowledge_graph.DomainGraphTests.test_writer_rejects_empty_or_cross_dataset_graph | passed | 1 | 0 | 0 | 0 | 0.222365 |  |
| test_domain_retrieval.DomainRetrievalTests.test_bounded_neo4j_paths_cover_current_owned_recipe_edges | passed | 1 | 0 | 0 | 0 | 0.000484 |  |
| test_domain_retrieval.DomainRetrievalTests.test_burgers_advection_uses_already_diffused_state | passed | 1 | 0 | 0 | 0 | 0.014273 |  |
| test_domain_retrieval.DomainRetrievalTests.test_cached_reaction_is_read_at_produced_version | passed | 1 | 0 | 0 | 0 | 0.015171 |  |
| test_domain_retrieval.DomainRetrievalTests.test_dataset_isolation_filters_local_nodes_and_edges | passed | 1 | 0 | 0 | 0 | 0.032896 |  |
| test_domain_retrieval.DomainRetrievalTests.test_default_context_budget_preserves_every_recipe_step | passed | 1 | 0 | 0 | 0 | 0.084892 |  |
| test_domain_retrieval.DomainRetrievalTests.test_empty_graph_and_unknown_domain_fall_back_cleanly | passed | 1 | 0 | 0 | 0 | 0.008161 |  |
| test_domain_retrieval.DomainRetrievalTests.test_explicit_selection_does_not_follow_incoming_shared_api_edges | passed | 1 | 0 | 0 | 0 | 0.00972 |  |
| test_domain_retrieval.DomainRetrievalTests.test_helper_formulas_parameters_and_output_conventions_are_preserved | passed | 1 | 0 | 0 | 0 | 0.012787 |  |
| test_domain_retrieval.DomainRetrievalTests.test_input_snapshot_and_returned_context_are_independent | passed | 1 | 0 | 0 | 0 | 0.022172 |  |
| test_domain_retrieval.DomainRetrievalTests.test_julia_temporary_parameter_is_not_lost | passed | 1 | 0 | 0 | 0 | 0.013438 |  |
| test_domain_retrieval.DomainRetrievalTests.test_missing_or_blank_domain_does_not_infer_from_task | passed | 1 | 0 | 0 | 0 | 0.010847 |  |
| test_domain_retrieval.DomainRetrievalTests.test_neo4j_domain_cannot_change_query_structure | passed | 1 | 0 | 0 | 0 | 0.019569 |  |
| test_domain_retrieval.DomainRetrievalTests.test_neo4j_empty_result_is_clean_and_read_errors_remain_visible | passed | 1 | 0 | 0 | 0 | 0.02189 |  |
| test_domain_retrieval.DomainRetrievalTests.test_neo4j_null_projection_fields_match_local_export | passed | 1 | 0 | 0 | 0 | 0.03142 |  |
| test_domain_retrieval.DomainRetrievalTests.test_neo4j_read_uses_safe_parameterized_query_and_explicit_database | passed | 1 | 0 | 0 | 0 | 0.045316 |  |
| test_domain_retrieval.DomainRetrievalTests.test_oversized_core_is_flagged_without_cutting_json_or_steps | passed | 1 | 0 | 0 | 0 | 0.027986 |  |
| test_domain_retrieval.DomainRetrievalTests.test_public_alias_survives_missing_observed_call | passed | 1 | 0 | 0 | 0 | 0.033278 |  |
| test_domain_retrieval.DomainRetrievalTests.test_public_aliases_are_usable_code_search_hints | passed | 1 | 0 | 0 | 0 | 0.021432 |  |
| test_domain_retrieval.DomainRetrievalTests.test_reference_steps_follow_source_order_not_storage_order | passed | 1 | 0 | 0 | 0 | 0.061651 |  |
| test_domain_retrieval.DomainRetrievalTests.test_schema_and_adapter_ambiguities_fail_visibly | passed | 1 | 0 | 0 | 0 | 0.000988 |  |
| test_domain_retrieval.DomainRetrievalTests.test_task_requirements_override_reference_output_defaults | passed | 1 | 0 | 0 | 0 | 0.019071 |  |
| test_domain_retrieval.DomainRetrievalTests.test_unresolved_apis_are_candidates_without_verification_claim | passed | 1 | 0 | 0 | 0 | 0.024417 |  |
| test_domain_retrieval.DomainRetrievalTests.test_whole_program_and_save_expression_are_not_prompt_context | passed | 1 | 0 | 0 | 0 | 0.036765 |  |
| test_pipeline_config.PipelineConfigTests.test_connection_interpolation_rejected_for_every_setting | passed | 1 | 0 | 0 | 0 | 0.041171 |  |
| test_pipeline_config.PipelineConfigTests.test_describe_connection_is_read_only_and_secret_free | passed | 1 | 0 | 0 | 0 | 0.018203 |  |
| test_pipeline_config.PipelineConfigTests.test_driver_construction_is_lazy_bounded_and_does_not_create_session | passed | 1 | 0 | 0 | 0 | 0.022041 |  |
| test_pipeline_config.PipelineConfigTests.test_driver_constructor_error_is_redacted | passed | 1 | 0 | 0 | 0 | 0.008345 |  |
| test_pipeline_config.PipelineConfigTests.test_explicit_code_and_domain_files_do_not_mix | passed | 1 | 0 | 0 | 0 | 0.032156 |  |
| test_pipeline_config.PipelineConfigTests.test_inherited_values_are_ignored_and_environment_is_unchanged | passed | 1 | 0 | 0 | 0 | 0.024471 |  |
| test_pipeline_config.PipelineConfigTests.test_invalid_role_and_implicit_file_are_rejected | passed | 1 | 0 | 0 | 0 | 0.008572 |  |
| test_pipeline_config.PipelineConfigTests.test_llm_interpolation_and_placeholders_rejected | passed | 1 | 0 | 0 | 0 | 0.035275 |  |
| test_pipeline_config.PipelineConfigTests.test_llm_missing_key_does_not_use_environment | passed | 1 | 0 | 0 | 0 | 0.015312 |  |
| test_pipeline_config.PipelineConfigTests.test_llm_model_and_workspace_must_be_literal_if_provided | passed | 1 | 0 | 0 | 0 | 0.03915 |  |
| test_pipeline_config.PipelineConfigTests.test_llm_model_precedence_and_optional_workspace | passed | 1 | 0 | 0 | 0 | 0.020298 |  |
| test_pipeline_config.PipelineConfigTests.test_llm_only_file_does_not_require_database_settings | passed | 1 | 0 | 0 | 0 | 0.026208 |  |
| test_pipeline_config.PipelineConfigTests.test_missing_domain_password_never_uses_root_or_environment | passed | 1 | 0 | 0 | 0 | 0.015811 |  |
| test_pipeline_config.PipelineConfigTests.test_missing_selected_file_never_falls_back | passed | 1 | 0 | 0 | 0 | 0.010378 |  |
| test_pipeline_config.PipelineConfigTests.test_placeholder_credentials_rejected_without_echoing_value | passed | 1 | 0 | 0 | 0 | 0.030674 |  |
| test_pipeline_config.PipelineConfigTests.test_redaction_covers_database_password_and_api_key | passed | 1 | 0 | 0 | 0 | 0.021741 |  |
| test_pipeline_config.PipelineConfigTests.test_relative_path_is_explicitly_resolved_under_root | passed | 1 | 0 | 0 | 0 | 0.016658 |  |
| test_pipeline_config.PipelineConfigTests.test_uri_with_embedded_credentials_is_rejected | passed | 1 | 0 | 0 | 0 | 0.035024 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_blueprint_errors_are_redacted_before_logging | passed | 1 | 0 | 0 | 0 | 0.021856 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_definition_with_only_description_edge_remains_available | passed | 1 | 0 | 0 | 0 | 0.000868 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_disabled_llm_blocks_even_injected_client | passed | 1 | 0 | 0 | 0 | 0.001206 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_generation_prioritizes_task_and_records_usage | passed | 1 | 0 | 0 | 0 | 0.001367 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_generation_sees_unresolved_mapping_evidence | passed | 1 | 0 | 0 | 0 | 0.001597 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_injected_resources_are_not_closed | passed | 1 | 0 | 0 | 0 | 0.000884 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_injection_does_not_load_config_or_embedding_model | passed | 1 | 0 | 0 | 0 | 0.001407 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_metadata_closure_is_idempotent_and_ignores_unselected_definitions | passed | 1 | 0 | 0 | 0 | 0.000624 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_method_description_rows_respect_owning_class_quota | passed | 1 | 0 | 0 | 0 | 0.001005 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_namespace_attribute_import_and_class_import_are_valid_patterns | passed | 1 | 0 | 0 | 0 | 0.000589 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_parameter_type_metadata_survives_filtering_and_row_order | passed | 1 | 0 | 0 | 0 | 0.00107 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_public_method_uses_initialized_instance | passed | 1 | 0 | 0 | 0 | 0.000569 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_sessions_use_read_access_and_selected_database | passed | 1 | 0 | 0 | 0 | 0.001008 |  |
| test_pipeline_integration.PipelineIntegrationTests.test_truncated_generation_is_rejected | passed | 1 | 0 | 0 | 0 | 0.001558 |  |
| test_saved_context_experiment.SavedContextExperimentTests.test_all_eight_source_arms_validate_before_clients_exist | passed | 1 | 0 | 0 | 0 | 0.478901 |  |
| test_saved_context_experiment.SavedContextExperimentTests.test_authentication_failure_blocks_remaining_calls_without_reroll | passed | 1 | 0 | 0 | 0 | 0.819575 |  |
| test_saved_context_experiment.SavedContextExperimentTests.test_changed_current_task_is_rejected | passed | 1 | 0 | 0 | 0 | 0.176325 |  |
| test_saved_context_experiment.SavedContextExperimentTests.test_combined_prior_requires_available_status_and_nonempty_text | passed | 1 | 0 | 0 | 0 | 0.197789 |  |
| test_saved_context_experiment.SavedContextExperimentTests.test_credit_failure_also_blocks_remaining_generations | passed | 1 | 0 | 0 | 0 | 0.355757 |  |
| test_saved_context_experiment.SavedContextExperimentTests.test_effective_blueprint_hash_is_validated | passed | 1 | 0 | 0 | 0 | 0.199735 |  |
| test_saved_context_experiment.SavedContextExperimentTests.test_eight_fresh_generations_preserve_snapshot_provenance_and_api_evidence | passed | 1 | 0 | 0 | 0 | 0.403986 |  |
| test_saved_context_experiment.SavedContextExperimentTests.test_historical_rows_are_ignored_without_becoming_fresh_arms | passed | 1 | 0 | 0 | 0 | 0.193486 |  |
| test_saved_context_experiment.SavedContextExperimentTests.test_incomplete_manifest_is_rejected | passed | 1 | 0 | 0 | 0 | 0.077112 |  |
| test_saved_context_experiment.SavedContextExperimentTests.test_isolated_generation_failure_does_not_retry_or_discard_other_results | passed | 1 | 0 | 0 | 0 | 0.381297 |  |
| test_saved_context_experiment.SavedContextExperimentTests.test_missing_or_duplicate_arms_fail_before_any_paid_call | passed | 1 | 0 | 0 | 0 | 0.180106 |  |
| test_saved_context_experiment.SavedContextExperimentTests.test_no_graph_guards_reject_accidental_reads | passed | 1 | 0 | 0 | 0 | 0.058986 |  |
| test_saved_context_experiment.SavedContextExperimentTests.test_output_collision_prevents_api_or_generation_access | passed | 1 | 0 | 0 | 0 | 0.186501 |  |
| test_saved_context_experiment.SavedContextExperimentTests.test_paired_base_blueprints_must_match | passed | 1 | 0 | 0 | 0 | 0.169602 |  |
| test_saved_context_experiment.SavedContextExperimentTests.test_tampered_code_context_is_rejected | passed | 1 | 0 | 0 | 0 | 0.18878 |  |
| test_saved_context_experiment.SavedContextExperimentTests.test_test_outcomes_load_into_all_report_exports | passed | 1 | 0 | 0 | 0 | 0.413332 |  |

## Historical files (read only; not new generation results)

Historical objective/physics scores and RMSE retain their original definitions. They are not combined with fresh metrics. CSV exports contain every supplied historical row; previews below show at most 20 per source.

| path | status | rows | bytes | sha256 | provenance | error |
| --- | --- | --- | --- | --- | --- | --- |
| D:\Vivek\research\evaluation_report.csv | available | 8 | 605 | 944652f4f9b8ef61f464152c82ee4da85c81329c2c99c3bd66989988e2a3c705 | historical_read_only |  |
| D:\Vivek\research\evaluation_report.json | available | 8 | 8931 | ca6d8ab636abb9c5b9e90d5fd852152f10fc43384146c9838a5d1ee0c54d2580 | historical_read_only |  |
| D:\Vivek\research\l2summary.csv | available | 3 | 611 | ed09577aed8ab3a477743650428565b1447601ef82d6928aa173b81354fbaae7 | historical_read_only |  |

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

## Interpretation limits

- Fresh generation outcomes require real LLM calls; offline graph/retrieval checks do not establish generation improvement.
- Execution success is separate from numerical agreement and physical validity.
- Reference hashes identify the exact stored arrays; references were not regenerated by this report.
- Historical RMSE/objective/physics-score formulas differ from this report and are not directly comparable.
- One paired sample per domain is descriptive evidence and cannot establish statistical superiority.
