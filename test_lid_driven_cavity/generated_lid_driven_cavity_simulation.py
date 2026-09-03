from phi.flow import *
import numpy as np

Nx, Ny = 50, 32
nu = 0.1
dt = 1.0

domain_bounds = Box(x=Nx, y=Ny)
grid = UniformGrid(x=Nx, y=Ny, bounds=domain_bounds)

top_velocity = extrapolation.ConstantExtrapolation(vec(x=1.0, y=0.0))
velocity_boundary = extrapolation.combine_sides(
    x=extrapolation.ZERO,
    y=(extrapolation.ZERO, top_velocity)
)

velocity = StaggeredGrid(values=(0.0, 0.0), boundary=velocity_boundary, bounds=domain_bounds, x=Nx, y=Ny)

pressure = Field(grid, values=0.0, boundary=extrapolation.ZERO)
hard_bcs = Field(grid, values=1.0, boundary=extrapolation.ZERO)
active = Field(grid, values=1.0, boundary=extrapolation.ZERO)

def step(velocity, pressure, dt=dt, nu=nu):
    convection = advect.differential(velocity, velocity, order=2)
    diffusion = diffuse.differential(velocity, nu)
    velocity = velocity + dt * (convection + diffusion)
    velocity = fluid.apply_boundary_conditions(velocity, ())
    div = divergence(velocity)
    pressure = math.solve_linear(
        fluid.masked_laplace,
        div,
        Solve('CG-adaptive', 1e-5, 1e-5, x0=pressure),
        hard_bcs=hard_bcs,
        active=active
    )
    grad_p = spatial_gradient(pressure, type=StaggeredGrid)
    velocity = velocity - grad_p
    velocity = fluid.apply_boundary_conditions(velocity, ())
    return velocity, pressure

def to_numpy(v):
    centered = Field(grid, values=v, boundary=extrapolation.ZERO)
    return centered.values.numpy(['x', 'y', 'vector'])

velocity_trj = [to_numpy(velocity)]

for i in range(100):
    velocity, pressure = step(velocity, pressure)
    velocity_trj.append(to_numpy(velocity))

velocity_trj = np.stack(velocity_trj, axis=0)
np.save('lid_driven_cavity_velocity_trj.npy', velocity_trj)