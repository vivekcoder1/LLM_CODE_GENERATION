import numpy as np

Nx, Ny = 256, 256
x = np.linspace(-2, 2, Nx)
y = np.linspace(-2, 2, Ny)
X, Y = np.meshgrid(x, y, indexing='ij')
z0 = X + 1j * Y

N_escape = 50
T = 100

domain_trj = np.zeros((T, Nx, Ny), dtype=np.float64)

for t in range(T):
    c = 0.7885 * np.exp(1j * 2 * np.pi * t / 100)
    z = z0.copy()
    J = np.zeros((Nx, Ny), dtype=np.float64)
    for _ in range(N_escape):
        z = z ** 2 + c
        J += (np.abs(z) < 2).astype(np.float64)
    domain_trj[t] = J

np.save('julia_set_domain_trj.npy', domain_trj)