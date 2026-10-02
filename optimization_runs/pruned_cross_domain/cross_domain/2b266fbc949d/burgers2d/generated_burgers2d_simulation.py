from phi.flow import *
import numpy as np

Lx, Ly = 40.0, 20.0
Nx, Ny = 64, 64
nu = 0.1
dt = 0.5
steps = 100

domain = Box(x=Lx, y=Ly)
grid = UniformGrid(x=Nx, y=Ny, bounds=domain)

def initial_velocity(x, y):
    val = math.exp(-(x - Lx / 2) ** 2 - (y - Ly / 2) ** 2)
    return vec(x=val, y=val)

velocity = Field(grid, values=initial_velocity, boundary=PERIODIC)

velocity_trj = [velocity.values.numpy(('x', 'y', 'vector'))]

for _ in range(steps):
    velocity = velocity + dt * (advect.differential(velocity, velocity) + diffuse.differential(velocity, nu))
    velocity_trj.append(velocity.values.numpy(('x', 'y', 'vector')))

velocity_trj = np.stack(velocity_trj)
np.save('burgers2d_velocity_trj.npy', velocity_trj)