from phi.flow import *
import numpy as np

domain = Box(x=200, y=100, z=5)
resolution = spatial(x=128, y=64, z=8)

inflow_velocity = vec(x=2, y=0, z=0)

boundary = extrapolation.combine_sides(
    x=(extrapolation.ConstantExtrapolation(inflow_velocity), extrapolation.ZERO_GRADIENT),
    y=extrapolation.PERIODIC,
    z=extrapolation.PERIODIC
)

velocity = StaggeredGrid(vec(x=8, y=0, z=0), boundary, bounds=domain, resolution=resolution)

cyl = Cylinder(center=vec(x=20, y=50, z=2.5), radius=10, depth=5, axis='z')
obstacle = Obstacle(cyl)

def step(v, dt=1.0):
    v = advect.mac_cormack(v, v, dt)
    v, p = fluid.make_incompressible(v, obstacles=[obstacle])
    v = fluid.apply_boundary_conditions(v, [obstacle])
    return v

def to_centered(v):
    c = CenteredGrid(v, resolution=resolution, bounds=domain)
    return c.values.numpy(['x', 'y', 'z', 'vector'])

velocity_trj = [to_centered(velocity)]

for i in range(400):
    velocity = step(velocity)
    velocity_trj.append(to_centered(velocity))

velocity_trj = np.stack(velocity_trj, axis=0)
np.save('wake_flow_velocity_trj.npy', velocity_trj)