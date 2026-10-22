# Combining domain knowledge with the code knowledge graph

The simulation pipeline now retrieves ground-truth domain recipes and the
existing PhiFlow code graph. It finds the public classes/functions needed by a
recipe, retrieves their API documentation, and supplies both kinds of evidence
to generation. The current task controls initial conditions, equations,
parameters, and output filenames when reference evidence differs.

The connection happens during retrieval. The databases retain their schemas and
can remain on separate Aura instances. This integration performs **Neo4j reads
only**: it does not migrate nodes, create cross-database relationships, update
flags, create indexes, or run either graph constructor.

## Quick start

From the research directory, compare retrieval using cached search plans and no
LLM/API calls:

```powershell
python .\knowledge_context\run_combined_experiment.py
```

The existing entry points forward arguments to the same runner:

```powershell
python .\llm-querying.py --mode retrieval
.\run_pipeline.ps1 --mode retrieval
```

To also rerun each existing simulation once in a new directory:

```powershell
python .\knowledge_context\run_combined_experiment.py --mode retrieval --also-rerun-existing --execute
```

This creates two retrieval records (`code_only`, `combined`) and one independent
`historical_rerun` record per domain. The historical script is copied and
executed once per domain per replicate. Its output is never attributed to either
newly retrieved context, and no new scripts are generated.

To rerun existing scripts without graph access:

```powershell
python .\knowledge_context\run_combined_experiment.py --mode existing --execute
```

The runner prints manifest and report paths. Check each record's status: a
completed report can contain blocked retrievals, failed executions, missing
artifacts, and unavailable numerical comparisons. The process exit code alone
does not mean every domain passed.

## Which files configure which service

| Role | Default selected file | Settings used | When accessed |
| --- | --- | --- | --- |
| Existing code graph | Project root `.env` | `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`; optional `NEO4J_DATABASE` | Retrieval/generation |
| Domain graph | `knowledge_context/.env` | Same Neo4j keys, independently parsed | `--domain-source neo4j` |
| LLM | Project root `.env` | `ANTHROPIC_API_KEY`; optional `ANTHROPIC_WORKSPACE_ID`, `ANTHROPIC_MODEL` | Explicit `generate` mode |
| Domain inspection export | `knowledge_context/domain_knowledge_graph.json` | No connection credentials | Explicit `--domain-source json` |

The constructor in [KNOWLEDGE_GRAPH.md](KNOWLEDGE_GRAPH.md) still selects
`knowledge_context/.env` for its own domain-graph writes. The combined runner is
a separate read-only consumer. Selecting root `.env` for the **code** role is
intentional and does not alter the constructor's credential isolation.

[`pipeline_config.py`](pipeline_config.py) uses `dotenv_values` with interpolation
disabled. Each role reads one complete, explicitly selected file. Missing files,
required values, placeholders such as `YOUR-PASSWORD`, and `${...}` references
fail validation. Inherited `NEO4J_*` or `ANTHROPIC_*` variables cannot fill gaps
or override the selected file. Reading settings does not mutate `os.environ`.

Select different files explicitly when needed:

```powershell
python .\knowledge_context\run_combined_experiment.py --code-env-file .\code-graph.env --domain-env-file .\domain-graph.env
```

Files must contain literal credentials. Omitting optional `NEO4J_DATABASE` uses
the selected server's default database; when supplied, use that instance's exact
database name. Connection summaries include the selected file, role, sanitized
URI, user, database, and `READ` mode. Loaded passwords/API keys are redacted from
diagnostics.

Drivers are lazy, with a 10-second connection timeout, 20-second acquisition
timeout, and no transaction retry window. Sessions select
`default_access_mode="READ"`. Read routing describes this pipeline's behavior;
it does not change the database user's permissions.

## Graph schemas and the retrieval join

| Information | Existing code graph | Domain graph |
| --- | --- | --- |
| Purpose | Describe available APIs and Python structure | Describe a labeled reference simulation's approach |
| Producers | `TreeGen.py`, then `public_api_checker.py` | `domain_knowledge_graph_creater.py` |
| Main entities | `File`, `Class`, `Function`, `Method`, `Parameter`, `Type`, `GeneratedDescription` | `ReferenceSimulation`, `Domain`, `FieldSpec`, `UpdateStep`, `ParameterSpec`, `OutputSpec`, `CodeComponent`, `ApiCandidate`, `Guidance` |
| API identity | Legacy IDs such as `diffuse.py:implicit` and annotated public import paths | Namespaced IDs, qualified names, configured aliases, local definition provenance |
| Main relationships | `defines_class`, `defines_function`, `has_method`, `has_parameter`, `of_type`, `returns_type`, `has_description` | `HAS_FIELD`, `HAS_STEP`, `NEXT_STEP`, `READS`, `WRITES`, `USES_API`, `USES_PARAMETER`, `PRODUCES`, `GUIDED_BY` |
| Model context | Public usage, docstrings, descriptions, parameter/return metadata | Initialization, coefficients, order, state dependencies, output conventions, source spans, unresolved differences |

`domain_retrieval.py` follows the selected reference's owned outgoing recipe
relationships within `ground_truth_domains`. It does not traverse backward
through shared API components into unrelated recipes. Facts retain source paths,
hashes, line spans, evidence categories, and review status.

The prompt view omits the full reference program. It retains structured
expressions, ordered operations, helper formulas, and state dependencies. The
default domain context budget is 16,000 characters, with optional prose omitted
first. An oversized core remains intact and reports `core_exceeds_budget` rather
than silently losing an operation. Character budgets are not model token counts.

`combined_retrieval.py` performs the integration:

1. Start both variants from the same base search blueprint.
2. For `combined`, add domain semantic searches and API hints within configured
   limits, reserving space for domain hints.
3. Search the existing code graph's full-text and vector indexes.
4. Resolve statically identified domain APIs against public code nodes. Prefer
   exact alias matches; retain legacy file-basename matches as candidates.
5. Add resolved API nodes to the seeds and expand their code neighborhoods.
6. Rank public APIs, retain recipe APIs, complete structural metadata, and
   serialize documented usage.
7. Return code/domain context, merged blueprint, API resolution evidence,
   coverage statistics, and the combined context.

Join results are request-local dictionaries, never new Neo4j relationships.
`resolved_candidate` based on a basename cannot prove a package namespace:
TreeGen uses file basenames rather than complete module identities. Public
import annotations are also not runtime verification. Ambiguous and unresolved
matches remain visible.

The code retriever recognizes `of_type` edges, preserves isolated seed metadata,
carries generated descriptions into context, and emits valid `phi.flow`
attribute usage examples. Domain records are serialized separately so code
public-API filtering does not discard them.

## Required indexes and cached embedding model

| Existing code index | Retrieval use |
| --- | --- |
| `classNames` | Full-text class names |
| `functionNames` | Full-text function names |
| `descEmbed` | Generated-description semantic search |
| `funcDocEmbed` | Function-docstring semantic search |
| `classDocEmbed` | Class-docstring semantic search |

The runner reads `SHOW INDEXES` and records missing/offline indexes; it does not
repair them. The embedding model must match stored embeddings. The original
pipeline uses 384-dimensional `all-MiniLM-L6-v2`. Loading sets
`local_files_only=True`: a missing cache blocks retrieval instead of downloading.

The live Aura retrieval check returned results while emitting deprecation
notifications for the existing `db.index.fulltext.queryNodes` and
`db.index.vector.queryNodes` procedures. Those notifications did not prevent
this run's queries from succeeding. A future compatibility update should change
and test the retrieval query syntax against the intended Neo4j version; this
integration does not change indexes or perform a database migration.

## Modes and experimental controls

| Mode | Graph reads | LLM/API calls | Script execution | Evidence produced |
| --- | --- | --- | --- | --- |
| `retrieval` (default) | Code and selected domain source | None | None | Context contents and retrieval/API coverage |
| `retrieval --also-rerun-existing --execute` | As above | None | Independent copied historical scripts | Retrieval comparison plus current-environment execution evidence |
| `existing --execute` | None | None | Copied historical scripts | Existing-code execution/artifact contracts |
| `generate` | Code and selected domain source | Model-list preflight, planning, new code generation when configured | Only with `--execute` | New context-conditioned outputs, subject to controls/caveats |

Cached plans must have the optimizer's original filename:
`<domain>_<first 12 characters of SHA1(task text)>_blueprint.json`. The default
directory is `optimization_runs/cache`. Changed tasks need matching plans.
Retrieval mode never asks an LLM to replace missing cache entries. Records save
the plan path, task SHA1, and plan SHA256.

Default domains are Burgers 2D, heat flow, Julia set, and reaction diffusion,
which have populated recipes and stored references. Other selectable domains
may lack a recipe, numerical profile, or cached plan; absences receive explicit
statuses.

Fresh generation is a separate future opt-in. A later authorized run can use
`--mode generate --execute`, a valid `--llm-env-file`, and an appropriate
`--model`. The runner checks the account's model listing first. Model precedence
is explicit `--model`, then `ANTHROPIC_MODEL` in that file, then
`claude-sonnet-4-6`. Authentication/model errors block generation. Retrieval and
existing modes do not perform that preflight or create an LLM client.

Generation receives code documentation and reference prior separately. Its
prompt permits local step/initialization helpers and standard Python/NumPy
operations while requiring documented public framework APIs. The current task
takes priority over reference values and filenames. A response stopped by
`max_tokens` is rejected as incomplete.

## CLI reference

| Option | Default | Meaning |
| --- | --- | --- |
| `--mode` | `retrieval` | `retrieval`, `existing`, or explicit `generate` |
| `--domains` | Four populated domains | Domains to process |
| `--output-dir` | New UTC-stamped directory under `integration_runs/` | Must not already exist |
| `--execute` | Off | Execute scripts supplied by the selected mode |
| `--also-rerun-existing` | Off | Add independent historical reruns in retrieval mode |
| `--repeats` | `1` | Replicates; also repeats historical reruns |
| `--timeout` | `120` | Execution timeout in seconds |
| `--max-tokens` | `20000` | Generation output limit |
| `--code-env-file` | Root `.env` | Code-graph credentials |
| `--domain-env-file` | `knowledge_context/.env` | Domain-graph credentials |
| `--llm-env-file` | Root `.env` | Generation credentials |
| `--model` | File setting, then `claude-sonnet-4-6` | Model override |
| `--domain-source` | `neo4j` | Explicit `neo4j` or `json` |
| `--domain-graph-json` | `knowledge_context/domain_knowledge_graph.json` | Export for JSON mode |
| `--blueprint-dir` | `optimization_runs/cache` | Task-matched cached plans |
| `--embedding-model` | `all-MiniLM-L6-v2` | Cached model matching graph embeddings |
| `--settings-file` | None | Retrieval-settings JSON overrides |
| `--test-results` | None | JSON list of recorded offline test outcomes to attach to the report |
| `--project-root` | Directory containing `llm-querying.py` | Task/source/history root; credential options remain independently explicit |

The runner's configuration uses `top_k=32`, `min_score=0.2`,
`method_min_score=0.3`, at most five methods per class, `max_nodes=12`, full-text
limit 5, description limit 8, and function/class limits 6. The lower-level
`combined_retrieval.DEFAULT_SETTINGS` has general defaults; experiments supply
and record their own settings. Settings overrides are hashed into `config_id`.

Example: read domain knowledge from JSON while querying the code KG:

```powershell
.\run_pipeline.ps1 --domain-source json --domains julia_set reaction_diffusion
```

## Output layout and detailed tables

Each invocation creates a new directory and refuses to overwrite an existing
one. The manifest is updated incrementally, preserving blocked/failed records.

```text
integration_runs/<new run>/
  manifest.json
  runs/<domain>/<variant>_<replicate>/
    task.md
    blueprint.json
    record.json
    code_context.md                 # successful retrieval
    domain_context.md               # empty for code_only
    context.md
    generated_<domain>_simulation.py # copied/generated script records only
    stdout.txt                      # attempted execution
    stderr.txt
    <requested output arrays>
  reports/
    combined_evaluation.md
    combined_evaluation.json
    combined_evaluation.csv
    numerical_comparisons.csv
    retrieval_coverage.csv
    test_outcomes.csv
    paired_comparisons.csv
    historical_inventory.csv
    historical_rows.csv
```

| File | Contents | Interpretation |
| --- | --- | --- |
| `manifest.json` | Settings, explicit targets, preflight, plans, records, graph checks, report paths | Audit trail for this invocation |
| `combined_evaluation.md` | Outcome/control/metric/hash/retrieval/test tables and historical previews | Human-readable entry point |
| `combined_evaluation.json` | Full enriched records, criteria, limitations, supplied tests/history | Structured source |
| `combined_evaluation.csv` | One row per domain/variant/replicate with statuses, controls, provenance | Which stages actually ran |
| `numerical_comparisons.csv` | Component-level shapes, RMSE, L2, hashes, paths, caveats | Discrepancy measurements with evidence |
| `retrieval_coverage.csv` | Code/domain counts, API matches, unresolved matches, seeds/relations, context size | Retrieved evidence coverage; not generation accuracy |
| `test_outcomes.csv` | Supplied automated suite results | Empty means no test evidence was supplied to this report |
| `paired_comparisons.csv` | Eligibility/control matching and descriptive deltas | Historical reruns never qualify as fresh paired generation |
| `historical_inventory.csv` | Existing report paths, hashes, sizes, row counts, availability | Historical evidence identity |
| `historical_rows.csv` | Every supplied historical row with its original source | Original metric definitions retained |

Graph integrity reads node/relationship counts and hashes of element-ID sets
before/after. `unchanged_topology_ids` means those observations match. It does
not compare property values, exclude concurrent activity, or provide a backup.

## Execution and artifact contracts

The runner executes copied/new scripts in isolated run directories, with a
timeout, a restricted child environment without inherited service credentials,
and an AST screen for obvious network/process/configuration access and unsafe
output paths. This is not an operating-system security sandbox. Original test
scripts/arrays are not execution targets.

Numerical evaluation requires successful execution, explicit current-run
provenance, and reported artifacts inside the isolated directory using exact
requested names. Cached arrays, missing/wrongly named artifacts, nonfinite
trajectories, and failed executions remain distinct statuses.

| Domain | Requested output(s) | Reference shape(s) |
| --- | --- | --- |
| Burgers 2D | `burgers2d_velocity_trj.npy` | `(101, 64, 64, 2)` |
| Heat flow | `heat_flow_temperature_trj.npy` | `(101, 100, 50)` |
| Julia set | `julia_set_domain_trj.npy` | `(100, 256, 256)` |
| Reaction diffusion | `reaction_diffusion_u_trj.npy`, `reaction_diffusion_v_trj.npy` | Each `(101, 100, 100)` |

A script can exit successfully while writing an older filename. That is an
execution pass and an artifact-contract failure; both facts remain visible.
The runner does not rename outputs to make a contract appear to pass.

## Numerical definitions and interpretation

| Measure | Definition | Meaning |
| --- | --- | --- |
| RMSE | `sqrt(mean(abs(g - r)**2))` over all elements | Field units; normalized for array size |
| Reference RMS | `sqrt(mean(abs(r)**2))` | Normalization magnitude |
| Relative RMSE | `RMSE / RMS(reference)` | Dimensionless; undefined for zero reference with nonzero error |
| Per-frame L2 | `sqrt(sum(abs(g[t] - r[t])**2))` | Euclidean error norm of a frame |
| `mean_l2`, `max_l2` | Mean/max of per-frame norms | Array-size-dependent trajectory summaries |

Metrics use float64/complex128 and reject nonfinite inputs. Unavailable values
are null in JSON and blank in CSV, never zero. Time-axis moves require explicit
metadata. The only unequal-length alignment allowed is a declared included/
excluded initial frame with exactly a one-frame gap. No implicit interpolation,
truncation, spatial transpose, or broadcasting forces arrays to compare.

Historical `compute_l2_errors.py` labeled root-mean-square **frame L2 norm** RMSE
for multi-frame arrays. It omitted division by the number of spatial/component
elements. Historical RMSE, relative-RMSE, and derived physics-score columns use
a different normalization and cannot be combined directly with corrected
metrics. The new report assigns no synthetic objective or physics ranking.

| Reference issue | Consequence |
| --- | --- |
| Burgers task uses Gaussian initial data; reference uses unseeded noise | Discrepancy is not controlled solver/model accuracy; matching a seed alone does not prove identical fields |
| Heat task specifies x-only diffusion; reference calls multidimensional implicit diffusion | Establish operator agreement before interpreting numerical agreement as the same requested problem |
| Julia source does not explicitly save the stored reference array | Hashes identify the array without proving production history |
| Reaction diffusion has u and v trajectories | Both retain individual statuses; one successful component cannot hide a failed one |
| Cavity/smoke/wake lack labeled implementations; structural source is empty | No invented ground-truth score is assigned |

`measured_caveated` values quantify discrepancy but are excluded from paired
numerical deltas. Eligible pairs require one fresh `code_only` and one fresh
`combined` record per replicate, matched model/task/code-context/temperature
metadata, and attempted execution in both. Historical reruns receive
`not_fresh_generation`. Differing retrieved code contexts prevent a claim that
the pair isolates only the added domain prior. Even eligible single pairs are
descriptive observations without variance estimates or statistical superiority.

## Offline audit and additional data tables

[`audit_experiment.py`](audit_experiment.py) reads a completed manifest, its
saved contexts/output artifacts, and an explicitly selected local domain graph
export. It makes no API/database calls and does not execute simulations. Run it
with a new output directory, for example:

```powershell
python .\knowledge_context\audit_experiment.py --manifest .\integration_runs\20261022T020018_419755Z\manifest.json --output-dir .\integration_runs\20261022T020018_419755Z\audit_followup
```

`--manifest` and `--output-dir` are required. Optional `--domain-graph` defaults
to `knowledge_context/domain_knowledge_graph.json`; `--chunk-elements` defaults
to 1,000,000 for chunked array diagnostics. The manifest must contain
`completed_utc`. Existing output directories and audit directories placed inside
simulation run directories are rejected.

The main experiment writes nine report artifacts under `reports/`: seven CSV
tables, JSON, and Markdown. The audit adds **14 CSV tables**, `audit.json`, and
`audit_report.md`, for 21 experiment CSV tables in total. Validation CSVs are
separate. The audit table dictionary is:

| Audit table | Main contents | Evidence origin |
| --- | --- | --- |
| `api_resolution.csv` | Each domain API hint's match/candidates, quality, namespace caveat | Completed run's mappings |
| `api_resolution_summary.csv` | Exact/candidate/ambiguous/unresolved counts per arm | Completed run's mappings |
| `domain_prior_summary.csv` | Selected recipe nodes, edges, fields, parameters, helpers, steps, outputs, API counts | Selected local snapshot |
| `domain_fields.csv` | Field variables, representations, initialization, provenance | Selected local snapshot |
| `domain_parameters.csv` | Scoped reference parameters, expressions/values, provenance | Selected local snapshot |
| `domain_helpers.csv` | Helper arguments/local/return formulas, provenance | Selected local snapshot |
| `domain_update_steps.csv` | Ordered step expressions, scope, provenance | Selected local snapshot |
| `domain_dependencies.csv` | Reads/writes/parameter/helper dependencies and state versions | Selected local snapshot |
| `domain_outputs.csv` | Output axes, frame/save conventions, artifact observations | Selected local snapshot |
| `domain_api_coverage.csv` | Statically verified APIs and unresolved candidates with evidence | Selected local snapshot |
| `domain_guidance.csv` | Curated guidance and its provenance | Selected local snapshot |
| `api_documentation_retention.csv` | Literal `Import Path` documentation retained in saved code contexts for the same resolved hints | Run mappings plus saved code contexts |
| `api_documentation_summary.csv` | Per-domain baseline/combined retention with unresolved hints excluded from the matchable denominator | Run mappings plus saved code contexts |
| `artifact_diagnostics.csv` | Actual filename/contract status, hashes, shape/dtype, finite/nonfinite counts, first nonfinite frame, finite ranges | Manifest-reported artifacts inside isolated run directories |

Recipe tables describe the selected local snapshot, not a new live graph read;
they cannot prove identical live-graph contents. Documentation retention examines
literal `Import Path` fields in `code_context.md`, excluding API-resolution
metadata elsewhere in the prompt. It measures evidence coverage, not generated
code quality. Unresolved hints are reported outside the resolved-hint denominator.

Artifact diagnostics inspect actual files even when their names fail the task
contract. They never rename/substitute files or assign a numerical task score.
When recorded hashes are available, the audit checks them. First nonfinite frame
uses the declared time axis and zero-based indexing. Finite ranges omit NaN/
infinite values and do not establish stability or physical validity.

The [measured results](INTEGRATION_RESULTS.md) link the completed run's audit,
coverage comparison, artifact diagnostics, and validation evidence.

## Tests and extensions

Run the focused offline suites and save auditable results in a **new** directory:

```powershell
python .\knowledge_context\run_offline_tests.py --output-dir .\integration_runs\validation_new
```

The output directory must not already exist. Omitting `--output-dir` creates a
new UTC-stamped validation directory under `integration_runs/`. The command
returns a nonzero exit code if the suite fails and creates:

| Validation artifact | Contents |
| --- | --- |
| `test_outcomes.json` | A JSON list with one record per test: name, status, failure/error/skip counts, duration, and details |
| `test_outcomes.csv` | The same per-test outcome records as a table |
| `unittest.log` | Full captured unittest output and test diagnostics |
| `summary.json` | Suite totals, success flag, elapsed time, scope, and UTC creation time |

Attach that exact recorded test evidence to a new retrieval/run report:

```powershell
python .\knowledge_context\run_combined_experiment.py --test-results .\integration_runs\validation_new\test_outcomes.json
```

The manifest records the test-results path and SHA256, and `test_outcomes.csv`
contains those supplied records. The runner does not infer a pass count or run
the tests implicitly. An empty test table means no outcome evidence was
supplied. Tests can also be run directly without saving those four artifacts:

```powershell
python -m unittest discover -s knowledge_context -p "test_*.py" -v
```

Suites cover credential isolation/redaction, read-only adapters, recipe order
and state versions, API ambiguity, current-task priority, context composition,
cached plans, execution isolation, artifact freshness, metric normalization,
and report provenance. Existing constructor tests use mocked writes; the test
command does not synchronize a live database. Measured graph reads and script
reruns belong in experiment reports, separate from offline test pass counts.

For another domain, begin with a populated labeled reference and the workflow in
[KNOWLEDGE_GRAPH.md](KNOWLEDGE_GRAPH.md). Add a reviewed profile/source note,
rebuild/export through the separate constructor as an intentional ingestion
task, and add numerical contracts only after verifying their semantics and
provenance. Missing domain recipes remain visible instead of being invented
from generated scripts. Changed scripts, tasks, graph state, or metrics should
receive a new experiment directory and explicit provenance.
