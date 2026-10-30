from phi.flow import *
import numpy as np

domain_x = 10.0
domain_y = 5.0
Nx = 100
Ny = 50
dt = 1.0
num_steps = 100

grid = UniformGrid(spatial(x=Nx, y=Ny), Box(x=(0, domain_x), y=(0, domain_y)))

x_centers = grid.center.vector['x'].numpy(order='x,y')
y_centers = grid.center.vector['y'].numpy(order='x,y')

in_B = ((y_centers >= 2.0) & (y_centers <= 3.0)) | ((x_centers >= 4.5) & (x_centers <= 5.5) & (y_centers >= 1.0) & (y_centers <= 4.0))

kappa_np = np.where(in_B, 1.01, 0.01)

kappa_tensor = math.tensor(kappa_np, spatial('x,y'))

u_init = math.zeros(spatial(x=Nx, y=Ny))

temperature = Field(grid, values=u_init, boundary={'x-': 1.0, 'x+': ZERO_GRADIENT, 'y': PERIODIC})

kappa_field = Field(grid, values=kappa_tensor, boundary={'x-': 1.0, 'x+': ZERO_GRADIENT, 'y': PERIODIC})

def step(u, kappa, dt):
    diffused = diffuse.explicit(u, kappa, dt, substeps=1)
    return diffused

trajectory = []

u_np = temperature.values.numpy(order='x,y')
trajectory.append(u_np.copy())

current = temperature

for i in range(num_steps):
    current = step(current, kappa_field, dt)
    u_np = current.values.numpy(order='x,y')
    trajectory.append(u_np.copy())

trajectory_array = np.array(trajectory)

np.save('heat_flow_temperature_trj.npy', trajectory_array)