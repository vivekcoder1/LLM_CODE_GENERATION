Looking at this problem, I need to:

1. Set up a 2D grid (100×50) over domain [0,10]×[0,5]
2. Apply mixed boundary conditions: Dirichlet (u=1) at x=0, Neumann (∂u/∂x=0) at x=10, and periodic in y
3. Build a spatially-varying conductivity field based on the two inclusion boxes
4. Implement an explicit Euler step for `∂u/∂t = κ ∂²u/∂x²` (Laplacian restricted to x-axis only)
5. Run for 100 steps and save all 101 snapshots

```python
"""
Heat Flow Simulation with Variable Conductivity using PhiFlow
================================================================
Governing equation:  du/dt = kappa * d2u/dx2   (diffusion only along x)

Domain      : [0,10] x [0,5]
BCs         : u(0,y,t)=1 (Dirichlet)
              du/dx(10,y,t)=0 (Neumann / zero-gradient)
              u(x,0,t)=u(x,5,t) (periodic in y)
Inclusions  : B = ([0,10]x[2,3]) U ([4.5,5.5]x[1,4])  -> kappa = 1.01
              elsewhere                                -> kappa = 0.01
Resolution  : Nx=100, Ny=50
dt          : 1.0
Steps       : 100  (=> 101 saved snapshots)
"""

from phi.flow import *
from phi import field, math
import numpy as np


# ----------------------------------------------------------------------
# Step 1: Define computational grid, domain, boundary conditions, IC
# ----------------------------------------------------------------------

# Physical domain
domain_bounds = Box(x=10, y=5)

# Grid resolution
Nx, Ny = 100, 50
resolution = spatial(x=Nx, y=Ny)

# Boundary conditions for the temperature field u:
#   x-lower  : Dirichlet u = 1.0
#   x-upper  : Neumann (zero gradient)  -> extrapolation.BOUNDARY
#   y-sides  : periodic
u_extrapolation = extrapolation.combine_sides(
    x=(extrapolation.ConstantExtrapolation(1.0), extrapolation.BOUNDARY),
    y=extrapolation.PERIODIC
)

# Initial condition: temperature = 0 everywhere in the interior.
# (The Dirichlet value of 1 at x=0 is enforced through the extrapolation
#  of the field, so it will be respected whenever ghost cells are sampled.)
u0 = CenteredGrid(
    0.0,
    extrapolation=u_extrapolation,
    bounds=domain_bounds,
    resolution=resolution
)

# ----------------------------------------------------------------------
# Build the spatially varying conductivity field kappa(x,y)
# ----------------------------------------------------------------------

# Physical coordinates of the cell centers (same shape as u0)
points = u0.points
x_coord = points.vector['x']
y_coord = points.vector['y']

# Inclusion 1: full x-range, y in [2,3]
box1_mask = (y_coord >= 2) & (y_coord <= 3)

# Inclusion 2: x in [4.5,5.5], y in [1,4]
box2_mask = (x_coord >= 4.5) & (x_coord <= 5.5) & (y_coord >= 1) & (y_coord <= 4)

inclusion_mask = box1_mask | box2_mask

kappa_values = math.where(inclusion_mask, 1.01, 0.01)

# Conductivity field uses a simple zero-gradient extrapolation
# (its own boundary treatment does not affect the physics of u).
kappa = CenteredGrid(
    kappa_values,
    extrapolation=extrapolation.BOUNDARY,
    bounds=domain_bounds,
    resolution=resolution
)

# ----------------------------------------------------------------------
# Step 2: Define the step function for the governing equation
#          du/dt = kappa * d2u/dx2   (Laplacian only along x)
# ----------------------------------------------------------------------

dt = 1.0


def step(u: CenteredGrid, kappa: CenteredGrid, dt: float) -> CenteredGrid:
    """Explicit Euler update for the 1D (x-direction) heat equation
    with spatially varying conductivity kappa."""
    laplace_x = field.laplace(u, axes='x')   # d2u/dx2 only
    du_dt = kappa * laplace_x
    return u + dt * du_dt


# ----------------------------------------------------------------------
# Run the simulation for 100 time steps, storing every snapshot
# ----------------------------------------------------------------------

n_steps = 100
trajectory = [u0]

u = u0
for i in range(n_steps):
    u = step(u, kappa, dt)
    trajectory.append(u)
    print(f"Step {i + 1:3d}/{n_steps} completed "
          f"(mean T = {float(math.mean(u.values)):.4f})")

# ----------------------------------------------------------------------
# Convert the trajectory to a NumPy array of shape [steps+1, Nx, Ny]
# and save to disk
# ----------------------------------------------------------------------

temperature_trj = np.stack(
    [snapshot.values.numpy(order=('x', 'y')) for snapshot in trajectory],
    axis=0
)

print("Final trajectory shape:", temperature_trj.shape)  # (101, 100, 50)

np.save('heat_flow_temperature_trj.npy', temperature_trj)
print("Saved trajectory to 'heat_flow_temperature_trj.npy'")
```

### Notes on the implementation

- **Boundary conditions** are encoded directly in the `CenteredGrid`'s `extrapolation`: a `ConstantExtrapolation(1.0)` on the lower x-side enforces the Dirichlet condition, `extrapolation.BOUNDARY` on the upper x-side gives a zero-gradient (Neumann) condition, and `extrapolation.PERIODIC` on the y-sides enforces `u(x,0,t)=u(x,5,t)`.
- **Conductivity field** `kappa` is built by evaluating the union of the two inclusion boxes on the grid's cell-center coordinates using `math.where`.
- **`field.laplace(u, axes='x')`** restricts the second-derivative computation to the x-direction only, matching the governing PDE `∂u/∂t = κ ∂²u/∂x²`.
- The **explicit Euler step** directly implements `u_new = u + dt * kappa * d²u/dx²`.
- The trajectory (including the initial condition) is collected into a list of 101 `CenteredGrid` snapshots, converted to NumPy arrays with axis order `(x, y)`, stacked, and saved as `heat_flow_temperature_trj.npy` with shape `(101, 100, 50)`.