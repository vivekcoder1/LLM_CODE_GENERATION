from phi.flow import *
from phi.flow import extrapolation, diffuse, math
import numpy as np

bounds = Box(x=10, y=5)
res = spatial(x=100, y=50)
dt = 1.0
steps = 100

boundary = extrapolation.combine_sides(x=(1.0, extrapolation.ZERO_GRADIENT), y=extrapolation.PERIODIC)

u = CenteredGrid(0.0, extrapolation=boundary, bounds=bounds, resolution=res)

def kappa_function(x):
    x_ = x['x']
    y_ = x['y']
    mask1 = (y_ >= 2) & (y_ <= 3)
    mask2 = (x_ >= 4.5) & (x_ <= 5.5) & (y_ >= 1) & (y_ <= 4)
    mask = mask1 | mask2
    return math.where(mask, 1.01, 0.01)

kappa = CenteredGrid(kappa_function, extrapolation=extrapolation.ZERO_GRADIENT, bounds=bounds, resolution=res)

diffusivity = kappa * vec(x=1, y=0)

temperature_trj = [u.values.numpy(('x', 'y'))]

for _ in range(steps):
    u = diffuse.explicit(u, diffusivity=diffusivity, dt=dt)
    temperature_trj.append(u.values.numpy(('x', 'y')))

temperature_trj = np.stack(temperature_trj)
np.save('heat_flow_temperature_trj.npy', temperature_trj)