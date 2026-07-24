# Simulate the wake flow with following initial conditions using given governing equation. 
## Step 1: Define the computational grid, domain, boundary condition, initial condition using the following information:

$$
\begin{aligned}
&\text{Domain:} && \Omega = [0,200]\times[0,100]\times[0,5]\\
&\text{Object:} && \mathcal{C} = {(x,y,z): (x-20)^2+(y-50)^2\le 10^2}\\
&\text{Boundary Conditions:} &&
\begin{cases}
\mathbf{u}(0,y,z,t) = (2,0,0),\\
\dfrac{\partial \mathbf{u(200,y,z,t)}}{\partial x}=\mathbf{0},\\
\mathbf{u}(x,0,z,t)=\mathbf{u}(x,100,z,t),\\
\mathbf{u}(x,y,0,t)=\mathbf{u}(x,y,5,t),\\
\end{cases}\\
&\text{Initial Condition:} && \mathbf{u}(x,y,z,0)=(8,0,0)\\
&\text{Grid Resolution:} && (N_x,N_y,N_z)=(128,64,8).
\end{aligned}

$$

---

## Step 2: Define a step function using the following governing equations.

$$
\begin{aligned}
\dfrac {\partial {u}}{\partial {t}} + (\mathbf{u}\cdot\nabla)\mathbf{u} = 0 \\
&\nabla\cdot \mathbf{u} &= 0
\end{aligned}
$$

---

Run the simulation for 400 time steps and save the `velocity_trj` in files `wake_flow_velocity_trj.npy`. The file should contain `[time_step+1,N_x,N_y,N_z,3]` shape i.e. 401 snapshots of the velocity field.
