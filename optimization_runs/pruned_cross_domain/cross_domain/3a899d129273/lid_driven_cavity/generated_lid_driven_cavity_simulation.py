from phi.flow import *
from phi.flow import fluid, diffuse, advect
import numpy as np

Nx = 50
Ny = 32
nu = 0.1
dt = 1.0
steps = 100

boundary = extrapolation.combine_sides(
    x=extrapolation.ZERO,
    y=(extrapolation.ZERO, extrapolation.combine_by_direction(normal=extrapolation.ZERO, tangential=vec(x=1, y=0)))
)

velocity = StaggeredGrid(0, boundary, x=Nx, y=Ny, bounds=Box(x=Nx, y=Ny))

def step(velocity, dt):
    velocity = advect.mac_cormack(velocity, velocity, dt)
    velocity = diffuse.explicit(velocity, nu, dt)
    velocity, pressure = fluid.make_incompressible(velocity)
    return velocity

trajectory = []
centered_velocity = CenteredGrid(velocity, extrapolation.ZERO, x=Nx, y=Ny, bounds=Box(x=Nx, y=Ny))
trajectory.append(centered_velocity.values.numpy(['x', 'y', 'vector']))

for i in range(steps):
    velocity = step(velocity, dt)
    centered_velocity = CenteredGrid(velocity, extrapolation.ZERO, x=Nx, y=Ny, bounds=Box(x=Nx, y=Ny))
    trajectory.append(centered_velocity.values.numpy(['x', 'y', 'vector']))

velocity_trj = np.stack(trajectory, axis=0)
np.save('lid_driven_cavity_velocity_trj.npy', velocity_trj)