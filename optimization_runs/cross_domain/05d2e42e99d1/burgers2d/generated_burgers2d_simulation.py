from phi.flow import *
import numpy as np

Lx, Ly = 40., 20.
Nx, Ny = 64, 64
nu = 0.1
dt = 0.5
steps = 100

domain = Box(x=Lx, y=Ly)
resolution = spatial(x=Nx, y=Ny)

def initial_velocity(x):
    gauss = math.exp(-((x['x'] - Lx / 2) ** 2 + (x['y'] - Ly / 2) ** 2))
    return vec(x=gauss, y=gauss)

velocity = CenteredGrid(initial_velocity, extrapolation.PERIODIC, bounds=domain, resolution=resolution)

def step(velocity, dt):
    velocity = advect.semi_lagrangian(velocity, velocity, dt)
    velocity = diffuse.explicit(velocity, nu, dt)
    return velocity

trajectory = [velocity.values.numpy(['x', 'y', 'vector'])]

for i in range(steps):
    velocity = step(velocity, dt)
    trajectory.append(velocity.values.numpy(['x', 'y', 'vector']))

trajectory = np.stack(trajectory, axis=0)
np.save('burgers2d_velocity_trj.npy', trajectory)