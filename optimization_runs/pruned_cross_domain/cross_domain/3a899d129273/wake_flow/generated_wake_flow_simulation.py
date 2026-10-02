from phi.flow import *
import numpy as np

domain_bounds = Box(x=200, y=100, z=5)
res = spatial(x=128, y=64, z=8)

inflow_extrap = extrapolation.ConstantExtrapolation(vec(x=2, y=0, z=0))
outflow_extrap = extrapolation.ZERO_GRADIENT
boundary = extrapolation.combine_sides(
    x=(inflow_extrap, outflow_extrap),
    y=extrapolation.PERIODIC,
    z=extrapolation.PERIODIC
)

velocity = StaggeredGrid(vec(x=8, y=0, z=0), boundary, bounds=domain_bounds, resolution=res)

cyl = Cylinder(center=vec(x=20, y=50, z=2.5), radius=10, depth=5, axis='z')
obstacles = [Obstacle(cyl)]

pressure = None
velocity_trj = []

centered = CenteredGrid(velocity, resolution=res, bounds=domain_bounds, extrapolation=boundary)
velocity_trj.append(centered.values.numpy(('x', 'y', 'z', 'vector')))

dt = 1.0
for i in range(400):
    velocity = advect.mac_cormack(velocity, velocity, dt)
    velocity = apply_boundary_conditions(velocity, obstacles)
    if pressure is None:
        velocity, pressure = make_incompressible(velocity, obstacles=obstacles, solve=Solve('auto', 1e-5, 1e-5))
    else:
        velocity, pressure = make_incompressible(velocity, obstacles=obstacles, solve=Solve('auto', 1e-5, 1e-5, x0=pressure))
    centered = CenteredGrid(velocity, resolution=res, bounds=domain_bounds, extrapolation=boundary)
    velocity_trj.append(centered.values.numpy(('x', 'y', 'z', 'vector')))

velocity_trj = np.stack(velocity_trj, axis=0)
np.save('wake_flow_velocity_trj.npy', velocity_trj)