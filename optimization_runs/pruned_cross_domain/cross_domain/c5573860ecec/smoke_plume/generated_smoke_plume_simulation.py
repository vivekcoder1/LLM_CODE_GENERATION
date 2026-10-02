from phi.flow import *
import numpy as np

bounds = Box(x=100, y=100)
dt = 0.5
alpha = 0.2
beta = 0.1

INFLOW = CenteredGrid(Sphere(center=vec(x=50, y=9.5), radius=5), extrapolation.BOUNDARY, x=200, y=200, bounds=bounds)
smoke = CenteredGrid(0, extrapolation.ZERO_GRADIENT, x=200, y=200, bounds=bounds)
velocity = StaggeredGrid(0, extrapolation.ZERO, x=64, y=64, bounds=bounds)
pressure = None

def step(velocity, smoke, pressure):
    smoke = advect.mac_cormack(smoke, velocity, dt) + alpha * dt * INFLOW
    buoyancy_force = (smoke * beta * vec(x=0, y=1)) @ velocity
    velocity = advect.mac_cormack(velocity, velocity, dt) + dt * buoyancy_force
    velocity, pressure = fluid.make_incompressible(velocity, obstacles=(), solve=Solve('CG', 1e-5, 1e-5, x0=pressure))
    return velocity, smoke, pressure

smoke_trj = [smoke.values.numpy('x,y')]
pressure_trj = []

for i in range(100):
    velocity, smoke, pressure = step(velocity, smoke, pressure)
    smoke_trj.append(smoke.values.numpy('x,y'))
    pressure_trj.append(pressure.values.numpy('x,y'))

smoke_trj = np.stack(smoke_trj, axis=0)
pressure_trj = np.stack(pressure_trj, axis=0)

np.save('smoke_plume_smoke_trj.npy', smoke_trj)
np.save('smoke_plume_pressure_trj.npy', pressure_trj)