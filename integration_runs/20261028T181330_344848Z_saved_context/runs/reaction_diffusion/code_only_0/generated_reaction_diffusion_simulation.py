from phi.flow import *
import numpy as np

Lx = 100.0
Ly = 100.0
Nx = 100
Ny = 100
dt = 0.5
Du = 0.19
Dv = 0.05
f = 0.06
k = 0.062
s = 3.0

bounds = Box(x=(0, Lx), y=(0, Ly))

def init_field(x, y):
    cx = Lx / 2.0
    cy = Ly / 2.0
    r = math.sqrt((x - cx)**2 + (y - cy)**2)
    return math.cos(r / s)

u = CenteredGrid(lambda x: math.cos(math.sqrt((x['x'] - Lx/2)**2 + (x['y'] - Ly/2)**2) / s),
                 extrapolation.PERIODIC,
                 bounds=bounds,
                 resolution=spatial(x=Nx, y=Ny))

v = CenteredGrid(lambda x: math.cos(math.sqrt((x['x'] - Lx/2)**2 + (x['y'] - Ly/2)**2) / s),
                 extrapolation.PERIODIC,
                 bounds=bounds,
                 resolution=spatial(x=Nx, y=Ny))

def get_numpy(field):
    return field.values.numpy(['x', 'y'])

u_trj = [get_numpy(u)]
v_trj = [get_numpy(v)]

for _ in range(100):
    lap_u = diffuse.explicit(u, Du, dt, substeps=1)
    lap_v = diffuse.explicit(v, Dv, dt, substeps=1)
    
    u_val = u.values
    v_val = v.values
    
    reaction_u = -(u_val * v_val * v_val) + f * (1.0 - u_val)
    reaction_v = (u_val * v_val * v_val) - (f + k) * v_val
    
    u_new_values = lap_u.values + dt * reaction_u
    v_new_values = lap_v.values + dt * reaction_v
    
    u = CenteredGrid(u_new_values, extrapolation.PERIODIC, bounds=bounds, resolution=spatial(x=Nx, y=Ny))
    v = CenteredGrid(v_new_values, extrapolation.PERIODIC, bounds=bounds, resolution=spatial(x=Nx, y=Ny))
    
    u_trj.append(get_numpy(u))
    v_trj.append(get_numpy(v))

u_array = np.array(u_trj)
v_array = np.array(v_trj)

np.save('reaction_diffusion_u_trj.npy', u_array)
np.save('reaction_diffusion_v_trj.npy', v_array)