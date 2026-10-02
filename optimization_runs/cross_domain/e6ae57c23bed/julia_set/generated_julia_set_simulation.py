from phi.flow import *
import numpy as np

Nx = 256
Ny = 256

domain = CenteredGrid(0, extrapolation.ZERO, x=Nx, y=Ny, bounds=Box(x=(-2, 2), y=(-2, 2)))

points = domain.points
x_np = points.vector['x'].numpy(('x', 'y'))
y_np = points.vector['y'].numpy(('x', 'y'))

z = x_np + 1j * y_np
J = np.zeros((Nx, Ny), dtype=np.float64)

N_escape = 50
num_steps = 100

domain_trj = np.zeros((num_steps, Nx, Ny), dtype=np.float64)

for t in range(num_steps):
    c = 0.7885 * np.exp(1j * 2 * np.pi * t / 100)
    z = z ** 2 + c
    mask = np.abs(z) < 2
    J = J + mask.astype(np.float64)
    domain_trj[t] = J

np.save('julia_set_domain_trj.npy', domain_trj)