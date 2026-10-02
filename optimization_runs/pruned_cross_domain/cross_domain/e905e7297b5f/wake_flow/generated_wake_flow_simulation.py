from phi.flow import *
import numpy as np

domain_bounds = Box(x=200, y=100, z=5)
resolution = spatial(x=128, y=64, z=8)

inflow_value = vec(x=2, y=0, z=0)
boundary = extrapolation.combine_sides(
    x=(extrapolation.ConstantExtrapolation(inflow_value), extrapolation.BOUNDARY),
    y=extrapolation.PERIODIC,
    z=extrapolation.PERIODIC
)

velocity = StaggeredGrid(vec(x=8, y=0, z=0), boundary, bounds=domain_bounds, resolution=resolution)

obstacle_geometry = cylinder(x=20, y=50, z=2.5, radius=10, axis='z')
obstacles = [Obstacle(obstacle_geometry)]

pressure_solve = Solve('CG', 1e-5, 1e-5)

dt = 1.0

def step(v):
    v = advect.mac_cormack(v, v, dt)
    v = apply_boundary_conditions(v, obstacles)
    v, p = make_incompressible(v, obstacles=obstacles, solve=pressure_solve)
    return v

def to_numpy(v):
    centered = CenteredGrid(v, boundary, bounds=domain_bounds, resolution=resolution)
    return centered.values.numpy('x,y,z,vector')

trajectory = [to_numpy(velocity)]

for i in range(400):
    velocity = step(velocity)
    trajectory.append(to_numpy(velocity))

trajectory = np.stack(trajectory, axis=0)
np.save('wake_flow_velocity_trj.npy', trajectory)