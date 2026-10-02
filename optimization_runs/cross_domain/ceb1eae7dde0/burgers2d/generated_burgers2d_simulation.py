from phi.flow import *
import numpy as np

Lx, Ly = 40, 20
Nx, Ny = 64, 64
nu = 0.1
dt = 0.5
n_steps = 100

def init(x):
    gauss = math.exp(-(x['x'] - Lx / 2) ** 2 - (x['y'] - Ly / 2) ** 2)
    return vec(x=gauss, y=gauss)

velocity = CenteredGrid(init, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=Box(x=Lx, y=Ly))

def step(v, dt):
    diff = diffuse.differential(v, nu)
    adv = advect.differential(v, v)
    return v + dt * (adv + diff)

trajectory = [velocity.values.numpy(['x', 'y', 'vector'])]

for i in range(n_steps):
    velocity = step(velocity, dt)
    trajectory.append(velocity.values.numpy(['x', 'y', 'vector']))

trajectory = np.stack(trajectory, axis=0)
np.save('burgers2d_velocity_trj.npy', trajectory)