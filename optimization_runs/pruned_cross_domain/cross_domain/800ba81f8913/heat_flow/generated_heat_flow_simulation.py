from phi.flow import *
import numpy as np

domain = Box(x=10, y=5)
resolution = spatial(x=100, y=50)

boundary = extrapolation.combine_sides(
    x=(extrapolation.ConstantExtrapolation(1.0), extrapolation.ZERO_GRADIENT),
    y=extrapolation.PERIODIC
)

def kappa_func(x):
    x_ = x['x']
    y_ = x['y']
    in_box1 = (y_ >= 2) & (y_ <= 3)
    in_box2 = (x_ >= 4.5) & (x_ <= 5.5) & (y_ >= 1) & (y_ <= 4)
    inside = in_box1 | in_box2
    return math.where(inside, 1.01, 0.01)

kappa = CenteredGrid(kappa_func, extrapolation=extrapolation.PERIODIC, bounds=domain, resolution=resolution)

temperature = CenteredGrid(0.0, extrapolation=boundary, bounds=domain, resolution=resolution)

dt = 1.0
diffusivity = kappa * vec(x=1, y=0)

def step(u):
    return diffuse.explicit(u, diffusivity, dt)

trajectory = []
trajectory.append(temperature.values.numpy(('x', 'y')))

for i in range(100):
    temperature = step(temperature)
    trajectory.append(temperature.values.numpy(('x', 'y')))

temperature_trj = np.stack(trajectory, axis=0)
np.save('heat_flow_temperature_trj.npy', temperature_trj)