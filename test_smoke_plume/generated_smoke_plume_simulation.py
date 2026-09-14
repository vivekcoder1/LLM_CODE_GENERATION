import numpy as np
from phi.flow import *

DOMAIN = Box(x=100, y=100)

velocity = StaggeredGrid(0, extrapolation.ZERO, x=64, y=64, bounds=DOMAIN)
smoke = CenteredGrid(0, extrapolation.ZERO_GRADIENT, x=200, y=200, bounds=DOMAIN)
pressure = None

inflow_geometry = Sphere(center=vec(x=50, y=9.5), radius=5)
inflow = CenteredGrid(inflow_geometry, extrapolation.ZERO, x=200, y=200, bounds=DOMAIN)

dt = 0.5
buoyancy_coefficient = 0.1
inflow_rate = 0.2

smoke_trj = [smoke.values.numpy('x,y')]
pressure_trj = []

for _ in range(100):
    smoke = advect.mac_cormack(smoke, velocity, dt) + inflow_rate * dt * inflow
    buoyancy_force = StaggeredGrid(smoke * vec(x=0, y=buoyancy_coefficient), velocity.extrapolation, bounds=velocity.bounds, resolution=velocity.resolution)
    velocity = advect.semi_lagrangian(velocity, velocity, dt) + dt * buoyancy_force
    velocity, pressure = fluid.make_incompressible(velocity, obstacles=(), solve=Solve('CG', 1e-5, 1e-5, x0=pressure))
    smoke_trj.append(smoke.values.numpy('x,y'))
    pressure_trj.append(pressure.values.numpy('x,y'))

smoke_trj = np.stack(smoke_trj, axis=0)
pressure_trj = np.stack(pressure_trj, axis=0)

np.save('smoke_plume_smoke_trj.npy', smoke_trj)
np.save('smoke_plume_pressure_trj.npy', pressure_trj)