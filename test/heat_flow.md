# Simulate the heat flow equation with following initial conditions using given governing equation. 
## Step 1: Define the computational grid, domain, boundary condition, initial condition using the following information:
$$

\begin{aligned}
&\text{Domain:} && \Omega = [0, 10] \times [0, 5] \\
&\text{Boundaries:} &&
\begin{cases}
u(0,y,t) = 1, \\
\dfrac{\partial u}{\partial x}(10,y,t) = 0,\\
u(x,0,t) = u(x,5,t),
\end{cases}\\
&\text{Inclusions:} &&
\mathcal{B} = ([0,10]\times[2,3]) \cup ([4.5,5.5]\times[1,4])\\
&\text{Conductivity:} &&
\kappa(x,y) =
\begin{cases}
1.01, & (x,y) \in \mathcal{B},\\
0.01, & \text{otherwise}
\end{cases} \\
&\text{Grid Resolution:} && (N_x, N_y) = (100, 50) \\
&\Delta t && = 1.0
\end{aligned}

$$

---

## Step 2: Define a step function using the following governing equations.

$$
\frac{\partial u}{\partial t} = \kappa \frac{\partial^2 u}{\partial x^2}
$$

---

Run the simulation for 100 time steps and save the `temperature_trj` in a file `heat_flow_temperature_trj.npy`. The file should contain `[time_step+1,N_x,N_y]` shape i.e. 101 snapshots of the temperature field.
