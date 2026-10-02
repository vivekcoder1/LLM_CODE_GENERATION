from phi.flow import *
import numpy as np

DOMAIN = dict(x=64, y=64, bounds=Box(x=100, y=100))
SMOKE_DOMAIN = dict(x=200, y=200, bounds=Box(x=100, y=100))

smoke = CenteredGrid(0, extrapolation.BOUNDARY, **SMOKE_DOMAIN)
velocity = StaggeredGrid(0, extrapolation.ZERO, **DOMAIN)
pressure = None

INFLOW = CenteredGrid(Sphere(center=vec(x=50, y=9.5), radius=5), extrapolation.BOUNDARY, **SMOKE_DOMAIN)

inflow_rate = 0.2
buoyancy_coefficient = 0.1
dt = 0.5

smoke_trj = [smoke.values.numpy('x,y')]
pressure_trj = []

for i in range(100):
    smoke = advect.mac_cormack(smoke, velocity, dt) + inflow_rate * dt * INFLOW
    buoyancy_force = smoke * vec(x=0, y=1) * buoyancy_coefficient @ velocity
    velocity = advect.semi_implicit_euler(velocity, velocity, dt) + dt * buoyancy_force
    velocity, pressure = fluid.make_incompressible(velocity, obstacles=(), solve=Solve('CG', 1e-5, 1e-5))
    smoke_trj.append(smoke.values.numpy('x,y'))
    pressure_trj.append(pressure.values.numpy('x,y'))

np.save('smoke_plume_smoke_trj.npy', np.stack(smoke_trj))
np.save('smoke_plume_pressure_trj.npy', np.stack(pressure_trj))