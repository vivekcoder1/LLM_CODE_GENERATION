# Instructions for using ground-truth domain knowledge

Status: proposed LLM guidance for this project, 2026-10-21.
Implementation: [constructor and graph documentation](KNOWLEDGE_GRAPH.md).

## Objective and evidence

Use the labeled ground-truth simulations to identify the approach a model should
retrieve, explain, or reproduce. Capture the relationships between the problem,
its field representation, initialization, boundaries, update operations, and
outputs. These notes are curated context for the domain knowledge graph.

Use these evidence categories:

- **Source fact:** directly visible in a labeled ground-truth simulation. Cite
  the repository-relative source path and line range.
- **Artifact observation:** read from an existing reference output, such as its
  array shape. This alone does not prove which code produced it.
- **Interpretation:** an explanation derived from the source. Identify the
  derivation and avoid attributing unstated intent to its author.
- **Proposed hint:** an expert or LLM suggestion for retrieval or graph design.
  It becomes a fact about the implementation only after source verification.
- **Unresolved:** missing information, a contradiction, or unverified behavior.

For reference reproduction, prefer the ground-truth implementation over task
sheets and generated scripts. Record disagreements explicitly. For a new request
that intentionally changes the reference, apply the stated change and identify
the resulting departure; do not silently replace the requested problem.

## What to preserve

1. Read the actual field construction: scalar or vector, named dimensions,
   resolution, physical bounds, boundary settings, and initialization.
2. Trace a complete update. Preserve operation order and which version of each
   field appears on the right-hand side. Cache shared terms where the reference
   does so. A list of function names alone cannot capture this behavior.
3. Retain coefficient fields, constants, backend imports, and time-step defaults.
   Treat the numerical values as reference-specific. Record absent random seeds,
   solver settings, and dependency versions as absent.
4. Separate the main simulation from demonstration or plotting code. State which
   code contributes to the trajectory.
5. Capture output variable names, explicit axis order, initial-frame inclusion,
   and save calls. Distinguish a computed array from one explicitly written to
   disk. Check library behavior before generalizing an `iterate()` convention.
6. Treat API spellings in these notes as usage observed in the reference. Verify
   import paths and signatures against the target local library before emitting
   runnable code. Graph-generated import metadata also needs verification.

Missing ground truth means missing reference knowledge. Do not fill that gap
using generated code or general textbook expectations and label it as reference
behavior. An empty structural-mechanics file currently supplies no simulation
facts.

## Graph representation

The existing graph in `TreeGen.py` describes Python structure, including `File`,
`Class`, `Function`, `Method`, `Parameter`, `Type`, `Attribute`, and
`GeneratedDescription`. The separate `domain_knowledge_graph_creater.py`
constructor now implements the domain concepts and relations below, plus
provenance and dependency details documented in `KNOWLEDGE_GRAPH.md`. The existing
simulation retriever does not yet traverse the new graph.

Represent a reference run separately from a broad domain. For example,
`reference:burgers2d:ground_truth` can belong to `domain:burgers2d` without making
its random initialization a rule for every Burgers problem.

| Proposed relationship | Meaning |
| --- | --- |
| `ReferenceSimulation --IN_DOMAIN--> Domain` | Identifies the domain of a specific reference |
| `ReferenceSimulation --HAS_FIELD--> FieldSpec` | Connects to an initialized field and its grid/boundaries |
| `ReferenceSimulation --HAS_STEP--> UpdateStep` | Links to an ordered update operation |
| `UpdateStep --NEXT_STEP--> UpdateStep` | Preserves execution order |
| `UpdateStep --USES_API--> CodeComponent` | Connects an operation to a verified code symbol |
| `UpdateStep --READS/WRITES--> FieldSpec` | Records state dependencies |
| `ReferenceSimulation --PRODUCES--> OutputSpec` | Records computed or explicitly saved outputs |

For each assertion, retain `source_path`, `source_lines`, `evidence_kind`, and
`review_status`. Scope constants and field identifiers to the reference. Use
repository-relative paths and qualified symbol names for code identity; a bare
function name such as `implicit` is ambiguous. Resolve API targets to existing
code nodes before creating links. Store unresolved links as candidates.

Keep conditional advice in separate guidance records. Record its condition,
suggested action, rationale, and source or author. Preserve conflicting evidence
as separate assertions with provenance rather than merging it into one value.

## Retrieval and response behavior

Use the matching domain note to form plain-English searches for initialization,
boundaries, numerical operators, and output conversion. Exact API names are
additional candidates, not evidence that a retrieved match is correct.

If using the current search planner, return only its existing JSON fields:
`semantic_queries`, `target_classes`, and `target_functions`. Domain graph
relations require an additional retrieval implementation; putting new names in a
prompt does not make them traversable by the existing pipeline.

Before generating code, check that retrieved documentation covers every required
operation and its parameters. Preserve the full reference recipe, including
update order and output conventions. Report missing evidence during planning
instead of inventing it. Apply the requested final output format only after the
plan is sufficiently grounded.
