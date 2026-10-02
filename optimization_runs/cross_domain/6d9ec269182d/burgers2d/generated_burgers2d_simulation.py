from phi.flow import *
import numpy as np

Lx = 40.
Ly = 20.
Nx = 64
Ny = 64
nu = 0.1
dt = 0.5
steps = 100

domain = Box(x=Lx, y=Ly)
grid = UniformGrid(x=Nx, y=Ny, bounds=domain)
pos = grid.center
x = pos['x']
y = pos['y']
init_val = math.exp(-(x - Lx / 2) ** 2 - (y - Ly / 2) ** 2)
init_vec = vec(x=init_val, y=init_val)

velocity = Field(grid, values=init_vec, boundary=extrapolation.PERIODIC)

velocity_trj = [velocity.values.numpy(['x', 'y', 'vector'])]

def step(velocity, dt):
    advection_term = advect.differential(velocity, velocity, order=2)
    velocity = velocity + dt * advection_term
    velocity = diffuse.explicit(velocity, nu, dt)
    return velocity

for i in range(steps):
    velocity = step(velocity, dt)
    velocity_trj.append(velocity.values.numpy(['x', 'y', 'vector']))

velocity_trj = np.stack(velocity_trj, axis=0)
np.save('burgers2d_velocity_trj.npy', velocity_trj)