from phi.flow import *
from phi import math
from phi.flow import diffuse
import numpy as np

DOMAIN_BOUNDS = Box(x=10, y=5)
RESOLUTION = spatial(x=100, y=50)
DT = 1.0
STEPS = 100

boundary = extrapolation.combine_sides(
    x=(extrapolation.ConstantExtrapolation(1.0), extrapolation.ZERO_GRADIENT),
    y=extrapolation.PERIODIC
)

def diffusivity_function(x):
    px = x.vector['x']
    py = x.vector['y']
    region1 = (py >= 2) & (py <= 3)
    region2 = (px >= 4.5) & (px <= 5.5) & (py >= 1) & (py <= 4)
    inside = region1 | region2
    kappa = math.where(inside, 1.01, 0.01)
    return vec(x=kappa, y=0.0)

diffusivity = CenteredGrid(diffusivity_function, boundary=extrapolation.ZERO_GRADIENT, bounds=DOMAIN_BOUNDS, resolution=RESOLUTION)

temperature = CenteredGrid(0.0, boundary=boundary, bounds=DOMAIN_BOUNDS, resolution=RESOLUTION)

trajectory = [temperature.values.numpy('x,y')]

for _ in range(STEPS):
    temperature = diffuse.explicit(temperature, diffusivity, DT)
    trajectory.append(temperature.values.numpy('x,y'))

trajectory = np.stack(trajectory, axis=0)
np.save('heat_flow_temperature_trj.npy', trajectory)