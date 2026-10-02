from phi.flow import *
import numpy as np

Nx, Ny = 50, 32
nu = 0.1
dt = 1.0
steps = 100

boundary = extrapolation.combine_sides(
    x=extrapolation.ZERO,
    y=(extrapolation.ZERO, extrapolation.ConstantExtrapolation(vec(x=1, y=0)))
)

velocity = StaggeredGrid(0, boundary, bounds=Box(x=Nx, y=Ny), x=Nx, y=Ny)

def step(v, dt, nu):
    v = advect.mac_cormack(v, v, dt)
    v = diffuse.explicit(v, nu, dt)
    v, p = fluid.make_incompressible(v)
    return v

velocity_trj = [velocity]
for i in range(steps):
    velocity = step(velocity, dt, nu)
    velocity_trj.append(velocity)

data = []
for v in velocity_trj:
    centered = CenteredGrid(v, extrapolation=v.extrapolation, bounds=v.bounds, resolution=v.resolution)
    arr = centered.values.numpy(('x', 'y', 'vector'))
    data.append(arr)

data = np.stack(data, axis=0)
np.save('lid_driven_cavity_velocity_trj.npy', data)