from phi.flow import *
import numpy as np

dt = 1.0
resolution = spatial(x=100, y=50)
domain_bounds = Box(x=10, y=5)

temp_boundary = extrapolation.combine_sides(
    x=(extrapolation.ConstantExtrapolation(1.0), extrapolation.ZERO_GRADIENT),
    y=extrapolation.PERIODIC
)

box1 = Box(x=(0, 10), y=(2, 3))
box2 = Box(x=(4.5, 5.5), y=(1, 4))
inclusion = union(box1, box2)

kappa_mask = CenteredGrid(inclusion, extrapolation=extrapolation.PERIODIC, bounds=domain_bounds, resolution=resolution)
kappa_field = kappa_mask * (1.01 - 0.01) + 0.01

diffusivity = kappa_field * vec(x=1.0, y=0.0)

u = CenteredGrid(0.0, extrapolation=temp_boundary, bounds=domain_bounds, resolution=resolution)

trajectory = [u.values.numpy('x,y')]

for _ in range(100):
    u = diffuse.explicit(u, diffusivity, dt=dt)
    trajectory.append(u.values.numpy('x,y'))

trajectory = np.stack(trajectory, axis=0)
np.save('heat_flow_temperature_trj.npy', trajectory)