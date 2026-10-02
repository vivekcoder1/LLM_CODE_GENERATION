from phi.flow import *
import numpy as np

N = 256
domain = Box(x=(-2, 2), y=(-2, 2))
grid = UniformGrid(x=N, y=N, bounds=domain)
z_field = Field(grid, values=lambda x, y: x + 1j * y, boundary=0)
z = z_field.values

J = math.zeros(spatial(x=N, y=N))

domain_trj = []

for t in range(100):
    c = 0.7885 * math.exp(1j * 2 * np.pi * t / 100)
    z = z ** 2 + c
    escaped = math.abs(z) < 2
    J = J + escaped
    domain_trj.append(J.numpy(('x', 'y')))

domain_trj = np.stack(domain_trj, axis=0)
np.save('julia_set_domain_trj.npy', domain_trj)