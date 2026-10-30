# Review of the newly generated scripts and saved outputs

The eight scripts in this experiment were newly generated and executed on
October 28, 2026. Their input contexts were restored from the validated October
21 retrieval snapshot; they were not retrieved again during generation. This
review used the completed manifest, saved scripts, stderr files, and the existing
numerical report. No script was edited or rerun, and no API or database was
accessed to prepare this review.

## Execution versus saved-output quality

All eight processes exited successfully. All ten arrays use their requested
filenames and shapes, and all ten hashes match the completed manifest. Successful
execution does not imply finite output: the code-only Burgers and heat scripts
saved arrays containing NaN/infinite values.

| Domain | Code-only saved output | Combined saved output | Reference-array comparison |
| --- | --- | --- | --- |
| Burgers 2D | 501,554 nonfinite values of 827,392; first at frame 13 | All 827,392 values finite | Baseline RMSE unavailable; combined RMSE 0.379806692, with incompatible initial-data caveat |
| Heat flow | 210,074 nonfinite values of 505,000; first at frame 16 | All 505,000 values finite | Baseline RMSE unavailable; combined RMSE 0.00000208263, with task/operator caveat |
| Julia set | All 6,553,600 saved counts finite | All 6,553,600 saved counts finite | RMSE 7.519814524 versus 0 |
| Reaction diffusion | Both arrays finite, 1,010,000 values each | Both arrays finite, 1,010,000 values each | Baseline u/v RMSE 3.72229e-8 / 4.71372e-8; combined 0 / 0 |

Frames in this table are zero-based on the declared time axis. Reference errors
are values from the existing numerical report, not a new task-correctness score.

## Burgers 2D

The [code-only step](D:/Vivek/research/integration_runs/20261028T181330_344848Z_saved_context/runs/burgers2d/code_only_0/generated_burgers2d_simulation.py:19)
adds differential advection and differential diffusion using one forward-Euler
increment at `dt=0.5`. Its stderr records overflow and invalid arithmetic. The
[combined step](D:/Vivek/research/integration_runs/20261028T181330_344848Z_saved_context/runs/burgers2d/combined_0/generated_burgers2d_simulation.py:30)
applies implicit diffusion first, then semi-Lagrangian self-advection. This
method change is consistent with the observed difference in saved-output
finiteness; this single comparison does not isolate which individual operation
caused that difference.

Both scripts initialize the two velocity components from the task's Gaussian.
The labeled reference source instead uses unseeded noise. The combined run's
RMSE therefore measures discrepancy from a different initial field and cannot
establish the correctness or accuracy of its Burgers solver.

## Heat flow

The [code-only update](D:/Vivek/research/integration_runs/20261028T181330_344848Z_saved_context/runs/heat_flow/code_only_0/generated_heat_flow_simulation.py:29)
uses explicit diffusion with `dt=1` and `substeps=1`. Its stderr directly reports
`CFL = 101.0 > 0.5` and recommends increasing substeps or using implicit
diffusion. The array then contains nonfinite entries from frame 16. The
[combined update](D:/Vivek/research/integration_runs/20261028T181330_344848Z_saved_context/runs/heat_flow/combined_0/generated_heat_flow_simulation.py:15)
uses implicit diffusion and saves finite temperatures; its stderr is empty.

Both generated scripts call the library's diffusion operators over spatial
dimensions. The task equation specifies x-only diffusion, while the reference
also calls multidimensional implicit diffusion with spatial conductivity. The
combined run's close agreement with that reference is not proof of compliance
with the task's x-only equation.

## Julia set

The [code-only script](D:/Vivek/research/integration_runs/20261028T181330_344848Z_saved_context/runs/julia_set/code_only_0/generated_julia_set_simulation.py:14)
restarts `z` and the count array for every output time and performs 50 inner
iterations at each parameter value. It also uses endpoint-inclusive NumPy
coordinates. The [combined script](D:/Vivek/research/integration_runs/20261028T181330_344848Z_saved_context/runs/julia_set/combined_0/generated_julia_set_simulation.py:25)
keeps the complex state and cumulative count across the 100 updates, makes one
quadratic update per saved frame, and uses the centered-grid coordinates of the
reference recipe. Its saved array hash matches the reference array hash.

The reset/inner-iteration difference explains a concrete recipe mismatch in the
baseline, rather than merely a lower similarity score. The task separately lists
`N_escape=50`; the combined script follows the provided update equations and
reference's persistent-state interpretation rather than inventing 50 inner
iterations.

Both scripts emit overflow/invalid-square warnings for their internal complex
state. Their saved indicator-count arrays remain finite. Describe these as
finite saved outputs, not as warning-free computations or proof that every
internal state remains finite.

## Reaction diffusion

The [code-only script](D:/Vivek/research/integration_runs/20261028T181330_344848Z_saved_context/runs/reaction_diffusion/code_only_0/generated_reaction_diffusion_simulation.py:39)
first obtains explicit diffusion increments, computes reaction terms from the
old species values, then constructs the new fields. The
[combined script](D:/Vivek/research/integration_runs/20261028T181330_344848Z_saved_context/runs/reaction_diffusion/combined_0/generated_reaction_diffusion_simulation.py:31)
caches `u * v**2` and computes both increments with the reference's Laplacian
expressions before assigning the new fields.

Both produce finite arrays with the requested shapes. The combined arrays match
the saved reference hashes. The baseline errors, roughly 4e-8, are consistent
with arithmetic-order/roundoff differences; they do not establish a meaningful
physical-accuracy advantage. Combined stderr contains a `vec_length` deprecation
warning, not a numerical failure.

## Scope of the evidence

This is one fresh generation per arm and domain, at temperature zero without a
provider seed. The two arms also use different retrieved public-code contexts,
as intended by the complete-pipeline comparison. The observations describe this
saved-context experiment and do not establish a general improvement rate or
performance for newly retrieved live contexts.

See [artifact diagnostics](artifact_diagnostics.csv),
[per-domain review rows](manual_script_review.csv), and
[the existing numerical comparison](../reports/numerical_comparisons.csv).
