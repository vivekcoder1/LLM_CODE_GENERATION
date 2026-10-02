from phi.flow import *
from phi.flow import fluid, diffuse, advect
import numpy as np

Nx = 50
Ny = 32
nu = 0.1
dt = 1.0
steps = 100

DOMAIN = dict(x=Nx, y=Ny, bounds=Box(x=Nx, y=Ny))

boundary = extrapolation.combine_sides(
    x=extrapolation.ZERO,
    y=(extrapolation.ZERO, extrapolation.ConstantExtrapolation(vec(x=1, y=0)))
)

velocity = StaggeredGrid(0, boundary, **DOMAIN)
pressure = None

def step(velocity, pressure, dt, nu):
    velocity = advect.mac_cormack(velocity, velocity, dt=dt)
    velocity = diffuse.explicit(velocity, nu, dt=dt)
    velocity, pressure = fluid.make_incompressible(velocity, (), Solve('CG', 1e-5, 1e-5, x0=pressure))
    return velocity, pressure

velocity_trj = []
centered = CenteredGrid(velocity, resolution=spatial(x=Nx, y=Ny), bounds=Box(x=Nx, y=Ny))
velocity_trj.append(centered.values.numpy(['x', 'y', 'vector']))

for i in range(steps):
    velocity, pressure = step(velocity, pressure, dt, nu)
    centered = CenteredGrid(velocity, resolution=spatial(x=Nx, y=Ny), bounds=Box(x=Nx, y=Ny))
    velocity_trj.append(centered.values.numpy(['x', 'y', 'vector']))

velocity_trj = np.stack(velocity_trj, axis=0)
np.save('lid_driven_cavity_velocity_trj.npy', velocity_trj)