from phi.flow import *
import numpy as np

domain = Box(x=10, y=5)
resolution = spatial(x=100, y=50)

boundary = extrapolation.combine_sides(x=(1.0, extrapolation.ZERO_GRADIENT), y=extrapolation.PERIODIC)

temperature = CenteredGrid(0, extrapolation=boundary, bounds=domain, resolution=resolution)

box1 = Box(x=(0, 10), y=(2, 3))
box2 = Box(x=(4.5, 5.5), y=(1, 4))

mask1 = CenteredGrid(box1, extrapolation=extrapolation.ZERO_GRADIENT, bounds=domain, resolution=resolution)
mask2 = CenteredGrid(box2, extrapolation=extrapolation.ZERO_GRADIENT, bounds=domain, resolution=resolution)

mask = mask1 + mask2 - mask1 * mask2

kappa = 0.01 + mask * (1.01 - 0.01)

diffusivity_tensor = math.stack([kappa.values, kappa.values * 0], channel(vector='x,y'))

dt = 1.0
steps = 100

trajectory = [temperature.values.numpy('x,y')]

for i in range(steps):
    temperature = diffuse.explicit(temperature, diffusivity_tensor, dt=dt, substeps=1)
    trajectory.append(temperature.values.numpy('x,y'))

trajectory = np.stack(trajectory, axis=0)
np.save('heat_flow_temperature_trj.npy', trajectory)