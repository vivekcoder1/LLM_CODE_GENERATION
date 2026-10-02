from phi.flow import *
import numpy as np

extrap = extrapolation.combine_sides(x=(1.0, extrapolation.ZERO_GRADIENT), y=extrapolation.PERIODIC)

domain_bounds = Box(x=10, y=5)
res = spatial(x=100, y=50)

def diffusivity_fn(x):
    xv = x.vector['x']
    yv = x.vector['y']
    in_box1 = (yv >= 2) & (yv <= 3)
    in_box2 = (xv >= 4.5) & (xv <= 5.5) & (yv >= 1) & (yv <= 4)
    inside = in_box1 | in_box2
    kappa_val = math.where(inside, 1.01, 0.01)
    return vec(x=kappa_val, y=0.0 * kappa_val)

diffusivity = CenteredGrid(diffusivity_fn, extrapolation=extrap, resolution=res, bounds=domain_bounds)

temperature = CenteredGrid(0.0, extrapolation=extrap, resolution=res, bounds=domain_bounds)

dt = 1.0
steps = 100

trj = [temperature.values.numpy(['x', 'y'])]

for _ in range(steps):
    temperature = diffuse.explicit(temperature, diffusivity, dt)
    trj.append(temperature.values.numpy(['x', 'y']))

trj = np.stack(trj, axis=0)
np.save('heat_flow_temperature_trj.npy', trj)