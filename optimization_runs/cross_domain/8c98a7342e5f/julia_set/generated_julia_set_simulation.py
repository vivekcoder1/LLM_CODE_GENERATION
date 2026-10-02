from phi.flow import *
import numpy as np

domain = Box(x=(-2, 2), y=(-2, 2))
grid = CenteredGrid(0, extrapolation.ZERO, bounds=domain, resolution=spatial(x=256, y=256))
points = grid.points

x_np = points.vector['x'].numpy(('y', 'x'))
y_np = points.vector['y'].numpy(('y', 'x'))

z = x_np + 1j * y_np
J = np.zeros_like(x_np, dtype=np.float64)
domain_trj = np.zeros((100, 256, 256), dtype=np.float64)

for t in range(100):
    c = 0.7885 * np.exp(1j * 2 * np.pi * t / 100)
    z = z ** 2 + c
    mask = np.abs(z) < 2
    J = J + mask.astype(np.float64)
    domain_trj[t] = J

np.save('julia_set_domain_trj.npy', domain_trj)