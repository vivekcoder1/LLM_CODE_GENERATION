from phi.flow import *
from phi.flow import fluid, advect
import numpy as np

DOMAIN_BOUNDS = Box(x=100, y=100)
dt = 0.5
buoyancy_coefficient = 0.1
inflow_rate = 0.2

def inflow_mask(x):
    return math.where((x['x'] - 50) ** 2 + (x['y'] - 9.5) ** 2 <= 5 ** 2, 1.0, 0.0)

inflow = CenteredGrid(inflow_mask, extrapolation=extrapolation.BOUNDARY, bounds=DOMAIN_BOUNDS, x=200, y=200)
smoke = CenteredGrid(0, extrapolation=extrapolation.BOUNDARY, bounds=DOMAIN_BOUNDS, x=200, y=200)
velocity = StaggeredGrid(0, boundary=0, bounds=DOMAIN_BOUNDS, x=64, y=64)
pressure = None

smoke_trj = [smoke.values.numpy(('x', 'y'))]
pressure_trj = []

def step(smoke, velocity, pressure, dt):
    smoke = advect.mac_cormack(smoke, velocity, dt) + inflow_rate * dt * inflow
    buoyancy_force = smoke * (0, buoyancy_coefficient)
    force_grid = StaggeredGrid(buoyancy_force, boundary=velocity.boundary, bounds=velocity.bounds, resolution=velocity.resolution)
    velocity = advect.semi_lagrangian(velocity, velocity, dt) + dt * force_grid
    velocity, pressure = fluid.make_incompressible(velocity, obstacles=(), solve=Solve('CG', 1e-5, 1e-5, x0=pressure))
    return smoke, velocity, pressure

for i in range(100):
    smoke, velocity, pressure = step(smoke, velocity, pressure, dt)
    smoke_trj.append(smoke.values.numpy(('x', 'y')))
    pressure_trj.append(pressure.values.numpy(('x', 'y')))

smoke_trj = np.stack(smoke_trj, axis=0)
pressure_trj = np.stack(pressure_trj, axis=0)

np.save('smoke_plume_smoke_trj.npy', smoke_trj)
np.save('smoke_plume_pressure_trj.npy', pressure_trj)