import numpy as np
from phi.flow import *
from phi.flow import diffuse, extrapolation, math

bounds = Box(x=10, y=5)
resolution = spatial(x=100, y=50)

box1 = Box(x=(0, 10), y=(2, 3))
box2 = Box(x=(4.5, 5.5), y=(1, 4))

kappa = CenteredGrid(lambda x: math.where(box1.lies_inside(x) | box2.lies_inside(x), 1.01, 0.01),
                      extrapolation.ZERO_GRADIENT, bounds=bounds, resolution=resolution)

u_extrapolation = extrapolation.combine_sides(
    x=(extrapolation.ConstantExtrapolation(1.0), extrapolation.ZERO_GRADIENT),
    y=extrapolation.PERIODIC
)

temperature = CenteredGrid(0.0, u_extrapolation, bounds=bounds, resolution=resolution)

dt = 1.0

def step(u):
    return diffuse.explicit(u, kappa, dt)

trajectory = [temperature.values.numpy(['x', 'y'])]

for i in range(100):
    temperature = step(temperature)
    trajectory.append(temperature.values.numpy(['x', 'y']))

trajectory = np.stack(trajectory, axis=0)
np.save('heat_flow_temperature_trj.npy', trajectory)