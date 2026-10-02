from phi.flow import *
import numpy as np

Lx, Ly = 40., 20.
Nx, Ny = 64, 64
nu = 0.1
dt = 0.5
steps = 100

def initial_velocity(x):
    x_loc = x['x']
    y_loc = x['y']
    val = math.exp(-(x_loc - Lx / 2) ** 2 - (y_loc - Ly / 2) ** 2)
    return vec(x=val, y=val)

velocity = CenteredGrid(initial_velocity, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=Box(x=Lx, y=Ly))

def step(v):
    convection = advect.differential(v, v, order=2)
    diffusion = diffuse.differential(v, nu)
    return v + dt * (convection + diffusion)

trajectory = [velocity.values.numpy(('x', 'y', 'vector'))]

for _ in range(steps):
    velocity = step(velocity)
    trajectory.append(velocity.values.numpy(('x', 'y', 'vector')))

velocity_trj = np.stack(trajectory, axis=0)
np.save('burgers2d_velocity_trj.npy', velocity_trj)