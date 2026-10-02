from phi.flow import *
import numpy as np

Lx = Ly = 100
Nx = Ny = 100
dt = 0.5
Du = 0.19
Dv = 0.05
f = 0.06
k = 0.062
s = 3


def initial(x):
    center = vec(x=Lx / 2, y=Ly / 2)
    r = math.vec_length(x - center)
    return math.cos(r / s)


u = CenteredGrid(initial, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=Box(x=Lx, y=Ly))
v = CenteredGrid(initial, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=Box(x=Lx, y=Ly))


def step(u, v, dt):
    u_diff = diffuse.explicit(u, Du, dt)
    v_diff = diffuse.explicit(v, Dv, dt)
    reaction = u * v * v
    u_new = u_diff + dt * (-reaction + f * (1 - u))
    v_new = v_diff + dt * (reaction - (f + k) * v)
    return u_new, v_new


u_trj = [u.values.numpy(('x', 'y'))]
v_trj = [v.values.numpy(('x', 'y'))]

for _ in range(100):
    u, v = step(u, v, dt)
    u_trj.append(u.values.numpy(('x', 'y')))
    v_trj.append(v.values.numpy(('x', 'y')))

u_trj = np.stack(u_trj, axis=0)
v_trj = np.stack(v_trj, axis=0)

np.save('reaction_diffusion_u_trj.npy', u_trj)
np.save('reaction_diffusion_v_trj.npy', v_trj)