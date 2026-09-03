from phi.flow import *
import numpy as np

Lx = Ly = 100
Nx = Ny = 100
Du = 0.19
Dv = 0.05
feed = 0.06
kill = 0.062
dt = 0.5
s = 3

def initial_condition(x):
    r = math.vec_length(x - vec(x=Lx / 2, y=Ly / 2))
    return math.cos(r / s)

domain = Box(x=Lx, y=Ly)

u = CenteredGrid(initial_condition, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=domain)
v = CenteredGrid(initial_condition, extrapolation.PERIODIC, x=Nx, y=Ny, bounds=domain)

u_trj = [u.values.numpy(('x', 'y'))]
v_trj = [v.values.numpy(('x', 'y'))]

for step in range(100):
    diffused_u = diffuse.explicit(u, Du, dt)
    diffused_v = diffuse.explicit(v, Dv, dt)
    reaction_u = -u * v ** 2 + feed * (1 - u)
    reaction_v = u * v ** 2 - (feed + kill) * v
    u = diffused_u + dt * reaction_u
    v = diffused_v + dt * reaction_v
    u_trj.append(u.values.numpy(('x', 'y')))
    v_trj.append(v.values.numpy(('x', 'y')))

u_trj = np.stack(u_trj)
v_trj = np.stack(v_trj)

np.save('reaction_diffusion_u_trj.npy', u_trj)
np.save('reaction_diffusion_v_trj.npy', v_trj)