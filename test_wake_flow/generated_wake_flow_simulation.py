```python
"""
Wake-Flow (Karman-Vortex-Street) Simulation in PhiFlow
=======================================================

Governing equations (incompressible Navier-Stokes, inviscid / Euler form
as requested by the task):

    du/dt + (u . grad) u = 0
    div(u) = 0

Domain:      Omega = [0,200] x [0,100] x [0,5]
Object:      Cylinder (x-20)^2 + (y-50)^2 <= 10^2   (extends through full z range)
Grid:        (Nx, Ny, Nz) = (128, 64, 8)

Boundary Conditions:
    x = 0    : Dirichlet inflow  u = (2, 0, 0)
    x = 200  : Neumann (zero-gradient) outflow
    y = 0/100: Periodic
    z = 0/5  : Periodic

Initial Condition:
    u(x, y, z, 0) = (8, 0, 0)

The simulation is advanced for 400 time steps and the full velocity
trajectory (401 snapshots, including the initial condition) is stored
in `wake_flow_velocity_trj.npy` with shape [401, 128, 64, 8, 3].
"""

from phi.flow import *
import numpy as np


# ---------------------------------------------------------------------
# Step 1: Domain, Grid, Boundary Conditions & Initial Condition
# ---------------------------------------------------------------------

# Physical domain bounds: Omega = [0,200] x [0,100] x [0,5]
DOMAIN_BOUNDS = Box(x=200, y=100, z=5)

# Grid resolution
RES_X, RES_Y, RES_Z = 128, 64, 8

# Dirichlet inflow value at x = 0: u = (2, 0, 0)
inflow_value = math.tensor([2.0, 0.0, 0.0], channel(vector='x,y,z'))

# Boundary conditions for the velocity field:
#   x-lower : constant inflow  u = (2, 0, 0)
#   x-upper : zero-gradient (Neumann) outflow  du/dx = 0
#   y       : periodic
#   z       : periodic
boundary_conditions = extrapolation.combine_sides(
    x=(extrapolation.ConstantExtrapolation(inflow_value), extrapolation.ZERO_GRADIENT),
    y=extrapolation.PERIODIC,
    z=extrapolation.PERIODIC,
)

# Cylindrical obstacle: (x-20)^2 + (y-50)^2 <= 10^2, independent of z
# -> a disk in the x-y plane extruded across the full z-extent of the domain.
cylinder_disk = Sphere(x=20, y=50, radius=10)          # circular cross-section
full_z_extent = Box(z=(0, 5))                          # spans entire z domain
obstacle_geometry = cylinder_disk & full_z_extent      # intersection -> 3D cylinder
obstacle = Obstacle(obstacle_geometry)

# Initial condition: u(x, y, z, 0) = (8, 0, 0), defined on a staggered grid
velocity = StaggeredGrid(
    (8.0, 0.0, 0.0),
    boundary=boundary_conditions,
    bounds=DOMAIN_BOUNDS,
    x=RES_X, y=RES_Y, z=RES_Z
)

pressure = None  # will hold the pressure guess for warm-starting the solver


# ---------------------------------------------------------------------
# Step 2: Governing Equations - Step Function
# ---------------------------------------------------------------------

@jit_compile
def step(v, p, dt=1.0):
    """
    Advances the velocity field by one time step using:
        1) Semi-Lagrangian advection: du/dt + (u . grad) u = 0
        2) Incompressibility (pressure) projection: div(u) = 0
           while enforcing the no-through-flow condition at the obstacle.
    """
    # Advection term: (u . grad) u
    v = advect.semi_lagrangian(v, v, dt=dt)

    # Enforce div(u) = 0, respecting the cylindrical obstacle
    v, p = fluid.make_incompressible(
        v,
        obstacles=(obstacle,),
        solve=Solve('auto', 1e-5, 1e-5, x0=p)
    )
    return v, p


# ---------------------------------------------------------------------
# Run Simulation
# ---------------------------------------------------------------------

N_STEPS = 400

trajectory = [velocity]  # store initial condition (snapshot 0)

v, p = velocity, pressure
for i in range(N_STEPS):
    v, p = step(v, p)
    trajectory.append(v)
    print(f"Step {i + 1}/{N_STEPS} completed")


# ---------------------------------------------------------------------
# Save Trajectory
# ---------------------------------------------------------------------

# Stack all snapshots along a new batch dimension 'time'
velocity_trj = field.stack(trajectory, batch('time'))

# Interpolate the staggered velocity components to cell centers
# and export as numpy array with shape [time_step+1, Nx, Ny, Nz, 3]
velocity_np = velocity_trj.at_centers().numpy(['time', 'x', 'y', 'z', 'vector'])

np.save('wake_flow_velocity_trj.npy', velocity_np)

print("Saved velocity trajectory with shape:", velocity_np.shape)
```