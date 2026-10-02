import numpy as np
from phi.flow import *

Lx = 40.0
Ly = 20.0
Nx = 64
Ny = 64
nu = 0.1
dt = 0.5
num_steps = 100

domain_bounds = Box(x=Lx, y=Ly)

def initial_velocity(x):
    x0 = x['x']
    y0 = x['y']
    val = math.exp(-((x0 - Lx / 2) ** 2 + (y0 - Ly / 2) ** 2))
    return vec(x=val, y=val)

velocity = CenteredGrid(initial_velocity, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=domain_bounds)

def step(v):
    convection = advect.differential(v, v, order=2)
    diffusion = diffuse.differential(v, nu)
    return v + dt * (convection + diffusion)

trajectory = [velocity.numpy(('x', 'y', 'vector'))]

for _ in range(num_steps):
    velocity = step(velocity)
    trajectory.append(velocity.numpy(('x', 'y', 'vector')))

velocity_trj = np.stack(trajectory, axis=0)
np.save('burgers2d_velocity_trj.npy', velocity_trj)