```python
"""
Wake-flow simulation (flow past a circular cylinder) using PhiFlow.

Governing equations (inviscid, incompressible):
    du/dt + (u . grad) u = 0
    div(u) = 0

Domain:      Omega = [0,200] x [0,100] x [0,5]
Object:      infinite cylinder (axis = z) centered at (x,y) = (20,50), radius = 10
Boundary:    x=0   -> Dirichlet inflow u = (2,0,0)
             x=200 -> zero-gradient (Neumann) outflow
             y     -> periodic
             z     -> periodic
Initial:     u(x,y,z,0) = (8,0,0)
Resolution:  (Nx,Ny,Nz) = (128,64,8)

The trajectory of the velocity field (401 snapshots, i.e. the initial
condition plus 400 time steps) is stored in "wake_flow_velocity_trj.npy"
with shape (401, 128, 64, 8, 3).
"""

from phi.flow import *
from phi.geom import Cylinder
import numpy as np


def main():
    # ------------------------------------------------------------------
    # 1. Domain, grid resolution and boundary conditions
    # ------------------------------------------------------------------
    bounds = Box(x=200, y=100, z=5)
    resolution = spatial(x=128, y=64, z=8)

    # velocity boundary conditions
    inflow_extrap = extrapolation.ConstantExtrapolation(vec(x=2.0, y=0.0, z=0.0))
    outflow_extrap = extrapolation.ZERO_GRADIENT  # d(u)/dx = 0 at x = 200

    velocity_extrapolation = extrapolation.combine_sides(
        x=(inflow_extrap, outflow_extrap),
        y=extrapolation.PERIODIC,
        z=extrapolation.PERIODIC,
    )

    # pressure boundary conditions (Neumann in x, periodic in y,z)
    pressure_extrapolation = extrapolation.combine_sides(
        x=(extrapolation.ZERO_GRADIENT, extrapolation.ZERO_GRADIENT),
        y=extrapolation.PERIODIC,
        z=extrapolation.PERIODIC,
    )

    # ------------------------------------------------------------------
    # 2. Initial condition
    # ------------------------------------------------------------------
    velocity = StaggeredGrid(
        vec(x=8.0, y=0.0, z=0.0),
        velocity_extrapolation,
        bounds=bounds,
        resolution=resolution,
    )

    # ------------------------------------------------------------------
    # 3. Obstacle: infinite cylinder along z, centered at (20,50), radius 10
    # ------------------------------------------------------------------
    cylinder_geom = Cylinder(
        center=vec(x=20.0, y=50.0, z=2.5),
        radius=10.0,
        depth=5.0,
        axis="z",
    )
    obstacle = Obstacle(cylinder_geom)

    # ------------------------------------------------------------------
    # 4. Step function (advection + pressure projection for incompressibility)
    # ------------------------------------------------------------------
    dt = 0.1  # time step size (CFL-safe for u_max=8, dx ~ 1.56)

    @jit_compile
    def step(v, p_guess):
        v = advect.semi_lagrangian(v, v, dt)
        v, p = fluid.make_incompressible(
            v,
            obstacles=[obstacle],
            solve=Solve("CG", 1e-5, 1e-5, x0=p_guess),
        )
        return v, p

    # ------------------------------------------------------------------
    # 5. Run simulation for 400 steps, storing the trajectory
    # ------------------------------------------------------------------
    n_steps = 400
    trajectory_np = []

    # store initial condition (converted to cell-centered values)
    def to_numpy(v):
        return v.at_centers().values.numpy(["x", "y", "z", "vector"])

    trajectory_np.append(to_numpy(velocity))

    v = velocity
    pressure_guess = CenteredGrid(
        0.0, pressure_extrapolation, bounds=bounds, resolution=resolution
    )

    for i in range(n_steps):
        v, pressure_guess = step(v, pressure_guess)
        trajectory_np.append(to_numpy(v))
        if (i + 1) % 20 == 0:
            print(f"Step {i + 1}/{n_steps} completed.")

    # ------------------------------------------------------------------
    # 6. Save trajectory
    # ------------------------------------------------------------------
    velocity_trj = np.stack(trajectory_np, axis=0)  # shape (401, Nx, Ny, Nz, 3)
    print("Final trajectory shape:", velocity_trj.shape)

    np.save("wake_flow_velocity_trj.npy", velocity_trj)
    print("Saved trajectory to wake_flow_velocity_trj.npy")


if __name__ == "__main__":
    main()
```