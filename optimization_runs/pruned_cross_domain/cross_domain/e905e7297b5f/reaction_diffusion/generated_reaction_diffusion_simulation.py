from phi.flow import *
import numpy as np

Lx = Ly = 100
Nx = Ny = 100
dt = 0.5
Du = 0.19
Dv = 0.05
f = 0.06
k = 0.062

def initial(x):
    r = math.sqrt((x['x'] - Lx / 2) ** 2 + (x['y'] - Ly / 2) ** 2)
    return math.cos(r / 3)

bounds = Box(x=Lx, y=Ly)

u = CenteredGrid(initial, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=bounds)
v = CenteredGrid(initial, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=bounds)

def step(u, v, dt):
    reaction_u = -(u * v * v) + f * (1 - u)
    reaction_v = (u * v * v) - (f + k) * v
    diffusion_u = diffuse.differential(u, Du)
    diffusion_v = diffuse.differential(v, Dv)
    u_new = u + dt * (diffusion_u + reaction_u)
    v_new = v + dt * (diffusion_v + reaction_v)
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