# Fresh code-only versus combined generation: October 28 results

The fresh comparison completed **8 new generations and 8 successful script
executions**, one code-only and one combined attempt for each of four domains.
Every script wrote its requested output filenames. Numerical validity was more
selective: code-only Burgers and heat outputs contained nonfinite values, while
all four combined outputs were finite. Combined Julia and both combined reaction
diffusion arrays exactly matched their stored references by SHA256.

After both database instances became available, a separate live retrieval
rechecked all eight arms. Its saved task/code/domain/API-resolution inputs
matched the inputs used for generation exactly. This verification made no
additional LLM requests and did not repeat any generations.

These generations used the **validated October 21 retrieval snapshot**. They did
not perform new planning, embedding, graph retrieval, or graph integrity checks.
The comparison measures new generation conditioned on those frozen contexts,
not the availability or present contents of either database. One attempt per
arm is a descriptive result, not evidence of statistical superiority.

The domain priors were extracted from the same labeled reference simulations
used for numerical comparison. This evaluates reference reproduction with
reference-derived guidance, subject to the task/reference disagreements below.
It does not evaluate held-out tasks or demonstrate generalization to new domains.

## Run, inputs, and validation

| Item | Recorded value |
| --- | --- |
| New run | `20261028T181330_344848Z_saved_context` |
| Started | October 28, 2026, 2:13:30 p.m. EDT / 18:13:30 UTC |
| Completed | October 28, 2026, 2:16:32 p.m. EDT / 18:16:32 UTC |
| Model | `claude-sonnet-4-6` |
| Generation controls | Temperature 0; maximum 20,000 output tokens; no provider seed |
| Attempts | One per domain/variant; no retries, rerolls, or manual script repairs |
| Retrieval source | `20261022T020018_419755Z`, completed October 21 at 10:04:31 p.m. EDT |
| Retrieval configuration | `1ad8c65e9940` |
| Context status | `restored_not_requeried`, origin `saved_retrieval_snapshot` |
| Graph status during generation | `not_queried` |
| Recorded offline tests | 199 passed; zero failures/errors/skips; 17.473 seconds |

The four current task sheets matched the original task hashes. All eight source
arms passed saved-context validation before provider access: configuration,
passed original retrieval, task/context text hashes, available nonempty combined
priors, matching paired base blueprints, and recorded mapping/effective-blueprint
hashes where available. Windows newline normalization is accounted for when
checking text hashes; separate raw source-file hashes are preserved.

The source manifest SHA256 was
`f29e6cdfebdae1f218392201c2bbddc6eace2fd5a2dabf63258c1503e792809f`.
The original snapshot stored a character count rather than a hash for complete
`context.md`; that limitation remains explicit. Code/domain context hashes,
source dates, API mappings, original records, and source directories accompany
the new records. Cached contexts are inputs; the scripts and output arrays are
fresh artifacts.

The separate live-graph [preflight at 2:03 p.m. EDT](../integration_runs/20261028T180317_552196Z/manifest.json)
passed API authentication/model availability but could not retrieve the code
graph because of DNS resolution failure; the selected local domain endpoint
also could not supply routing information. The saved-context run did not change
those connection files or claim the connections had recovered.

See the [new manifest](../integration_runs/20261028T181330_344848Z_saved_context/manifest.json),
[full report](../integration_runs/20261028T181330_344848Z_saved_context/reports/combined_evaluation.md),
and [saved-context workflow](COMBINED_PIPELINE.md#fresh-generation-from-a-frozen-retrieval-snapshot).
The recorded saved-context invocation was:

```powershell
python knowledge_context/run_saved_context_experiment.py --context-manifest integration_runs/20261022T020018_419755Z/manifest.json --execute --timeout 120 --test-results integration_runs/validation_20261028T181257_012262Z/test_outcomes.json
```

Every invocation creates a new output directory. Repeating it would be a new
generation sample, not a reproduction guaranteed to return identical code.

## Eight generation and execution outcomes

All responses ended with `end_turn`; none hit the output-token limit. Execution
duration below excludes provider latency and is not a controlled runtime
benchmark. Each script ran in its own new directory under the usual AST screen,
restricted child environment, and timeout; those controls are not an OS sandbox.

| Domain | Variant and generated script | Generation | Execution | Duration (s) | Requested arrays | Numerical result |
| --- | --- | --- | --- | ---: | --- | --- |
| Burgers 2D | [code_only](../integration_runs/20261028T181330_344848Z_saved_context/runs/burgers2d/code_only_0/generated_burgers2d_simulation.py) | generated | passed | 18.248828 | Present | Comparison error: nonfinite output |
| Burgers 2D | [combined](../integration_runs/20261028T181330_344848Z_saved_context/runs/burgers2d/combined_0/generated_burgers2d_simulation.py) | generated | passed | 32.313646 | Present | Measured, reference/task caveat |
| Heat flow | [code_only](../integration_runs/20261028T181330_344848Z_saved_context/runs/heat_flow/code_only_0/generated_heat_flow_simulation.py) | generated | passed | 9.978705 | Present | Comparison error: nonfinite output |
| Heat flow | [combined](../integration_runs/20261028T181330_344848Z_saved_context/runs/heat_flow/combined_0/generated_heat_flow_simulation.py) | generated | passed | 36.898029 | Present | Measured, reference/task caveat |
| Julia set | [code_only](../integration_runs/20261028T181330_344848Z_saved_context/runs/julia_set/code_only_0/generated_julia_set_simulation.py) | generated | passed | 9.631615 | Present | Measured |
| Julia set | [combined](../integration_runs/20261028T181330_344848Z_saved_context/runs/julia_set/combined_0/generated_julia_set_simulation.py) | generated | passed | 2.429867 | Present | Measured; reference hash match |
| Reaction diffusion | [code_only](../integration_runs/20261028T181330_344848Z_saved_context/runs/reaction_diffusion/code_only_0/generated_reaction_diffusion_simulation.py) | generated | passed | 3.302460 | Both u/v present | Both measured |
| Reaction diffusion | [combined](../integration_runs/20261028T181330_344848Z_saved_context/runs/reaction_diffusion/combined_0/generated_reaction_diffusion_simulation.py) | generated | passed | 3.714028 | Both u/v present | Both measured; reference hash matches |

Passing execution means the process exited successfully. It does not imply
finite results, reference agreement, or fulfillment of the intended physics.
The run produced ten requested arrays: two contained nonfinite values, and
eight were finite. All four combined arms were finite; two code-only arms were.

## Numerical comparisons

RMSE uses `sqrt(mean(abs(generated-reference)**2))` over all aligned elements;
relative RMSE divides by the reference RMS. These corrected definitions differ
from historical frame-L2-based RMSE reports. No spatial transpose, truncation,
or initial-frame removal was used for these measured comparisons.

| Domain/component | Code-only RMSE | Combined RMSE | Code-only relative RMSE | Combined relative RMSE | Interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| Burgers 2D | Unavailable | 0.3798066919711809 | Unavailable | 0.9961133520880253 | Baseline nonfinite; reference has unseeded noise rather than requested Gaussian initial data |
| Heat flow | Unavailable | 2.082628732015258e-6 | Unavailable | 5.54557562481197e-6 | Baseline nonfinite; x-only task versus multidimensional reference operator remains unresolved |
| Julia set | 7.519814523885068 | 0 | 4.823887539800515 | 0 | Combined array matches the stored reference |
| Reaction diffusion u | 3.7222935701477625e-8 | 0 | 7.051910545897388e-8 | 0 | Both finite; combined array matches the stored reference |
| Reaction diffusion v | 4.713715222466051e-8 | 0 | 1.1019166615607521e-7 | 0 | Both finite; combined array matches the stored reference |

The Burgers and heat combined measurements are labeled `measured_caveated`.
They quantify reference discrepancy, not proof of solving exactly the task's
requested problem. In particular, heat's small reference error cannot resolve
the x-only-versus-multidimensional operator disagreement. Stored references were
read rather than regenerated and do not independently establish physical truth.

| Diagnostic | Code-only Burgers | Code-only heat |
| --- | ---: | ---: |
| Array elements | 827,392 | 505,000 |
| NaN/infinite values | 501,554 | 210,074 |
| First nonfinite frame, zero-based | 13 | 16 |
| Expected filename present | Yes | Yes |

Unlike the October 21 historical reruns, these fresh baselines wrote the correct
filenames. Their failures are numerical, not missing-name failures. The
[artifact diagnostics](../integration_runs/20261028T181330_344848Z_saved_context/audit/artifact_diagnostics.csv)
retain shapes, dtypes, counts, hashes, and finite-only ranges for all ten arrays.

### Exact combined-reference matches

| Component | Combined artifact and reference | Shared SHA256 |
| --- | --- | --- |
| Julia set | [New output](../integration_runs/20261028T181330_344848Z_saved_context/runs/julia_set/combined_0/julia_set_domain_trj.npy) / [stored reference](../test_julia_set/julia_set_ground_truth_trj.npy) | `d8986a5d23f0f668bc284c180ed24a628bbfdf906709fce9251acb318809fca0` |
| Reaction diffusion u | [New output](../integration_runs/20261028T181330_344848Z_saved_context/runs/reaction_diffusion/combined_0/reaction_diffusion_u_trj.npy) / [stored reference](../test_reaction_diffusion/reaction_diffusion_ground_truth_u_trj.npy) | `031c9fa2b47db15a669c9e12191d5987f20706ce668106e209f2b91432d8fd07` |
| Reaction diffusion v | [New output](../integration_runs/20261028T181330_344848Z_saved_context/runs/reaction_diffusion/combined_0/reaction_diffusion_v_trj.npy) / [stored reference](../test_reaction_diffusion/reaction_diffusion_ground_truth_v_trj.npy) | `246398cc9ac3d33e7c1d99f21ebf1f48502a496e92abb5909a329221fa5c4b72` |

Full generated/reference/source hashes and per-frame L2 summaries appear in
[numerical_comparisons.csv](../integration_runs/20261028T181330_344848Z_saved_context/reports/numerical_comparisons.csv).

## Paired observations and evidence limits

The paired report compares the complete code-only versus combined prompt and
retrieval-context treatment. The saved base plan/configuration, task, model,
temperature, output-token budget, and replicate agree; retrieved code contexts
may differ intentionally and both hashes remain visible.

| Domain | Execution delta, combined minus code-only | Eligible RMSE delta(s) |
| --- | ---: | --- |
| Burgers 2D | 0 | None: baseline nonfinite and reference/task caveat |
| Heat flow | 0 | None: baseline nonfinite and reference/task caveat |
| Julia set | 0 | -7.519814523885068 |
| Reaction diffusion | 0 | u: -3.7222935701477625e-8; v: -4.713715222466051e-8 |

Each row is an `observed_pair`, not a general improvement estimate. Both scripts
exited successfully in every domain, so execution deltas are zero even when
numerical outputs differ substantially. Caveated/unavailable metrics are not
turned into zero errors. No provider seed was supplied; temperature zero does
not establish identical future generations. There was one sample per arm and
no repair loop, so there are no variance estimates or significance claims.

See [paired_comparisons.csv](../integration_runs/20261028T181330_344848Z_saved_context/reports/paired_comparisons.csv)
and [full report criteria](../integration_runs/20261028T181330_344848Z_saved_context/reports/combined_evaluation.json).

## Input evidence, usage, and audit tables

The restored coverage remains the October 21 coverage: 12 serialized code nodes
per arm, combined domain counts 23/25/27/40, 13 exact-alias API matches across
the four combined contexts, and unresolved reaction `field.laplace`. None of
those counts were freshly queried during generation. The saved-context labels
remain explicit in [retrieval_coverage.csv](../integration_runs/20261028T181330_344848Z_saved_context/reports/retrieval_coverage.csv).

| Domain | Code-only input/output tokens | Combined input/output tokens |
| --- | ---: | ---: |
| Burgers 2D | 5,289 / 344 | 7,715 / 390 |
| Heat flow | 3,572 / 520 | 7,407 / 244 |
| Julia set | 4,181 / 268 | 6,996 / 284 |
| Reaction diffusion | 5,380 / 752 | 8,439 / 491 |

Recorded provider usage totals 48,979 input tokens and 3,293 output tokens across
the eight generations. These are usage observations, not a monetary cost or a
controlled latency comparison.

The [detailed audit](../integration_runs/20261028T181330_344848Z_saved_context/audit/audit_report.md)
and [audit JSON](../integration_runs/20261028T181330_344848Z_saved_context/audit/audit.json)
provide 14 additional CSV tables covering restored API mappings, literal import
documentation retention, the selected local domain snapshot, and current-run
artifact diagnostics. Local-snapshot recipe tables do not establish current
live-graph contents. The seven main report CSVs and 14 audit CSVs give
21 core experiment tables; the later live-comparison and automated validation
CSVs are separate.

The run embeds 199 passing offline test records. Their independently saved
[summary](../integration_runs/validation_20261028T181257_012262Z/summary.json),
[per-test CSV](../integration_runs/validation_20261028T181257_012262Z/test_outcomes.csv),
[JSON](../integration_runs/validation_20261028T181257_012262Z/test_outcomes.json),
and [log](../integration_runs/validation_20261028T181257_012262Z/unittest.log)
document the 17.473-second validation. The experiment also exports its attached
[test outcome table](../integration_runs/20261028T181330_344848Z_saved_context/reports/test_outcomes.csv).

The earlier [integration results](INTEGRATION_RESULTS.md) remain a separate
historical record of retrieval and existing-script reruns. Their numerical
outcomes are not substituted into this fresh comparison.

## Post-generation live verification

After the user opened both instances, a separate read-only retrieval ran from
2:18:03 to 2:21:32 p.m. EDT on October 28 (18:18:03–18:21:32 UTC). This started
after fresh generation completed at 2:16:32 p.m. It made no LLM requests and did
not regenerate or modify the eight scripts.

| Verification | Recorded result |
| --- | --- |
| Live retrieval arms | 8 / 8 passed |
| Task/code-context/domain-context/API-resolution hashes | All four hashes matched for all 8 arms |
| Saved artifacts independently checked against their hashes | Both used-input and live-input files verified for all 8 arms |
| Complete context text | Identical in all 8 arms |
| Base/effective plans and core retrieval statistics | Identical in all 8 arms |
| Code graph, before/after this live retrieval | 6,391 nodes / 8,483 relationships; element-ID hashes unchanged |
| Domain graph, before/after this live retrieval | 108 nodes / 178 relationships; element-ID hashes unchanged |

The [live manifest](../integration_runs/20261028T181803_519861Z/manifest.json)
and [live report](../integration_runs/20261028T181803_519861Z/reports/combined_evaluation.md)
record this separate successful retrieval. The offline comparison is preserved
as [Markdown](../integration_runs/20261028T181330_344848Z_saved_context/audit/live_context_comparison.md),
[CSV](../integration_runs/20261028T181330_344848Z_saved_context/audit/live_context_comparison.csv),
and [JSON](../integration_runs/20261028T181330_344848Z_saved_context/audit/live_context_comparison.json),
with a [reproducible comparison script](../integration_runs/20261028T181330_344848Z_saved_context/audit/compare_live_contexts.py).

This confirms that the later live retrieval returned the same recorded inputs
used in the frozen-context generation experiment. It does not retroactively
make the generations a fresh-planning/live-retrieval run, establish equivalence
of every database property, or compare old versus restored-database element IDs.
Topology checks compare each graph with itself before/after this later retrieval;
properties were not hashed. Neither operation wrote to the databases.
