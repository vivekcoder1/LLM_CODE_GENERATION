from phi.flow import *
from phi.flow import advect, diffuse
import numpy as np

Lx, Ly = 40., 20.
Nx, Ny = 64, 64
nu = 0.1
dt = 0.5
steps = 100

bounds = Box(x=Lx, y=Ly)

def init(x):
    r = math.exp(-(x['x'] - Lx / 2) ** 2 - (x['y'] - Ly / 2) ** 2)
    return vec(x=r, y=r)

velocity = CenteredGrid(init, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=bounds)

def step(v, dt):
    rhs = advect.differential(v, v) + diffuse.differential(v, nu)
    return v + dt * rhs

trj = [velocity.values.numpy('x,y,vector')]

for i in range(steps):
    velocity = step(velocity, dt)
    trj.append(velocity.values.numpy('x,y,vector'))

trj = np.stack(trj, axis=0)
np.save('burgers2d_velocity_trj.npy', trj)