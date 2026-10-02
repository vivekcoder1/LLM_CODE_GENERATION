from phi.flow import *
import numpy as np

domain = Box(x=(-2, 2), y=(-2, 2))
res = spatial(x=256, y=256)

x_grid = CenteredGrid(lambda x: x['x'], extrapolation=0, bounds=domain, resolution=res)
y_grid = CenteredGrid(lambda x: x['y'], extrapolation=0, bounds=domain, resolution=res)

z_re = x_grid.values.numpy(('x', 'y')).astype(np.float64)
z_im = y_grid.values.numpy(('x', 'y')).astype(np.float64)

N_x, N_y = 256, 256
N_escape = 50

J = np.zeros((N_x, N_y), dtype=np.float64)
domain_trj = np.zeros((100, N_x, N_y), dtype=np.float64)

for t in range(100):
    c_re = 0.7885 * np.cos(2 * np.pi * t / 100)
    c_im = 0.7885 * np.sin(2 * np.pi * t / 100)
    new_re = z_re * z_re - z_im * z_im + c_re
    new_im = 2 * z_re * z_im + c_im
    z_re, z_im = new_re, new_im
    mag = np.sqrt(z_re * z_re + z_im * z_im)
    mask = (mag < 2).astype(np.float64)
    J = J + mask
    domain_trj[t] = J

np.save('julia_set_domain_trj.npy', domain_trj)