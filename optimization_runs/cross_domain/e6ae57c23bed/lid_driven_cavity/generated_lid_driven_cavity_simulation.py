from phi.flow import *
from phi.flow import fluid, diffuse, advect, extrapolation
import numpy as np

Nx = 50
Ny = 32
nu = 0.1
dt = 1.0
steps = 100

domain_bounds = Box(x=Nx, y=Ny)
top_velocity = vec(x=1.0, y=0.0)

boundary = extrapolation.combine_sides(
    x=extrapolation.ZERO,
    y=(extrapolation.ZERO, extrapolation.ConstantExtrapolation(top_velocity))
)

velocity = StaggeredGrid(0, boundary, x=Nx, y=Ny, bounds=domain_bounds)


def step(velocity, dt=dt, nu=nu):
    convection = advect.differential(velocity, velocity, order=2)
    diffusion = diffuse.differential(velocity, nu)
    velocity = velocity + dt * (convection + diffusion)
    velocity, pressure = fluid.make_incompressible(velocity, obstacles=())
    return velocity


trajectory = [velocity]
for i in range(steps):
    velocity = step(velocity)
    trajectory.append(velocity)

frames = []
for v in trajectory:
    centered = CenteredGrid(v, 0, resolution=spatial(x=Nx, y=Ny), bounds=domain_bounds)
    arr = centered.values.numpy(('x', 'y', 'vector'))
    frames.append(arr)

velocity_trj = np.stack(frames, axis=0)
np.save('lid_driven_cavity_velocity_trj.npy', velocity_trj)