from phi.flow import *
import numpy as np

Nx = Ny = 256
bounds = Box(x=(-2, 2), y=(-2, 2))
resolution = spatial(x=Nx, y=Ny)

x_grid = CenteredGrid(lambda loc: loc.vector['x'], extrapolation=0.0, bounds=bounds, resolution=resolution)
y_grid = CenteredGrid(lambda loc: loc.vector['y'], extrapolation=0.0, bounds=bounds, resolution=resolution)

z_re = x_grid.values
z_im = y_grid.values

J = CenteredGrid(0.0, extrapolation=0.0, bounds=bounds, resolution=resolution).values

n_steps = 100
domain_trj = []

for t in range(n_steps):
    c = 0.7885 * np.exp(1j * 2 * np.pi * t / 100)
    c_re = float(c.real)
    c_im = float(c.imag)
    new_re = z_re * z_re - z_im * z_im + c_re
    new_im = 2.0 * z_re * z_im + c_im
    z_re = new_re
    z_im = new_im
    mag2 = z_re * z_re + z_im * z_im
    mask = (mag2 < 4.0) * 1.0
    J = J + mask
    domain_trj.append(J.numpy(['x', 'y']))

domain_trj = np.stack(domain_trj, axis=0)
np.save('julia_set_domain_trj.npy', domain_trj)