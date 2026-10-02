from phi.flow import *
import numpy as np

domain = Box(x=10, y=5)
resolution = spatial(x=100, y=50)
dt = 1.0

boundary = extrapolation.combine_sides(
    x=(extrapolation.ConstantExtrapolation(1.0), extrapolation.ZERO_GRADIENT),
    y=extrapolation.PERIODIC
)

temperature = CenteredGrid(0.0, boundary, bounds=domain, resolution=resolution)

inclusion_1 = Box(x=(0, 10), y=(2, 3))
inclusion_2 = Box(x=(4.5, 5.5), y=(1, 4))

mask1 = CenteredGrid(inclusion_1, extrapolation.ZERO_GRADIENT, bounds=domain, resolution=resolution)
mask2 = CenteredGrid(inclusion_2, extrapolation.ZERO_GRADIENT, bounds=domain, resolution=resolution)

combined_mask = mask1 + mask2 - mask1 * mask2
kappa = 0.01 + combined_mask * 1.0

diffusivity = kappa * vec(x=1.0, y=0.0)

trj = [temperature.values.numpy(['x', 'y'])]

for step in range(100):
    temperature = diffuse.explicit(temperature, diffusivity=diffusivity, dt=dt, substeps=1)
    trj.append(temperature.values.numpy(['x', 'y']))

trj = np.stack(trj, axis=0)
np.save('heat_flow_temperature_trj.npy', trj)