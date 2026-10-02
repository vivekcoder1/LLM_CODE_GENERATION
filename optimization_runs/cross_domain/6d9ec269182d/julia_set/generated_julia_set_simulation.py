import numpy as np
from phi.flow import *

Nx = 256
Ny = 256
domain = Box(x=(-2, 2), y=(-2, 2))
grid = CenteredGrid(lambda x: x, extrapolation=0, bounds=domain, resolution=spatial(x=Nx, y=Ny))

x_vals = grid.values.vector['x'].numpy(['x', 'y'])
y_vals = grid.values.vector['y'].numpy(['x', 'y'])

z = x_vals + 1j * y_vals

N_escape = 50
T = 100
J = np.zeros((Nx, Ny), dtype=np.float64)
domain_trj = np.zeros((T, Nx, Ny), dtype=np.float64)

for t in range(T):
    c = 0.7885 * np.exp(1j * 2 * np.pi * t / 100)
    z = z ** 2 + c
    mask = np.abs(z) < 2
    J = J + mask.astype(np.float64)
    domain_trj[t] = J

np.save('julia_set_domain_trj.npy', domain_trj)