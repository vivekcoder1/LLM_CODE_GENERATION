```python
"""
Julia Set Simulation using PhiFlow
------------------------------------------------------------------
Domain:      Omega = { x + i*y | x in [-2, 2], y in [-2, 2] }
Resolution:  Nx = Ny = 256
Initial condition:  z(x, y, 0) = x + i*y
Governing map:       f_theta(z) = z^2 + c(t)
                      c(t) = 0.7885 * exp(i * 2*pi*t / 100),  t = 0, ..., 99
Escape criterion:    |z| < 2   ->  accumulate into Julia-set field J
Output:              domain_trj.npy of shape [time_step, N_x, N_y]
------------------------------------------------------------------
"""

from phi.flow import *
import numpy as np


# ------------------------------------------------------------------
# Step 1: Define the computational grid, domain and boundary condition
# ------------------------------------------------------------------
N_x = N_y = 256
N_escape = 50            # escape-radius related parameter (kept for reference,
                          # escape test itself uses |z| < 2 as specified)
N_steps = 100             # number of time steps t = 0, ..., 99

# Domain covering the complex plane region [-2, 2] x [-2, 2]
domain = Domain(
    x=N_x, y=N_y,
    boundaries=extrapolation.ZERO,
    bounds=Box(x=(-2, 2), y=(-2, 2))
)


def _initial_z(location):
    """
    Initial condition: z(x, y, 0) = x + i*y

    `location` is a Tensor with a `vector` dimension holding the
    physical (x, y) coordinates of each grid cell center.
    """
    x = location.vector['x']
    y = location.vector['y']
    return x + 1j * y


# Complex-valued grid representing z(x, y, t)
z = domain.grid(_initial_z)

# Real-valued grid representing the accumulated Julia set J(x, y, t)
J = domain.grid(0.)


# ------------------------------------------------------------------
# Step 2: Step function implementing the governing equations
# ------------------------------------------------------------------
def step(z, J, t):
    """
    Advances the Julia set simulation by one time step:

        z(x, y, t) <- z(x, y, t)^2 + c(t)
        J(x, y, t) <- J(x, y, t) + 1_{|z| < 2}

    Args:
        z: complex-valued CenteredGrid, current state of z
        J: real-valued CenteredGrid, accumulated escape-time field
        t: current (integer) time step, t in {0, ..., 99}

    Returns:
        (z, J): updated grids after applying the map and the escape test
    """
    c_t = 0.7885 * np.exp(1j * 2 * np.pi * t / 100.0)   # c(t)
    z = z ** 2 + c_t                                     # z <- z^2 + c(t)
    escaped_mask = abs(z) < 2                            # 1_{|z| < 2}
    J = J + escaped_mask                                 # accumulate Julia set
    return z, J


# ------------------------------------------------------------------
# Run the simulation for 100 time steps and collect the trajectory
# ------------------------------------------------------------------
domain_trj = []

for t in range(N_steps):
    z, J = step(z, J, t)
    # Store snapshot of the Julia-set accumulator field, ordered (x, y)
    domain_trj.append(J.values.numpy(('x', 'y')))

domain_trj = np.stack(domain_trj, axis=0)   # shape: [time_step, N_x, N_y]

# ------------------------------------------------------------------
# Save the trajectory to disk
# ------------------------------------------------------------------
np.save('julia_set_domain_trj.npy', domain_trj)

print("Simulation complete.")
print("domain_trj shape:", domain_trj.shape)
```