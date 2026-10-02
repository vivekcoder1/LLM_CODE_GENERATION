from phi.flow import *
import numpy as np

Nx, Ny = 50, 32
nu = 0.1
dt = 1.0
steps = 100

domain_bounds = Box(x=Nx, y=Ny)

boundary = extrapolation.combine_sides(
    x=extrapolation.ZERO,
    y=(extrapolation.ZERO, extrapolation.ConstantExtrapolation(vec(x=1, y=0)))
)

velocity = StaggeredGrid(0, boundary, x=Nx, y=Ny, bounds=domain_bounds)

def step(velocity, dt, nu):
    velocity = advect.mac_cormack(velocity, velocity, dt)
    velocity = diffuse.explicit(velocity, nu, dt)
    velocity, pressure = fluid.make_incompressible(velocity)
    return velocity

def to_centered(velocity):
    centered = CenteredGrid(velocity, boundary, x=Nx, y=Ny, bounds=domain_bounds)
    return centered.values.numpy(['x', 'y', 'vector'])

velocity_trj = [to_centered(velocity)]

for i in range(steps):
    velocity = step(velocity, dt, nu)
    velocity_trj.append(to_centered(velocity))

velocity_trj = np.stack(velocity_trj, axis=0)
np.save('lid_driven_cavity_velocity_trj.npy', velocity_trj)