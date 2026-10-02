from phi.flow import *
from phi.flow import fluid, advect
import numpy as np

DOMAIN = Box(x=100, y=100)
dt = 0.5
steps = 100

velocity = StaggeredGrid(0, extrapolation.ZERO, x=64, y=64, bounds=DOMAIN)
smoke = CenteredGrid(0, extrapolation.BOUNDARY, x=200, y=200, bounds=DOMAIN)
pressure = None

inflow_geom = Sphere(center=vec(x=50, y=9.5), radius=5)
inflow = CenteredGrid(inflow_geom, extrapolation.BOUNDARY, x=200, y=200, bounds=DOMAIN)

smoke_trj = [smoke.values.numpy(['x', 'y'])]
pressure_trj = []

for i in range(steps):
    smoke = advect.mac_cormack(smoke, velocity, dt) + inflow * 0.2 * dt
    buoyancy_force = (smoke * (0, 0.1)) @ velocity
    velocity = advect.mac_cormack(velocity, velocity, dt) + buoyancy_force * dt
    velocity, pressure = fluid.make_incompressible(velocity, obstacles=(), solve=Solve('auto', 1e-5, 1e-5))
    smoke_trj.append(smoke.values.numpy(['x', 'y']))
    pressure_trj.append(pressure.values.numpy(['x', 'y']))

smoke_trj = np.stack(smoke_trj, axis=0)
pressure_trj = np.stack(pressure_trj, axis=0)
np.save('smoke_plume_smoke_trj.npy', smoke_trj)
np.save('smoke_plume_pressure_trj.npy', pressure_trj)