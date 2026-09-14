from phi.flow import *
import numpy as np

Nx = 50
Ny = 32
nu = 0.1
dt = 1.0
steps = 100

domain_bounds = Box(x=Nx, y=Ny)

top_velocity = vec(x=1.0, y=0.0)
velocity_boundary = extrapolation.combine_sides(
    x=extrapolation.ZERO,
    y=(extrapolation.ZERO, extrapolation.ConstantExtrapolation(top_velocity))
)

pressure_boundary = extrapolation.ZERO

velocity = StaggeredGrid(0, velocity_boundary, x=Nx, y=Ny, bounds=domain_bounds)
pressure = CenteredGrid(0, pressure_boundary, x=Nx, y=Ny, bounds=domain_bounds)

pressure_solve = Solve('CG', 1e-5, 1e-5, x0=pressure)

def step(velocity, pressure, dt, nu):
    velocity = advect.semi_lagrangian(velocity, velocity, dt)
    velocity = diffuse.explicit(velocity, nu, dt)
    velocity, pressure = fluid.make_incompressible(velocity, (), solve=pressure_solve)
    return velocity, pressure

def to_numpy(velocity):
    centered = CenteredGrid(velocity, extrapolation.ZERO, x=Nx, y=Ny, bounds=domain_bounds)
    return centered.values.numpy(['x', 'y', 'vector'])

velocity_trj = [to_numpy(velocity)]

for i in range(steps):
    velocity, pressure = step(velocity, pressure, dt, nu)
    velocity_trj.append(to_numpy(velocity))

velocity_trj = np.stack(velocity_trj, axis=0)
np.save('lid_driven_cavity_velocity_trj.npy', velocity_trj)