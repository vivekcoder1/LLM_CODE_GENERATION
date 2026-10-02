from phi.flow import *
import numpy as np

domain = Box(x=100, y=100)
dt = 0.5
INFLOW_RATE = 0.2
BUOYANCY = 0.1

velocity = StaggeredGrid(0, extrapolation=0, resolution=spatial(x=64, y=64), bounds=domain)
smoke = CenteredGrid(0, extrapolation=extrapolation.BOUNDARY, resolution=spatial(x=200, y=200), bounds=domain)
pressure = None

inflow = CenteredGrid(Sphere(center=vec(x=50, y=9.5), radius=5), extrapolation=extrapolation.BOUNDARY, resolution=spatial(x=200, y=200), bounds=domain)

def step(v, s, p, dt):
    s = advect.mac_cormack(s, v, dt) + INFLOW_RATE * dt * inflow
    buoyancy_force = s * vec(x=0, y=BUOYANCY)
    v = advect.mac_cormack(v, v, dt) + buoyancy_force * dt
    v, p = fluid.make_incompressible(v, ())
    return v, s, p

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