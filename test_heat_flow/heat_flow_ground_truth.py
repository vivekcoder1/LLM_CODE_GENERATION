
from phi.jax.flow import *
from tqdm.notebook import trange
def step(t, dt):
    return diffuse.implicit(t, conductivity, dt)

t0 = CenteredGrid(0, boundary, domain, x=100, y=50)
v_trj = iterate(step, batch(time=100), t0, dt=1, range=trange)