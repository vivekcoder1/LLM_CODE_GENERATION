from phi.flow import *
import numpy as np

domain = Box(x=200, y=100, z=5)
resolution = spatial(x=128, y=64, z=8)

boundary = extrapolation.combine_sides(
    x=(extrapolation.ConstantExtrapolation(vec(x=2, y=0, z=0)), extrapolation.ZERO_GRADIENT),
    y=extrapolation.PERIODIC,
    z=extrapolation.PERIODIC
)

velocity = StaggeredGrid(vec(x=8, y=0, z=0), boundary, bounds=domain, resolution=resolution)

obstacle_geometry = cylinder(center=vec(x=20, y=50, z=2.5), radius=10, depth=5, axis='z')
obstacle = Obstacle(obstacle_geometry)

def step(v, dt=1.0):
    v = advect.mac_cormack(v, v, dt)
    v = apply_boundary_conditions(v, [obstacle])
    v, _ = make_incompressible(v, obstacles=[obstacle])
    return v

trajectory = []
centered = CenteredGrid(velocity, resolution=resolution, bounds=domain)
trajectory.append(centered.values.numpy(['x', 'y', 'z', 'vector']))

for i in range(400):
    velocity = step(velocity)
    centered = CenteredGrid(velocity, resolution=resolution, bounds=domain)
    trajectory.append(centered.values.numpy(['x', 'y', 'z', 'vector']))

trajectory = np.stack(trajectory, axis=0)
np.save('wake_flow_velocity_trj.npy', trajectory)