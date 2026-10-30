from phi.flow import *
import numpy as np

PERIODIC = extrapolation.PERIODIC

dt = 0.5
nu = 0.1
Lx = 40
Ly = 20
Nx = 64
Ny = 64

def gaussian_init(x):
    cx = Lx / 2.0
    cy = Ly / 2.0
    r2 = (x['x'] - cx) ** 2 + (x['y'] - cy) ** 2
    return math.exp(-r2)

v = CenteredGrid(
    lambda x: math.stack([math.exp(-((x['x'] - Lx/2)**2 + (x['y'] - Ly/2)**2)),
                           math.exp(-((x['x'] - Lx/2)**2 + (x['y'] - Ly/2)**2))], channel(vector='x,y')),
    extrapolation.PERIODIC,
    x=Nx, y=Ny,
    bounds=Box(x=Lx, y=Ly)
)

snapshots = [v.values.numpy('x,y,vector')]

for _ in range(100):
    v = diffuse.implicit(v, nu, dt=dt)
    v = advect.semi_lagrangian(v, v, dt=dt)
    snapshots.append(v.values.numpy('x,y,vector'))

velocity_trj = np.stack(snapshots, axis=0)
np.save('burgers2d_velocity_trj.npy', velocity_trj)