from phi.flow import *
import numpy as np

Lx, Ly = 40., 20.
Nx, Ny = 64, 64
nu = 0.1
dt = 0.5
steps = 100

domain = Box(x=Lx, y=Ly)

def initial_field(x):
    gauss = math.exp(-(x['x'] - Lx / 2) ** 2 - (x['y'] - Ly / 2) ** 2)
    return vec(x=gauss, y=gauss)

velocity = CenteredGrid(initial_field, extrapolation.PERIODIC, bounds=domain, resolution=spatial(x=Nx, y=Ny))

def step(velocity, dt):
    diffusion_term = diffuse.differential(velocity, nu)
    advection_term = advect.differential(velocity, velocity, order=2)
    return velocity + dt * (diffusion_term + advection_term)

trajectory = [velocity.values.numpy(('x', 'y', 'vector'))]

for i in range(steps):
    velocity = step(velocity, dt)
    trajectory.append(velocity.values.numpy(('x', 'y', 'vector')))

trajectory = np.stack(trajectory, axis=0)
np.save('burgers2d_velocity_trj.npy', trajectory)