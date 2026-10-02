import numpy as np
from phi.flow import *
from phi.flow import fluid, diffuse, advect

Nx = 50
Ny = 32
nu = 0.1
dt = 1.0
steps = 100

velocity = StaggeredGrid(vec(x=0, y=0), boundary={'x': 0, 'y': (0, vec(x=1, y=0))}, bounds=Box(x=Nx, y=Ny), x=Nx, y=Ny)

def step(v, dt, nu):
    v = advect.semi_lagrangian(v, v, dt)
    v = diffuse.explicit(v, nu, dt)
    v, p = fluid.make_incompressible(v)
    return v

trj = []
centered = CenteredGrid(velocity, resolution=velocity.resolution, bounds=velocity.bounds)
trj.append(centered.values.numpy(['x', 'y', 'vector']))

for i in range(steps):
    velocity = step(velocity, dt, nu)
    centered = CenteredGrid(velocity, resolution=velocity.resolution, bounds=velocity.bounds)
    trj.append(centered.values.numpy(['x', 'y', 'vector']))

trj = np.stack(trj, axis=0)
np.save('lid_driven_cavity_velocity_trj.npy', trj)