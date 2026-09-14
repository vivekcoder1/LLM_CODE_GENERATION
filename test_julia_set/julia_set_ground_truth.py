from phi.flow import *
import cmath
import numpy as np


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
escape_count = math.zeros(resolution)
trajectory = []

for step in range(steps):
    c = 0.7885 * cmath.exp(1j * 2 * cmath.pi * step / steps)
    z = z ** 2 + c
    escape_count = escape_count + (abs(z) < 2)
    trajectory.append(escape_count.numpy(('x', 'y')))

v_trj = np.stack(trajectory, axis=0)