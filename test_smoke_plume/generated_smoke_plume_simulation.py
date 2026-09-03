from phi.flow import *
import numpy as np

DOMAIN = Box(x=100, y=100)
INFLOW_SPHERE = Sphere(x=50, y=9.5, radius=5)

smoke = CenteredGrid(0, extrapolation.BOUNDARY, x=200, y=200, bounds=DOMAIN)
velocity = StaggeredGrid(0, 0, x=64, y=64, bounds=DOMAIN)
pressure = None

inflow = CenteredGrid(INFLOW_SPHERE, extrapolation.BOUNDARY, x=200, y=200, bounds=DOMAIN)

alpha = 0.2
beta = 0.1
dt = 0.5

smoke_trj = [smoke.values.numpy('x,y')]
pressure_trj = []

for i in range(100):
    smoke = advect.euler(smoke, velocity, dt) + alpha * dt * inflow
    buoyancy_force = (smoke * (0, beta)).at(velocity)
    velocity = advect.euler(velocity, velocity, dt) + dt * buoyancy_force
    velocity, pressure = fluid.make_incompressible(velocity)
    smoke_trj.append(smoke.values.numpy('x,y'))
    pressure_trj.append(pressure.values.numpy('x,y'))

smoke_trj = np.stack(smoke_trj, axis=0)
pressure_trj = np.stack(pressure_trj, axis=0)

np.save('smoke_plume_smoke_trj.npy', smoke_trj)
np.save('smoke_plume_pressure_trj.npy', pressure_trj)