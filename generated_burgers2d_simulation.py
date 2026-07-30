"""
2D Burgers Equation Simulation using PhiFlow
=============================================

Governing equations:
    du/dt + u*du/dx + v*du/dy = nu*(d2u/dx2 + d2u/dy2)
    dv/dt + u*dv/dx + v*dv/dy = nu*(d2v/dx2 + d2v/dy2)

Domain:      Omega = [0, Lx] x [0, Ly],  Lx=40, Ly=20
Resolution:  Nx = Ny = 64
BC:          Periodic in both x and y
IC:          u(x,y,0) = v(x,y,0) = exp(-((x-Lx/2)^2 + (y-Ly/2)^2))
nu:          0.1
dt:          0.5
Steps:       100  (=> 101 snapshots including t=0)

Output:      burgers2d_velocity_trj.npy  with shape [101, 64, 64, 2]
"""

from phi.flow import *
import numpy as np

# ----------------------------------------------------------------------
# Simulation / domain parameters
# ----------------------------------------------------------------------
Lx, Ly = 40., 20.          # physical domain size
Nx, Ny = 64, 64            # grid resolution
nu = 0.1                   # diffusivity
dt = 0.5                   # time step size
num_steps = 100            # number of time steps to simulate

domain_bounds = Box(x=Lx, y=Ly)


# ----------------------------------------------------------------------
# Initial condition: Gaussian bump centered at (Lx/2, Ly/2)
# Both velocity components (u, v) are initialized with the same profile.
# ----------------------------------------------------------------------
def gaussian_bump(x):
    x_coord = x.vector['x']
    y_coord = x.vector['y']
    return math.exp(-((x_coord - Lx / 2) ** 2 + (y_coord - Ly / 2) ** 2))


velocity = CenteredGrid(
    lambda x: vec(x=gaussian_bump(x), y=gaussian_bump(x)),
    extrapolation=extrapolation.PERIODIC,
    x=Nx, y=Ny,
    bounds=domain_bounds
)


# ----------------------------------------------------------------------
# Step function implementing the 2D Burgers equation:
#   - Nonlinear advection (self-advection of the velocity field)
#   - Explicit diffusion with diffusivity nu
# ----------------------------------------------------------------------
def burgers_step(v: CenteredGrid, dt: float, nu: float) -> CenteredGrid:
    v = advect.semi_lagrangian(v, v, dt)      # advection term: u*du/dx + v*du/dy (and for v-component)
    v = diffuse.explicit(v, nu, dt)           # diffusion term: nu*(d2/dx2 + d2/dy2)
    return v


# ----------------------------------------------------------------------
# Run the simulation and collect the trajectory
# ----------------------------------------------------------------------
velocity_trj = [velocity.values.numpy(('x', 'y', 'vector'))]

for step_i in range(num_steps):
    velocity = burgers_step(velocity, dt, nu)
    velocity_trj.append(velocity.values.numpy(('x', 'y', 'vector')))
    print(f"Step {step_i + 1}/{num_steps} completed.")

velocity_trj = np.stack(velocity_trj, axis=0)  # shape: [num_steps+1, Nx, Ny, 2]
print("Final velocity_trj shape:", velocity_trj.shape)

# ----------------------------------------------------------------------
# Save trajectory to disk
# ----------------------------------------------------------------------
np.save('burgers2d_velocity_trj.npy', velocity_trj)
print("Saved trajectory to 'burgers2d_velocity_trj.npy'")
