# Reaction diffusion: ground-truth context

Status: source-derived draft for human refinement, 2026-10-21.
Primary source: [reaction_diffusion_ground_truth.py](../../test_reaction_diffusion/reaction_diffusion_ground_truth.py).
Source line numbers below refer to this file as inspected on that date.

## Context to give an LLM

This reference evolves two periodic centered scalar fields with Laplacian
diffusion, a shared nonlinear reaction, feed, and removal terms. Both fields start
from the same radial cosine. Each update caches `u*v**2` before changing either
field, then applies the two explicit increments. Preserve that dependency, the
separate diffusion coefficients, and the initial snapshot in both trajectories.

## Source facts

- Import: `from phi.flow import *` (line 1).
- Bounds: `Box(x=100, y=100)`; resolution: `spatial(x=100, y=100)`
  (lines 3-6,14-15).
- Time step `dt=0.5`; coefficients `Du=0.19`, `Dv=0.05`, `feed_rate=0.06`,
  `kill_rate=0.062`; radial scale `s=3` (lines 7-12).
- Initialization function computes `cos(radius/s)`, where radius is the distance
  from `vec(x=Lx/2, y=Ly/2)` (lines 18-21).
- `u` and `v` both use that initializer, the same bounds/resolution, and `PERIODIC`
  boundaries (lines 24-25).
- The initial field values are placed in `u_trj` and `v_trj` before the 100-update
  loop begins (lines 27-30).

## Update recipe and dependencies

The source executes the following sequence (lines 30-35):

```python
reaction = u * v ** 2
u = u + dt * (Du * field.laplace(u) - reaction + feed_rate * (1 - u))
v = v + dt * (Dv * field.laplace(v) + reaction - (feed_rate + kill_rate) * v)
```

Interpretation: both increments use the old shared reaction. The second update
does not recompute `reaction` from the newly assigned `u`. Its other terms still
use the old `v`, so these assignments implement an explicit update of both old
states. Recomputing the nonlinear term between the assignments would change the
reference recipe. Append both new states after the two assignments.

The code after the saves (lines 44-50) constructs three alternative initial
fields, stacks them along an `initialization` batch dimension, and plots them.
Those fields are auxiliary examples; they do not initialize the trajectories
saved at lines 40-41.

## Outputs and artifact observations

- Each list begins with the initial field and receives 100 new states. The
  resulting arrays have 101 snapshots (lines 27-38).
- Both arrays use named spatial order `('x', 'y')` and are stacked with time on
  axis 0 (lines 27-38).
- Explicit saves: `reaction_diffusion_ground_truth_u_trj.npy` and
  `reaction_diffusion_ground_truth_v_trj.npy` (lines 40-41).
- Existing headers for those two files under `test_reaction_diffusion/` each
  report shape `(101, 100, 100)` and dtype `<f4`. Header inspection only,
  2026-10-21; numerical agreement was not checked.

## Retrieval hints

- Semantic searches: periodic scalar grid with radial cosine initialization;
  explicit coupled reaction diffusion with cached nonlinear reaction; Laplacian
  of a scalar field; initial-frame-preserving trajectory export.
- API candidates observed in the main simulation: `CenteredGrid`, `Box`,
  `spatial`, `vec`, `math.vec_length`, `math.cos`, `field.laplace`, `np.stack`.
- Retrieve the operator as `field.laplace`, with its namespace. The main
  trajectory does not call `diffuse.implicit`, and its nonlinear terms are
  arithmetic expressions rather than a named reaction solver.

## Proposed graph facts

| Subject | Relationship | Object | Evidence in primary source |
| --- | --- | --- | --- |
| `reference:reaction_diffusion:ground_truth` | `HAS_FIELD` | Two periodic centered scalar fields with radial cosine initial state | Lines 18-25 |
| `reaction_diffusion:step:cache_reaction` | `READS` | Old u and old v | Line 31 |
| `reaction_diffusion:step:cache_reaction` | `NEXT_STEP` | `reaction_diffusion:step:update_u` | Lines 31-32 |
| `reaction_diffusion:step:update_u` | `NEXT_STEP` | `reaction_diffusion:step:update_v` | Lines 32-33 |
| `reaction_diffusion:step:update_u` and `update_v` | `USES_API` | `field.laplace` | Lines 32-33 |
| `reference:reaction_diffusion:ground_truth` | `PRODUCES` | Two saved scalar trajectories including initial state | Lines 27-41 |

The constructor expands the combined API row into separate assertions through
the AST-validated profile in `domain_graph_spec.json`. It retains the cached-term
dependency; this table remains an explanatory summary.

## Differences and unresolved details

- `test/reaction_diffusion.md` omits a boundary specification. The ground-truth
  source supplies `PERIODIC`; retain that source-derived detail.
- The task uses output names without `ground_truth`; distinguish those names
  from the source's explicit save calls.
- The source contains no clipping, normalization, or pressure projection in the
  main update. Adding those operations would change the reference.
- Dependency versions and explicit Laplacian options are unspecified; matching
  operator defaults may matter when reproducing numerical values.

## Human refinement

- Rationale for the initial state and coefficient choices: <add knowledge>.
- When this explicit update should change: <add conditions and rationale>.
- Reviewed claims, corrections, and numerical validation evidence: <add notes>.
