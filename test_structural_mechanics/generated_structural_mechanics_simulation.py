from phi.flow import Box, Field, Obstacle, StaggeredGrid, UniformGrid, fluid, advect, diffuse, vec, Solve

domain = Box(x=100, y=100)
resolution = dict(x=64, y=64)
grid = UniformGrid(bounds=domain, **resolution)

viscosity = 0.01
dt = 0.1
num_steps = 20

pillar = Obstacle(Box(x=(45, 55), y=(45, 55)))
obstacles = [pillar]

velocity = StaggeredGrid(vec(x=1.0, y=0.0), boundary=0, bounds=domain, resolution=resolution)
pressure = Field(grid, values=0.0, boundary=0)

velocity = fluid.apply_boundary_conditions(velocity, obstacles)

def structural_flow_pde(v, p, nu):
    advection_term = advect.differential(v, v, order=2)
    diffusion_term = diffuse.differential(v, diffusivity=nu, order=2)
    return advection_term + diffusion_term

velocity_history = [velocity]
pressure_history = [pressure]

for step in range(num_steps):
    velocity, pressure = fluid.incompressible_rk4(
        structural_flow_pde,
        velocity,
        pressure,
        dt,
        pressure_order=2,
        pressure_solve=Solve('CG', 1e-5, 1e-5),
        nu=viscosity
    )
    velocity = fluid.apply_boundary_conditions(velocity, obstacles)
    velocity_history.append(velocity)
    pressure_history.append(pressure)

for i, (v, p) in enumerate(zip(velocity_history, pressure_history)):
    print(f"Time step {i}: max_pressure={float(p.values.max):.6f}, max_velocity_x={float(v.values.vector['x'].max):.6f}")