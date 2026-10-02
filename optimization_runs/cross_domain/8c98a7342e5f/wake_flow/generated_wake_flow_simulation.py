from phi.flow import *
import numpy as np

bounds = Box(x=200, y=100, z=5)

inflow_velocity = vec(x=2, y=0, z=0)

boundary_velocity = {
    'x': (extrapolation.ConstantExtrapolation(inflow_velocity), extrapolation.BOUNDARY),
    'y': extrapolation.PERIODIC,
    'z': extrapolation.PERIODIC
}

velocity = StaggeredGrid((8, 0, 0), boundary=boundary_velocity, bounds=bounds, x=128, y=64, z=8)

cylinder = Cylinder(center=vec(x=20, y=50, z=2.5), radius=10, depth=5, axis='z')
obstacle = Obstacle(cylinder)

pressure = None
dt = 0.1

def step(velocity, pressure, dt):
    velocity = advect.mac_cormack(velocity, velocity, dt)
    velocity, pressure = fluid.make_incompressible(velocity, obstacles=[obstacle], solve=Solve('CG', 1e-5, 1e-5, x0=pressure))
    velocity = fluid.apply_boundary_conditions(velocity, obstacle)
    return velocity, pressure

centered_resolution = spatial(x=128, y=64, z=8)

def to_numpy(v):
    centered = CenteredGrid(v, resolution=centered_resolution, bounds=bounds)
    return centered.values.numpy(('x', 'y', 'z', 'vector'))

trajectory = [to_numpy(velocity)]

for i in range(400):
    velocity, pressure = step(velocity, pressure, dt)
    trajectory.append(to_numpy(velocity))

data = np.stack(trajectory, axis=0)
np.save('wake_flow_velocity_trj.npy', data)