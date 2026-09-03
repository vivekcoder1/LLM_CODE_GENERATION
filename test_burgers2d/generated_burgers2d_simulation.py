from phi.flow import *
import numpy as np

Nx = Ny = 64
Lx, Ly = 40.0, 20.0
nu = 0.1
dt = 0.5
n_steps = 100

domain = Box(x=Lx, y=Ly)

def initial_velocity(x, y):
    val = math.exp(-(x - Lx / 2) ** 2 - (y - Ly / 2) ** 2)
    return vec(x=val, y=val)

velocity = CenteredGrid(initial_velocity, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=domain)

def step(velocity, dt):
    advection = advect.differential(velocity, velocity, order=2)
    diffusion = diffuse.differential(velocity, nu, order=2)
    return velocity + dt * (advection + diffusion)

trajectory = [velocity.values.numpy(('x', 'y', 'vector'))]

for _ in range(n_steps):
    velocity = step(velocity, dt)
    trajectory.append(velocity.values.numpy(('x', 'y', 'vector')))

velocity_trj = np.stack(trajectory, axis=0)
np.save('burgers2d_velocity_trj.npy', velocity_trj)