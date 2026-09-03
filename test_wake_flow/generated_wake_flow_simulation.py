from phi.flow import *
from phi.geom import infinite_cylinder
import numpy as np

domain_bounds = Box(x=200, y=100, z=5)
res = dict(x=128, y=64, z=8)

cylinder = Obstacle(infinite_cylinder(center=vec(x=20, y=50, z=0), radius=10, inf_dim='z'))

boundary = extrapolation.combine_sides(
    x=(extrapolation.ConstantExtrapolation(vec(x=2, y=0, z=0)), extrapolation.ZERO_GRADIENT),
    y=extrapolation.PERIODIC,
    z=extrapolation.PERIODIC
)

velocity = StaggeredGrid(vec(x=8, y=0, z=0), boundary, bounds=domain_bounds, **res)
pressure = CenteredGrid(0, extrapolation.ZERO_GRADIENT, bounds=domain_bounds, **res)

def to_numpy(v):
    centered = CenteredGrid(v, extrapolation.ZERO_GRADIENT, bounds=domain_bounds, **res)
    return centered.values.numpy(('x', 'y', 'z', 'vector'))

trajectory = [to_numpy(velocity)]

for i in range(400):
    velocity = advect.mac_cormack(velocity, velocity, dt=1.0)
    velocity = fluid.apply_boundary_conditions(velocity, cylinder)
    velocity, pressure = fluid.make_incompressible(velocity, cylinder, Solve('CG', 1e-5, 1e-5, x0=pressure))
    trajectory.append(to_numpy(velocity))

velocity_trj = np.stack(trajectory, axis=0)
np.save('wake_flow_velocity_trj.npy', velocity_trj)