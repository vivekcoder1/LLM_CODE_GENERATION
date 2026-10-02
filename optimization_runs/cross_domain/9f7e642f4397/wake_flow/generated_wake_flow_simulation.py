from phi.flow import *
import numpy as np

resolution = spatial(x=128, y=64, z=8)
bounds = Box(x=200, y=100, z=5)

obstacle = cylinder(center=vec(x=20, y=50, z=2.5), radius=10, depth=5, axis='z')

inflow_velocity = vec(x=2, y=0, z=0)

boundary = extrapolation.combine_sides(
    x=(extrapolation.ConstantExtrapolation(inflow_velocity), extrapolation.BOUNDARY),
    y=extrapolation.PERIODIC,
    z=extrapolation.PERIODIC
)

velocity = StaggeredGrid((8, 0, 0), boundary=boundary, bounds=bounds, resolution=resolution)
velocity = fluid.apply_boundary_conditions(velocity, obstacles=(obstacle,))

def step(v, dt=1.0):
    v = advect.mac_cormack(v, v, dt)
    v, _ = fluid.make_incompressible(v, obstacles=(obstacle,), solve=Solve('CG', 1e-5, 1e-5, max_iterations=1000))
    v = fluid.apply_boundary_conditions(v, obstacles=(obstacle,))
    return v

def to_numpy(v):
    centered = CenteredGrid(v, resolution=resolution, bounds=bounds)
    return centered.values.numpy(['x', 'y', 'z', 'vector'])

velocity_trj = [to_numpy(velocity)]

for i in range(400):
    velocity = step(velocity, dt=1.0)
    velocity_trj.append(to_numpy(velocity))

velocity_trj = np.stack(velocity_trj, axis=0)
np.save('wake_flow_velocity_trj.npy', velocity_trj)