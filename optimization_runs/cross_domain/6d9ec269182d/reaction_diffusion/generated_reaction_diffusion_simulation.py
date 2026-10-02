from phi.flow import *
import numpy as np

L_x = 100
L_y = 100
N_x = 100
N_y = 100
s = 3
dt = 0.5
D_u = 0.19
D_v = 0.05
f = 0.06
k = 0.062

bounds = Box(x=L_x, y=L_y)
res = spatial(x=N_x, y=N_y)

def initial_values(x):
    r = math.sqrt((x['x'] - L_x / 2) ** 2 + (x['y'] - L_y / 2) ** 2)
    return math.cos(r / s)

u = CenteredGrid(initial_values, extrapolation=extrapolation.PERIODIC, bounds=bounds, resolution=res)
v = CenteredGrid(initial_values, extrapolation=extrapolation.PERIODIC, bounds=bounds, resolution=res)

def step(u, v):
    diff_u = diffuse.differential(u, D_u)
    diff_v = diffuse.differential(v, D_v)
    reaction_u = -u * v ** 2 + f * (1 - u)
    reaction_v = u * v ** 2 - (f + k) * v
    u_new = u + dt * (diff_u + reaction_u)
    v_new = v + dt * (diff_v + reaction_v)
    return u_new, v_new

u_list = [u.values.numpy(('x', 'y'))]
v_list = [v.values.numpy(('x', 'y'))]

for _ in range(100):
    u, v = step(u, v)
    u_list.append(u.values.numpy(('x', 'y')))
    v_list.append(v.values.numpy(('x', 'y')))

u_trj = np.stack(u_list)
v_trj = np.stack(v_list)

np.save('reaction_diffusion_u_trj.npy', u_trj)
np.save('reaction_diffusion_v_trj.npy', v_trj)