from phi.flow import *
import numpy as np

Lx, Ly = 40., 20.
Nx, Ny = 64, 64
nu = 0.1
dt = 0.5
steps = 100

domain = UniformGrid(x=Nx, y=Ny, bounds=Box(x=Lx, y=Ly))

def initial(x, y):
    r = math.exp(-(x - Lx / 2) ** 2 - (y - Ly / 2) ** 2)
    return vec(x=r, y=r)

velocity = Field(domain, values=initial, boundary=PERIODIC)

def step(v, dt):
    return v + dt * (advect.differential(v, v) + diffuse.differential(v, nu))

trajectory = [velocity.values.numpy(['x', 'y', 'vector'])]

for i in range(steps):
    velocity = step(velocity, dt)
    trajectory.append(velocity.values.numpy(['x', 'y', 'vector']))

trajectory = np.stack(trajectory, axis=0)
np.save('burgers2d_velocity_trj.npy', trajectory)