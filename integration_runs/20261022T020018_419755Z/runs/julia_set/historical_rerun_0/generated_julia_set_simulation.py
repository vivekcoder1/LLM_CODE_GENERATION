from phi.flow import *
import numpy as np
import cmath

Nx = Ny = 256
bounds = Box(x=(-2, 2), y=(-2, 2))
resolution = spatial(x=Nx, y=Ny)

z_field = CenteredGrid(lambda pos: pos.vector['x'] + 1j * pos.vector['y'], extrapolation=0, bounds=bounds, resolution=resolution)
z = z_field.values

J = math.zeros(resolution)

domain_trj = []

for t in range(100):
    c = 0.7885 * cmath.exp(1j * 2 * cmath.pi * t / 100)
    z = z ** 2 + c
    escaped = abs(z) < 2
    J = J + escaped
    domain_trj.append(J.numpy(('x', 'y')))

domain_trj = np.stack(domain_trj, axis=0)
np.save('julia_set_domain_trj.npy', domain_trj)