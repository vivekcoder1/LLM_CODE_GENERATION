from phi.flow import *
from phi.flow import advect, diffuse, fluid
import numpy as np

Lx = 40.0
Ly = 20.0
Nx = 64
Ny = 64
nu = 0.1
dt = 0.5
num_steps = 100

domain = Box(x=Lx, y=Ly)
grid = UniformGrid(x=Nx, y=Ny, bounds=domain)

def init_velocity(x, y):
    u0 = math.exp(-(x - Lx / 2) ** 2 - (y - Ly / 2) ** 2)
    return vec(x=u0, y=u0)

velocity = Field(grid, values=init_velocity, boundary=extrapolation.PERIODIC)

def step(velocity, dt):
    diffusion_term = diffuse.differential(velocity, nu)
    advection_term = advect.differential(velocity, velocity)
    return velocity + dt * (diffusion_term + advection_term)

trajectory = [velocity.values.numpy(('x', 'y', 'vector'))]

for _ in range(num_steps):
    velocity = step(velocity, dt)
    trajectory.append(velocity.values.numpy(('x', 'y', 'vector')))

velocity_trj = np.stack(trajectory, axis=0)
np.save('burgers2d_trj.npy', velocity_trj)