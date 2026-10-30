import cmath
import numpy as np
from phi.flow import CenteredGrid, Box
from phi.math import spatial, zeros

Nx = Ny = 256
steps = 100
bounds = Box(x=(-2, 2), y=(-2, 2))
resolution = spatial(x=Nx, y=Ny)

z_field = CenteredGrid(
    lambda position: position.vector['x'] + 1j * position.vector['y'],
    extrapolation=0,
    bounds=bounds,
    resolution=resolution,
)

z = z_field.values
escape_count = zeros(resolution)

v_trj = []

for step in range(steps):
    c = 0.7885 * cmath.exp(1j * 2 * cmath.pi * step / steps)
    z = z ** 2 + c
    escape_count = escape_count + (abs(z) < 2)
    v_trj.append(escape_count.numpy('x,y'))

result = np.stack(v_trj, axis=0)
np.save('julia_set_domain_trj.npy', result)