from phi.flow import *
from phi.flow import advect, diffuse
import numpy as np

Lx = 40.0
Ly = 20.0
Nx = 64
Ny = 64
nu = 0.1
dt = 0.5
steps = 100

domain_bounds = Box(x=Lx, y=Ly)

def init_velocity(x):
    val = math.exp(-(x['x'] - Lx / 2) ** 2 - (x['y'] - Ly / 2) ** 2)
    return vec(x=val, y=val)

velocity = CenteredGrid(init_velocity, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=domain_bounds)

def step(v, dt):
    adv = advect.differential(v, v, order=2)
    v = v + dt * adv
    v = diffuse.explicit(v, nu, dt)
    return v

velocity_trj = [velocity.values.numpy(['x', 'y', 'vector'])]

for i in range(steps):
    velocity = step(velocity, dt)
    velocity_trj.append(velocity.values.numpy(['x', 'y', 'vector']))

velocity_trj = np.stack(velocity_trj)
np.save('burgers2d_velocity_trj.npy', velocity_trj)