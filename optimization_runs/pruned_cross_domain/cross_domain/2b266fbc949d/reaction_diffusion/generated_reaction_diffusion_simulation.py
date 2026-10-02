from phi.flow import *
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

domain_bounds = Box(x=Lx, y=Ly)
resolution = spatial(x=Nx, y=Ny)

def init_field(x):
    r = math.sqrt((x['x'] - Lx / 2) ** 2 + (x['y'] - Ly / 2) ** 2)
    return math.cos(r / s)

u = CenteredGrid(init_field, extrapolation=extrapolation.PERIODIC, bounds=domain_bounds, resolution=resolution)
v = CenteredGrid(init_field, extrapolation=extrapolation.PERIODIC, bounds=domain_bounds, resolution=resolution)

u_trj = [u.values.numpy(['x', 'y'])]
v_trj = [v.values.numpy(['x', 'y'])]

for step in range(100):
    diffusion_u = diffuse.explicit(u, Du, dt)
    diffusion_v = diffuse.explicit(v, Dv, dt)
    reaction_u = -u * v * v + f * (1 - u)
    reaction_v = u * v * v - (f + k) * v
    u = diffusion_u + dt * reaction_u
    v = diffusion_v + dt * reaction_v
    u_trj.append(u.values.numpy(['x', 'y']))
    v_trj.append(v.values.numpy(['x', 'y']))

u_trj = np.stack(u_trj)
v_trj = np.stack(v_trj)

np.save('reaction_diffusion_u_trj.npy', u_trj)
np.save('reaction_diffusion_v_trj.npy', v_trj)