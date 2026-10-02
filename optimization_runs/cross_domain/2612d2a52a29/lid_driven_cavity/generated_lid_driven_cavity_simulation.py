import numpy as np
from phi.flow import *

Nx = 50
Ny = 32
nu = 0.1
dt = 1.0
steps = 100

bounds = Box(x=Nx, y=Ny)
boundary = extrapolation.combine_sides(
    x=extrapolation.ZERO,
    y=(extrapolation.ZERO, extrapolation.ConstantExtrapolation(vec(x=1, y=0)))
)

velocity = StaggeredGrid(0, boundary=boundary, x=Nx, y=Ny, bounds=bounds)
pressure = None

def step(v, p, dt, nu):
    v = advect.mac_cormack(v, v, dt)
    v = diffuse.explicit(v, nu, dt)
    v, p = fluid.make_incompressible(v, obstacles=(), solve=Solve('CG', 1e-5, 1e-5))
    return v, p

def to_numpy_frame(v):
    centered = CenteredGrid(v, resolution=spatial(x=Nx, y=Ny), bounds=bounds)
    arr = centered.values.numpy(['x', 'y', 'vector'])
    return arr

velocity_trj = [to_numpy_frame(velocity)]

for i in range(steps):
    velocity, pressure = step(velocity, pressure, dt, nu)
    velocity_trj.append(to_numpy_frame(velocity))

velocity_trj = np.stack(velocity_trj, axis=0)
np.save('lid_driven_cavity_velocity_trj.npy', velocity_trj)