from phi.flow import *
from phi.flow import fluid
import numpy as np

DOMAIN_BOUNDS = Box(x=200, y=100, z=5)
RESOLUTION = spatial(x=128, y=64, z=8)

INFLOW_VALUE = vec(x=2., y=0., z=0.)
BOUNDARY = extrapolation.combine_sides(
    x=(extrapolation.ConstantExtrapolation(INFLOW_VALUE), extrapolation.BOUNDARY),
    y=extrapolation.PERIODIC,
    z=extrapolation.PERIODIC
)

velocity = StaggeredGrid(vec(x=8., y=0., z=0.), BOUNDARY, bounds=DOMAIN_BOUNDS, resolution=RESOLUTION)

cyl = cylinder(center=vec(x=20, y=50, z=2.5), radius=10, depth=5, axis='z')
obstacle = Obstacle(cyl)

solve = Solve('CG', 1e-5, 1e-5, max_iterations=1000)

def step(v, dt=1.0):
    v = advect.mac_cormack(v, v, dt)
    v = fluid.apply_boundary_conditions(v, obstacles=[obstacle])
    v, _ = fluid.make_incompressible(v, obstacles=[obstacle], solve=solve)
    return v

def to_numpy(v):
    centered = CenteredGrid(v, extrapolation=v.extrapolation, bounds=v.bounds, resolution=v.resolution)
    return centered.values.numpy(['x', 'y', 'z', 'vector'])

trajectory = [to_numpy(velocity)]

for i in range(400):
    velocity = step(velocity)
    trajectory.append(to_numpy(velocity))

velocity_trj = np.stack(trajectory, axis=0)
np.save('wake_flow_velocity_trj.npy', velocity_trj)