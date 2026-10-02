from phi.flow import *
import numpy as np

domain = Box(x=200, y=100, z=5)

inflow_extrap = extrapolation.ConstantExtrapolation(vec(x=2, y=0, z=0))
velocity_extrapolation = extrapolation.combine_sides(
    x=(inflow_extrap, extrapolation.BOUNDARY),
    y=extrapolation.PERIODIC,
    z=extrapolation.PERIODIC
)

velocity = StaggeredGrid(vec(x=8, y=0, z=0), velocity_extrapolation, x=128, y=64, z=8, bounds=domain)

obstacle_geometry = cylinder(center=vec(x=20, y=50, z=2.5), radius=10, depth=5, axis='z')
obstacle = Obstacle(obstacle_geometry)

pressure = None
dt = 0.05

trajectory = []

centered_velocity = CenteredGrid(velocity, velocity_extrapolation, x=128, y=64, z=8, bounds=domain)
trajectory.append(centered_velocity.values.numpy(('x', 'y', 'z', 'vector')))

for i in range(400):
    velocity = advect.mac_cormack(velocity, velocity, dt=dt)
    velocity = apply_boundary_conditions(velocity, obstacles=[obstacle])
    velocity, pressure = fluid.make_incompressible(velocity, obstacles=[obstacle], solve=Solve('CG', 1e-5, 1e-5, x0=pressure))
    centered_velocity = CenteredGrid(velocity, velocity_extrapolation, x=128, y=64, z=8, bounds=domain)
    trajectory.append(centered_velocity.values.numpy(('x', 'y', 'z', 'vector')))

velocity_trj = np.stack(trajectory, axis=0)
np.save('wake_flow_velocity_trj.npy', velocity_trj)