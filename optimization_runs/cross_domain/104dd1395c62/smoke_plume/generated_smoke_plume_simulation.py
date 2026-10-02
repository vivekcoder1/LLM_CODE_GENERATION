from phi.flow import *
import numpy as np

DOMAIN = dict(x=64, y=64, bounds=Box(x=100, y=100))
SMOKE_DOMAIN = dict(x=200, y=200, bounds=Box(x=100, y=100))

INFLOW_GEOM = Sphere(center=vec(x=50, y=9.5), radius=5)
inflow = CenteredGrid(INFLOW_GEOM, extrapolation.BOUNDARY, **SMOKE_DOMAIN)

smoke = CenteredGrid(0, extrapolation.BOUNDARY, **SMOKE_DOMAIN)
velocity = StaggeredGrid(0, extrapolation.ZERO, **DOMAIN)
pressure = None

alpha = 0.2
beta = 0.1
dt = 0.5

def step(velocity, smoke, pressure, dt):
    smoke = advect.mac_cormack(smoke, velocity, dt) + inflow * alpha * dt
    buoyancy_force = (smoke * beta) * vec(x=0, y=1)
    velocity = advect.mac_cormack(velocity, velocity, dt) + buoyancy_force * dt
    velocity, pressure = fluid.make_incompressible(velocity, obstacles=(), solve=Solve('auto', 1e-5, 1e-5, x0=pressure))
    return velocity, smoke, pressure

smoke_trj = [smoke.values.numpy(['x', 'y'])]
pressure_trj = []

for i in range(100):
    velocity, smoke, pressure = step(velocity, smoke, pressure, dt)
    smoke_trj.append(smoke.values.numpy(['x', 'y']))
    pressure_trj.append(pressure.values.numpy(['x', 'y']))

smoke_trj = np.stack(smoke_trj, axis=0)
pressure_trj = np.stack(pressure_trj, axis=0)

np.save('smoke_plume_smoke_trj.npy', smoke_trj)
np.save('smoke_plume_pressure_trj.npy', pressure_trj)