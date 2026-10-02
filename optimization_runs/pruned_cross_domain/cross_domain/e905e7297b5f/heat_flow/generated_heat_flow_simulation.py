from phi.flow import *
from phi.flow import diffuse, math, extrapolation
import numpy as np

domain = Box(x=10, y=5)
resolution = spatial(x=100, y=50)

def kappa_func(x):
    xs = x['x']
    ys = x['y']
    in_B1 = (ys >= 2) & (ys <= 3)
    in_B2 = (xs >= 4.5) & (xs <= 5.5) & (ys >= 1) & (ys <= 4)
    inB = in_B1 | in_B2
    return math.where(inB, 1.01, 0.01)

boundary = extrapolation.combine_sides(
    x=(extrapolation.ConstantExtrapolation(1.0), extrapolation.BOUNDARY),
    y=extrapolation.PERIODIC
)

temperature = CenteredGrid(0.0, extrapolation=boundary, bounds=domain, resolution=resolution)

kappa = CenteredGrid(kappa_func, extrapolation=extrapolation.BOUNDARY, bounds=domain, resolution=resolution)

kappa_vec = kappa * vec(x=1.0, y=0.0)

dt = 1.0
steps = 100

trajectory = [temperature.values.numpy('x,y')]

for _ in range(steps):
    temperature = diffuse.explicit(temperature, diffusivity=kappa_vec, dt=dt, substeps=1)
    trajectory.append(temperature.values.numpy('x,y'))

trajectory = np.stack(trajectory, axis=0)
np.save('heat_flow_temperature_trj.npy', trajectory)