```python
"""
Heat-flow (anisotropic diffusion) simulation using the PhiFlow framework.

Governing equation (diffusion only along x):
    du/dt = kappa(x, y) * d^2u/dx^2

Domain:        Omega = [0, 10] x [0, 5]
Boundaries:
    x = 0  -> Dirichlet,      u = 1
    x = 10 -> Neumann,        du/dx = 0 (zero-gradient)
    y = 0 / y = 5             -> periodic

Conductivity:
    kappa = 1.01 inside  B = ([0,10]x[2,3]) U ([4.5,5.5]x[1,4])
    kappa = 0.01 outside B

Grid resolution: (Nx, Ny) = (100, 50)
Time step:       dt = 1.0
Steps:           100  (101 stored snapshots, including t = 0)

Output:
    heat_flow_temperature_trj.npy  -> shape (101, 100, 50)
"""

from phi.flow import *
import numpy as np


# ----------------------------------------------------------------------
# Step 1: Domain, boundary conditions, grid, and initial condition setup
# ----------------------------------------------------------------------

# Grid resolution
Nx, Ny = 100, 50

# Time stepping parameters
dt = 1.0
n_steps = 100

# Physical domain bounds: x in [0, 10], y in [0, 5]
bounds = Box(x=10, y=5)

# Mixed boundary conditions:
#   x-: Dirichlet u = 1 (constant extrapolation)
#   x+: zero-gradient (Neumann, du/dx = 0)
#   y : periodic (top and bottom are identified)
boundary = extrapolation.combine_sides(
    x=(extrapolation.ConstantExtrapolation(1.0), extrapolation.ZERO_GRADIENT),
    y=extrapolation.PERIODIC,
)

# Build the computational domain (resolution + physical bounds + boundaries)
domain = Domain(x=Nx, y=Ny, boundaries=boundary, bounds=bounds)

# ----------------------------------------------------------------------
# Conductivity field kappa(x, y)
# ----------------------------------------------------------------------
# Inclusions (union of two boxes) where conductivity is high (1.01),
# everywhere else conductivity is low (0.01).
box1 = Box(x=(0, 10), y=(2, 3))
box2 = Box(x=(4.5, 5.5), y=(1, 4))
inclusion = union(box1, box2)

# domain.grid() with a Geometry produces the volume fraction (0..1) of each
# cell that lies inside the geometry. Since the grid resolution aligns
# exactly with the inclusion boundaries, this yields a binary 0/1 mask.
inclusion_mask = domain.grid(inclusion)

kappa_low = 0.01
kappa_high = 1.01
kappa = kappa_low + inclusion_mask * (kappa_high - kappa_low)

# ----------------------------------------------------------------------
# Initial condition: u(x, y, 0) = 0 everywhere (boundary values enforced
# through extrapolation when differential operators are evaluated).
# ----------------------------------------------------------------------
u = domain.grid(0.0)


# ----------------------------------------------------------------------
# Step 2: Define the simulation step function
# ----------------------------------------------------------------------
def step(u: CenteredGrid, kappa: CenteredGrid, dt: float) -> CenteredGrid:
    """
    Advance the temperature field u by one explicit Euler step according to

        du/dt = kappa * d^2u/dx^2

    Only the x-direction second derivative is used, as specified by the
    governing equation (diffusion acts exclusively along x).

    Args:
        u: Current temperature `CenteredGrid`.
        kappa: Spatially varying conductivity `CenteredGrid`.
        dt: Time step size.

    Returns:
        Updated temperature `CenteredGrid`.
    """
    laplace_x_u = field.laplace(u, axes='x')  # second derivative along x only
    return u + dt * kappa * laplace_x_u


# ----------------------------------------------------------------------
# Run the simulation and record the trajectory
# ----------------------------------------------------------------------
temperature_trj = [u.values.numpy(['x', 'y'])]

for i in range(n_steps):
    u = step(u, kappa, dt)
    temperature_trj.append(u.values.numpy(['x', 'y']))

temperature_trj = np.stack(temperature_trj, axis=0)  # shape: (n_steps+1, Nx, Ny)

print(f"Trajectory shape: {temperature_trj.shape}")

# ----------------------------------------------------------------------
# Save trajectory to file
# ----------------------------------------------------------------------
np.save('heat_flow_temperature_trj.npy', temperature_trj)
print("Saved trajectory to 'heat_flow_temperature_trj.npy'")
```