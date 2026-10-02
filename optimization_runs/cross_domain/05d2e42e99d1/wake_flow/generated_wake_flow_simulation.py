from phi.flow import *
import numpy as np

DOMAIN_BOUNDS = Box(x=200, y=100, z=5)
RESOLUTION = spatial(x=128, y=64, z=8)

obstacle_geometry = Cylinder(center=vec(x=20, y=50, z=2.5), radius=10, depth=5, axis='z')
obstacle = Obstacle(obstacle_geometry)

boundary = extrapolation.combine_sides(
    x=(extrapolation.ConstantExtrapolation(vec(x=2, y=0, z=0)), extrapolation.ZERO_GRADIENT),
    y=extrapolation.PERIODIC,
    z=extrapolation.PERIODIC
)

velocity = StaggeredGrid(vec(x=8, y=0, z=0), boundary=boundary, bounds=DOMAIN_BOUNDS, resolution=RESOLUTION)
pressure = None

def to_numpy(vel):
    centered = vel.at_centers()
    return centered.values.numpy(('x', 'y', 'z', 'vector'))

def step(vel, pres, dt):
    vel = advect.mac_cormack(vel, vel, dt)
    vel = fluid.apply_boundary_conditions(vel, obstacle)
    vel, pres = fluid.make_incompressible(vel, obstacles=[obstacle], solve=Solve('CG', 1e-5, 1e-5))
    return vel, pres

dt = 0.1
trajectory = [to_numpy(velocity)]

for i in range(400):
    velocity, pressure = step(velocity, pressure, dt)
    trajectory.append(to_numpy(velocity))

velocity_trj = np.stack(trajectory, axis=0)
np.save('wake_flow_velocity_trj.npy', velocity_trj)