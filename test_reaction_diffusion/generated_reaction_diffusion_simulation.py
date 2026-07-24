```python
"""
Gray-Scott Reaction-Diffusion Simulation using PhiFlow
=======================================================

Governing equations:
    ∂u/∂t = D_u * ∇²u - u*v² + f*(1-u)
    ∂v/∂t = D_v * ∇²v + u*v² - (f+k)*v

Initial condition:
    u(x,y,0) = v(x,y,0) = cos(r / s),   r = sqrt((x - Lx/2)^2 + (y - Ly/2)^2)

The simulation is run for 100 explicit Euler time steps and the full
trajectories (including the initial state) of `u` and `v` are stored as
NumPy arrays of shape [time_step+1, Nx, Ny].
"""

from phi.flow import *
import numpy as np


# --------------------------------------------------------------------------
# Step 1: Define the computational grid, domain and boundary conditions
# --------------------------------------------------------------------------

# Domain size and resolution
Lx, Ly = 100., 100.
Nx, Ny = 100, 100

# Time step
dt = 0.5

# Diffusion coefficients
Du = 0.19
Dv = 0.05

# Reaction parameters (feed rate f, kill rate k)
feed = 0.06
kill = 0.062

# Width parameter for the initial cosine profile
s = 3.0

# Physical domain: Omega = [0, Lx] x [0, Ly]
bounds = Box(x=Lx, y=Ly)


def initial_field(x):
    """
    Initial condition:
        u_{i,j}(0) = v_{i,j}(0) = cos(r_{i,j} / s)
        r_{i,j}    = sqrt((x_i - Lx/2)^2 + (y_j - Ly/2)^2)
    """
    center = math.tensor([Lx / 2, Ly / 2], channel(vector='x,y'))
    r = math.vec_length(x - center)
    return math.cos(r / s)


# Create the centered grids for u and v with periodic boundary conditions
u = CenteredGrid(initial_field, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=bounds)
v = CenteredGrid(initial_field, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=bounds)


# --------------------------------------------------------------------------
# Step 2: Define the step function using the governing (reaction-diffusion)
#         equations, integrated with explicit Euler time stepping.
# --------------------------------------------------------------------------

def reaction_diffusion_step(u: CenteredGrid, v: CenteredGrid, dt: float):
    """
    Advance the Gray-Scott reaction-diffusion system by one explicit
    Euler time step.

    ∂u/∂t = D_u * ∇²u - u*v² + f*(1-u)
    ∂v/∂t = D_v * ∇²v + u*v² - (f+k)*v

    Args:
        u: Current `u` field (CenteredGrid).
        v: Current `v` field (CenteredGrid).
        dt: Time step size.

    Returns:
        Tuple of updated (u, v) fields.
    """
    lap_u = field.laplace(u)
    lap_v = field.laplace(v)

    reaction = u * v * v  # u*v^2 term shared by both equations

    du_dt = Du * lap_u - reaction + feed * (1 - u)
    dv_dt = Dv * lap_v + reaction - (feed + kill) * v

    u_next = u + dt * du_dt
    v_next = v + dt * dv_dt

    return u_next, v_next


# --------------------------------------------------------------------------
# Run the simulation for 100 time steps
# --------------------------------------------------------------------------

n_steps = 100

# Store the initial state as the first snapshot
u_trj = [u.values.numpy(('x', 'y'))]
v_trj = [v.values.numpy(('x', 'y'))]

for step_i in range(n_steps):
    u, v = reaction_diffusion_step(u, v, dt)
    u_trj.append(u.values.numpy(('x', 'y')))
    v_trj.append(v.values.numpy(('x', 'y')))

# Stack snapshots along the time axis -> shape [n_steps+1, Nx, Ny]
u_trj = np.stack(u_trj, axis=0)
v_trj = np.stack(v_trj, axis=0)

# --------------------------------------------------------------------------
# Save results
# --------------------------------------------------------------------------

np.save('reaction_diffusion_u_trj.npy', u_trj)
np.save('reaction_diffusion_v_trj.npy', v_trj)

print(f"Saved u_trj with shape {u_trj.shape} to 'reaction_diffusion_u_trj.npy'")
print(f"Saved v_trj with shape {v_trj.shape} to 'reaction_diffusion_v_trj.npy'")
```