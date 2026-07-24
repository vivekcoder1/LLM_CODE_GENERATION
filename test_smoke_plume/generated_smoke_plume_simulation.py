```python
"""
Smoke Plume Simulation using PhiFlow
=====================================
Solves the incompressible Navier-Stokes equations coupled with a passive
smoke (scalar) transport equation, including buoyancy forcing.

Governing equations:
    dS/dt + (u . grad) S = alpha * S            (smoke transport + inflow)
    du/dt + (u . grad) u = -grad(p) + beta*S*e_y (momentum + buoyancy)
    div(u) = 0                                    (incompressibility)

Domain: [0,100] x [0,100]
Velocity/Pressure resolution: 64 x 64
Smoke resolution: 200 x 200
"""

from phi.flow import *
import numpy as np

# ----------------------------------------------------------------------
# Domain and simulation parameters
# ----------------------------------------------------------------------
DOMAIN_BOUNDS = Box(x=100, y=100)
DT = 0.5
N_STEPS = 100

INFLOW_RATE = 0.2      # alpha: smoke inflow rate
BUOYANCY = 0.1          # beta: buoyancy coefficient
BUOYANCY_DIR = (0, 1)   # e_y: buoyancy direction

INFLOW_CENTER = vec(x=50, y=9.5)
INFLOW_RADIUS = 5

VELOCITY_RES = dict(x=64, y=64)
PRESSURE_RES = dict(x=64, y=64)
SMOKE_RES = dict(x=200, y=200)

# ----------------------------------------------------------------------
# Initial fields
# ----------------------------------------------------------------------
# Smoke field: Neumann (zero-gradient) boundary conditions -> extrapolation.BOUNDARY
smoke = CenteredGrid(0, extrapolation.BOUNDARY, bounds=DOMAIN_BOUNDS, **SMOKE_RES)

# Velocity field: no-slip / zero Dirichlet boundary conditions -> extrapolation.ZERO
velocity = StaggeredGrid(0, extrapolation.ZERO, bounds=DOMAIN_BOUNDS, **VELOCITY_RES)

# Pressure field: initialized to None, solved implicitly (Neumann BC handled internally)
pressure = None

# Inflow source: circular region centered at (50, 9.5) with radius 5
INFLOW_GEOMETRY = Sphere(center=INFLOW_CENTER, radius=INFLOW_RADIUS)
INFLOW = CenteredGrid(INFLOW_GEOMETRY, extrapolation.BOUNDARY, bounds=DOMAIN_BOUNDS, **SMOKE_RES) * INFLOW_RATE


# ----------------------------------------------------------------------
# Step function
# ----------------------------------------------------------------------
@jit_compile
def step(velocity, smoke, pressure, dt=DT):
    # --- Smoke transport with inflow source ---
    smoke = advect.mac_cormack(smoke, velocity, dt) + INFLOW * dt

    # --- Buoyancy force resampled onto the velocity grid ---
    buoyancy_force = (smoke * (BUOYANCY * BUOYANCY_DIR[0], BUOYANCY * BUOYANCY_DIR[1])) @ velocity

    # --- Momentum equation: advection + buoyancy forcing ---
    velocity = advect.semi_lagrangian(velocity, velocity, dt) + buoyancy_force * dt

    # --- Pressure projection to enforce incompressibility ---
    velocity, pressure = fluid.make_incompressible(
        velocity,
        (),  # no obstacles
        Solve('CG', 1e-5, 1e-5, x0=pressure)
    )
    return velocity, smoke, pressure


# ----------------------------------------------------------------------
# Run simulation
# ----------------------------------------------------------------------
smoke_trj = [smoke.values.numpy('x,y')]
pressure_trj = []

for i in range(N_STEPS):
    velocity, smoke, pressure = step(velocity, smoke, pressure)
    smoke_trj.append(smoke.values.numpy('x,y'))
    pressure_trj.append(pressure.values.numpy('x,y'))
    print(f"Step {i + 1}/{N_STEPS} completed.")

smoke_trj = np.stack(smoke_trj, axis=0)      # shape: [N_STEPS+1, 200, 200]
pressure_trj = np.stack(pressure_trj, axis=0)  # shape: [N_STEPS, 64, 64]

# ----------------------------------------------------------------------
# Save results
# ----------------------------------------------------------------------
np.save('smoke_plume_smoke_trj.npy', smoke_trj)
np.save('smoke_plume_pressure_trj.npy', pressure_trj)

print("Simulation complete.")
print("smoke_trj shape:", smoke_trj.shape)
print("pressure_trj shape:", pressure_trj.shape)
```