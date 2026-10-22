# Julia set: ground-truth context

Status: source-derived draft for human refinement, 2026-10-21.
Primary source: [julia_set_ground_truth.py](../../test_julia_set/julia_set_ground_truth.py).
Source line numbers below refer to this file as inspected on that date.

## Context to give an LLM

This reference constructs complex coordinates on a centered 2D grid, then evolves
one persistent complex state for 100 updates while rotating the parameter `c`.
After each update it adds the Boolean condition `abs(z) < 2` to a cumulative
count and stores that count. It does not restart the complex state for each frame,
freeze escaped points, or run an inner escape loop. Preserve these details when
reproducing this particular implementation.

## Source facts

- Imports: `phi.flow`, `cmath`, and `numpy as np` (lines 1-3).
- Spatial resolution: `Nx = Ny = 256`, represented by `spatial(x=Nx, y=Ny)`
  (lines 6,9).
- Bounds: `Box(x=(-2,2), y=(-2,2))` (line 8).
- Initial complex field: `CenteredGrid(lambda position:
  position.vector['x'] + 1j * position.vector['y'], extrapolation=0, ...)`
  (lines 11-16).
- `z` is initialized once from `z_field.values`; `escape_count` starts as
  `math.zeros(resolution)` and `trajectory` as an empty list (lines 17-19).
- `steps=100` (line 7); loop indices run from 0 to 99 (line 21).

## Update recipe and dependencies

For each `step` (lines 21-25):

1. Compute `c = 0.7885 * cmath.exp(1j * 2 * cmath.pi * step / steps)`.
2. Update the previous iteration's complex state: `z = z ** 2 + c`.
3. Increment the existing count with the post-update condition:
   `escape_count = escape_count + (abs(z) < 2)`.
4. Append `escape_count.numpy(('x', 'y'))` to the trajectory.

Stack the list with `np.stack(trajectory, axis=0)` into `v_trj` (line 27).
Interpretation: despite its name, `escape_count` stores a cumulative count of
updates for which the current magnitude is strictly below 2. Replacing that
behavior with first-escape time would change the reference. No diffusion,
advection, pressure solve, or spatial derivative appears in the update.

## Outputs and artifact observations

- Computed output: `v_trj`, with time first and spatial order x,y (lines 25-27).
- The source appends after each update and never appends an initial count frame.
  Its stack therefore contains 100 snapshots.
- The source contains no `np.save()` call. A save filename cannot be extracted
  from this script.
- Existing artifact `test_julia_set/julia_set_ground_truth_trj.npy` has shape
  `(100, 256, 256)` and dtype `<f4`. Header inspection only, 2026-10-21. Its
  existence does not establish how it was saved or whether this exact script
  produced it.

## Retrieval hints

- Semantic searches: centered grid initialized with complex spatial coordinates;
  persistent quadratic complex iteration with rotating parameter; cumulative
  magnitude-threshold count; named spatial axes to NumPy trajectory.
- API candidates observed in source: `CenteredGrid`, `Box`, `spatial`,
  `math.zeros`, tensor `.numpy()`, `cmath.exp`, `np.stack`.
- Some operations are tensor arithmetic or standard-library/NumPy operations,
  which may be outside the ingested PhiFlow code graph. Record this coverage gap
  instead of substituting an unrelated physics solver.

## Proposed graph facts

| Subject | Relationship | Object | Evidence in primary source |
| --- | --- | --- | --- |
| `reference:julia_set:ground_truth` | `HAS_FIELD` | Complex coordinate state initialized once | Lines 11-17 |
| `julia_set:step:quadratic_update` | `READS/WRITES` | Persistent complex state z | Lines 21-23 |
| `julia_set:step:quadratic_update` | `NEXT_STEP` | `julia_set:step:threshold_count` | Lines 23-24 |
| `julia_set:step:threshold_count` | `READS/WRITES` | Cumulative count using strict abs(z) < 2 | Line 24 |
| `reference:julia_set:ground_truth` | `PRODUCES` | Computed stack of 100 post-update count fields | Lines 25-27 |

`READS/WRITES` abbreviates two separate edge types. The constructor ingests this
recipe through `domain_graph_spec.json`; the table is an explanatory summary.
External APIs remain candidates until a local definition can be resolved.

## Differences and unresolved details

- `test/julia_set.md` mentions `N_escape=50`; the reference has no 50-iteration
  inner loop or corresponding variable. Do not add one during reproduction.
- The task requests `julia_set_domain_trj.npy`; the reference only computes
  `v_trj`. Saving it is an additional output action when requested.
- No dependency versions or numeric precision settings are specified. Arithmetic
  behavior after large complex magnitudes has not been assessed in these notes.

## Human refinement

- Intended meaning of the cumulative count and persistent state: <add knowledge>.
- When a different Julia-set computation is desired: <add conditions/rationale>.
- Reviewed claims, corrections, and artifact provenance: <add notes>.
