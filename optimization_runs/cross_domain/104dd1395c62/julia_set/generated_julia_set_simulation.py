from phi.flow import *
import numpy as np

Nx, Ny = 256, 256
N_escape = 50
n_steps = 100

x = math.tensor(np.linspace(-2, 2, Nx), spatial('x'))
y = math.tensor(np.linspace(-2, 2, Ny), spatial('y'))

zr = x + 0.0 * y
zi = 0.0 * x + y

J = math.zeros(spatial(x=Nx, y=Ny))

domain_trj = []

for t in range(n_steps):
    theta = 2 * np.pi * t / 100
    c_r = 0.7885 * np.cos(theta)
    c_i = 0.7885 * np.sin(theta)
    zr_new = zr * zr - zi * zi + c_r
    zi_new = 2 * zr * zi + c_i
    zr, zi = zr_new, zi_new
    mag_sq = zr * zr + zi * zi
    mask = math.where(mag_sq < 4.0, 1.0, 0.0)
    J = J + mask
    domain_trj.append(J.numpy(order='x,y'))

domain_trj = np.stack(domain_trj, axis=0)
np.save('julia_set_domain_trj.npy', domain_trj)