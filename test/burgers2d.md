# Simulate the 2d burgers equation with following initial conditions using given governing equation. 
## Step 1: Define the computational grid, domain, boundary condition using the following information:

$$
\begin{aligned}
\Omega = [0, L_x] \times [0, L_y]\\
\quad L_x =40, L_y=20 \\ 
\quad N_x = N_y = 64 \\
u(x_i, y_j, 0) = \exp\left(-\left(x_i - \frac{L_x}{2}\right)^2 - \left(y_j - \frac{L_y}{2}\right)^2\right) \\
u(0, y, t) = u(L_x, y, t)\\
u(x, 0, t) = u(x, L_y, t)\\
\nu = 0.1 \\
\Delta t = 0.5
\end{aligned}
$$

where $u$ is the velocity field and $\nu$ is diffusivity.

--- 

## Step 2: Define a step function using the following governing equations.
$$
    \frac{\partial u}{\partial t} + u (\frac{\partial u}{\partial x}) + v (\frac{\partial u}{\partial y} )= \nu( \frac{\partial^2 u}{\partial x^2} + \frac{\partial ^2 u}{\partial y^2})\\
    \frac{\partial v}{\partial t} + u (\frac{\partial v}{\partial x}) + v (\frac{\partial v}{\partial y} )= \nu( \frac{\partial^2 v}{\partial x^2} + \frac{\partial ^2 v}{\partial y^2})
$$

---

Run the simulation for 100 time steps and save the `velocity_trj` in a file `burgers2d_velocity_trj.npy`. The file should contain `[time_step+1,N_x,N_y,2]` shape i.e. 101 snapshots of the velocity field.
