from phi.flow import *
import numpy as np

domain = Box(x=100, y=100)

velocity = StaggeredGrid(0, extrapolation.ZERO, x=64, y=64, bounds=domain)
pressure = None
smoke = CenteredGrid(0, extrapolation.BOUNDARY, x=200, y=200, bounds=domain)

inflow_geom = Sphere(center=vec(x=50, y=9.5), radius=5)
inflow = CenteredGrid(inflow_geom, extrapolation.BOUNDARY, x=200, y=200, bounds=domain)

inflow_rate = 0.2
buoyancy_factor = 0.1
dt = 0.5

smoke_trj = [smoke.values.numpy(('x', 'y'))]
pressure_trj = []

for i in range(100):
    smoke = advect.mac_cormack(smoke, velocity, dt) + inflow_rate * dt * inflow
    buoyancy_force = (smoke * vec(x=0, y=1)) @ velocity
    velocity = advect.mac_cormack(velocity, velocity, dt) + dt * buoyancy_factor * buoyancy_force
    velocity, pressure = fluid.make_incompressible(velocity, obstacles=(), solve=Solve('CG', 1e-5, 1e-5, x0=pressure))
    smoke_trj.append(smoke.values.numpy(('x', 'y')))
    pressure_trj.append(pressure.values.numpy(('x', 'y')))

np.save('smoke_plume_smoke_trj.npy', np.stack(smoke_trj))
np.save('smoke_plume_pressure_trj.npy', np.stack(pressure_trj))