
"""
Smoke Plume Simulation using PhiFlow
-------------------------------------
Domain      : [0,100] x [0,100]
Velocity/Pressure grid : 64 x 64  (staggered / centered)
Smoke grid  : 200 x 200
Governing equations:
    dS/dt + (u.grad)S = alpha * S            (smoke transport + inflow growth)
    du/dt + (u.grad)u = -grad(p) + beta*S*e_y (momentum + buoyancy)
    div(u) = 0                                (incompressibility)

Boundary conditions:
    u = 0 on boundary                (no-slip / closed domain)
    dS/dn = 0 on boundary             (zero gradient - extrapolation.BOUNDARY)
    dp/dn = 0 on boundary             (zero gradient - extrapolation.BOUNDARY)

Time step: dt = 0.5
Steps: 100  -> smoke_trj has 101 snapshots, pressure_trj has 100 snapshots
"""

import numpy as np
from phi.flow import *

# -----------------------------
# Domain / Grid Definitions
# -----------------------------
DOMAIN_BOUNDS = Box(x=100, y=100)

# Velocity field: staggered grid, 64x64, Dirichlet zero boundary (u = 0 on walls)
velocity = StaggeredGrid(
    0,
    extrapolation=extrapolation.ZERO,
    x=64, y=64,
    bounds=DOMAIN_BOUNDS
)

# Smoke field: centered grid, 200x200, zero-gradient (Neumann) boundary
smoke = CenteredGrid(
    0,
    extrapolation=extrapolation.BOUNDARY,
    x=200, y=200,
    bounds=DOMAIN_BOUNDS
)

# Pressure field: initialized as None (solved for at first step), 64x64 domain
pressure = None

# -----------------------------
# Inflow definition
# -----------------------------
# Inflow source: circular region centered at (50, 9.5) with radius 5
INFLOW_RATE = 0.2       # alpha
BUOYANCY_FACTOR = 0.1   # beta
DT = 0.5                # time step
N_STEPS = 100

inflow_source = CenteredGrid(
    Sphere(center=(50, 9.5), radius=5),
    extrapolation=extrapolation.BOUNDARY,
    x=200, y=200,
    bounds=DOMAIN_BOUNDS
)

# -----------------------------
# Step function (single simulation step)
# -----------------------------
def step(velocity, smoke, pressure, dt):
    # Advect smoke field, then add inflow growth (alpha * S)
    smoke = advect.mac_cormack(smoke, velocity, dt=dt)
    smoke = smoke + dt * INFLOW_RATE * inflow_source

    # Buoyancy force applied to velocity, resampled to velocity's staggered grid
    buoyancy_force = (smoke * (0, BUOYANCY_FACTOR)) @ velocity

    # Advect velocity (momentum term), add buoyancy force
    velocity = advect.semi_lagrangian(velocity, velocity, dt=dt)
    velocity = velocity + dt * buoyancy_force

    # Solve for incompressibility (projection step)
    velocity, pressure = fluid.make_incompressible(
        velocity,
        solve=Solve('CG', 1e-5, 1e-5, x0=pressure)
    )

    return velocity, smoke, pressure


# -----------------------------
# Run Simulation
# -----------------------------
smoke_trj = []
pressure_trj = []

# store initial smoke field (t=0)
smoke_trj.append(smoke.values.numpy('x,y'))

for i in range(N_STEPS):
    velocity, smoke, pressure = step(velocity, smoke, pressure, dt=DT)

    smoke_trj.append(smoke.values.numpy('x,y'))
    pressure_trj.append(pressure.values.numpy('x,y'))

    print(f"Step {i+1}/{N_STEPS} completed. "
          f"Max smoke: {float(math.max(smoke.values)):.4f}, "
          f"Max |u|: {float(math.max(math.abs(velocity.staggered_tensor()))):.4f}")

# -----------------------------
# Convert to numpy arrays and save
# -----------------------------
smoke_trj = np.stack(smoke_trj, axis=0)        # shape: [101, 200, 200]
pressure_trj = np.stack(pressure_trj, axis=0)  # shape: [100, 64, 64]

np.save('smoke_plume_smoke_trj.npy', smoke_trj)
np.save('smoke_plume_pressure_trj.npy', pressure_trj)

print("Simulation complete.")
print(f"smoke_trj shape: {smoke_trj.shape}")
print(f"pressure_trj shape: {pressure_trj.shape}")
