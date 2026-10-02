import numpy as np
from phi.flow import *

Lx = 100.
Ly = 100.
Nx = 100
Ny = 100
dt = 0.5
Du = 0.19
Dv = 0.05
f = 0.06
k = 0.062
s = 3.

domain = Box(x=Lx, y=Ly)

def init(x):
    r = math.sqrt((x['x'] - Lx / 2) ** 2 + (x['y'] - Ly / 2) ** 2)
    return math.cos(r / s)

u = CenteredGrid(init, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=domain)
v = CenteredGrid(init, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=domain)

u_trj = [u.values.numpy(['x', 'y'])]
v_trj = [v.values.numpy(['x', 'y'])]

def step(u, v):
    u_new = diffuse.explicit(u, Du, dt) + dt * (-u * v ** 2 + f * (1 - u))
    v_new = diffuse.explicit(v, Dv, dt) + dt * (u * v ** 2 - (f + k) * v)
    return u_new, v_new

for i in range(100):
    u, v = step(u, v)
    u_trj.append(u.values.numpy(['x', 'y']))
    v_trj.append(v.values.numpy(['x', 'y']))

u_trj = np.stack(u_trj)
v_trj = np.stack(v_trj)

np.save('reaction_diffusion_u_trj.npy', u_trj)
np.save('reaction_diffusion_v_trj.npy', v_trj)