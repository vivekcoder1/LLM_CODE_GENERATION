from phi.flow import *
import numpy as np

domain_bounds = Box(x=100, y=100)
velocity = StaggeredGrid(0, extrapolation=0, bounds=domain_bounds, resolution=spatial(x=64, y=64))
smoke = CenteredGrid(0, extrapolation=extrapolation.BOUNDARY, bounds=domain_bounds, resolution=spatial(x=200, y=200))
pressure = None

inflow_geometry = Sphere(center=vec(x=50, y=9.5), radius=5)
inflow_grid = CenteredGrid(inflow_geometry, extrapolation=0, bounds=domain_bounds, resolution=spatial(x=200, y=200))

inflow_rate = 0.2
buoyancy_coeff = 0.1
dt = 0.5

smoke_trj = [smoke.values.numpy('x,y')]
pressure_trj = []

for i in range(100):
    smoke = advect.mac_cormack(smoke, velocity, dt) + inflow_rate * dt * inflow_grid
    buoyancy_force = smoke * buoyancy_coeff * vec(x=0, y=1)
    velocity_buoyancy = StaggeredGrid(buoyancy_force, extrapolation=0, bounds=velocity.bounds, resolution=velocity.resolution)
    velocity = advect.mac_cormack(velocity, velocity, dt) + dt * velocity_buoyancy
    velocity, pressure = fluid.make_incompressible(velocity, obstacles=(), solve=Solve('CG', 1e-5, 1e-5, x0=pressure))
    smoke_trj.append(smoke.values.numpy('x,y'))
    pressure_trj.append(pressure.values.numpy('x,y'))

np.save('smoke_plume_smoke_trj.npy', np.stack(smoke_trj))
np.save('smoke_plume_pressure_trj.npy', np.stack(pressure_trj))