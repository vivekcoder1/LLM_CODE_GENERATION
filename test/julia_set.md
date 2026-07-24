# Simulate the Julia set with following initial conditions using given governing equation. 
## Step 1: Define the computational grid, domain, boundary condition using the following information:

$$ 
\begin{aligned}
\Omega = \{ x + i y \mid x \in [-2,2], \, y \in [-2,2] \} \\
N_x = N_y = 256 \\
z(x,y,0) = x + i y\\

f_\theta(z) = z^2 + c(t), \quad \theta \in [0, 2\pi] \\
c(t) = 0.7885 \, e^{i \frac{2 \pi t}{100}}, t \in \{0,1,...99\} \\
N_\text{escape} = 50
\end{aligned}
$$

---

## Step 2: Define a step function using the following governing equations.

$$
\begin{aligned}
z(x,y,t) \gets z(x,y,t)^2 + c(t) \\
J(x,y,t ) \gets J(x,y,t) + \mathbf{1}_{\{|z| < 2\}}
\end{aligned}\\
\text{where $J$ is Julia Set.}
$$

---
Run the simulation for 100 time steps and save the `domain_trj` in a file `julia_set_domain_trj.npy`. The file should contain `[time_step,N_x,N_y]` shape i.e. 100 snapshots of the domain field.
