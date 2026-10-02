from phi.flow import *
import numpy as np

domain = Box(x=200, y=100, z=5)
resolution = spatial(x=128, y=64, z=8)

boundary = {
    'x': (vec(x=2, y=0, z=0), extrapolation.ZERO_GRADIENT),
    'y': extrapolation.PERIODIC,
    'z': extrapolation.PERIODIC
}

velocity = StaggeredGrid(vec(x=8, y=0, z=0), boundary=boundary, bounds=domain, resolution=resolution)

obstacle_geom = cylinder(center=vec(x=20, y=50, z=2.5), radius=10, depth=5, axis='z')
obstacle = Obstacle(obstacle_geom)

solve = Solve('CG', 1e-5, 1e-5)

velocity_trj = [velocity.values.numpy(['x', 'y', 'z', 'vector'])]

pressure = None
for i in range(400):
    velocity = advect.semi_lagrangian(velocity, velocity, dt=1.0)
    velocity, pressure = fluid.make_incompressible(velocity, obstacles=[obstacle], solve=solve)
    velocity_trj.append(velocity.values.numpy(['x', 'y', 'z', 'vector']))

velocity_trj = np.stack(velocity_trj, axis=0)
np.save('wake_flow_velocity_trj.npy', velocity_trj)