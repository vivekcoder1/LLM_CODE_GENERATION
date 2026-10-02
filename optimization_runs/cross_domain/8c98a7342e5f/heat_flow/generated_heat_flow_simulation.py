from phi.flow import *
import numpy as np

domain = Box(x=10, y=5)
resolution = spatial(x=100, y=50)

boundary = extrapolation.combine_sides(
    x=(extrapolation.ConstantExtrapolation(1.0), extrapolation.ZERO_GRADIENT),
    y=extrapolation.PERIODIC
)

def kappa_func(x):
    xs = x['x']
    ys = x['y']
    in_box1 = (xs >= 0) & (xs <= 10) & (ys >= 2) & (ys <= 3)
    in_box2 = (xs >= 4.5) & (xs <= 5.5) & (ys >= 1) & (ys <= 4)
    inside = in_box1 | in_box2
    return math.where(inside, 1.01, 0.01)

kappa = CenteredGrid(kappa_func, extrapolation.ZERO_GRADIENT, bounds=domain, resolution=resolution)

temperature = CenteredGrid(0.0, boundary, bounds=domain, resolution=resolution)

dt = 1.0
num_steps = 100

trajectory = [temperature.values.numpy(['x', 'y'])]

for _ in range(num_steps):
    temperature = diffuse.explicit(temperature, kappa, dt, substeps=1)
    trajectory.append(temperature.values.numpy(['x', 'y']))

trajectory = np.stack(trajectory, axis=0)
np.save('heat_flow_temperature_trj.npy', trajectory)