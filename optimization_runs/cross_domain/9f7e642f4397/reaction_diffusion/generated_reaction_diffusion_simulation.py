from phi.flow import *
import numpy as np

Lx = 100.
Ly = 100.
Nx = 100
Ny = 100
dt = 0.5
Du = 0.19
Dv = 0.05
feed = 0.06
kill = 0.062
s = 3.

def init(x):
    r = math.vec_length(x - vec(x=Lx / 2, y=Ly / 2))
    return math.cos(r / s)

u = CenteredGrid(init, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=Box(x=Lx, y=Ly))
v = CenteredGrid(init, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=Box(x=Lx, y=Ly))

def step(u, v):
    u = diffuse.explicit(u, Du, dt)
    v = diffuse.explicit(v, Dv, dt)
    reaction_u = -u * v * v + feed * (1 - u)
    reaction_v = u * v * v - (feed + kill) * v
    u = u + dt * reaction_u
    v = v + dt * reaction_v
    return u, v

u_trj = [u.values.numpy(['x', 'y'])]
v_trj = [v.values.numpy(['x', 'y'])]

for i in range(100):
    u, v = step(u, v)
    u_trj.append(u.values.numpy(['x', 'y']))
    v_trj.append(v.values.numpy(['x', 'y']))

np.save('reaction_diffusion_u_trj.npy', np.stack(u_trj))
np.save('reaction_diffusion_v_trj.npy', np.stack(v_trj))