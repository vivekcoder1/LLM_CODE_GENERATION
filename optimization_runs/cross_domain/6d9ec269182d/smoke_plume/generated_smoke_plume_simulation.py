from phi.flow import *
import numpy as np

domain_bounds = Box(x=100, y=100)

velocity = StaggeredGrid(0, extrapolation.ZERO, x=64, y=64, bounds=domain_bounds)
pressure = None

inflow_geometry = Sphere(center=vec(x=50, y=9.5), radius=5)
inflow = CenteredGrid(inflow_geometry, extrapolation.BOUNDARY, x=200, y=200, bounds=domain_bounds)
smoke = CenteredGrid(0, extrapolation.BOUNDARY, x=200, y=200, bounds=domain_bounds)

inflow_rate = 0.2
buoyancy_coeff = 0.1
dt = 0.5
num_steps = 100

def step(v, s, p, dt):
    s = advect.mac_cormack(s, v, dt) + inflow_rate * dt * inflow
    buoyancy_force = (s * vec(x=0, y=1) * buoyancy_coeff).at(v)
    v = advect.mac_cormack(v, v, dt) + dt * buoyancy_force
    v, p = fluid.make_incompressible(v, (), Solve('CG', 1e-5, 1e-5, x0=p))
    return v, s, p

smoke_trj = [smoke.values.numpy(('x', 'y'))]
pressure_trj = []

for i in range(num_steps):
    velocity, smoke, pressure = step(velocity, smoke, pressure, dt)
    smoke_trj.append(smoke.values.numpy(('x', 'y')))
    pressure_trj.append(pressure.values.numpy(('x', 'y')))

smoke_trj = np.stack(smoke_trj, axis=0)
pressure_trj = np.stack(pressure_trj, axis=0)

np.save('smoke_plume_smoke_trj.npy', smoke_trj)
np.save('smoke_plume_pressure_trj.npy', pressure_trj)