from phi.flow import *
import numpy as np

Lx = Ly = 100.0
Nx = Ny = 100
dt = 0.5
Du = 0.19
Dv = 0.05
f = 0.06
k = 0.062
s = 3.0

def initial(x):
    dx = x['x'] - Lx / 2
    dy = x['y'] - Ly / 2
    r = math.sqrt(dx ** 2 + dy ** 2)
    return math.cos(r / s)

domain_bounds = Box(x=Lx, y=Ly)

u = CenteredGrid(initial, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=domain_bounds)
v = CenteredGrid(initial, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=domain_bounds)

def step(u, v):
    diff_u = diffuse.differential(u, Du)
    diff_v = diffuse.differential(v, Dv)
    reaction = u * v * v
    u_next = u + dt * (diff_u - reaction + f * (1 - u))
    v_next = v + dt * (diff_v + reaction - (f + k) * v)
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