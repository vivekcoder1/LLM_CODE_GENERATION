from phi.flow import *
from phi.flow import advect, fluid, extrapolation
import numpy as np

domain_bounds = Box(x=100, y=100)

velocity = StaggeredGrid(0, extrapolation.ZERO, x=64, y=64, bounds=domain_bounds)
smoke = CenteredGrid(0, extrapolation.BOUNDARY, x=200, y=200, bounds=domain_bounds)
pressure = None

inflow = CenteredGrid(Sphere(center=vec(x=50, y=9.5), radius=5), extrapolation.BOUNDARY, x=200, y=200, bounds=domain_bounds)

inflow_rate = 0.2
buoyancy_coefficient = 0.1
dt = 0.5

smoke_trj = [smoke.values.numpy(('x', 'y'))]
pressure_trj = []

for i in range(100):
    smoke = advect.mac_cormack(smoke, velocity, dt) + inflow_rate * dt * inflow
    buoyancy_force = smoke * (buoyancy_coefficient * vec(x=0, y=1))
    buoyancy_force = StaggeredGrid(buoyancy_force, extrapolation.ZERO, bounds=domain_bounds, x=64, y=64)
    velocity = advect.semi_lagrangian(velocity, velocity, dt) + dt * buoyancy_force
    velocity, pressure = fluid.make_incompressible(velocity, (), Solve('CG', 1e-5, 1e-5, x0=pressure))
    smoke_trj.append(smoke.values.numpy(('x', 'y')))
    pressure_trj.append(pressure.values.numpy(('x', 'y')))

smoke_trj = np.stack(smoke_trj, axis=0)
pressure_trj = np.stack(pressure_trj, axis=0)

np.save('smoke_plume_smoke_trj.npy', smoke_trj)
np.save('smoke_plume_pressure_trj.npy', pressure_trj)