from phi.flow import *
import numpy as np

Lx = 100
Ly = 100
Nx = 100
Ny = 100
s = 3
dt = 0.5
Du = 0.19
Dv = 0.05
f = 0.06
k = 0.062

def init(x):
    r = math.sqrt((x['x'] - Lx / 2) ** 2 + (x['y'] - Ly / 2) ** 2)
    return math.cos(r / s)

u = CenteredGrid(init, extrapolation.PERIODIC, bounds=Box(x=Lx, y=Ly), resolution=spatial(x=Nx, y=Ny))
v = CenteredGrid(init, extrapolation.PERIODIC, bounds=Box(x=Lx, y=Ly), resolution=spatial(x=Nx, y=Ny))

def step(u, v, dt):
    u_diff = diffuse.explicit(u, Du, dt)
    v_diff = diffuse.explicit(v, Dv, dt)
    reaction_u = -u.values * v.values ** 2 + f * (1 - u.values)
    reaction_v = u.values * v.values ** 2 - (f + k) * v.values
    u_new = u_diff + CenteredGrid(reaction_u * dt, extrapolation.PERIODIC, bounds=Box(x=Lx, y=Ly), resolution=spatial(x=Nx, y=Ny))
    v_new = v_diff + CenteredGrid(reaction_v * dt, extrapolation.PERIODIC, bounds=Box(x=Lx, y=Ly), resolution=spatial(x=Nx, y=Ny))
    return u_new, v_new

u_trj = [u.values.numpy(['x', 'y'])]
v_trj = [v.values.numpy(['x', 'y'])]

for _ in range(100):
    u, v = step(u, v, dt)
    u_trj.append(u.values.numpy(['x', 'y']))
    v_trj.append(v.values.numpy(['x', 'y']))

u_trj = np.stack(u_trj, axis=0)
v_trj = np.stack(v_trj, axis=0)

np.save('reaction_diffusion_u_trj.npy', u_trj)
np.save('reaction_diffusion_v_trj.npy', v_trj)