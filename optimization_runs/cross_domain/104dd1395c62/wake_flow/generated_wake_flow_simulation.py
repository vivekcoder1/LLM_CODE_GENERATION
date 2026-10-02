from phi.flow import *
import numpy as np

domain = Box(x=200, y=100, z=5)
resolution = spatial(x=128, y=64, z=8)

velocity_extrapolation = extrapolation.combine_sides(
    x=(extrapolation.ConstantExtrapolation(vec(x=2, y=0, z=0)), extrapolation.BOUNDARY),
    y=extrapolation.PERIODIC,
    z=extrapolation.PERIODIC
)

velocity = StaggeredGrid(vec(x=8, y=0, z=0), velocity_extrapolation, bounds=domain, resolution=resolution)

obstacle_geometry = cylinder(center=vec(x=20, y=50, z=2.5), radius=10, depth=5, axis='z')
obstacle = Obstacle(obstacle_geometry)

pressure_solve = Solve('CG-adaptive', 1e-5, 1e-5)

def to_numpy(v):
    centered = CenteredGrid(v, 0.0, bounds=domain, resolution=resolution)
    return centered.values.numpy(['x', 'y', 'z', 'vector'])

velocity_trj = [to_numpy(velocity)]

def step(v, dt=1.0):
    v = advect.mac_cormack(v, v, dt=dt)
    v = fluid.apply_boundary_conditions(v, obstacle)
    v, p = fluid.make_incompressible(v, obstacles=[obstacle], solve=pressure_solve)
    return v

for i in range(400):
    velocity = step(velocity)
    velocity_trj.append(to_numpy(velocity))

velocity_trj = np.stack(velocity_trj, axis=0)
np.save('wake_flow_velocity_trj.npy', velocity_trj)