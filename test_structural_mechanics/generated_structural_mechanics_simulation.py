```python
"""
Structural Mechanics Simulation: Transient Transverse Vibration of a
Tensioned Membrane (PhiFlow Wave-Equation Formulation)

Physical model
---------------
A thin, pre-tensioned membrane (e.g. a drumhead, tensioned fabric roof panel,
or diaphragm) undergoes small transverse deflections w(x, y, t) governed by
the 2-D wave equation, which is the structural-dynamics equilibrium equation
for a membrane under uniform tension T and areal mass density rho:

    rho * d^2w/dt^2 = T * grad^2(w) + f(x, y, t)

Rewriting as a first-order system (displacement w, velocity v = dw/dt):

    dw/dt = v
    dv/dt = c^2 * grad^2(w) + f/rho ,      c = sqrt(T / rho)

The system is advanced in time using symplectic (semi-implicit) Euler
integration via `wave.euler_step`, which guarantees good long-term energy
behavior -- an important property for structural dynamics simulations where
spurious energy growth/decay would corrupt the vibration response.

Boundary conditions: all four edges are clamped (Dirichlet, w = 0), modeling
a membrane rigidly fixed to its supporting frame.

Initial conditions: the membrane is released from rest ("plucked") with an
initial Gaussian displacement bump at the center and zero initial velocity.
"""

from phi.flow import *
import numpy as np


# ---------------------------------------------------------------------------
# 1. Structural / Material Properties
# ---------------------------------------------------------------------------
tension = 5000.0            # Membrane tension per unit length, T [N/m]
areal_density = 1.2         # Areal mass density, rho [kg/m^2]
wave_speed = math.sqrt(tension / areal_density)   # Transverse wave speed, c [m/s]

# ---------------------------------------------------------------------------
# 2. Domain & Spatial Discretization
# ---------------------------------------------------------------------------
domain_size_x = 1.0         # Membrane span in x [m]
domain_size_y = 1.0         # Membrane span in y [m]
resolution_x = 64           # Number of cells in x
resolution_y = 64           # Number of cells in y

bounds = Box(x=domain_size_x, y=domain_size_y)
dx = domain_size_x / resolution_x
dy = domain_size_y / resolution_y

# ---------------------------------------------------------------------------
# 3. Time Discretization (CFL-stable time step for explicit wave integration)
# ---------------------------------------------------------------------------
cfl_safety_factor = 0.4
dt = cfl_safety_factor * min(dx, dy) / (wave_speed * math.sqrt(2))

n_time_steps = 100          # N additional steps beyond t=0 -> N+1 stored states

# ---------------------------------------------------------------------------
# 4. Boundary Conditions: Clamped edges (Dirichlet, w = 0)
# ---------------------------------------------------------------------------
displacement_boundary = 0.0

# ---------------------------------------------------------------------------
# 5. Initial Conditions: Membrane released from rest with a central bump
# ---------------------------------------------------------------------------
center_position = vec(x=domain_size_x / 2.0, y=domain_size_y / 2.0)
bump_amplitude = 0.02        # Initial peak displacement [m]
bump_radius = 0.15           # Characteristic width of the initial bump [m]


def initial_displacement(x):
    """Gaussian-shaped initial displacement field, centered on the membrane."""
    r2 = math.vec_squared(x - center_position)
    return bump_amplitude * math.exp(-r2 / (2.0 * bump_radius ** 2))


w = CenteredGrid(initial_displacement, boundary=displacement_boundary,
                  bounds=bounds, x=resolution_x, y=resolution_y)
v = CenteredGrid(0.0, boundary=displacement_boundary,
                  bounds=bounds, x=resolution_x, y=resolution_y)  # released from rest

# ---------------------------------------------------------------------------
# 6. Optional External Forcing (e.g. localized structural excitation)
# ---------------------------------------------------------------------------
load_position = vec(x=0.25, y=0.25)
load_amplitude = 0.0        # [N/m^2]; set > 0 to activate a driven point load
drive_frequency = 5.0       # [Hz] forcing frequency, used only if load_amplitude > 0


def point_load(x, t):
    """Localized, time-harmonic forcing term representing an applied structural load."""
    r2 = math.vec_squared(x - load_position)
    spatial_profile = math.exp(-r2 / (2.0 * dx ** 2))
    time_profile = math.sin(2.0 * PI * drive_frequency * t)
    return load_amplitude * spatial_profile * time_profile


# ---------------------------------------------------------------------------
# 7. Storage for the time-history of the structural response
# ---------------------------------------------------------------------------
displacement_history = [w]
velocity_history = [v]
time_points = [0.0]
max_displacement_history = [float(math.max(math.abs(w.values)))]

print(f"Wave speed (c):            {wave_speed:.4f} m/s")
print(f"Time step (dt):            {dt:.6f} s")
print(f"Total simulated duration:  {n_time_steps * dt:.4f} s")
print(f"Step 0 (t=0.0000 s): max|w| = {max_displacement_history[0]:.6f} m")

# ---------------------------------------------------------------------------
# 8. Time Integration Loop (Symplectic Euler via wave.euler_step)
#    N = n_time_steps additional steps -> N+1 total stored states (incl. t=0)
# ---------------------------------------------------------------------------
current_time = 0.0
for step in range(1, n_time_steps + 1):
    current_time += dt

    source_field = None
    if load_amplitude != 0.0:
        source_field = CenteredGrid(lambda x, t=current_time: point_load(x, t),
                                     boundary=displacement_boundary, bounds=bounds,
                                     x=resolution_x, y=resolution_y)

    w, v = wave.euler_step(w, v, c=wave_speed, dt=dt, source=source_field)

    displacement_history.append(w)
    velocity_history.append(v)
    time_points.append(current_time)

    max_disp = float(math.max(math.abs(w.values)))
    max_displacement_history.append(max_disp)

    if step % 10 == 0 or step == n_time_steps:
        print(f"Step {step:4d} (t={current_time:.4f} s): max|w| = {max_disp:.6f} m")

# ---------------------------------------------------------------------------
# 9. Analytical Validation: Fundamental Natural Frequency of a Clamped
#    Rectangular Membrane (mode m=n=1)
#
#       f_11 = (c / 2) * sqrt( (1/Lx)^2 + (1/Ly)^2 )
# ---------------------------------------------------------------------------
f_11_analytical = (wave_speed / 2.0) * math.sqrt((1.0 / domain_size_x) ** 2 +
                                                  (1.0 / domain_size_y) ** 2)
period_11 = 1.0 / f_11_analytical

print("\n--- Analytical Reference (mode 1,1) ---")
print(f"Fundamental natural frequency: {f_11_analytical:.4f} Hz")
print(f"Fundamental period:            {period_11:.4f} s")
print(f"Number of periods simulated:   {(n_time_steps * dt) / period_11:.4f}")


# ---------------------------------------------------------------------------
# 10. Energy Consistency Check (Structural Mechanics Sanity Check)
#
#     E_kinetic  = 0.5 * rho * Integral( v^2 ) dA
#     E_strain   = 0.5 * T   * Integral( |grad(w)|^2 ) dA
#     E_total    = E_kinetic + E_strain  (should remain nearly constant
#                                          for the undamped, unforced case)
# ---------------------------------------------------------------------------
def compute_total_energy(w_field, v_field):
    w_np = w_field.values.numpy(['y', 'x'])
    v_np = v_field.values.numpy(['y', 'x'])

    kinetic_energy = 0.5 * areal_density * np.sum(v_np ** 2) * dx * dy

    grad_wx = np.gradient(w_np, dx, axis=1)
    grad_wy = np.gradient(w_np, dy, axis=0)
    strain_energy = 0.5 * tension * np.sum(grad_wx ** 2 + grad_wy ** 2) * dx * dy

    return float(kinetic_energy + strain_energy)


energy_initial = compute_total_energy(displacement_history[0], velocity_history[0])
energy_final = compute_total_energy(displacement_history[-1], velocity_history[-1])
relative_drift = abs(energy_final - energy_initial) / max(energy_initial, 1e-12) * 100.0

print("\n--- Energy Consistency Check ---")
print(f"Initial total mechanical energy: {energy_initial:.6e} J")
print(f"Final total mechanical energy:   {energy_final:.6e} J")
print(f"Relative energy drift:           {relative_drift:.4f} %")

print(f"\nTotal stored time steps (including t=0): {len(displacement_history)} "
      f"(N={n_time_steps} steps + 1 initial state)")
```