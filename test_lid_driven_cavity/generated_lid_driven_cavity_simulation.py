```python
"""
Lid-Driven Cavity Flow Simulation using PhiFlow
================================================

Governing equations (viscous, incompressible Navier-Stokes, advection-diffusion form):

    du/dt + u . grad(u) = nu * laplace(u)
    div(u) = 0

Domain:
    Nx = 50, Ny = 32
    nu = 0.1
    dt = 1.0

Boundary Conditions:
    left (x=0)    : u = 0
    right (x=Nx)  : u = 0
    bottom (y=0)  : u = 0
    top (y=Ny)    : u = [1, 0]   (moving lid)

The simulation runs for 100 time steps and the resulting velocity trajectory
(101 snapshots including the initial condition) is stored with shape
[time_step+1, Nx, Ny, 2] in 'lid_driven_cavity_velocity_trj.npy'.
"""

from phi.flow import *
import numpy as np


# ============================================================
# Simulation / grid parameters
# ============================================================
N_x, N_y = 50, 32          # grid resolution
nu = 0.1                   # kinematic viscosity
dt = 1.0                   # time step
n_steps = 100               # number of simulation steps


# ============================================================
# Boundary conditions
# ============================================================
# Left / right walls -> no-slip (zero velocity)
# Bottom wall        -> no-slip (zero velocity)
# Top wall (lid)     -> constant moving velocity (1, 0)
lid_velocity = extrapolation.ConstantExtrapolation(
    math.tensor([1., 0.], channel(vector='x,y'))
)

velocity_boundary = extrapolation.combine_sides(
    x=extrapolation.ZERO,                     # left & right: u = 0
    y=(extrapolation.ZERO, lid_velocity)       # bottom: u = 0, top: u = [1, 0]
)


# ============================================================
# Domain definition
# ============================================================
DOMAIN = Domain(
    x=N_x, y=N_y,
    boundaries={'scalar': extrapolation.BOUNDARY, 'vector': velocity_boundary},
    bounds=Box(x=N_x, y=N_y)
)

# ----- Initial velocity field: u0(x, y) = 0 everywhere -----
velocity = DOMAIN.staggered_grid(0)


# ============================================================
# Step function implementing the governing equations
# ============================================================
def step(velocity: StaggeredGrid, dt: float = dt, nu: float = nu):
    """
    Advances the velocity field by one time step according to:
        du/dt + u . grad(u) = nu * laplace(u)
        div(u) = 0

    Args:
        velocity: Current velocity `StaggeredGrid`.
        dt: Time step size.
        nu: Kinematic viscosity.

    Returns:
        Updated velocity `StaggeredGrid` satisfying incompressibility.
    """
    # --- Advection term: u . grad(u) ---
    velocity = advect.semi_lagrangian(velocity, velocity, dt)

    # --- Diffusion term: nu * laplace(u) ---
    velocity = diffuse.explicit(velocity, nu, dt)

    # --- Re-enforce boundary conditions (no-slip walls + moving lid) ---
    velocity = apply_boundary_conditions(velocity, [])

    # --- Pressure projection to satisfy div(u) = 0 ---
    velocity, pressure = fluid.make_incompressible(velocity, DOMAIN)

    return velocity


# ============================================================
# Run simulation and record trajectory
# ============================================================
velocity_trj = [DOMAIN.grid(velocity).values.numpy('x,y,vector')]

for i in range(n_steps):
    velocity = step(velocity, dt, nu)
    centered_velocity = DOMAIN.grid(velocity)
    velocity_trj.append(centered_velocity.values.numpy('x,y,vector'))
    print(f"Step {i + 1}/{n_steps} completed.")

velocity_trj = np.stack(velocity_trj, axis=0)
print("Final trajectory shape:", velocity_trj.shape)  # Expected: (101, 50, 32, 2)


# ============================================================
# Save results
# ============================================================
np.save('lid_driven_cavity_velocity_trj.npy', velocity_trj)
print("Saved velocity trajectory to 'lid_driven_cavity_velocity_trj.npy'")
```