from phi.flow import *
import numpy as np

Nx = 50
Ny = 32
nu = 0.1
dt = 1.0
steps = 100

boundary = extrapolation.combine_sides(
    x=extrapolation.ZERO,
    y=(extrapolation.ZERO, extrapolation.ConstantExtrapolation(vec(x=1.0, y=0.0)))
)

velocity = StaggeredGrid(0, boundary, x=Nx, y=Ny, bounds=Box(x=Nx, y=Ny))
pressure = None

def step(velocity, pressure, dt):
    velocity = advect.mac_cormack(velocity, velocity, dt)
    velocity = diffuse.explicit(velocity, nu, dt)
    velocity, pressure = fluid.make_incompressible(velocity, obstacles=(), solve=Solve('CG', 1e-5, 1e-5))
    return velocity, pressure

velocity_trj = []
centered = velocity.at_centers()
velocity_trj.append(centered.values.numpy(['x', 'y', 'vector']))

for i in range(steps):
    velocity, pressure = step(velocity, pressure, dt)
    centered = velocity.at_centers()
    velocity_trj.append(centered.values.numpy(['x', 'y', 'vector']))

velocity_trj = np.stack(velocity_trj, axis=0)
np.save('lid_driven_cavity_velocity_trj.npy', velocity_trj)