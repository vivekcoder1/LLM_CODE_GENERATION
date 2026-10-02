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

domain = Box(x=Lx, y=Ly)

def init(x):
    dx = x.vector['x'] - Lx / 2
    dy = x.vector['y'] - Ly / 2
    r = math.sqrt(dx ** 2 + dy ** 2)
    return math.cos(r / s)

u = CenteredGrid(init, extrapolation=extrapolation.PERIODIC, bounds=domain, resolution=spatial(x=Nx, y=Ny))
v = CenteredGrid(init, extrapolation=extrapolation.PERIODIC, bounds=domain, resolution=spatial(x=Nx, y=Ny))

def step(u, v, dt):
    u = diffuse.explicit(u, Du, dt)
    v = diffuse.explicit(v, Dv, dt)
    reaction_u = -u * v ** 2 + f * (1 - u)
    reaction_v = u * v ** 2 - (f + k) * v
    u = u + dt * reaction_u
    v = v + dt * reaction_v
    return u, v

u_trj = [u.values.numpy(('x', 'y'))]
v_trj = [v.values.numpy(('x', 'y'))]

for i in range(100):
    u, v = step(u, v, dt)
    u_trj.append(u.values.numpy(('x', 'y')))
    v_trj.append(v.values.numpy(('x', 'y')))

np.save('reaction_diffusion_u_trj.npy', np.stack(u_trj))
np.save('reaction_diffusion_v_trj.npy', np.stack(v_trj))