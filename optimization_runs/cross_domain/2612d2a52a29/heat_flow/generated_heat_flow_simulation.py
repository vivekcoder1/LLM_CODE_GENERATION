from phi.flow import *
import numpy as np

domain = Box(x=10, y=5)
resolution = spatial(x=100, y=50)

def kappa_init(x, y):
    in_band = (y >= 2) & (y <= 3)
    in_block = (x >= 4.5) & (x <= 5.5) & (y >= 1) & (y <= 4)
    inside = in_band | in_block
    return math.where(inside, 1.01, 0.01)

boundary = {'x': (1.0, extrapolation.ZERO_GRADIENT), 'y': extrapolation.PERIODIC}

temperature = CenteredGrid(0.0, boundary, bounds=domain, resolution=resolution)
kappa = CenteredGrid(kappa_init, extrapolation.PERIODIC, bounds=domain, resolution=resolution)

dt = 1.0

def step(u, dt):
    return diffuse.explicit(u, kappa, dt=dt)

temperature_trj = [temperature.values.numpy(('x', 'y'))]

for _ in range(100):
    temperature = step(temperature, dt)
    temperature_trj.append(temperature.values.numpy(('x', 'y')))

temperature_trj = np.stack(temperature_trj, axis=0)
np.save('heat_flow_temperature_trj.npy', temperature_trj)