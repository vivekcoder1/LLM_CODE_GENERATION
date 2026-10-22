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
res = spatial(x=Nx, y=Ny)

def init_field(x):
    center = vec(x=Lx / 2, y=Ly / 2)
    r = math.vec_length(x - center)
    return math.cos(r / s)

u = CenteredGrid(init_field, extrapolation.PERIODIC, bounds=bounds, resolution=res)
v = CenteredGrid(init_field, extrapolation.PERIODIC, bounds=bounds, resolution=res)

u_trj = [u.values.numpy(['x', 'y'])]
v_trj = [v.values.numpy(['x', 'y'])]

for i in range(100):
    diffusion_u = diffuse.explicit(u, Du, dt)
    diffusion_v = diffuse.explicit(v, Dv, dt)
    reaction_u = -u * v ** 2 + f * (1 - u)
    reaction_v = u * v ** 2 - (f + k) * v
    u = diffusion_u + dt * reaction_u
    v = diffusion_v + dt * reaction_v
    u_trj.append(u.values.numpy(['x', 'y']))
    v_trj.append(v.values.numpy(['x', 'y']))

np.save('reaction_diffusion_u_trj.npy', np.stack(u_trj))
np.save('reaction_diffusion_v_trj.npy', np.stack(v_trj))