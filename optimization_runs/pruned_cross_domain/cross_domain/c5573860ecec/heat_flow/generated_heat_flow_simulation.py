from phi.flow import *
import numpy as np

domain = Box(x=10, y=5)
resolution = spatial(x=100, y=50)

box1 = Box(x=(0, 10), y=(2, 3))
box2 = Box(x=(4.5, 5.5), y=(1, 4))
inclusion = box1 | box2

kappa_mask = CenteredGrid(inclusion, extrapolation=0.0, bounds=domain, resolution=resolution)
kappa = 0.01 + (1.01 - 0.01) * kappa_mask

boundary = {'x-': 1.0, 'x+': ZERO_GRADIENT, 'y': PERIODIC}

temperature = CenteredGrid(0.0, boundary=boundary, bounds=domain, resolution=resolution)

dt = 1.0

def step(u, kappa, dt):
    return diffuse.explicit(u, kappa, dt)

trajectory = [temperature.values.numpy(['x', 'y'])]

for _ in range(100):
    temperature = step(temperature, kappa, dt)
    trajectory.append(temperature.values.numpy(['x', 'y']))

trajectory = np.stack(trajectory, axis=0)
np.save('heat_flow_temperature_trj.npy', trajectory)