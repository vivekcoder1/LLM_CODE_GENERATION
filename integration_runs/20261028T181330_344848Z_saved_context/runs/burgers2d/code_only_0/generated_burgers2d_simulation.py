from phi.flow import *
import numpy as np

Lx = 40
Ly = 20
Nx = 64
Ny = 64
nu = 0.1
dt = 0.5
num_steps = 100

grid = UniformGrid(spatial(x=Nx, y=Ny), Box(x=(0, Lx), y=(0, Ly)))

def gaussian_init(x, y):
    return math.exp(-((x - Lx/2)**2 + (y - Ly/2)**2))

velocity = Field(grid, values=lambda x, y: math.stack([gaussian_init(x, y), gaussian_init(x, y)], channel(vector='x,y')), boundary=PERIODIC)

def step(vel, dt):
    adv = advect.differential(vel, vel, order=2)
    diff = diffuse.differential(vel, nu, order=2)
    return vel + dt * (adv + diff)

snapshots = [velocity.values.numpy(order='x,y,vector')]

vel = velocity
for i in range(num_steps):
    vel = step(vel, dt)
    snapshots.append(vel.values.numpy(order='x,y,vector'))

velocity_trj = np.stack(snapshots, axis=0)
np.save('burgers2d_velocity_trj.npy', velocity_trj)