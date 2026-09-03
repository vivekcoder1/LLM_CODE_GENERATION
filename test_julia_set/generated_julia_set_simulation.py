import numpy as np
import math
from phi.flow import *

Nx = Ny = 256
domain = Box(x=(-2, 2), y=(-2, 2))

real = CenteredGrid(lambda pos: pos.vector['x'], bounds=domain, x=Nx, y=Ny)
imag = CenteredGrid(lambda pos: pos.vector['y'], bounds=domain, x=Nx, y=Ny)
J = CenteredGrid(0.0, bounds=domain, x=Nx, y=Ny)

domain_trj = []

for t in range(100):
    real_new = real * real - imag * imag
    imag_new = 2 * real * imag
    theta = 2 * math.pi * t / 100
    c_real = 0.7885 * math.cos(theta)
    c_imag = 0.7885 * math.sin(theta)
    real = real_new + c_real
    imag = imag_new + c_imag
    escape_mask = (real * real + imag * imag) < 4
    J = J + escape_mask
    domain_trj.append(J.values.numpy(['x', 'y']))

domain_trj = np.stack(domain_trj, axis=0)
np.save('julia_set_domain_trj.npy', domain_trj)