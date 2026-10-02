from phi.flow import *
import numpy as np

Lx, Ly = 40., 20.
Nx, Ny = 64, 64
nu = 0.1
dt = 0.5
steps = 100

bounds = Box(x=Lx, y=Ly)

def init_velocity(x):
    val = math.exp(-(x['x'] - Lx / 2) ** 2 - (x['y'] - Ly / 2) ** 2)
    return vec(x=val, y=val)

velocity = CenteredGrid(init_velocity, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=bounds)

def step(velocity, dt):
    advection_term = advect.differential(velocity, velocity, order=2)
    diffusion_term = diffuse.differential(velocity, nu)
    return velocity + dt * (advection_term + diffusion_term)

trj = [velocity.values.numpy(('x', 'y', 'vector'))]
for i in range(steps):
    velocity = step(velocity, dt)
    trj.append(velocity.values.numpy(('x', 'y', 'vector')))

trj = np.stack(trj, axis=0)
np.save('burgers2d_velocity_trj.npy', trj)