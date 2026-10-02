from phi.flow import *
import numpy as np

Lx = 40.
Ly = 20.
Nx = 64
Ny = 64
nu = 0.1
dt = 0.5
n_steps = 100

domain = Box(x=Lx, y=Ly)
grid = UniformGrid(x=Nx, y=Ny, bounds=domain)

def init(x, y):
    val = math.exp(-(x - Lx / 2) ** 2 - (y - Ly / 2) ** 2)
    return vec(x=val, y=val)

velocity = Field(grid, values=init, boundary=PERIODIC)

def step(velocity, dt):
    diffusion = diffuse.differential(velocity, nu)
    advection = advect.differential(velocity, velocity)
    return velocity + dt * (advection + diffusion)

trajectory = [velocity.values.numpy(('x', 'y', 'vector'))]

for i in range(n_steps):
    velocity = step(velocity, dt)
    trajectory.append(velocity.values.numpy(('x', 'y', 'vector')))

velocity_trj = np.stack(trajectory, axis=0)
np.save('burgers2d_velocity_trj.npy', velocity_trj)