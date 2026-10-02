import numpy as np
import math
from phi.flow import *

Nx = 256
Ny = 256
bounds = Box(x=(-2, 2), y=(-2, 2))

z_real = CenteredGrid(lambda x: x['x'], extrapolation=0, bounds=bounds, x=Nx, y=Ny)
z_imag = CenteredGrid(lambda x: x['y'], extrapolation=0, bounds=bounds, x=Nx, y=Ny)
J = CenteredGrid(0, extrapolation=0, bounds=bounds, x=Nx, y=Ny)

domain_trj = []

for t in range(100):
    theta = 2 * math.pi * t / 100
    c_real = 0.7885 * math.cos(theta)
    c_imag = 0.7885 * math.sin(theta)
    new_real = z_real * z_real - z_imag * z_imag + c_real
    new_imag = 2 * z_real * z_imag + c_imag
    z_real = new_real
    z_imag = new_imag
    mag_sq = z_real * z_real + z_imag * z_imag
    mask = mag_sq < 4
    J = J + mask
    domain_trj.append(J.values.numpy(('x', 'y')))

domain_trj = np.stack(domain_trj, axis=0)
np.save('julia_set_domain_trj.npy', domain_trj)