from phi.flow import *
import numpy as np

domain = Box(x=200, y=100, z=5)
res = spatial(x=128, y=64, z=8)

inflow_velocity = vec(x=2, y=0, z=0)

boundary = extrapolation.combine_sides(
    x=(extrapolation.ConstantExtrapolation(inflow_velocity), extrapolation.ZERO_GRADIENT),
    y=extrapolation.PERIODIC,
    z=extrapolation.PERIODIC
)

velocity = StaggeredGrid(vec(x=8, y=0, z=0), boundary, domain, resolution=res)

obstacle_geom = Cylinder(center=vec(x=20, y=50, z=2.5), radius=10, depth=5, axis='z')
obstacle = Obstacle(obstacle_geom)

dt = 0.1
pressure_solve = Solve('CG', 1e-5, 1e-5, max_iterations=1000)

def step(v):
    v = advect.mac_cormack(v, v, dt)
    v = fluid.apply_boundary_conditions(v, [obstacle])
    v, p = fluid.make_incompressible(v, obstacles=[obstacle], solve=pressure_solve)
    return v

trj = []
centered_init = CenteredGrid(velocity, resolution=res, bounds=domain)
trj.append(centered_init.numpy('x,y,z,vector'))

for i in range(400):
    velocity = step(velocity)
    centered = CenteredGrid(velocity, resolution=res, bounds=domain)
    trj.append(centered.numpy('x,y,z,vector'))

velocity_trj = np.stack(trj, axis=0)
np.save('wake_flow_velocity_trj.npy', velocity_trj)