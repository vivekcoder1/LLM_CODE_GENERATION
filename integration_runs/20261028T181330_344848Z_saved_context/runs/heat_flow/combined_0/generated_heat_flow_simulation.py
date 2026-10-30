from phi.flow import *
import numpy as np

domain = Box(x=10, y=5)
boundary = {'x-': 1, 'x+': ZERO_GRADIENT, 'y': PERIODIC}
bars = union(Box(x=(0, 10), y=(2, 3)), Box(x=(4.5, 5.5), y=(1, 4)))
conductivity = CenteredGrid(bars, ZERO_GRADIENT, domain, x=100, y=50) + .01
t = CenteredGrid(0, boundary, domain, x=100, y=50)

dt = 1.0

snapshots = [t.values.numpy('x,y')]

for _ in range(100):
    t = diffuse.implicit(t, conductivity, dt)
    snapshots.append(t.values.numpy('x,y'))

trajectory = np.stack(snapshots, axis=0)
np.save('heat_flow_temperature_trj.npy', trajectory)