from phi.flow import *
import numpy as np

domain = Box(x=10, y=5)

boundary = extrapolation.combine_sides(
    x=(1.0, extrapolation.ZERO_GRADIENT),
    y=extrapolation.PERIODIC
)

temperature = CenteredGrid(0.0, extrapolation=boundary, x=100, y=50, bounds=domain)

box1 = Box(x=(0, 10), y=(2, 3))
box2 = Box(x=(4.5, 5.5), y=(1, 4))

points = temperature.points
inside_mask = box1.lies_inside(points) | box2.lies_inside(points)
kappa_scalar = math.where(inside_mask, 1.01, 0.01)

diffusivity = kappa_scalar * vec(x=1.0, y=0.0)

dt = 1.0

def step(u):
    return diffuse.explicit(u, diffusivity, dt, substeps=1)

trajectory = [temperature.values.numpy('x,y')]

for i in range(100):
    temperature = step(temperature)
    trajectory.append(temperature.values.numpy('x,y'))

trajectory = np.stack(trajectory, axis=0)
np.save('heat_flow_temperature_trj.npy', trajectory)