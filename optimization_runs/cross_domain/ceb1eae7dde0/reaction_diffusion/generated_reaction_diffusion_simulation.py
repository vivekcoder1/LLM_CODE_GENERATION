from phi.flow import *
import numpy as np

Lx = Ly = 100.0
Nx = Ny = 100
dt = 0.5
Du = 0.19
Dv = 0.05
feed = 0.06
kill = 0.062
s = 3.0

def init_field(x):
    r = math.sqrt((x['x'] - Lx / 2) ** 2 + (x['y'] - Ly / 2) ** 2)
    return math.cos(r / s)

bounds = Box(x=Lx, y=Ly)
resolution = spatial(x=Nx, y=Ny)

u = CenteredGrid(init_field, extrapolation.PERIODIC, bounds=bounds, resolution=resolution)
v = CenteredGrid(init_field, extrapolation.PERIODIC, bounds=bounds, resolution=resolution)

def step(u, v):
    diff_u = diffuse.differential(u, Du)
    diff_v = diffuse.differential(v, Dv)
    reaction = u * v * v
    u_next = u + dt * (diff_u - reaction + feed * (1 - u))
    v_next = v + dt * (diff_v + reaction - (feed + kill) * v)
    return u_next, v_next

u_trj = [u.values.numpy(['x', 'y'])]
v_trj = [v.values.numpy(['x', 'y'])]

for i in range(100):
    u, v = step(u, v)
    u_trj.append(u.values.numpy(['x', 'y']))
    v_trj.append(v.values.numpy(['x', 'y']))

u_trj = np.stack(u_trj, axis=0)
v_trj = np.stack(v_trj, axis=0)

np.save('reaction_diffusion_u_trj.npy', u_trj)
np.save('reaction_diffusion_v_trj.npy', v_trj)