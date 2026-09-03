from phi.flow import *
import numpy as np

domain = Box(x=10, y=5)
grid = UniformGrid(x=100, y=50, bounds=domain)

def kappa_func(x, y):
    in_box1 = (y >= 2) & (y <= 3)
    in_box2 = (x >= 4.5) & (x <= 5.5) & (y >= 1) & (y <= 4)
    inside = in_box1 | in_box2
    return math.where(inside, 1.01, 0.01)

kappa_scalar = Field(grid, values=kappa_func, boundary=0.01)
diffusivity = kappa_scalar * vec(x=1, y=0)

boundary = {'x-': 1, 'x+': ZERO_GRADIENT, 'y': PERIODIC}
temperature = Field(grid, values=0.0, boundary=boundary)

dt = 1.0
steps = 100

trajectory = [temperature.values.numpy(('x', 'y'))]

for _ in range(steps):
    temperature = diffuse.explicit(temperature, diffusivity, dt)
    trajectory.append(temperature.values.numpy(('x', 'y')))

trajectory = np.stack(trajectory, axis=0)
np.save('heat_flow_temperature_trj.npy', trajectory)