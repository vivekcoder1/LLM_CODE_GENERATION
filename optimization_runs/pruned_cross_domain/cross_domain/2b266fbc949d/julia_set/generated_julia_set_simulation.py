import numpy as np
from phi.flow import *

Nx = Ny = 256
bounds = Box(x=(-2, 2), y=(-2, 2))
resolution = spatial(x=Nx, y=Ny)

x_field = CenteredGrid(lambda p: p.vector['x'], extrapolation.ZERO_GRADIENT, resolution=resolution, bounds=bounds)
y_field = CenteredGrid(lambda p: p.vector['y'], extrapolation.ZERO_GRADIENT, resolution=resolution, bounds=bounds)

X = x_field.values.numpy('x,y')
Y = y_field.values.numpy('x,y')

z = X + 1j * Y
J = np.zeros((Nx, Ny), dtype=np.float64)
domain_trj = np.zeros((100, Nx, Ny), dtype=np.float64)

for t in range(100):
    c = 0.7885 * np.exp(1j * 2 * np.pi * t / 100)
    z = z ** 2 + c
    J += (np.abs(z) < 2).astype(np.float64)
    domain_trj[t] = J

np.save('julia_set_domain_trj.npy', domain_trj)