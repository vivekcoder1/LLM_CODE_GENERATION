from phi.flow import *
import numpy as np

DOMAIN = dict(x=64, y=64, bounds=Box(x=100, y=100))
SMOKE_DOMAIN = dict(x=200, y=200, bounds=Box(x=100, y=100))

INFLOW_GEOM = Sphere(center=vec(x=50, y=9.5), radius=5)
INFLOW = CenteredGrid(INFLOW_GEOM, extrapolation.BOUNDARY, **SMOKE_DOMAIN)

smoke = CenteredGrid(0, extrapolation.BOUNDARY, **SMOKE_DOMAIN)
velocity = StaggeredGrid(0, extrapolation.ZERO, **DOMAIN)
pressure = None

buoyancy_factor = 0.1
inflow_rate = 0.2
dt = 0.5

smoke_trj = [smoke.values.numpy('x,y')]
pressure_trj = []

for i in range(100):
    smoke = advect.mac_cormack(smoke, velocity, dt) + inflow_rate * dt * INFLOW
    buoyancy_force = (smoke * vec(x=0, y=1) * buoyancy_factor).at(velocity)
    velocity = advect.semi_lagrangian(velocity, velocity, dt) + buoyancy_force * dt
    velocity, pressure = fluid.make_incompressible(velocity, obstacles=(), solve=Solve('CG', 1e-5, 1e-5, x0=pressure))
    smoke_trj.append(smoke.values.numpy('x,y'))
    pressure_trj.append(pressure.values.numpy('x,y'))

np.save('smoke_plume_smoke_trj.npy', np.stack(smoke_trj))
np.save('smoke_plume_pressure_trj.npy', np.stack(pressure_trj))