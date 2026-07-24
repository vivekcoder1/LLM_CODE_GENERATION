# Simulate the smoke plume with following initial conditions using given governing equation. 
## Step 1: Define the velocity and pressure field using the following domain, grid and initial and boundary conditions.

$$
\Omega = [0,100]\times[0,100]\subset\mathbb{R}^2
$$

$$\text{Velocity resolution: }
N_x^{(u)}=64,\; N_y^{(u)}=64$$

$$\text{Pressure resolution: }
N_x^{(p)}=64,\; N_y^{(p)}=64$$

$$\text{Smoke resolution: }
N_x^{(p)}=200,\; N_y^{(p)}=200$$

* Inflow Region and Parameters

$$
\text{Inflow Source (i)}=\bigl\{(x,y)\in\Omega:\ (x-50)^2+(y-9.5)^2\le 5^2\bigr\},
$$

$$
\text{Smoke Grid}(S_{i_x})=\begin{cases}
1,&\mathbf{x}\in\mathcal{i},\\
0,&\mathbf{x}\notin\mathcal{i},
\end{cases}
$$

$$
\text{Smoke inflow rate} (\alpha)=0.2 \\ 
\text{Buoyancy coefficient}(\beta)=0.1 \\ 
\text{Buoyancy vector: }e_y=(0,1)
$$

* Initial Conditions

$$
\text{Velocity field }u(x,0)=\mathbf{0},\\
\text{Smoke field }s(x,0)=0,\\
\text{Pressure field }p(x,0)= None 
$$

* Boundary Conditions

$$
\frac{\partial S}{\partial n}(x,t)=0, \quad x \in \partial\Omega \\
u(x,t)=0, \quad x \in \partial\Omega \\
\frac{\partial p}{\partial n}(x,t)=0, \quad x \in \partial\Omega \\
$$

* Simulation Parameters

$$
\Delta t = 0.5
$$

---

## Step 2: Define a step function using the following governing equations.
$$
\begin{aligned}
    \frac{\partial S_{i_x}}{\partial t} +( u\cdot\nabla) S_{i_x} &= \alpha\,S_{i_x}, \\
    \frac{\partial u}{\partial t} + (u\cdot\nabla)u &= -\nabla p \;+\; \beta\,S_{i_x}\,\mathbf{e}_y, \\
    \nabla\cdot u &= 0.
\end{aligned}
$$

---
Run the simulation for 100 time steps and save the `smoke_trj` and `pressure_trj` in files `smoke_plume_smoke_trj.npy` and `smoke_plume_pressure_trj.npy`. The files should contain `[time_step+1,N_x,N_y]` shape for `smoke_trj` and `[time_step,N_x,N_y]` shape for `pressure_trj` i.e. 101 snapshots of the smoke field and 100 snapshots of the pressure field.
