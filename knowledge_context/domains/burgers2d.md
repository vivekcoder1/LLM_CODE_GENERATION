# Burgers 2D: ground-truth context

Status: source-derived draft for human refinement, 2026-10-21.
Primary source: [burgers2d_ground_truth.py](../../test_burgers2d/burgers2d_ground_truth.py).
Source line numbers below refer to this file as inspected on that date.

## Context to give an LLM

To reproduce this Burgers reference, construct a periodic, cell-centered 2D vector
field initialized with noise. Each update applies implicit diffusion first and
then semi-Lagrangian self-advection using the diffused field as both the advected
quantity and the transport velocity. Preserve this order and the two vector
components. The initialization and method choices describe this reference run.

## Source facts

- Imports: `from phi.flow import *` and `import numpy` (lines 1-3).
- Field: `CenteredGrid(Noise(vector='x,y'), PERIODIC, x=64, y=64,
  bounds=Box(x=40, y=20))` (line 10).
- The vector channel has named components `x,y`; the grid has 64 cells along each
  spatial axis and physical extents 40 by 20 (line 10).
- The step has default `dt=.5`, and diffusion uses coefficient `0.1`
  (lines 5-6).
- The trajectory is built with `iterate(step, batch(time=100), v0)` (line 11).

## Update recipe and dependencies

1. Read the current vector field and apply
   `v = diffuse.implicit(v, 0.1, dt=dt)` (line 6).
2. Apply `v = advect.semi_lagrangian(v, v, dt=dt)` (line 7). Both arguments
   now refer to the diffused field.
3. Return that field for the next iteration (line 8).

Interpretation: this is a sequential diffusion/advection recipe. Swapping its
operations or supplying the pre-diffusion transport velocity would change the
reference update. No pressure projection appears in this implementation.

## Outputs and artifact observations

- Computed field trajectory: `v_trj` (line 11).
- Explicit save: `burgers2d_ground_truth.npy`, with named axis order
  `('time', 'x', 'y', 'vector')` (line 13).
- Existing headers: both `test_burgers2d/burgers2d_ground_truth.npy` and
  `test_burgers2d/burgers2d_ground_truth_trj.npy` have shape
  `(101, 64, 64, 2)` and dtype `<f4`. Header inspection only, 2026-10-21.
- The 101 stored frames are consistent with including an initial state plus 100
  updates. The source delegates trajectory assembly to `iterate()`; verify that
  library convention when reproducing in another environment.
- No random seed or dependency version is specified. The recipe does not by
  itself identify the exact random initial field in the saved artifacts.

## Retrieval hints

- Semantic searches: periodic centered vector grid with noise initialization;
  implicit vector diffusion followed by self-advection; named vector-channel
  trajectory export.
- API candidates observed in source: `CenteredGrid`, `Noise`, `Box`,
  `diffuse.implicit`, `advect.semi_lagrangian`, `iterate`, `batch`.
- Retrieve both numerical operations and the grid/initialization APIs. Retrieving
  only an advection function leaves part of the reference recipe unspecified.

## Proposed graph facts

| Subject | Relationship | Object | Evidence in primary source |
| --- | --- | --- | --- |
| `reference:burgers2d:ground_truth` | `HAS_FIELD` | Periodic centered vector field initialized with noise | Line 10 |
| `burgers2d:step:diffusion` | `USES_API` | `diffuse.implicit` | Line 6 |
| `burgers2d:step:diffusion` | `NEXT_STEP` | `burgers2d:step:self_advection` | Lines 6-7 |
| `burgers2d:step:self_advection` | `USES_API` | `advect.semi_lagrangian` | Line 7 |
| `reference:burgers2d:ground_truth` | `PRODUCES` | Saved vector trajectory with axes time,x,y,vector | Lines 11-13 |

This table is an explanatory summary. The constructor ingests an AST-validated
profile from `domain_graph_spec.json`, resolving local API definitions where
possible and retaining unresolved calls as candidates.

## Differences and unresolved details

- `test/burgers2d.md` specifies a Gaussian initial expression. The labeled
  reference instead uses `Noise(vector='x,y')`; use the latter for reproducing
  this reference and retain the disagreement as separate evidence.
- The task sheet requests `burgers2d_velocity_trj.npy`; the source explicitly
  saves `burgers2d_ground_truth.npy`. Output names depend on whether the current
  request is reference reproduction or fulfillment of the task sheet.
- The saved artifacts were not regenerated or compared numerically during this
  extraction. Random seed, noise defaults, and solver defaults remain to be
  recorded for exact reproduction.

## Human refinement

- Why this reference uses diffusion before self-advection: <add explanation>.
- Conditions for selecting a different method or initialization: <add guidance>.
- Reviewed claims, corrections, and supporting evidence: <add notes>.
