```python
"""
Reaction-Diffusion (Gray-Scott) simulation using PhiFlow
=========================================================

Governing equations:
    du/dt = Du * lap(u) - u*v^2 + f*(1-u)
    dv/dt = Dv * lap(v) + u*v^2 - (f+k)*v

Domain:
    Omega = [0, Lx] x [0, Ly],  Lx = Ly = 100
    Nx = Ny = 100
    Periodic boundary conditions

Initial condition:
    u(0) = v(0) = cos(r/s),  r = sqrt((x-Lx/2)^2 + (y-Ly/2)^2), s = 3

Time stepping:
    dt = 0.5, 100 steps -> 101 snapshots (including initial state)

Outputs:
    reaction_diffusion_u_trj.npy  -> shape [101, 100, 100]
    reaction_diffusion_v_trj.npy  -> shape [101, 100, 100]
"""

import numpy as np
from phi.flow import *   # brings in math, CenteredGrid, Box, extrapolation, field, etc.

# -----------------------------
# Step 1: Domain / grid / parameters
# -----------------------------
Lx, Ly = 100.0, 100.0
Nx, Ny = 100, 100
dt = 0.5
n_steps = 100

Du, Dv = 0.19, 0.05
f, k = 0.06, 0.062
s = 3.0

domain_bounds = Box(x=Lx, y=Ly)

def initial_field(x):
    # x is a dict-like Tensor with 'x' and 'y' components (physical coordinates)
    r = math.sqrt((x['x'] - Lx / 2) ** 2 + (x['y'] - Ly / 2) ** 2)
    return math.cos(r / s)

u0 = CenteredGrid(initial_field, extrapolation.PERIODIC, bounds=domain_bounds, x=Nx, y=Ny)
v0 = CenteredGrid(initial_field, extrapolation.PERIODIC, bounds=domain_bounds, x=Nx, y=Ny)

# -----------------------------
# Step 2: Step function (Gray-Scott reaction-diffusion)
# -----------------------------
def step(u: CenteredGrid, v: CenteredGrid, dt: float):
    lap_u = field.laplace(u)
    lap_v = field.laplace(v)

    uvv = u * v * v

    u_new = u + dt * (Du * lap_u - uvv + f * (1 - u))
    v_new = v + dt * (Dv * lap_v + uvv - (f + k) * v)

    return u_new, v_new

# -----------------------------
# Run simulation, storing trajectories
# -----------------------------
u = u0
v = v0

u_trj = np.zeros((n_steps + 1, Nx, Ny), dtype=np.float32)
v_trj = np.zeros((n_steps + 1, Nx, Ny), dtype=np.float32)

# store initial condition
u_trj[0] = u.values.numpy('x,y')
v_trj[0] = v.values.numpy('x,y')

for i in range(1, n_steps + 1):
    u, v = step(u, v, dt)
    u_trj[i] = u.values.numpy('x,y')
    v_trj[i] = v.values.numpy('x,y')
    print(f"Step {i}/{n_steps} completed.")

# -----------------------------
# Save trajectories
# -----------------------------
np.save('reaction_diffusion_u_trj.npy', u_trj)
np.save('reaction_diffusion_v_trj.npy', v_trj)

print("Simulation complete.")
print("u_trj shape:", u_trj.shape)
print("v_trj shape:", v_trj.shape)
```

**Notes on the implementation:**

- The simulation uses **periodic boundary conditions** (`extrapolation.PERIODIC`), which is the standard choice for Gray–Scott reaction–diffusion simulations on a finite domain, since none were explicitly specified.
- `field.laplace(u)` computes the discrete Laplacian on the `CenteredGrid` using PhiFlow's built-in finite-difference stencil, automatically respecting the grid spacing (`dx = Lx/Nx`, `dy = Ly/Ny`) and the periodic boundary condition.
- The explicit (forward Euler) integration scheme is used with `dt = 0.5`, iterated for 100 steps, producing 101 total snapshots (`t=0` through `t=100`), matching the required output shape `[101, 100, 100]`.
- `u.values.numpy('x,y')` converts each PhiFlow `CenteredGrid` field back into a plain NumPy array in the requested `(Nx, Ny)` order for storage.