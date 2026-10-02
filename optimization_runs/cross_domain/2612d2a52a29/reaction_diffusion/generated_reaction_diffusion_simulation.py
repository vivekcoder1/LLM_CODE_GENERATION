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

x_coords = np.linspace(0, Lx, Nx, endpoint=False) + Lx / (2 * Nx)
y_coords = np.linspace(0, Ly, Ny, endpoint=False) + Ly / (2 * Ny)
xx, yy = np.meshgrid(x_coords, y_coords, indexing='ij')
r = np.sqrt((xx - Lx / 2) ** 2 + (yy - Ly / 2) ** 2)
init_values = np.cos(r / s)

u_tensor = math.tensor(init_values, spatial('x,y'))
v_tensor = math.tensor(init_values, spatial('x,y'))

bounds = Box(x=Lx, y=Ly)

u = CenteredGrid(u_tensor, extrapolation=extrapolation.PERIODIC, bounds=bounds, resolution=spatial(x=Nx, y=Ny))
v = CenteredGrid(v_tensor, extrapolation=extrapolation.PERIODIC, bounds=bounds, resolution=spatial(x=Nx, y=Ny))

def step(u, v):
    u_diffused = diffuse.explicit(u, Du, dt)
    v_diffused = diffuse.explicit(v, Dv, dt)
    reaction_u = -u.values * v.values ** 2 + f * (1 - u.values)
    reaction_v = u.values * v.values ** 2 - (f + k) * v.values
    u_new = u_diffused + dt * reaction_u
    v_new = v_diffused + dt * reaction_v
    return u_new, v_new

u_trj = [u.values.numpy('x,y')]
v_trj = [v.values.numpy('x,y')]

for _ in range(100):
    u, v = step(u, v)
    u_trj.append(u.values.numpy('x,y'))
    v_trj.append(v.values.numpy('x,y'))

u_trj = np.stack(u_trj, axis=0)
v_trj = np.stack(v_trj, axis=0)

np.save('reaction_diffusion_u_trj.npy', u_trj)
np.save('reaction_diffusion_v_trj.npy', v_trj)