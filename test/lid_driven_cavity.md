# Simulate the lid driven cavity flow with following initial conditions using given governing equation. 
## Step 1: Define the computational grid, domain, boundary condition using the following information:
* Grid Definition

$$
\Omega_u \in \mathbb{R}^{N_x \times N_y} \\
N_x = 50, \quad N_y = 32
$$

* Initial values

$$
u_0(x, y) = 0, \quad \forall x \in [0, N_x], \; y \in [0, N_y]
$$

$$
\text{Kinematic viscosity}(\nu) = 0.1 \\
\text{Time step}(\Delta t) = 1.0 \quad 
$$

* Boundary Conditions

$$
\begin{cases}
u(x=0, y) = 0, & \text{(Left boundary)} \\
u(x=N_x,y)=0, & \text{(Right boundary)}\\ 
u(x, y=0) = 0, & \text{(Bottom boundary)} \\
u(x,y=N_y) = 
\begin{bmatrix} 1 \\ 0 \end{bmatrix}, & \text{(Top boundary)}
\end{cases}
$$

---

## Step 2: Define a step function using the following governing equation and function signature.

$$
    \frac{\partial u}{\partial t} + u \frac{\partial u}{\partial x} = \nu \frac{\partial^2u}{\partial x^2}\\
    \quad \nabla \cdot u = 0
$$

---
Run the simulation for 100 time steps and save the `velocity_trj` in a file `lid_driven_cavity_velocity_trj.npy`. The file should contain `[time_step+1,N_x,N_y,2]` shape i.e. 101 snapshots of the velocity field.
