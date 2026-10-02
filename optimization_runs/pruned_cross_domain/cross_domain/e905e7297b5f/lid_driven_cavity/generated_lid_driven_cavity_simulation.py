from phi.flow import *
import numpy as np

N_x = 50
N_y = 32
nu = 0.1
dt = 1.0
steps = 100

bounds = Box(x=N_x, y=N_y)

boundary = extrapolation.combine_sides(
    x=extrapolation.ZERO,
    y=(extrapolation.ZERO, extrapolation.ConstantExtrapolation(vec(x=1, y=0)))
)

velocity = StaggeredGrid(0, boundary, x=N_x, y=N_y, bounds=bounds)


def step(velocity, dt, nu):
    velocity = advect.mac_cormack(velocity, velocity, dt)
    velocity = diffuse.explicit(velocity, nu, dt)
    velocity, pressure = fluid.make_incompressible(velocity, obstacles=())
    return velocity


trajectory = []

centered = CenteredGrid(velocity, resolution=spatial(x=N_x, y=N_y), bounds=bounds)
trajectory.append(centered.values.numpy(order=['x', 'y', 'vector']))

for i in range(steps):
    velocity = step(velocity, dt, nu)
    centered = CenteredGrid(velocity, resolution=spatial(x=N_x, y=N_y), bounds=bounds)
    trajectory.append(centered.values.numpy(order=['x', 'y', 'vector']))

velocity_trj = np.stack(trajectory, axis=0)
np.save('lid_driven_cavity_velocity_trj.npy', velocity_trj)