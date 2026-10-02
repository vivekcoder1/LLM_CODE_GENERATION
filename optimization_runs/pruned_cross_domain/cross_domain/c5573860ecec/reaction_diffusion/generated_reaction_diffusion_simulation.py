from phi.flow import *
from phi.flow import diffuse
import numpy as np

Lx, Ly = 100.0, 100.0
Nx, Ny = 100, 100
dt = 0.5
Du = 0.19
Dv = 0.05
feed = 0.06
kill = 0.062
s = 3.0
steps = 100

domain_bounds = Box(x=Lx, y=Ly)

def initial_field(x):
    center = vec(x=Lx / 2, y=Ly / 2)
    r = math.vec_length(x - center)
    return math.cos(r / s)

u = CenteredGrid(initial_field, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=domain_bounds)
v = CenteredGrid(initial_field, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=domain_bounds)

def step(u, v):
    diff_u = diffuse.differential(u, Du)
    diff_v = diffuse.differential(v, Dv)
    reaction = u * v ** 2
    u_next = u + dt * (diff_u - reaction + feed * (1 - u))
    v_next = v + dt * (diff_v + reaction - (feed + kill) * v)
    return u_next, v_next

u_trj = [u.values.numpy(['x', 'y'])]
v_trj = [v.values.numpy(['x', 'y'])]

for _ in range(steps):
    u, v = step(u, v)
    u_trj.append(u.values.numpy(['x', 'y']))
    v_trj.append(v.values.numpy(['x', 'y']))

u_trj = np.stack(u_trj)
v_trj = np.stack(v_trj)

np.save('reaction_diffusion_u_trj.npy', u_trj)
np.save('reaction_diffusion_v_trj.npy', v_trj)