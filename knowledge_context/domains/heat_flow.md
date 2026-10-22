# Heat flow: ground-truth context

Status: source-derived draft for human refinement, 2026-10-21.
Primary source: [heat_flow_ground_truth.py](../../test_heat_flow/heat_flow_ground_truth.py).
Source line numbers below refer to this file as inspected on that date.

## Context to give an LLM

To reproduce this heat-flow reference, use the JAX PhiFlow import, a zero-initialized
centered temperature field, mixed boundaries, and a spatial conductivity grid
formed from two rectangular inclusions. Advance temperature with
`diffuse.implicit(temperature, conductivity, dt)`. Preserve the conductivity as a
field and the different boundary settings on the two x faces and the y axis.

## Source facts

- Imports: `from phi.jax.flow import *` and `trange` from `tqdm.notebook`
  (lines 2-3).
- Domain: `Box(x=10, y=5)` (line 8).
- Temperature boundaries:
  `{'x-': 1, 'x+': ZERO_GRADIENT, 'y': PERIODIC}` (line 9).
- Inclusion geometry: the union of `Box(x=(0,10), y=(2,3))` and
  `Box(x=(4.5,5.5), y=(1,4))` (line 10).
- Conductivity construction:
  `CenteredGrid(bars, ZERO_GRADIENT, domain, x=100, y=50) + .01`
  (line 11). Preserve the exact mask construction; geometry sampling behavior
  belongs to the library.
- Initial temperature: `CenteredGrid(0, boundary, domain, x=100, y=50)`
  (line 15). Conductivity and temperature use separate boundary arguments.
- Iteration: `iterate(step, batch(time=100), t0, dt=1, range=trange)`
  (line 16).

## Update recipe and dependencies

1. Read the current temperature field and the preconstructed `conductivity` field.
2. Return `diffuse.implicit(t, conductivity, dt)` (lines 4-5).
3. Repeat through `iterate()` with `dt=1` (line 16).

Interpretation: the reference delegates its diffusion update to the library.
There is no explicit directional derivative or additional advection step in the
simulation source. The exact operator and solver defaults require the matching
library implementation; the function call alone does not specify all semantics.

## Outputs and artifact observations

- Computed temperature trajectory: `v_trj` (line 16). Its variable name does not
  make it a velocity field; its source is the initialized scalar temperature.
- Explicit save: `heat_flow_ground_truth.npy`, with axis order
  `('time', 'x', 'y')` (line 17).
- Existing headers: both `test_heat_flow/heat_flow_ground_truth.npy` and
  `test_heat_flow/heat_flow_ground_truth_trj.npy` have shape `(101, 100, 50)`
  and dtype `<f4`. Header inspection only, 2026-10-21.
- The 101 stored frames are consistent with an initial state plus 100 updates;
  verify the target library's `iterate()` behavior before generalizing this.

## Retrieval hints

- Semantic searches: implicit diffusion with a spatial coefficient field;
  centered scalar grid with fixed left value, zero-gradient right boundary, and
  periodic y boundaries; union of rectangular inclusions as a grid mask.
- API candidates observed in source: `CenteredGrid`, `Box`, `union`,
  `diffuse.implicit`, `iterate`, `batch`, `ZERO_GRADIENT`, `PERIODIC`.
- Boundary constants are retrieval concepts even if the current code graph does
  not represent them as searchable classes. Use semantic searches and verify
  their exports rather than assuming a class node exists.

## Proposed graph facts

| Subject | Relationship | Object | Evidence in primary source |
| --- | --- | --- | --- |
| `reference:heat_flow:ground_truth` | `HAS_FIELD` | Zero-initialized centered temperature with mixed boundaries | Lines 9,15 |
| `reference:heat_flow:ground_truth` | `HAS_FIELD` | Conductivity grid built from rectangular union plus .01 | Lines 10-11 |
| `heat_flow:step:diffusion` | `READS` | Temperature and conductivity fields | Lines 4-5 |
| `heat_flow:step:diffusion` | `USES_API` | `diffuse.implicit` | Line 5 |
| `reference:heat_flow:ground_truth` | `PRODUCES` | Saved scalar trajectory with axes time,x,y | Lines 16-17 |

This table is an explanatory summary. The constructor ingests an AST-validated
profile from `domain_graph_spec.json`, resolving local API definitions where
possible and retaining unresolved calls as candidates.

## Differences and unresolved details

- `test/heat_flow.md` writes a PDE with only an x second derivative. The reference
  calls `diffuse.implicit` without an explicit directional restriction. Preserve
  that call when reproducing the reference and record the PDE/API interpretation
  as a discrepancy to resolve against the matching library.
- The task sheet requests `heat_flow_temperature_trj.npy`; the source saves
  `heat_flow_ground_truth.npy`.
- No explicit solver configuration or dependency version is recorded. The source
  uses JAX; backend substitution and solver-default changes need review when
  exact reproduction matters.

## Human refinement

- Intended interpretation of the diffusion operator: <add explanation/evidence>.
- Rationale for the conductivity geometry and mixed boundaries: <add knowledge>.
- Reviewed claims, corrections, and reproduction settings: <add notes>.
