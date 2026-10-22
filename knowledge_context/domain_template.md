# <Domain>: ground-truth context

Status: draft; replace all placeholders before using as context.
Primary source: `<test_folder>/<domain>_ground_truth.py`.
Inspected: `<date>`.

## Context to give an LLM

<A short explanation of the approach visible in this reference. State its scope
and the details that matter when reproducing it.>

## Source facts

- Imports and backend: <names and source lines>.
- Fields, grids, and bounds: <construction and source lines>.
- Initialization and boundaries: <expressions and source lines>.
- Coefficients, time step, and iteration count: <values and source lines>.

## Update recipe and dependencies

1. <First operation, inputs, outputs, and source lines>.
2. <Next operation; identify whether it reads old or updated state>.

<Separate the main trajectory-producing code from auxiliary demonstrations.>

## Outputs and artifact observations

- Computed variables: <name and axis order>.
- Explicit save calls: <filename, or state that none exists>.
- Initial-frame convention: <explicit source evidence or unresolved dependency>.
- Existing artifact headers, if inspected: <path, shape, dtype, inspection date>.
- Reproduction limitations: <random seed, versions, solver defaults, etc.>.

## Retrieval hints

- Semantic searches: <plain-English intents derived from the source>.
- API candidates: <symbols used by the reference; verify their target versions>.

## Proposed graph facts

| Subject | Relationship | Object | Evidence |
| --- | --- | --- | --- |
| <reference or step> | <typed relation> | <scoped concept or API> | <source path and lines> |

This table explains the intended facts. Add an AST-validated profile to
`domain_graph_spec.json` to ingest the reference; the constructor does not parse
this table automatically. See `KNOWLEDGE_GRAPH.md` for the implemented schema.

## Differences and unresolved details

<List conflicts with task sheets, missing information, and uncertain semantics.
Do not resolve them by copying generated implementations.>

## Human refinement

- Expert explanation of this reference: <add your knowledge here>.
- Conditions under which this approach should change: <add scope and rationale>.
- Claims reviewed or corrected: <date, claim, and supporting evidence>.
