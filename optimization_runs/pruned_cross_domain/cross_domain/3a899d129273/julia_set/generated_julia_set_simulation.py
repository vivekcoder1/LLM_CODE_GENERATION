from phi.flow import CenteredGrid, Box, spatial
import numpy as np
import math as pymath

N = 256
bounds = Box(x=(-2, 2), y=(-2, 2))
res = spatial(x=N, y=N)

zr = CenteredGrid(lambda x: x['x'], extrapolation=0.0, bounds=bounds, resolution=res)
zi = CenteredGrid(lambda x: x['y'], extrapolation=0.0, bounds=bounds, resolution=res)
J = CenteredGrid(0.0, extrapolation=0.0, bounds=bounds, resolution=res)

domain_trj = []

for t in range(100):
    c_real = 0.7885 * pymath.cos(2 * pymath.pi * t / 100)
    c_imag = 0.7885 * pymath.sin(2 * pymath.pi * t / 100)
    zr_new = zr * zr - zi * zi + c_real
    zi_new = 2 * zr * zi + c_imag
    zr = zr_new
    zi = zi_new
    mag_sq = zr * zr + zi * zi
    escaped = mag_sq < 4.0
    J = J + escaped
    domain_trj.append(J.values.numpy(['x', 'y']))

domain_trj = np.stack(domain_trj)
np.save('julia_set_domain_trj.npy', domain_trj)