from phi.flow import *
import numpy as np
import cmath

domain = Box(x=(-2, 2), y=(-2, 2))
resolution = spatial(x=256, y=256)

z = CenteredGrid(lambda p: p.vector['x'] + 1j * p.vector['y'], extrapolation=0, bounds=domain, resolution=resolution)
J = CenteredGrid(0.0, extrapolation=0, bounds=domain, resolution=resolution)

domain_trj = []

for t in range(100):
    c_t = 0.7885 * cmath.exp(1j * 2 * cmath.pi * t / 100)
    z = z * z + c_t
    escaped_values = math.cast(abs(z.values) < 2, J.values.dtype)
    escaped_grid = CenteredGrid(escaped_values, extrapolation=0, bounds=domain, resolution=resolution)
    J = J + escaped_grid
    domain_trj.append(J.values.numpy(('x', 'y')))

domain_trj = np.stack(domain_trj, axis=0)
np.save('julia_set_domain_trj.npy', domain_trj)