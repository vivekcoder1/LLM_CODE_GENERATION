import numpy as np

Nx = Ny = 256
x = np.linspace(-2, 2, Nx)
y = np.linspace(-2, 2, Ny)
X, Y = np.meshgrid(x, y, indexing='ij')
z0 = X + 1j * Y

N_steps = 100
N_escape = 50

domain_trj = np.zeros((N_steps, Nx, Ny), dtype=np.float64)

z = z0.copy()
J = np.zeros((Nx, Ny), dtype=np.float64)

for t in range(N_steps):
    c = 0.7885 * np.exp(1j * 2 * np.pi * t / 100)
    z = z ** 2 + c
    mask = np.abs(z) < 2
    J = J + mask.astype(np.float64)
    domain_trj[t] = J

np.save('julia_set_domain_trj.npy', domain_trj)