from phi.flow import *
import numpy as np

domain_bounds = Box(x=100, y=100)
dt = 0.5
alpha = 0.2
beta = 0.1
steps = 100

velocity = StaggeredGrid(0, extrapolation=0, x=64, y=64, bounds=domain_bounds)
smoke = CenteredGrid(0, extrapolation=extrapolation.BOUNDARY, x=200, y=200, bounds=domain_bounds)
pressure = None

inflow_geometry = Sphere(center=vec(x=50, y=9.5), radius=5)
inflow = CenteredGrid(inflow_geometry, extrapolation=0, x=200, y=200, bounds=domain_bounds)

smoke_trj = [smoke.numpy(('x', 'y'))]
pressure_trj = []

def step(v, s, p, dt):
    s = advect.mac_cormack(s, v, dt) + inflow * alpha * dt
    buoyancy_force = (s * beta * vec(x=0, y=1)) @ v
    v = advect.mac_cormack(v, v, dt) + buoyancy_force * dt
    v, p = fluid.make_incompressible(v, (), Solve('CG', 1e-5, 1e-5, x0=p))
    return v, s, p

for i in range(steps):
    velocity, smoke, pressure = step(velocity, smoke, pressure, dt)
    smoke_trj.append(smoke.numpy(('x', 'y')))
    pressure_trj.append(pressure.numpy(('x', 'y')))

smoke_trj = np.stack(smoke_trj, axis=0)
pressure_trj = np.stack(pressure_trj, axis=0)

np.save('smoke_plume_smoke_trj.npy', smoke_trj)
np.save('smoke_plume_pressure_trj.npy', pressure_trj)