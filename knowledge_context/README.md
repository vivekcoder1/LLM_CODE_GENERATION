# Domain knowledge for LLM context

Status: initial draft for human refinement, 2026-10-21.

These notes extract implementation knowledge from the simulations explicitly
labeled `ground_truth` in this project. Their purpose is to help an LLM find the
reference approach and, later, connect domain concepts to code in a knowledge
graph. Parameters describe these particular reference simulations; they are not
universal defaults for a domain.

## Start here

The [graph constructor](domain_knowledge_graph_creater.py) now builds these
reference recipes into Neo4j by default and saves a JSON inspection export. See the
[detailed graph documentation](KNOWLEDGE_GRAPH.md) for the schema, commands,
provenance rules, tests, and extension workflow. The editable structured input is
[domain_graph_spec.json](domain_graph_spec.json); the generated snapshot is
[domain_knowledge_graph.json](domain_knowledge_graph.json).

Neo4j credentials come only from `knowledge_context/.env`, or the one file
explicitly selected with `--env-file`. Root `.env` and inherited `NEO4J_*`
variables are ignored. Use `--check-config` to verify the selected target without
connecting. See [.env.example](.env.example) for the required keys.

1. Read [LLM context](llm_context.md) for the source policy and graph guidance.
2. Open the relevant domain note below and refine its final section.
3. Supply `llm_context.md`, that domain note, and the current request as context.
   Supply the referenced simulation source as well when exact reproduction is
   required. Include retrieved API documentation when generating executable code.

The simulation-generation pipeline does not load this directory automatically.
These files are ready to attach or concatenate into a prompt. Future integration
points are `generate_search_blueprint()` and `generate_grounded_code()` in
[`llm-querying.py`](../llm-querying.py). The new constructor ingests selected note
sections as draft guidance; `TreeGen.py` continues to parse the older code graph.

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

The saved array shapes were checked by reading existing `.npy` headers. The
simulations were not rerun, numerical correctness was not assessed, and the
existing arrays' production history was not verified. Notes distinguish source
behavior from observations about those saved artifacts.
