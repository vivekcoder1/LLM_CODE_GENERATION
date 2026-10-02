from phi.flow import *
import numpy as np

domain = Box(x=10, y=5)
resolution = spatial(x=100, y=50)

boundary = {'x-': 1.0, 'x+': extrapolation.ZERO_GRADIENT, 'y': extrapolation.PERIODIC}

def kappa_func(x):
    x_pos = x['x']
    y_pos = x['y']
    in_box1 = (y_pos >= 2) & (y_pos <= 3)
    in_box2 = (x_pos >= 4.5) & (x_pos <= 5.5) & (y_pos >= 1) & (y_pos <= 4)
    inside = in_box1 | in_box2
    return math.where(inside, 1.01, 0.01)

kappa = CenteredGrid(kappa_func, extrapolation=extrapolation.ZERO_GRADIENT, bounds=domain, resolution=resolution)

temperature = CenteredGrid(0.0, extrapolation=boundary, bounds=domain, resolution=resolution)

dt = 1.0
num_steps = 100

trajectory = [temperature.values.numpy(('x', 'y'))]

for _ in range(num_steps):
    diffusivity = vec(x=kappa.values, y=math.zeros_like(kappa.values))
    temperature = diffuse.explicit(temperature, diffusivity, dt)
    trajectory.append(temperature.values.numpy(('x', 'y')))

trajectory = np.stack(trajectory, axis=0)
np.save('heat_flow_temperature_trj.npy', trajectory)