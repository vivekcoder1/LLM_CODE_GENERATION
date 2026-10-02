from phi.flow import *
from phi.flow import diffuse, advect
import numpy as np

nu = 0.1
dt = 0.5
Lx, Ly = 40., 20.
Nx, Ny = 64, 64

def initial_velocity(x):
    gauss = math.exp(-(x['x'] - Lx / 2) ** 2 - (x['y'] - Ly / 2) ** 2)
    return vec(x=gauss, y=gauss)

velocity = CenteredGrid(initial_velocity, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=Box(x=Lx, y=Ly))

def step(v):
    diffusion = diffuse.differential(v, diffusivity=nu)
    advection = advect.differential(v, v)
    return v + dt * (diffusion + advection)

trajectory = [velocity.values.numpy(['x', 'y', 'vector'])]

for i in range(100):
    velocity = step(velocity)
    trajectory.append(velocity.values.numpy(['x', 'y', 'vector']))

trajectory = np.stack(trajectory, axis=0)
np.save('burgers2d_velocity_trj.npy', trajectory)