from phi.flow import *
import numpy as np

domain = Box(x=10, y=5)
res = spatial(x=100, y=50)

def kappa_func(x, y):
    in_box1 = (y >= 2) & (y <= 3)
    in_box2 = (x >= 4.5) & (x <= 5.5) & (y >= 1) & (y <= 4)
    inside = in_box1 | in_box2
    return math.where(inside, 1.01, 0.01)

kappa = CenteredGrid(kappa_func, extrapolation.ZERO_GRADIENT, x=100, y=50, bounds=domain)

diffusivity = kappa * vec(x=1, y=0)

boundary = {'x': (1.0, extrapolation.ZERO_GRADIENT), 'y': extrapolation.PERIODIC}

temperature = CenteredGrid(0.0, boundary, x=100, y=50, bounds=domain)

dt = 1.0
num_steps = 100

def step(u):
    return diffuse.explicit(u, diffusivity, dt)

trj = [temperature.values.numpy(('x', 'y'))]

for _ in range(num_steps):
    temperature = step(temperature)
    trj.append(temperature.values.numpy(('x', 'y')))

temperature_trj = np.stack(trj, axis=0)
np.save('heat_flow_trj.npy', temperature_trj)