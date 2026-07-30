```python
"""
2D Burgers' Equation Simulation using PhiFlow
==============================================

Solves:
    du/dt + u*du/dx + v*du/dy = nu*(d2u/dx2 + d2u/dy2)
    dv/dt + u*dv/dx + v*dv/dy = nu*(d2v/dx2 + d2v/dy2)

on a periodic 2D domain, using semi-Lagrangian advection followed by
explicit diffusion at each time step.

Saves the velocity trajectory (101 snapshots including t=0) to
'burgers2d_velocity_trj.npy' with shape [steps+1, Nx, Ny, 2].
"""

from phi.flow import *   # brings in CenteredGrid, Box, extrapolation, advect, diffuse, math, channel, etc.
import numpy as np


# ---------------------------------------------------------------------
# Step 1: Domain, grid and initial/boundary conditions
# ---------------------------------------------------------------------

Lx, Ly = 40.0, 20.0      # Domain size
Nx, Ny = 64, 64          # Grid resolution
nu = 0.1                 # Diffusivity
dt = 0.5                 # Time step
n_steps = 100            # Number of simulation steps


def init_gaussian(x):
    """Initial condition: u(x,y,0) = v(x,y,0) = exp(-(x-Lx/2)^2 - (y-Ly/2)^2)"""
    x_pos = x.vector['x']
    y_pos = x.vector['y']
    gauss = math.exp(-((x_pos - Lx / 2) ** 2 + (y_pos - Ly / 2) ** 2))
    # Both velocity components initialized identically
    return math.stack([gauss, gauss], channel(vector='x,y'))


# Periodic boundary conditions in both x and y directions
velocity = CenteredGrid(
    init_gaussian,
    extrapolation=extrapolation.PERIODIC,
    bounds=Box(x=Lx, y=Ly),
    x=Nx, y=Ny
)


# ---------------------------------------------------------------------
# Step 2: Define the simulation step function
# ---------------------------------------------------------------------

def burgers_step(v, dt=dt, nu=nu):
    """One time step of the 2D Burgers' equation:
       1) Semi-Lagrangian self-advection
       2) Explicit diffusion
    """
    v = advect.semi_lagrangian(v, v, dt)
    v = diffuse.explicit(v, nu, dt)
    return v


# ---------------------------------------------------------------------
# Run simulation and collect trajectory
# ---------------------------------------------------------------------

velocity_trj = [velocity.values.numpy(['x', 'y', 'vector'])]

v = velocity
for step in range(n_steps):
    v = burgers_step(v)
    velocity_trj.append(v.values.numpy(['x', 'y', 'vector']))
    if (step + 1) % 10 == 0:
        print(f"Step {step + 1}/{n_steps} completed.")

velocity_trj = np.stack(velocity_trj, axis=0)
print("Final trajectory shape:", velocity_trj.shape)  # Expect (101, 64, 64, 2)

# ---------------------------------------------------------------------
# Save results
# ---------------------------------------------------------------------

np.save('burgers2d_velocity_trj.npy', velocity_trj)
print("Saved velocity trajectory to 'burgers2d_velocity_trj.npy'")
```

**Notes on the implementation:**

- **Grid & BCs:** A `CenteredGrid` is used with `extrapolation.PERIODIC`, which enforces the periodic boundary conditions `u(0,y,t)=u(Lx,y,t)` and `u(x,0,t)=u(x,Ly,t)` automatically at the domain boundaries.
- **Initial condition:** Both velocity components (`u` and `v`) are initialized with the given Gaussian bump, stacked along the `vector` channel dimension.
- **Step function:** Implements Burgers' equation via operator splitting — self-advection (`advect.semi_lagrangian`) followed by diffusion (`diffuse.explicit`), which is the standard PhiFlow approach for this PDE.
- **Trajectory storage:** The velocity field values are converted to NumPy arrays each step (ordered as `x, y, vector`) and stacked to produce a final array of shape `(101, 64, 64, 2)`, saved via `np.save`.