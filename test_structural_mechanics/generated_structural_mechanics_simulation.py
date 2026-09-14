from phi.flow import *

beam_length = 10.0
grid_resolution = 100
dx = beam_length / grid_resolution
flexural_rigidity = 1.0
mass_per_length = 1.0
time_step = 0.0005
num_time_steps = 200

domain_bounds = Box(x=beam_length)
grid_shape = dict(x=grid_resolution)

initial_deflection = CenteredGrid(
    lambda x: math.exp(-((x.vector['x'] - beam_length / 2) ** 2) / (2 * (beam_length / 20) ** 2)),
    extrapolation.ZERO,
    bounds=domain_bounds,
    **grid_shape
)

displacement = initial_deflection
velocity = CenteredGrid(0.0, extrapolation.ZERO, bounds=domain_bounds, **grid_shape)

displacement_history = [displacement]
velocity_history = [velocity]

for step in range(num_time_steps):
    fourth_derivative = field.laplace(field.laplace(displacement))
    acceleration = -(flexural_rigidity / mass_per_length) * fourth_derivative
    velocity = velocity + time_step * acceleration
    displacement = displacement + time_step * velocity
    displacement_history.append(displacement)
    velocity_history.append(velocity)

for step_index, disp_field in enumerate(displacement_history):
    midpoint_value = disp_field.values.numpy('x')[grid_resolution // 2]
    print(f"Time step {step_index}: midpoint displacement = {midpoint_value:.6f}")