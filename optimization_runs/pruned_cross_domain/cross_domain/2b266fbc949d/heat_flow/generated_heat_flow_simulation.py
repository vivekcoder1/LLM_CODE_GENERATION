from phi.flow import *
import numpy as np

domain = Box(x=10, y=5)
resolution = spatial(x=100, y=50)
grid = UniformGrid(resolution, bounds=domain)

boundary = {'x': (1.0, ZERO_GRADIENT), 'y': PERIODIC}

temperature = Field(grid, values=0.0, boundary=boundary)

kappa = Field(
    grid,
    values=lambda x, y: where(
        (y >= 2) & (y <= 3) | ((x >= 4.5) & (x <= 5.5) & (y >= 1) & (y <= 4)),
        1.01,
        0.01
    ),
    boundary=0.0
)

diffusivity = kappa * vec(x=1, y=0)

dt = 1.0
num_steps = 100

trajectory = [temperature.values.numpy(['x', 'y'])]

for _ in range(num_steps):
    temperature = diffuse.explicit(temperature, diffusivity, dt=dt)
    trajectory.append(temperature.values.numpy(['x', 'y']))

temperature_trj = np.stack(trajectory, axis=0)
np.save('heat_flow_temperature_trj.npy', temperature_trj)