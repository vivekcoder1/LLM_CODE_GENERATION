from phi.flow import *
import numpy as np

Nx = 50
Ny = 32
nu = 0.1
dt = 1.0
steps = 100

domain_box = Box(x=Nx, y=Ny)
resolution = spatial(x=Nx, y=Ny)

top_velocity = vec(x=1.0, y=0.0)

boundary = extrapolation.combine_sides(
    x=extrapolation.ZERO,
    y=(extrapolation.ZERO, extrapolation.ConstantExtrapolation(top_velocity))
)

velocity = StaggeredGrid(0, boundary, domain_box, resolution)

def step(velocity, dt, nu):
    velocity = advect.mac_cormack(velocity, velocity, dt)
    velocity = diffuse.explicit(velocity, nu, dt)
    velocity, pressure = fluid.make_incompressible(velocity, obstacles=())
    return velocity

def to_array(velocity):
    centered = CenteredGrid(velocity, boundary, domain_box, resolution)
    return centered.values.numpy(['x', 'y', 'vector'])

velocity_trj = [to_array(velocity)]

for i in range(steps):
    velocity = step(velocity, dt, nu)
    velocity_trj.append(to_array(velocity))

velocity_trj = np.stack(velocity_trj, axis=0)
np.save('lid_driven_cavity_velocity_trj.npy', velocity_trj)