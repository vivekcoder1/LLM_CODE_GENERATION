from phi.flow import *
from phi.flow import fluid, advect, diffuse
import numpy as np

nx, ny = 50, 32
dt = 1.0
nu = 0.1
steps = 100

boundary = extrapolation.combine_sides(
    x=extrapolation.ZERO,
    y=(extrapolation.ZERO, extrapolation.ConstantExtrapolation(vec(x=1.0, y=0.0)))
)

velocity = StaggeredGrid(0, boundary, x=nx, y=ny, bounds=Box(x=nx, y=ny))


def step(velocity, dt=dt, nu=nu):
    advection_term = advect.differential(velocity, velocity, order=2)
    diffusion_term = diffuse.differential(velocity, nu)
    velocity = velocity + dt * (advection_term + diffusion_term)
    velocity, pressure = fluid.make_incompressible(velocity)
    return velocity


velocity_trj = []
centered = CenteredGrid(velocity, extrapolation=velocity.extrapolation, bounds=velocity.bounds, resolution=velocity.resolution)
velocity_trj.append(centered.values.numpy(['x', 'y', 'vector']))

for i in range(steps):
    velocity = step(velocity)
    centered = CenteredGrid(velocity, extrapolation=velocity.extrapolation, bounds=velocity.bounds, resolution=velocity.resolution)
    velocity_trj.append(centered.values.numpy(['x', 'y', 'vector']))

velocity_trj = np.stack(velocity_trj, axis=0)
np.save('lid_driven_cavity_velocity_trj.npy', velocity_trj)