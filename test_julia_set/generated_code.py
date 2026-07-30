# Julia Set Simulation using PhiFlow

Below is a complete, working PhiFlow script that simulates the time-dependent Julia set as described, and saves the accumulated escape-counter field `J` (the "domain trajectory") for all 100 time steps.

```python
"""
Julia Set Simulation using PhiFlow
====================================

Governing equations:
    Domain:      Omega = { x + i*y | x in [-2,2], y in [-2,2] }
    Grid:        Nx = Ny = 256
    Initial:     z(x,y,0) = x + i*y
    Parameter:   c(t) = 0.7885 * exp(i * 2*pi*t/100),  t = 0,1,...,99
    Update:      z(x,y,t) <- z(x,y,t)^2 + c(t)
                 J(x,y,t) <- J(x,y,t) + 1_{|z|<2}
    Escape:      N_escape = 50 (max iteration count reference, not used
                 directly in the accumulation formula above)

Output:
    julia_set_domain_trj.npy  -> shape [100, 256, 256]
"""

import numpy as np
from phi.flow import *   # brings in math, CenteredGrid, Box, extrapolation, spatial, etc.


def main():
    # ------------------------------------------------------------------
    # Step 1: Define computational grid, domain, and initial conditions
    # ------------------------------------------------------------------
    Nx = Ny = 256
    N_steps = 100
    N_escape = 50  # reference constant (not explicitly used in update formula)

    bounds = Box(x=(-2, 2), y=(-2, 2))

    # Coordinate vectors along each spatial dimension
    x_coords = math.tensor(np.linspace(-2, 2, Nx), spatial('x'))
    y_coords = math.tensor(np.linspace(-2, 2, Ny), spatial('y'))

    # Initial complex field z(x,y,0) = x + i*y  (broadcast over named dims)
    z0 = x_coords + 1j * y_coords

    # Complex-valued CenteredGrid representing z(x,y,t)
    z = CenteredGrid(z0, extrapolation.PERIODIC, bounds=bounds)

    # Julia set accumulator field J(x,y,t), initialized to zero
    J = CenteredGrid(0.0, extrapolation.ZERO, bounds=bounds, x=Nx, y=Ny)

    # ------------------------------------------------------------------
    # Step 2: Define the step function (update rule)
    # ------------------------------------------------------------------
    def step(z_grid, J_grid, t):
        # c(t) = 0.7885 * e^{i * 2*pi*t/100}
        c_t = 0.7885 * np.exp(1j * 2.0 * np.pi * t / 100.0)

        # z <- z^2 + c(t)
        z_new = z_grid ** 2 + c_t

        # Indicator field: 1 where |z| < 2, else 0
        mask_values = math.where(math.abs(z_new.values) < 2, 1.0, 0.0)
        mask_grid = CenteredGrid(mask_values, extrapolation.ZERO, bounds=bounds)

        # J <- J + indicator
        J_new = J_grid + mask_grid

        return z_new, J_new

    # ------------------------------------------------------------------
    # Run simulation for 100 time steps, storing J at every step
    # ------------------------------------------------------------------
    domain_trj = []

    for t in range(N_steps):
        z, J = step(z, J, t)

        # Convert current J field to a numpy array with (x, y) ordering
        J_np = J.values.numpy(('x', 'y'))
        domain_trj.append(J_np)

        if (t + 1) % 10 == 0 or t == 0:
            print(f"Step {t+1:3d}/{N_steps}  |  "
                  f"max(J) = {J_np.max():.2f}, mean(J) = {J_np.mean():.3f}")

    # Stack into shape [time_step, Nx, Ny]
    domain_trj = np.stack(domain_trj, axis=0).astype(np.float32)
    print("Final trajectory shape:", domain_trj.shape)

    # ------------------------------------------------------------------
    # Save result
    # ------------------------------------------------------------------
    out_file = "julia_set_domain_trj.npy"
    np.save(out_file, domain_trj)
    print(f"Saved Julia set trajectory to '{out_file}'")


if __name__ == "__main__":
    main()
```

### Notes on the implementation

1. **Grid & domain** — The domain Ω = [-2,2] × [-2,2] is discretized on a 256×256 `CenteredGrid` using `phi.flow`'s `Box` and named spatial dimensions (`x`, `y`).

2. **Complex field** — `z(x,y,0) = x + iy` is built by broadcasting a real `x`-vector and an imaginary `y`-vector across the two named dimensions, producing a complex-valued PhiFlow tensor stored inside a `CenteredGrid`.

3. **Step function** — At each time step `t`, the parameter `c(t) = 0.7885 e^{i2\pi t/100}` is computed, `z` is updated as `z² + c(t)`, and the escape-time indicator `1_{|z|<2}` is accumulated into `J`.

4. **`N_escape`** — Included as a defined constant per the problem statement; the accumulation rule given does not explicitly reference it (it typically represents the maximum iteration bound, which here is exactly the 100 simulation steps run).

5. **Output** — After 100 steps, `domain_trj` has shape `(100, 256, 256)` and is saved as `julia_set_domain_trj.npy`, containing the evolving Julia-set escape-count field at every timestep.

Run the script directly:

```bash
python julia_set_simulation.py
```

This will print progress and produce `julia_set_domain_trj.npy` in the working directory.