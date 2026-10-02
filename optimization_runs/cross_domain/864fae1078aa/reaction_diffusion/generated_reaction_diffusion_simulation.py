from phi.flow import *
from phi.flow import diffuse
import numpy as np

Lx = 100
Ly = 100
Nx = 100
Ny = 100
dt = 0.5
Du = 0.19
Dv = 0.05
f = 0.06
k = 0.062
s = 3

domain = Box(x=Lx, y=Ly)

def initial(x):
    r = math.sqrt((x['x'] - Lx / 2) ** 2 + (x['y'] - Ly / 2) ** 2)
    return math.cos(r / s)

u = CenteredGrid(initial, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=domain)
v = CenteredGrid(initial, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=domain)

u_trj = [u.values.numpy(['x', 'y'])]
v_trj = [v.values.numpy(['x', 'y'])]

for step in range(100):
    reaction_u = -u * v ** 2 + f * (1 - u)
    reaction_v = u * v ** 2 - (f + k) * v
    u_diff = diffuse.explicit(u, Du, dt)
    v_diff = diffuse.explicit(v, Dv, dt)
    u = u_diff + dt * reaction_u
    v = v_diff + dt * reaction_v
    u_trj.append(u.values.numpy(['x', 'y']))
    v_trj.append(v.values.numpy(['x', 'y']))

u_trj = np.stack(u_trj, axis=0)
v_trj = np.stack(v_trj, axis=0)

np.save('reaction_diffusion_u_trj.npy', u_trj)
np.save('reaction_diffusion_v_trj.npy', v_trj)