from phi.flow import *
import numpy as np

Nx, Ny = 50, 32
nu = 0.1
dt = 1.0
steps = 100

domain_bounds = Box(x=Nx, y=Ny)

boundary = extrapolation.combine_sides(
    x=extrapolation.ZERO,
    y=(extrapolation.ZERO, extrapolation.ConstantExtrapolation(vec(x=1, y=0)))
)

velocity = StaggeredGrid(0, boundary, x=Nx, y=Ny, bounds=domain_bounds)
pressure = None

def step(velocity, pressure, dt, nu):
    velocity = advect.mac_cormack(velocity, velocity, dt)
    velocity = diffuse.explicit(velocity, nu, dt)
    velocity, pressure = fluid.make_incompressible(velocity, obstacles=(), solve=Solve('CG', 1e-5, 1e-5, x0=pressure))
    return velocity, pressure

trajectory = [velocity.at_centers().values.numpy(('x', 'y', 'vector'))]

for i in range(steps):
    velocity, pressure = step(velocity, pressure, dt, nu)
    trajectory.append(velocity.at_centers().values.numpy(('x', 'y', 'vector')))

trajectory = np.stack(trajectory, axis=0)
np.save('lid_driven_cavity_velocity_trj.npy', trajectory)