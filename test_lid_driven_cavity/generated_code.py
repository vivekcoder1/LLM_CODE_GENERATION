```python
"""
Lid-Driven Cavity Flow Simulation using PhiFlow
=================================================
Grid: Nx=50, Ny=32
Governing equations (incompressible Navier-Stokes):
    du/dt + u . grad(u) = nu * laplace(u)
    div(u) = 0

Boundary conditions:
    - Left, Right, Bottom walls: no-slip (u = 0)
    - Top lid: u = (1, 0)  (moving lid)

The simulation is advanced for 100 time steps (dt = 1.0) and the full
velocity trajectory (101 snapshots, including the initial state) is
saved to 'lid_driven_cavity_velocity_trj.npy' with shape
[time_step+1, Nx, Ny, 2].
"""

from phi.flow import *
import numpy as np


def build_boundary_extrapolation():
    """
    Build the boundary extrapolation (BC) for the staggered velocity grid.

    - x-direction (left/right walls): zero velocity (no-slip)
    - y-direction:
        lower (bottom wall): zero velocity (no-slip)
        upper (top wall / lid): constant velocity (1, 0)
    """
    lid_velocity = tensor([1.0, 0.0], channel(vector='x,y'))

    velocity_extrapolation = extrapolation.combine_sides(
        x=extrapolation.ZERO,
        y=(extrapolation.ZERO, extrapolation.ConstantExtrapolation(lid_velocity))
    )
    return velocity_extrapolation


def step(velocity: StaggeredGrid, pressure, dt: float, nu: float):
    """
    Perform a single time step of the incompressible Navier-Stokes solver.

    Parameters
    ----------
    velocity : StaggeredGrid
        Current velocity field.
    pressure : CenteredGrid or None
        Previous pressure field (used as initial guess for the solver).
    dt : float
        Time step size.
    nu : float
        Kinematic viscosity.

    Returns
    -------
    velocity : StaggeredGrid
        Updated velocity field after advection, diffusion, and projection.
    pressure : CenteredGrid
        Updated pressure field.
    """
    # 1. Advection: u . grad(u)
    velocity = advect.semi_lagrangian(velocity, velocity, dt)

    # 2. Diffusion: nu * laplace(u)
    velocity = diffuse.explicit(velocity, nu, dt)

    # 3. Pressure projection to enforce div(u) = 0
    velocity, pressure = fluid.make_incompressible(
        velocity,
        solve=Solve('CG', rel_tol=1e-5, abs_tol=1e-5, x0=pressure)
    )

    return velocity, pressure


def main():
    # ------------------------------------------------------------------
    # Step 1: Domain / Grid / Boundary Condition definition
    # ------------------------------------------------------------------
    Nx, Ny = 50, 32
    nu = 0.1
    dt = 1.0
    n_steps = 100

    bounds = Box(x=Nx, y=Ny)

    velocity_extrapolation = build_boundary_extrapolation()

    # Initial velocity field: u0(x, y) = 0 everywhere
    velocity = StaggeredGrid(
        0,
        extrapolation=velocity_extrapolation,
        x=Nx, y=Ny,
        bounds=bounds
    )

    pressure = None

    # ------------------------------------------------------------------
    # Step 2 & simulation loop
    # ------------------------------------------------------------------
    trajectory = [velocity]

    for i in range(n_steps):
        velocity, pressure = step(velocity, pressure, dt, nu)
        trajectory.append(velocity)
        print(f"Step {i + 1}/{n_steps} completed.")

    # ------------------------------------------------------------------
    # Convert trajectory (StaggeredGrid list) -> numpy array
    # Shape required: [time_step+1, Nx, Ny, 2]
    # ------------------------------------------------------------------
    data = np.stack([
        v.at_centers().values.numpy(('x', 'y', 'vector')) for v in trajectory
    ])

    print("Final trajectory array shape:", data.shape)

    np.save('lid_driven_cavity_velocity_trj.npy', data)
    print("Saved trajectory to 'lid_driven_cavity_velocity_trj.npy'")


if __name__ == '__main__':
    main()
```

**Notes on the implementation:**

1. **Grid & Boundary Conditions:** A `StaggeredGrid` is used to represent the velocity field, which is the standard MAC-grid discretization in PhiFlow, ensuring a stable pressure-velocity coupling. The boundary condition is enforced through `extrapolation.combine_sides`, which allows independent extrapolation values for each domain face — zero velocity on the left, right, and bottom walls, and a constant `(1, 0)` velocity on the top (lid).

2. **Step Function:** The `step()` function implements the incompressible Navier–Stokes update in three stages:
   - **Advection** using semi-Lagrangian backtracing (`advect.semi_lagrangian`)
   - **Diffusion** solved explicitly (`diffuse.explicit`) using the kinematic viscosity `nu`
   - **Incompressibility (pressure projection)** enforced through a conjugate-gradient (CG) linear solve (`fluid.make_incompressible`), ensuring `div(u) = 0`.

3. **Trajectory Storage:** At every time step, the velocity field (originally a staggered representation) is converted to cell-centered format via `.at_centers()` before being stored as a NumPy array. This produces the required `[Nx, Ny, 2]` shape per snapshot, and stacking 101 snapshots (`n_steps + 1`) gives the final array of shape `[101, 50, 32, 2]`.

4. **Output:** The final trajectory is saved to `lid_driven_cavity_velocity_trj.npy`.