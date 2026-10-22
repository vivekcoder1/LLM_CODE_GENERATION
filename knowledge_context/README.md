# Domain knowledge for LLM context

Status: domain notes for human refinement; combined retrieval integrated,
2026-10-21.

These notes extract implementation knowledge from the simulations explicitly
labeled `ground_truth` in this project. Their purpose is to help an LLM find the
reference approach and connect domain concepts to code in a knowledge
graph. Parameters describe these particular reference simulations; they are not
universal defaults for a domain.

## Start here

The [combined pipeline guide](COMBINED_PIPELINE.md) documents the integration of
these recipes with the existing `TreeGen.py`/`public_api_checker.py` code graph,
explicit credentials, retrieval, execution, and detailed outcome tables. It
queries both graphs without modifying Neo4j.

The [measured integration results](INTEGRATION_RESULTS.md) summarize the completed
read-only experiment, its eight retrieval outcomes, isolated existing-script
reruns, final validation, graph snapshots, and detailed report/audit tables.
They distinguish retrieval success from fresh-generation performance.

From the research directory, compare code-only and combined retrieval using
cached search plans and no LLM calls:

```powershell
python .\knowledge_context\run_combined_experiment.py
```

To also rerun each existing simulation once in an isolated output directory:

```powershell
python .\knowledge_context\run_combined_experiment.py --also-rerun-existing --execute
```

Historical reruns are labeled separately from retrieval variants. They do not
measure fresh context-conditioned generation. Every invocation creates a new
`integration_runs/` directory with manifest and Markdown/JSON/CSV reports.

To save per-test evidence and attach it to a later report, run
`python .\knowledge_context\run_offline_tests.py --output-dir .\integration_runs\validation_new`,
then pass that directory's `test_outcomes.json` with `--test-results` to the
experiment runner. The validation directory must be new. See
[tests and report attachment](COMBINED_PIPELINE.md#tests-and-extensions) for the
recorded JSON/CSV/log/summary files.

The [graph constructor](domain_knowledge_graph_creater.py) now builds these
reference recipes into Neo4j by default and saves a JSON inspection export. See the
[detailed graph documentation](KNOWLEDGE_GRAPH.md) for the schema, commands,
provenance rules, tests, and extension workflow. The editable structured input is
[domain_graph_spec.json](domain_graph_spec.json); the generated snapshot is
[domain_knowledge_graph.json](domain_knowledge_graph.json).

The domain constructor's credentials come only from `knowledge_context/.env`, or the one file
explicitly selected with `--env-file`. Root `.env` and inherited `NEO4J_*`
variables are ignored. Use `--check-config` to verify the selected target without
connecting. See [.env.example](.env.example) for the required keys.

The combined pipeline explicitly selects root `.env` for the code graph and
`knowledge_context/.env` for the domain graph. Each is independently parsed
without inherited-variable or other-file fallback. LLM settings are used only
in explicit generation mode. See the [configuration table](COMBINED_PIPELINE.md#which-files-configure-which-service)
before selecting connection files.

1. Read [LLM context](llm_context.md) for the source policy and graph guidance.
2. Open the relevant domain note below and refine its final section.
3. Supply `llm_context.md`, that domain note, and the current request as context.
   Supply the referenced simulation source as well when exact reproduction is
   required. Include retrieved API documentation when generating executable code.

The pipeline loads selected domain evidence through
[`domain_retrieval.py`](domain_retrieval.py), joining API hints to the existing
code graph through [`combined_retrieval.py`](combined_retrieval.py).
[`llm-querying.py`](../llm-querying.py) exposes the combined retriever and forwards
its CLI to the isolated runner. The constructor ingests selected note sections
as draft guidance; `TreeGen.py` continues to produce the older graph. The
integration does not invoke either graph writer.

## Ground-truth source inventory

| Domain | Labeled simulation source | Notes |
| --- | --- | --- |
| Burgers 2D | [Source](../test_burgers2d/burgers2d_ground_truth.py) | [Draft](domains/burgers2d.md) |
| Heat flow | [Source](../test_heat_flow/heat_flow_ground_truth.py) | [Draft](domains/heat_flow.md) |
| Julia set | [Source](../test_julia_set/julia_set_ground_truth.py) | [Draft](domains/julia_set.md) |
| Reaction diffusion | [Source](../test_reaction_diffusion/reaction_diffusion_ground_truth.py) | [Draft](domains/reaction_diffusion.md) |
| Structural mechanics | [Source](../test_structural_mechanics/structural_mechanics_ground_truth.py) | Empty file; knowledge extraction pending |
| Lid-driven cavity | No labeled simulation source found in `test_lid_driven_cavity/` | Pending |
| Smoke plume | No labeled simulation source found in `test_smoke_plume/` | Pending |
| Wake flow | No labeled simulation source found in `test_wake_flow/` | Pending |

Inventory reflects the files inspected on 2026-10-21. Generated simulations,
retrieved contexts, task sheets, and API audit expectations are not substitutes
for missing ground-truth implementations.

## How to refine the notes

Use [the domain template](domain_template.md) for another reference simulation.
Keep source-derived facts separate from your own advice. Put new expert guidance
in the human refinement section and identify whether it explains the reference,
generalizes it, or intentionally changes it. Record its rationale and scope.

Each domain note includes source line ranges, operation order, retrieval hints,
proposed graph facts, and unresolved details. The constructor implements a
structured version of these recipes using AST-validated profiles. Markdown
tables remain explanatory; they are not automatically converted into facts.

Initial note extraction checked existing `.npy` headers; it did not rerun
simulations or verify artifact production history. Later isolated reruns and
comparisons have separate experiment manifests and provenance. Notes distinguish
source behavior from artifact observations; the [combined guide](COMBINED_PIPELINE.md#numerical-definitions-and-interpretation)
explains corrected metrics and task/reference disagreements.
