from phi.flow import *
import numpy as np

Nx = 256
Ny = 256
domain = CenteredGrid(0, extrapolation.ZERO, x=Nx, y=Ny, bounds=Box(x=(-2, 2), y=(-2, 2)))
x_np = domain.points['x'].numpy('x,y')
y_np = domain.points['y'].numpy('x,y')

z = x_np + 1j * y_np
J = np.zeros((Nx, Ny), dtype=np.float64)
domain_trj = np.zeros((100, Nx, Ny), dtype=np.float64)

N_escape = 50

for t in range(100):
    c = 0.7885 * np.exp(1j * 2 * np.pi * t / 100)
    z = z ** 2 + c
    mask_escape = np.abs(z) < 2
    J = J + mask_escape.astype(np.float64)
    domain_trj[t] = J

np.save('julia_set_domain_trj.npy', domain_trj)