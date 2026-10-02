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

bounds = Box(x=Lx, y=Ly)
resolution = spatial(x=Nx, y=Ny)

def initial_condition(x):
    r = math.vec_length(x - vec(x=Lx / 2, y=Ly / 2))
    return math.cos(r / s)

u = CenteredGrid(initial_condition, extrapolation.PERIODIC, bounds=bounds, resolution=resolution)
v = CenteredGrid(initial_condition, extrapolation.PERIODIC, bounds=bounds, resolution=resolution)

def step(u, v, dt):
    u_diff = diffuse.explicit(u, Du, dt)
    v_diff = diffuse.explicit(v, Dv, dt)
    reaction_u = -u_diff * v_diff ** 2 + f * (1 - u_diff)
    reaction_v = u_diff * v_diff ** 2 - (f + k) * v_diff
    u_next = u_diff + dt * reaction_u
    v_next = v_diff + dt * reaction_v
    return u_next, v_next

u_trj = [u.values.numpy('x,y')]
v_trj = [v.values.numpy('x,y')]

for i in range(100):
    u, v = step(u, v, dt)
    u_trj.append(u.values.numpy('x,y'))
    v_trj.append(v.values.numpy('x,y'))

u_trj = np.stack(u_trj)
v_trj = np.stack(v_trj)

np.save('reaction_diffusion_u_trj.npy', u_trj)
np.save('reaction_diffusion_v_trj.npy', v_trj)