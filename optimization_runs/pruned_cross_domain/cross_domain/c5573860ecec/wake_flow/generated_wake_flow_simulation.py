from phi.flow import *
import numpy as np

domain = Box(x=200, y=100, z=5)
resolution = spatial(x=128, y=64, z=8)

boundary = extrapolation.combine_sides(
    x=(extrapolation.ConstantExtrapolation(vec(x=2, y=0, z=0)), extrapolation.BOUNDARY),
    y=extrapolation.PERIODIC,
    z=extrapolation.PERIODIC
)

velocity = StaggeredGrid(vec(x=8, y=0, z=0), boundary, bounds=domain, resolution=resolution)

obstacle_geometry = cylinder(center=vec(x=20, y=50, z=2.5), radius=10, depth=5, axis='z')
obstacle = Obstacle(obstacle_geometry)

def step(velocity, dt=1.0):
    velocity = advect.mac_cormack(velocity, velocity, dt=dt)
    velocity = fluid.apply_boundary_conditions(velocity, obstacles=[obstacle])
    velocity, pressure = fluid.make_incompressible(velocity, obstacles=[obstacle])
    return velocity

def to_numpy(velocity):
    centered = velocity.at_centers()
    return centered.values.numpy(['x', 'y', 'z', 'vector'])

trajectory = [to_numpy(velocity)]

for i in range(400):
    velocity = step(velocity)
    trajectory.append(to_numpy(velocity))

trajectory = np.stack(trajectory, axis=0)
np.save('wake_flow_velocity_trj.npy', trajectory)