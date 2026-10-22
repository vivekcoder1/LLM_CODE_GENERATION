# Combined knowledge graph integration: measured results

The completed run retrieved both knowledge sources successfully for all four
supported domains: **8 of 8 retrieval variants passed**. It also reran the four
existing simulation scripts once each in isolated directories: **4 of 4 exited
successfully**. No new LLM generations or LLM/API requests occurred in this run.

The recorded offline suite attached to this experiment contains **164 passing
tests**. A separate final post-audit validation contains **180 passing tests**;
both suites recorded zero failures, errors, or skips. Both graph snapshots retained the
same node/relationship counts and element-ID hashes. Property values were not
compared.

This demonstrates working read-only retrieval integration and execution of
existing code. It does not measure whether domain knowledge improves newly
generated code, numerical accuracy, or physical correctness.

## Recorded run and commands

Run identifier: `20261022T020018_419755Z`; configuration: `1ad8c65e9940`.

| Recorded event | America/New_York | UTC |
| --- | --- | --- |
| Live experiment started | October 21, 2026, 10:00:18 p.m. EDT | October 22, 2026, 02:00:18 UTC |
| Live experiment completed | October 21, 2026, 10:04:31 p.m. EDT | October 22, 2026, 02:04:31 UTC |

The folder name uses UTC, which accounts for its October 22 date. The exact
experiment command, run from the research directory, was:

```powershell
python knowledge_context/run_combined_experiment.py --mode retrieval --also-rerun-existing --execute --domain-source neo4j --timeout 120 --test-results integration_runs/validation_20261022T015938_472015Z/test_outcomes.json
```

The runner selected root `.env` for the existing **code** graph and
`knowledge_context/.env` for the **domain** graph. Both connections used `READ`
mode with the selected server's default database. Configuration was independently
parsed without credential fallback. The five required code indexes were online;
preflight recorded no errors. Search blueprints came from task-hash-matched
cached files, and the embedding model loaded from its existing local cache.

Start with the [full human-readable report](../integration_runs/20261022T020018_419755Z/reports/combined_evaluation.md)
or the [complete manifest](../integration_runs/20261022T020018_419755Z/manifest.json).
The [pipeline guide](COMBINED_PIPELINE.md) documents configuration, CLI controls,
schemas, metrics, and extension workflows.

## Eight retrieval outcomes

The same cached base blueprint and retrieval configuration were supplied to both
variants for each task. The combined variant added the selected domain recipe
and its API/search hints. The resulting code contexts therefore also differ;
this run is not an experiment that holds retrieved code fixed while adding only
domain prose.

| Domain | Variant | Status | Code nodes | Domain nodes | API matches | Unresolved API hints | Context characters |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Burgers 2D | [code_only](../integration_runs/20261022T020018_419755Z/runs/burgers2d/code_only_0/context.md) | passed | 12 | 0 | 0 | 0 | 15,496 |
| Burgers 2D | [combined](../integration_runs/20261022T020018_419755Z/runs/burgers2d/combined_0/context.md) | passed | 12 | 23 | 5 | 0 | 23,033 |
| Heat flow | [code_only](../integration_runs/20261022T020018_419755Z/runs/heat_flow/code_only_0/context.md) | passed | 12 | 0 | 0 | 0 | 9,688 |
| Heat flow | [combined](../integration_runs/20261022T020018_419755Z/runs/heat_flow/combined_0/context.md) | passed | 12 | 25 | 4 | 0 | 22,432 |
| Julia set | [code_only](../integration_runs/20261022T020018_419755Z/runs/julia_set/code_only_0/context.md) | passed | 12 | 0 | 0 | 0 | 12,196 |
| Julia set | [combined](../integration_runs/20261022T020018_419755Z/runs/julia_set/combined_0/context.md) | passed | 12 | 27 | 2 | 0 | 21,347 |
| Reaction diffusion | [code_only](../integration_runs/20261022T020018_419755Z/runs/reaction_diffusion/code_only_0/context.md) | passed | 12 | 0 | 0 | 0 | 16,155 |
| Reaction diffusion | [combined](../integration_runs/20261022T020018_419755Z/runs/reaction_diffusion/combined_0/context.md) | passed | 12 | 40 | 2 | 1 | 25,198 |

Counts describe each retrieved context, not new database entities. Shared nodes
can occur in more than one domain's context. Context length is characters, not
an exact token count. The `code_only` variant does not attempt domain/API joins,
so zero domain counts there are expected rather than missing-data failures.

All 13 API matches across the four combined domain contexts were exact alias
matches. There was one unresolved hint:

| Domain | Exact alias matches | Unresolved hint |
| --- | --- | --- |
| Burgers 2D | `CenteredGrid`, `Noise`, `Box`, `advect.semi_lagrangian`, `diffuse.implicit` | None |
| Heat flow | `CenteredGrid`, `Box`, `union`, `diffuse.implicit` | None |
| Julia set | `CenteredGrid`, `Box` | None |
| Reaction diffusion | `CenteredGrid`, `Box` | `field.laplace` |

These are successful joins against public code metadata, not runtime verification
of every import, signature, or mathematical operation. The unresolved reaction
hint remains visible instead of being silently treated as verified. Complete
seed/relation counts are in [retrieval_coverage.csv](../integration_runs/20261022T020018_419755Z/reports/retrieval_coverage.csv);
each combined record preserves its candidate and resolution evidence.

### Documentation retained for the same resolved hints

The offline [detailed audit](../integration_runs/20261022T020018_419755Z/audit/audit_report.md)
checked whether each resolved hint's literal `Import Path` field appeared in the
saved **code context**, excluding API-resolution metadata elsewhere in a prompt.
This measures retained API documentation rather than simply mentioning a name.

| Domain | Resolved hints in denominator | Documented in code_only | Documented in combined | Excluded unresolved hints |
| --- | ---: | ---: | ---: | ---: |
| Burgers 2D | 5 | 1 / 5 | 5 / 5 | 0 |
| Heat flow | 4 | 0 / 4 | 4 / 4 | 0 |
| Julia set | 2 | 0 / 2 | 2 / 2 | 0 |
| Reaction diffusion | 2 | 1 / 2 | 2 / 2 | 1 |
| Total across domain contexts | 13 | 2 / 13 | 13 / 13 | 1 |

These count the same resolved recipe hints, with repeated APIs counted within
each applicable domain. The unresolved `field.laplace` hint is outside the
13-hint denominator. This is retrieval-documentation coverage, not a measured
generation-quality improvement. See [per-binding evidence](../integration_runs/20261022T020018_419755Z/audit/api_documentation_retention.csv)
and [per-domain totals](../integration_runs/20261022T020018_419755Z/audit/api_documentation_summary.csv).

The audit adds **14 CSV tables**, an [audit JSON](../integration_runs/20261022T020018_419755Z/audit/audit.json),
and its Markdown report. Together with the seven main report CSVs, there are
21 experiment CSV tables; the final validation CSV is separate. API mappings describe the completed live run; its
domain-field/parameter/step/dependency tables describe the selected **local domain
graph snapshot**. Those local tables do not establish identical live-graph
content. The [audit table dictionary](COMBINED_PIPELINE.md#offline-audit-and-additional-data-tables)
explains each export and its provenance.

## Independent existing-script reruns

Each existing script was copied into a `historical_rerun_0` directory and executed
there once. These are separate from the eight retrieval records. Their
provenance is `existing_outputs_rerun`, not fresh context-conditioned generation.

| Domain | Execution | Duration (s) | Requested output contract | Numerical status |
| --- | --- | ---: | --- | --- |
| [Burgers 2D script](../integration_runs/20261022T020018_419755Z/runs/burgers2d/historical_rerun_0/generated_burgers2d_simulation.py) | passed | 4.559137 | Expected `burgers2d_velocity_trj.npy`; script wrote `burgers2d_trj.npy` | `generated_artifact_missing` |
| [Heat flow script](../integration_runs/20261022T020018_419755Z/runs/heat_flow/historical_rerun_0/generated_heat_flow_simulation.py) | passed | 5.401386 | Expected `heat_flow_temperature_trj.npy`; script wrote `heat_flow_trj.npy` | `generated_artifact_missing` |
| [Julia set script](../integration_runs/20261022T020018_419755Z/runs/julia_set/historical_rerun_0/generated_julia_set_simulation.py) | passed | 1.671940 | `julia_set_domain_trj.npy` present | `measured` |
| [Reaction diffusion script](../integration_runs/20261022T020018_419755Z/runs/reaction_diffusion/historical_rerun_0/generated_reaction_diffusion_simulation.py) | passed | 3.611833 | Both requested u/v arrays present | `measured;measured` |

Exiting successfully does not establish the artifact contract or numerical
correctness. The evaluator did not rename the Burgers/heat arrays or substitute
old files from the source test directories. Their requested outputs are missing,
so this report assigns no numerical error to those reruns.

There are also substantive reference/task disagreements: Burgers requests a
Gaussian initialization while its labeled reference uses unseeded noise; heat
requests x-only diffusion while its reference calls multidimensional implicit
diffusion. Resolving filenames alone would not make these controlled comparisons
of the same requested problem.

The separate artifact audit inspected the files actually written, retaining their
wrong-name status and assigning no task score. It found numerical failures as
well as the naming failures:

| Observed artifact | Contract name matches | Elements | NaN/infinite values | First nonfinite frame (zero-based) | Recorded hash check |
| --- | --- | ---: | ---: | ---: | --- |
| `burgers2d_trj.npy` | No | 827,392 | 501,554 | 13 | matched |
| `heat_flow_trj.npy` | No | 505,000 | 209,082 | 16 | matched |
| `julia_set_domain_trj.npy` | Yes | 6,553,600 | 0 | None | matched |
| `reaction_diffusion_u_trj.npy` | Yes | 1,010,000 | 0 | None | matched |
| `reaction_diffusion_v_trj.npy` | Yes | 1,010,000 | 0 | None | matched |

All five actual artifact hashes matched their recorded values. The Burgers/heat
reruns therefore cannot be treated as numerically valid simply because their
processes exited successfully. Full shape/dtype, finite-value ranges, hashes,
and diagnostic provenance are in [artifact_diagnostics.csv](../integration_runs/20261022T020018_419755Z/audit/artifact_diagnostics.csv).

### Measured numerical evidence

The three measured components had matching trajectory shapes and required no
axis moves or initial-frame removal. All measured arrays passed finite-value
checks. RMSE below is conventional elementwise error, calculated in float64,
not the historical root-mean-square frame-L2 formula.

| Domain/component | Compared shape | RMSE | Relative RMSE | Mean frame L2 | Max frame L2 |
| --- | --- | ---: | ---: | ---: | ---: |
| Julia set | `(100, 256, 256)` | 0 | 0 | 0 | 0 |
| Reaction diffusion u | `(101, 100, 100)` | 3.759517680198327e-8 | 7.122431876168713e-8 | 3.4535277661947686e-6 | 5.751848220825195e-6 |
| Reaction diffusion v | `(101, 100, 100)` | 4.7717842180089515e-8 | 1.1154913453693643e-7 | 4.572451737224804e-6 | 8.242237986666813e-6 |

The fresh Julia rerun output has the same SHA256 as the stored reference, in
addition to zero measured array error. Reaction diffusion has small measured
discrepancies; this report does not attribute their cause. Stored references
were read, not regenerated, and their hashes identify the exact evidence used.

| Component | Current-run output | Stored reference | SHA256 evidence |
| --- | --- | --- | --- |
| Julia set | [Output array](../integration_runs/20261022T020018_419755Z/runs/julia_set/historical_rerun_0/julia_set_domain_trj.npy) | [Reference array](../test_julia_set/julia_set_ground_truth_trj.npy) | Both: `d8986a5d23f0f668bc284c180ed24a628bbfdf906709fce9251acb318809fca0` |
| Reaction u | [Output array](../integration_runs/20261022T020018_419755Z/runs/reaction_diffusion/historical_rerun_0/reaction_diffusion_u_trj.npy) | [Reference array](../test_reaction_diffusion/reaction_diffusion_ground_truth_u_trj.npy) | Output: `6fbbfae32c60e1ae3b88b05b1bf0b47016eed70124b9ebcc6a4a156c09589743`; reference: `031c9fa2b47db15a669c9e12191d5987f20706ce668106e209f2b91432d8fd07` |
| Reaction v | [Output array](../integration_runs/20261022T020018_419755Z/runs/reaction_diffusion/historical_rerun_0/reaction_diffusion_v_trj.npy) | [Reference array](../test_reaction_diffusion/reaction_diffusion_ground_truth_v_trj.npy) | Output: `51c1af6bfbef9ccb9e23c6653b7da2ceb9aa8a316fead44aea80d8444d844348`; reference: `246398cc9ac3d33e7c1d99f21ebf1f48502a496e92abb5909a329221fa5c4b72` |

[numerical_comparisons.csv](../integration_runs/20261022T020018_419755Z/reports/numerical_comparisons.csv)
also contains source hashes, reference RMS values, complete shapes, alignment
actions, statuses, and caveats. These results belong to existing scripts and
cannot be used as outcomes of the newly assembled combined prompts.

## Read-only graph evidence

| Graph role | Nodes before/after | Relationships before/after | Snapshot result |
| --- | ---: | ---: | --- |
| Existing code graph | 6,391 / 6,391 | 8,483 / 8,483 | `unchanged_topology_ids` |
| Domain graph | 108 / 108 | 178 / 178 | `unchanged_topology_ids` |

The complete ordered element-ID SHA256 values matched before and after:

| Graph | Node-ID SHA256 | Relationship-ID SHA256 |
| --- | --- | --- |
| Code | `61ad8abbdde054272a769502fbd30a4b6cb1326aea588c17afc30a44dec27ee8` | `49d2b92228a85e9153c0040e2b049e42abff272be65f3a4c13afc22d7fa8c489` |
| Domain | `755bae099e781a1f297387aefc72c1d18c83efb9eaee60fd52969db22b95609e` | `d444e98319ad3e008b4a9e504ce2e068790047fe4e91f8dc055d512163bb924f` |

This measures counts and identity sets only. It does not compare properties,
exclude concurrent activity, or constitute a database backup. The integration
ran graph reads and did not invoke `TreeGen.py`, `public_api_checker.py`, or the
domain constructor's synchronization operation.

Aura emitted deprecation notifications for the current full-text/vector
`queryNodes` procedures while returning successful retrieval results. Query
compatibility is a future maintenance concern, not a failed retrieval in this
recorded run.

## Attached automated validation

| Recorded suite | Tests | Failures | Errors | Skips | Duration (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Attached experiment snapshot | 164 | 0 | 0 | 0 | 15.297 |
| Final post-audit offline suite | 180 | 0 | 0 | 0 | 14.320 |

The first row is the suite snapshot attached to the measured experiment; the
second is the separate final validation after the audit and remaining integration
checks. Both use injected/mocked services and do not replace live retrieval or
simulation evidence. The experiment report retains its 164-test snapshot rather
than presenting later checks as having preceded it.

The recorded source [test_outcomes.json](../integration_runs/validation_20261022T015938_472015Z/test_outcomes.json)
has SHA256 `3f4001c5a25c8eae632b9e1947b0f2c4854b814a5b47be822058b79bb0e448ff`.
See its [summary](../integration_runs/validation_20261022T015938_472015Z/summary.json),
[full unittest log](../integration_runs/validation_20261022T015938_472015Z/unittest.log),
and the experiment's [test outcome table](../integration_runs/20261022T020018_419755Z/reports/test_outcomes.csv).

Final validation is recorded separately in
[summary.json](../integration_runs/validation_20261022T020915_342591Z/summary.json),
[test_outcomes.csv](../integration_runs/validation_20261022T020915_342591Z/test_outcomes.csv),
[test_outcomes.json](../integration_runs/validation_20261022T020915_342591Z/test_outcomes.json),
and [unittest.log](../integration_runs/validation_20261022T020915_342591Z/unittest.log).
Its UTC completion was October 22, 2026, 02:09:29, or October 21 at 10:09:29 p.m.
EDT in New York.

For another auditable validation, choose a new directory:

```powershell
python knowledge_context/run_offline_tests.py --output-dir integration_runs/validation_followup
```

Pass that directory's `test_outcomes.json` to a later experiment with
`--test-results`. The runner refuses an already-existing output directory.

## Local environment observed for this summary

| Component | Installed version |
| --- | --- |
| Python | 3.12.1, Windows AMD64 |
| NumPy | 2.3.5 |
| PhiFlow | 3.4.0 |
| PhiML | 1.16.1 |
| JAX | 0.11.1 |
| Neo4j Python driver | 6.2.0 |
| Sentence Transformers | 5.6.0 |
| Pydantic | 2.13.4 |
| python-dotenv | 1.2.2 |

These versions were inspected locally when preparing the summary. They are not
a complete dependency lockfile. The retrieval run used a cached embedding model;
no model download was requested. Provider model/API behavior was not tested by
this no-generation experiment.

## Evidence boundaries and follow-up

Every retrieval record has generation `not_requested` and execution `not_run`.
All four paired-comparison rows therefore say `not_fresh_generation`, with blank
execution/RMSE deltas. The independently executed historical scripts cannot fill
those fields. There is no observed generation-effect estimate, significance
test, or claim that a larger context improved model behavior.

The original evaluation, L2, and cross-domain reports remain read only. Their
rows are included in [historical_inventory.csv](../integration_runs/20261022T020018_419755Z/reports/historical_inventory.csv)
and [historical_rows.csv](../integration_runs/20261022T020018_419755Z/reports/historical_rows.csv)
with separate provenance. Their legacy metric definitions are not mixed with
the corrected current-run RMSE. Use the full [JSON report](../integration_runs/20261022T020018_419755Z/reports/combined_evaluation.json)
for the complete machine-readable record and the [pipeline guide](COMBINED_PIPELINE.md)
for a future explicitly authorized fresh-generation experiment.
