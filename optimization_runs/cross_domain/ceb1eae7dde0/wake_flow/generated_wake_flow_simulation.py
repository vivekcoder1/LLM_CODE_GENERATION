from phi.flow import *
import numpy as np

domain_bounds = Box(x=200, y=100, z=5)

boundary = extrapolation.combine_sides(
    x=(extrapolation.ConstantExtrapolation(vec(x=2, y=0, z=0)), extrapolation.BOUNDARY),
    y=extrapolation.PERIODIC,
    z=extrapolation.PERIODIC
)

velocity = StaggeredGrid(vec(x=8, y=0, z=0), boundary=boundary, bounds=domain_bounds, x=128, y=64, z=8)

cyl = geom.cylinder(center=vec(x=20, y=50, z=2.5), radius=10, depth=5, axis='z')
obstacle = Obstacle(cyl)
obstacles = [obstacle]

velocity = fluid.apply_boundary_conditions(velocity, obstacles)

pressure_solve = Solve('CG', 1e-5, 1e-5, max_iterations=1000)

dt = 0.1

trajectory = [velocity.at_centers().numpy(['x', 'y', 'z', 'vector'])]

for i in range(400):
    velocity = advect.mac_cormack(velocity, velocity, dt)
    velocity = fluid.apply_boundary_conditions(velocity, obstacles)
    velocity, pressure = fluid.make_incompressible(velocity, obstacles=obstacles, solve=pressure_solve)
    trajectory.append(velocity.at_centers().numpy(['x', 'y', 'z', 'vector']))

trajectory = np.stack(trajectory, axis=0)
np.save('wake_flow_velocity_trj.npy', trajectory)