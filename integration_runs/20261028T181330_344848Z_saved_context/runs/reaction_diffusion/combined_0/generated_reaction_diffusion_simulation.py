import numpy as np
from phi.flow import *
from phi import math, field

Lx = 100
Ly = 100
Nx = 100
Ny = 100
dt = 0.5
Du = 0.19
Dv = 0.05
feed_rate = 0.06
kill_rate = 0.062
s = 3

bounds = Box(x=Lx, y=Ly)
resolution = spatial(x=Nx, y=Ny)

def initial_condition(x):
    center = vec(x=Lx / 2, y=Ly / 2)
    radius = math.vec_length(x - center)
    return math.cos(radius / s)

u = CenteredGrid(initial_condition, extrapolation.PERIODIC, bounds=bounds, resolution=resolution)
v = CenteredGrid(initial_condition, extrapolation.PERIODIC, bounds=bounds, resolution=resolution)

u_trj = [u.values.numpy('x,y')]
v_trj = [v.values.numpy('x,y')]

for _ in range(100):
    reaction = u * v ** 2
    u_new = u + dt * (Du * field.laplace(u) - reaction + feed_rate * (1 - u))
    v_new = v + dt * (Dv * field.laplace(v) + reaction - (feed_rate + kill_rate) * v)
    u = u_new
    v = v_new
    u_trj.append(u.values.numpy('x,y'))
    v_trj.append(v.values.numpy('x,y'))

u_trj = np.stack(u_trj, axis=0)
v_trj = np.stack(v_trj, axis=0)

np.save('reaction_diffusion_u_trj.npy', u_trj)
np.save('reaction_diffusion_v_trj.npy', v_trj)