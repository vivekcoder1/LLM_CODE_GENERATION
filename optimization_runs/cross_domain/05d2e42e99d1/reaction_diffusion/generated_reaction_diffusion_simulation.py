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

center = vec(x=Lx / 2, y=Ly / 2)

def init(x):
    dx = x - center
    r = math.sqrt(math.sum(dx ** 2, 'vector'))
    return math.cos(r / 3)

DOMAIN = dict(x=Nx, y=Ny, bounds=Box(x=Lx, y=Ly))

u = CenteredGrid(init, extrapolation.PERIODIC, **DOMAIN)
v = CenteredGrid(init, extrapolation.PERIODIC, **DOMAIN)

def step(u, v):
    reaction_u = -u * v ** 2 + f * (1 - u)
    reaction_v = u * v ** 2 - (f + k) * v
    u_next = diffuse.explicit(u, Du, dt) + dt * reaction_u
    v_next = diffuse.explicit(v, Dv, dt) + dt * reaction_v
    return u_next, v_next

u_trj = [u.values.numpy(['x', 'y'])]
v_trj = [v.values.numpy(['x', 'y'])]

for _ in range(100):
    u, v = step(u, v)
    u_trj.append(u.values.numpy(['x', 'y']))
    v_trj.append(v.values.numpy(['x', 'y']))

u_trj = np.stack(u_trj, axis=0)
v_trj = np.stack(v_trj, axis=0)

np.save('reaction_diffusion_u_trj.npy', u_trj)
np.save('reaction_diffusion_v_trj.npy', v_trj)