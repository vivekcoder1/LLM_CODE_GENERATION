from phi.flow import *
import numpy as np

Nx, Ny = 50, 32
nu = 0.1
dt = 1.0
steps = 100

boundary = extrapolation.combine_sides(x=0, y=(0, vec(x=1, y=0)))

velocity = CenteredGrid((0, 0), extrapolation=boundary, bounds=Box(x=Nx, y=Ny), x=Nx, y=Ny)

def step(v, dt=dt, nu=nu):
    v = advect.mac_cormack(v, v, dt)
    v = diffuse.explicit(v, nu, dt)
    v, p = fluid.make_incompressible(v, obstacles=())
    return v

trj = [velocity.values.numpy(('x', 'y', 'vector'))]

for i in range(steps):
    velocity = step(velocity)
    trj.append(velocity.values.numpy(('x', 'y', 'vector')))

trj = np.stack(trj, axis=0)
np.save('lid_driven_cavity_velocity_trj.npy', trj)