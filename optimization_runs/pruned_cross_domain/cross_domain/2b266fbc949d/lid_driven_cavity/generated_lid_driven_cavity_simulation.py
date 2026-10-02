from phi.flow import *
import numpy as np

DOMAIN = dict(x=50, y=32, bounds=Box(x=50, y=32))

velocity = StaggeredGrid(0, extrapolation.combine_sides(
    x=extrapolation.ZERO,
    y=(extrapolation.ZERO, extrapolation.combine_by_direction(normal=0, tangential=1))
), **DOMAIN)

BOUNDARY_MASK = StaggeredGrid(
    Box(x=(0, 50), y=(31, 32)), extrapolation.ZERO, **DOMAIN
)

velocity = velocity * (1 - BOUNDARY_MASK) + BOUNDARY_MASK * vec(x=1, y=0)

pressure = None

def step(v, p, dt=1.0, nu=0.1):
    v = advect.differential(v, v, order=2) * dt + v
    v = diffuse.explicit(v, nu, dt)
    v = v * (1 - BOUNDARY_MASK) + BOUNDARY_MASK * vec(x=1, y=0)
    v, p = fluid.make_incompressible(v, (), Solve('CG', 1e-5, 1e-5, x0=p))
    return v, p

velocity_trj = [velocity.staggered_tensor().numpy(('x', 'y', 'vector'))]

for i in range(100):
    velocity, pressure = step(velocity, pressure)
    velocity_trj.append(velocity.staggered_tensor().numpy(('x', 'y', 'vector')))

velocity_trj = np.stack(velocity_trj, axis=0)
np.save('lid_driven_cavity_velocity_trj.npy', velocity_trj)