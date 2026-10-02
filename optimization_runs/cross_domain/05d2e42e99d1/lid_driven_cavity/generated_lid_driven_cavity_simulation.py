from phi.flow import *
import numpy as np

Nx = 50
Ny = 32
nu = 0.1
dt = 1.0

bounds = Box(x=Nx, y=Ny)

boundary = extrapolation.combine_sides(
    x=extrapolation.ZERO,
    y=(extrapolation.ZERO, extrapolation.ConstantExtrapolation(vec(x=1, y=0)))
)

velocity = StaggeredGrid(0, boundary, x=Nx, y=Ny, bounds=bounds)
pressure = None


def step(v, p, dt, nu):
    v = advect.semi_lagrangian(v, v, dt)
    v = diffuse.explicit(v, nu, dt)
    v, p = fluid.make_incompressible(v, (), Solve('CG', 1e-5, 1e-5, x0=p))
    return v, p


trajectory = [velocity]

for i in range(100):
    velocity, pressure = step(velocity, pressure, dt, nu)
    trajectory.append(velocity)

velocity_trj = np.stack([
    CenteredGrid(v, extrapolation.ZERO, x=Nx, y=Ny, bounds=bounds).values.numpy(('x', 'y', 'vector'))
    for v in trajectory
])

np.save('lid_driven_cavity_velocity_trj.npy', velocity_trj)