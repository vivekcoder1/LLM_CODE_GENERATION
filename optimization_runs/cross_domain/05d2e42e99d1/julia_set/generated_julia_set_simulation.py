from phi.flow import *
import numpy as np

Nx = Ny = 256
bounds = Box(x=(-2, 2), y=(-2, 2))
resolution = spatial(x=Nx, y=Ny)

def initial_z(x):
    return x.vector['x'] + 1j * x.vector['y']

z = CenteredGrid(initial_z, bounds=bounds, resolution=resolution)
J = CenteredGrid(0.0, bounds=bounds, resolution=resolution)

domain_trj = []

for t in range(100):
    c = 0.7885 * np.exp(1j * 2 * np.pi * t / 100)
    z = z * z + c
    escaped = abs(z) < 2
    J = J + escaped
    domain_trj.append(J.values.numpy(('x', 'y')))

domain_trj = np.stack(domain_trj, axis=0)
np.save('julia_set_domain_trj.npy', domain_trj)