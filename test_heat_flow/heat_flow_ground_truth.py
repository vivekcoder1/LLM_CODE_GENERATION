
from phi.jax.flow import *
from tqdm.notebook import trange
def step(t, dt):
    return diffuse.implicit(t, conductivity, dt)


domain = Box(x=10, y=5)
boundary = {'x-': 1, 'x+': ZERO_GRADIENT, 'y': PERIODIC}
bars = union(Box(x=(0, 10), y=(2, 3)), Box(x=(4.5, 5.5), y=(1, 4)))
conductivity = CenteredGrid(bars, ZERO_GRADIENT, domain, x=100, y=50) + .01



t0 = CenteredGrid(0, boundary, domain, x=100, y=50)
v_trj = iterate(step, batch(time=100), t0, dt=1, range=trange)
np.save('heat_flow_ground_truth.npy', v_trj.values.numpy(('time', 'x', 'y')))