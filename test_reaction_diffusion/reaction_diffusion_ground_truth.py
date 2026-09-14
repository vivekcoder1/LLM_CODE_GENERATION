from phi.flow import *

Lx = 100
Ly = 100
Nx = 100
Ny = 100
dt = 0.5
Du = 0.19
Dv = 0.05
feed_rate = 0.06
kill_rate = 0.062
s = 3

bounds = Box(x=Lx, y=Ly)
resolution = spatial(x=Nx, y=Ny)


def initial_condition(x):
    center = vec(x=Lx / 2, y=Ly / 2)
    radius = math.vec_length(x - center)
    return math.cos(radius / s)


u = CenteredGrid(initial_condition, PERIODIC, bounds=bounds, resolution=resolution)
v = CenteredGrid(initial_condition, PERIODIC, bounds=bounds, resolution=resolution)

u_trj = [u.values.numpy(('x', 'y'))]
v_trj = [v.values.numpy(('x', 'y'))]

for _ in range(100):
    reaction = u * v ** 2
    u = u + dt * (Du * field.laplace(u) - reaction + feed_rate * (1 - u))
    v = v + dt * (Dv * field.laplace(v) + reaction - (feed_rate + kill_rate) * v)
    u_trj.append(u.values.numpy(('x', 'y')))
    v_trj.append(v.values.numpy(('x', 'y')))

u_trj = np.stack(u_trj, axis=0)
v_trj = np.stack(v_trj, axis=0)

np.save('reaction_diffusion_ground_truth_u_trj.npy', u_trj)
np.save('reaction_diffusion_ground_truth_v_trj.npy', v_trj)


u0 = [
    CenteredGrid(Noise(scale=20, smoothness=1.3), x=100, y=100) * .2 + .1,
    CenteredGrid(lambda x: math.exp(-0.5 * math.sum((x - 50)**2) / 3**2), x=100, y=100),
    CenteredGrid(lambda x: math.cos(math.vec_length(x-50)/3), x=100, y=100) * .5,
]
u0 = stack(u0, batch('initialization'))
plot(u0)