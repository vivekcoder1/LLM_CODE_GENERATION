from phi.flow import *
from phi.flow import fluid, advect, extrapolation
import numpy as np

domain_bounds = Box(x=200, y=100, z=5)
res = spatial(x=128, y=64, z=8)

inflow_velocity = vec(x=2, y=0, z=0)
boundary = extrapolation.combine_sides(
    x=(extrapolation.ConstantExtrapolation(inflow_velocity), extrapolation.BOUNDARY),
    y=extrapolation.PERIODIC,
    z=extrapolation.PERIODIC
)

velocity = StaggeredGrid(vec(x=8, y=0, z=0), boundary=boundary, bounds=domain_bounds, resolution=res)

obstacle_geometry = Cylinder(center=vec(x=20, y=50, z=2.5), radius=10, depth=5, axis='z')
obstacle = Obstacle(obstacle_geometry)

pressure = None
dt = 0.1

trajectory = []

centered_velocity = CenteredGrid(velocity, extrapolation=boundary, bounds=domain_bounds, resolution=res)
trajectory.append(centered_velocity.numpy('x,y,z,vector'))

for step_idx in range(400):
    velocity = advect.mac_cormack(velocity, velocity, dt)
    velocity = fluid.apply_boundary_conditions(velocity, obstacle)
    velocity, pressure = fluid.make_incompressible(velocity, obstacles=[obstacle], solve=Solve('CG', 1e-5, 1e-5))
    centered_velocity = CenteredGrid(velocity, extrapolation=boundary, bounds=domain_bounds, resolution=res)
    trajectory.append(centered_velocity.numpy('x,y,z,vector'))

trajectory = np.stack(trajectory, axis=0)
np.save('wake_flow_velocity_trj.npy', trajectory)