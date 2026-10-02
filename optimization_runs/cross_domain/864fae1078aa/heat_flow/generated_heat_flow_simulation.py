from phi.flow import CenteredGrid, Box, vec, spatial, extrapolation, diffuse, math
import numpy as np

resolution = spatial(x=100, y=50)
bounds = Box(x=10, y=5)

boundary = extrapolation.combine_sides(
    x=(1.0, extrapolation.ZERO_GRADIENT),
    y=extrapolation.PERIODIC
)

def kappa_values(x):
    x_pos = x.vector['x']
    y_pos = x.vector['y']
    in_box1 = (y_pos >= 2) & (y_pos <= 3)
    in_box2 = (x_pos >= 4.5) & (x_pos <= 5.5) & (y_pos >= 1) & (y_pos <= 4)
    inside = in_box1 | in_box2
    return math.where(inside, 1.01, 0.01)

kappa = CenteredGrid(kappa_values, extrapolation.ZERO_GRADIENT, bounds, resolution=resolution)
temperature = CenteredGrid(0.0, boundary, bounds, resolution=resolution)

def step(u, kappa_field, dt=1.0):
    diffusivity = kappa_field * vec(x=1, y=0)
    return diffuse.explicit(u, diffusivity=diffusivity, dt=dt)

trajectory = [temperature.values.numpy(('x', 'y'))]
for _ in range(100):
    temperature = step(temperature, kappa, dt=1.0)
    trajectory.append(temperature.values.numpy(('x', 'y')))

trajectory = np.stack(trajectory)
np.save('heat_flow_temperature_trj.npy', trajectory)