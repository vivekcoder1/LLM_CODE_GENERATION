# Simulate the reaction diffusion equation with following initial conditions using given governing equation. 
## Step 1: Define the computational grid, domain, boundary condition using the following information:

$$
\Omega = [0,L_x] \times [0,L_y] \\
L_x= L_y = 100 \\
N_x =N_y =100 \\
u_{i,j}(0)= v_{i,j}(0) = \cos\left(\frac{r_{i,j}}{s}\right) \\
r_{i,j} = \sqrt{\left(x_i - \frac{L_x}{2}\right)^2 + \left(y_j - \frac{L_y}{2}\right)^2} \\
s = 3 \\
\Delta t = 0.5
$$

* Diffusion coefficients:

$$
D_u = 0.19, \quad D_v = 0.05
$$

* Reaction parameters:

$$
\text{feed rate}(f) = 0.06, \quad \text{kill rate}(k) = 0.062
$$
---

## Step 2. Define a step function using the following governing equations.
$$
\frac{\partial u}{\partial t} = D_u \nabla^2 u - u v^2 + f(1 - u) \\
\frac{\partial v}{\partial t} = D_v \nabla^2 v + u v^2 - (f + k)v
$$

---

Run the simulation for 100 time steps and save the `u_trj` and `v_trj` in files `reaction_diffusion_u_trj.npy` and `reaction_diffusion_v_trj.npy`. The files should contain `[time_step+1,N_x,N_y]` shape i.e. 101 snapshots of the u and v fields.
