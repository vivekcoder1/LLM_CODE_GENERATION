from phi.flow import *
import cmath
import numpy as np

Nx = Ny = 256
bounds = Box(x=(-2, 2), y=(-2, 2))

def init_z(x):
    return x.vector['x'] + 1j * x.vector['y']

z = CenteredGrid(init_z, extrapolation.ZERO, x=Nx, y=Ny, bounds=bounds)
J = CenteredGrid(0.0, extrapolation.ZERO, x=Nx, y=Ny, bounds=bounds)

domain_trj = []

for t in range(100):
    c = 0.7885 * cmath.exp(1j * 2 * cmath.pi * t / 100)
    z = z * z + c
    escaped = abs(z) < 2
    J = J + escaped * 1.0
    domain_trj.append(J.values.numpy(('x', 'y')))

domain_trj = np.stack(domain_trj, axis=0)
np.save('julia_set_domain_trj.npy', domain_trj)