from phi.flow import *
import numpy as np

Lx = 40.
Ly = 20.
Nx = 64
Ny = 64
nu = 0.1
dt = 0.5
steps = 100

domain = UniformGrid(x=Nx, y=Ny, bounds=Box(x=Lx, y=Ly))

def init_u(x, y):
    return math.exp(-(x - Lx / 2) ** 2 - (y - Ly / 2) ** 2)

velocity = Field(domain, values=lambda x, y: vec(x=init_u(x, y), y=init_u(x, y)), boundary=PERIODIC)

velocity_trj = [velocity.values.numpy(['x', 'y', 'vector'])]

for i in range(steps):
    diffusion_term = diffuse.differential(velocity, nu)
    advection_term = advect.differential(velocity, velocity, order=2)
    velocity = velocity + dt * (advection_term + diffusion_term)
    velocity_trj.append(velocity.values.numpy(['x', 'y', 'vector']))

velocity_trj = np.stack(velocity_trj, axis=0)
np.save('burgers2d_velocity_trj.npy', velocity_trj)