# CODEBASE COMPONENT SPECIFICATIONS & API REFERENCE

## 1. COMPONENT SIGNATURES & DOCSTRINGS

### [Function] fourier_poisson
```python
See `phi.math.fourier_poisson()` 
```

### [Function] differential
```python
Computes the differential advection term using the differentiation Scheme indicated by `order`, ´implicit´ and `upwind`.

For a velocity field u, the advection term as it appears on the right-hand-side of a PDE is -u·∇u, including the negative sign.

For unstructured meshes, computes -1/V ∑_f (n·u_prev) u ρ A

Args:
    u: Scalar or vector-valued `Field` sampled on a `CenteredGrid`, `StaggeredGrid` or `Mesh`.
    velocity: `Field` that can be sampled at the elements of `u`.
        For FVM, the advection term is typically linearized by setting `velocity = previous_velocity`.
        Passing `velocity=u` yields non-linear terms which cannot be traced inside linear functions.
    order: Spatial order of accuracy.
        Higher orders entail larger stencils and more computation time but result in more accurate results assuming a large enough resolution.
        Supported for grids: 2 explicit, 4 explicit, 6 implicit (inherited from `phi.field.spatial_gradient()` and resampling).
        Passing order=4 currently uses 2nd-order resampling. This is work-in-progress.
        For FVM, the order is used when interpolating centroid values to faces if needed.
    implicit: When a `Solve` object is passed, performs an implicit operation with the specified solver and tolerances.
        Otherwise, an explicit stencil is used.
    upwind: Whether to use upwind interpolation. Only supported for FVM at the moment.

Returns:
    Differential convection term as `Field` on the same geometry.
```

### [Function] apply_boundary_conditions
```python
Enforces velocities boundary conditions on a velocity grid.
Cells inside obstacles will get their velocity from the obstacle movement.
Cells outside far away will be unaffected.

Args:
  velocity: Velocity `Grid`.
    obstacles: `Obstacle` or `phi.geom.Geometry` or tuple/list thereof to specify boundary conditions inside the domain.

Returns:
    Velocity of same type as `velocity`
```

### [Function] make_incompressible
```python
Projects the given velocity field by solving for the pressure and subtracting its spatial_gradient.

This method is similar to :func:`field.divergence_free()` but differs in how the boundary conditions are specified.

Args:
    velocity: Vector field sampled on a grid.
    obstacles: `Obstacle` or `phi.geom.Geometry` or tuple/list thereof to specify boundary conditions inside the domain.
    solve: `Solve` object specifying method and tolerances for the implicit pressure solve.
    active: (Optional) Mask for which cells the pressure should be solved.
        If given, the velocity may take `NaN` values where it does not contribute to the pressure.
        Also, the total divergence will never be subtracted if active is given, even if all values are 1.
    order: spatial order for derivative computations.
        For Higher-order schemes, the laplace operation is not conducted with a stencil exactly corresponding to the one used in divergence calculations but a smaller one instead.
        While this disrupts the formal correctness of the method it only induces insignificant errors and yields considerable performance gains.
        supported: explicit 2/4th order - implicit 6th order (obstacles are only supported with explicit 2nd order)

Returns:
    velocity: divergence-free velocity of type `type(velocity)`
    pressure: solved pressure field, `CenteredGrid`
```

### [Function] incompressible_rk4
```python
Implements the 4th-order Runge-Kutta time advancement scheme for incompressible vector fields.
This approach is inspired by [Kampanis et. al., 2006](https://www.sciencedirect.com/science/article/pii/S0021999105005061) and incorporates the pressure treatment into the time step.

Args:
    pde: Momentum equation. Function that computes all PDE terms not related to pressure, e.g. diffusion, advection, external forces.
    velocity: Velocity grid at time `t`.
    pressure: Pressure at time `t`.
    dt: Time increment to integrate.
    pressure_order: spatial order for derivative computations.
        For Higher-order schemes, the laplace operation is not conducted with a stencil exactly corresponding to the one used in divergence calculations but a smaller one instead.
        While this disrupts the formal correctness of the method it only induces insignificant errors and yields considerable performance gains.
        supported: explicit 2/4th order - implicit 6th order (obstacles are only supported with explicit 2nd order)
    pressure_solve: `Solve` object specifying method and tolerances for the implicit pressure solve.
    **pde_aux_kwargs: Auxiliary arguments for `pde`. These are considered constant over time.

Returns:
    velocity: Velocity at time `t+dt`, same type as `velocity`.
    pressure: Pressure grid at time `t+dt`, `CenteredGrid`.
```

### [Function] euler_step
```python
Advance the wave equation by one time step using symplectic Euler integration.

Solves the first-order system:
    ∂u/∂t = v
    ∂v/∂t = c² ∇²u + f

This is useful when the initial velocity v = ∂u/∂t is known directly.

Args:
    u: Current wave amplitude as a `Field`.
    v: Current velocity (time derivative of u) as a `Field`.
    c: Wave speed. Can be a constant, `Tensor`, or spatially varying `Field`.
    dt: Time step size.
    source: Optional source term f(x, t) as a `Field`.

Returns:
    Tuple of `(u_next, v_next)` for the next time step.

Examples:
    >>> from phi.flow import *
    >>> u = CenteredGrid(0, x=64, y=64, bounds=Box(x=1, y=1))
    >>> v = CenteredGrid(Noise(), x=64, y=64, bounds=Box(x=1, y=1))
    >>> u_next, v_next = wave.euler_step(u, v, c=1.0, dt=0.01)
```

### [Function] differential
```python
Compute the differential diffusion term, d·∇²u.
For grids, uses a finite difference scheme specified by `order` and `implicit`.
For FVM, the scheme is specified via `order` and `upwind`.

In contrast to `explicit` and `implicit`, accuracy can be increased by using stencils of higher-order rather than calculating sub-steps.

Args:
    u: Scalar or vector-valued `Field` sampled on a `CenteredGrid`, `StaggeredGrid` or centered `Mesh`.
    diffusivity: Dynamic viscosity, i.e. diffusion per time. Constant or varying by cell.
    gradient: Only used by FVM at the moment. Approximate gradient of `u`, e.g. ∇u of the previous time step.
        If `None`, approximates the gradient as `(u_neighbor - u_self) / distance`.
    order: Spatial order of accuracy.
        Higher orders entail larger stencils and more computation time but result in more accurate results assuming a large enough resolution.
        Supported: 2 explicit, 4 explicit, 6 implicit (inherited from `phi.field.laplace()`).
        For FVM, the order is used when interpolating `v` and `prev_v` to cell faces if needed.
    implicit: When a `Solve` object is passed, performs an implicit operation with the specified solver and tolerances.
        Otherwise, an explicit stencil is used.
    upwind: For unstructured meshes only. Whether to use upwind interpolation.
    correct_skew: If `True`, adds a correction term for cell skewness. This requires `gradient` to be passed.

Returns:
    Differential diffusion as a `Field` on the same geometry.
```

### [Function] mac_cormack
```python
MacCormack advection uses a forward and backward lookup to determine the first-order error of semi-Lagrangian advection.
It then uses that error estimate to correct the field values.
To avoid overshoots, the resulting value is bounded by the neighbouring grid cells of the backward lookup.

Args:
    field: Field to be advected, one of `(CenteredGrid, StaggeredGrid)`
    velocity: Vector field, need not be sampled at same locations as `field`.
    dt: Time increment
    correction_strength: The estimated error is multiplied by this factor before being applied.
        The case correction_strength=0 equals semi-lagrangian advection. Set lower than 1.0 to avoid oscillations.
    integrator: ODE integrator for solving the movement.

Returns:
    Advected field of type `type(field)`
```

### [Function] masked_laplace
```python
Computes the laplace of `pressure` in the presence of obstacles.

Args:
    pressure: Pressure field.
    hard_bcs: Mask encoding which cells are connected to each other.
        One between fluid cells, zero inside and at the boundary of obstacles.
        This should be of the same type as the velocity, i.e. `StaggeredGrid` or `CenteredGrid`.
    active: Mask indicating for which cells the pressure value is valid.
        Linear solves will only determine the pressure for these cells.
        This is generally zero inside obstacles and in non-simulated regions.
    order: Spatial order of accuracy.
        Higher orders entail larger stencils and more computation time but result in more accurate results assuming a large enough resolution.
        Supported: 2 explicit, 4 explicit, 6 implicit (inherited from `phi.field.laplace()`).

Returns:
    `CenteredGrid`
```

### [Function] semi_lagrangian
```python
Semi-Lagrangian advection with simple backward lookup.

This method samples the `velocity` at the grid points of `field`
to determine the lookup location for each grid point by walking backwards along the velocity vectors.
The new values are then determined by sampling `field` at these lookup locations.

Args:
    field: quantity to be advected, stored on a grid (CenteredGrid or StaggeredGrid)
    velocity: vector field, need not be compatible with with `field`.
    dt: time increment
    integrator: ODE integrator for solving the movement.

Returns:
    Field with same sample points as `field`
```

### [Function] implicit
```python
Implicit Euler diffusion.

Diffusion by solving a linear system of equations.

Args:
    field: `phi.field.Field` to diffuse.
    diffusivity: Diffusion per time. `diffusion_amount = diffusivity * dt`
    dt: Time interval. `diffusion_amount = diffusivity * dt`
    solve: Implicit solve parameters.
    gradient: Only used by FVM at the moment. Approximate gradient of `u`, e.g. ∇u of the previous time step.
        If `None`, approximates the gradient as `(u_neighbor - u_self) / distance`.
    upwind: For unstructured meshes only. Whether to use upwind interpolation.
    correct_skew: If `True`, adds a correction term for cell skewness. This requires `gradient` to be passed.
    gradient_for_diffusivity: Whether to compute the gradient w.r.t. the diffusivity parameters.

Returns:
    Diffused field of same type as `field`.
```

### [Function] get_coefficients
```python
No docstring available.
```

### [Function] advect
```python
Advect `field` along the `velocity` vectors using the specified integrator.

The behavior depends on the type of `field`:

* `phi.field.PointCloud`: Points are advected forward, see `points`.
* `phi.field.Grid`: Sample points are traced backward, see `semi_lagrangian`.

Args:
    field: Field to be advected as `phi.field.Field`.
    velocity: Any `phi.field.Field` that can be sampled in the elements of `field`.
    dt: Time increment
    integrator: ODE integrator for solving the movement.

Returns:
    Advected field of same type as `field`
```

### [Function] step
```python
Advance the wave equation by one time step using leapfrog (Verlet) integration.

Solves ∂²u/∂t² = c² ∇²u + f where u is the wave amplitude, c is the wave speed,
and f is an optional source term.

This scheme is second-order accurate in both space and time and preserves energy.

Args:
    u: Current wave amplitude as a `CenteredGrid` or other `Field`.
    u_prev: Wave amplitude at the previous time step.
    c: Wave speed. Can be a constant, `Tensor`, or spatially varying `Field`.
    dt: Time step size.
    source: Optional source term f(x, t) as a `Field`.

Returns:
    Tuple of `(u_next, u)` where `u_next` is the amplitude at the new time step.
    Pass these as `(u, u_prev)` to advance again.

Examples:
    >>> from phi.flow import *
    >>> u = CenteredGrid(Noise(), x=64, y=64, bounds=Box(x=1, y=1))
    >>> u_prev = u  # start from rest
    >>> u_next, u = wave.step(u, u_prev, c=1.0, dt=0.01)
```

### [Function] curl
```python
Computes the finite-difference curl of the give 2D `StaggeredGrid`.

Args:
    field: `Field`
    at: Either `center` or `face`.
```

### [Function] explicit
```python
Explicit Euler diffusion with substeps.

Simulate a finite-time diffusion process of the form dF/dt = α · ΔF on a given `Field` Field with diffusion coefficient α.

Args:
    u: CenteredGrid, StaggeredGrid or ConstantField
    diffusivity: Diffusion per time. `diffusion_amount = diffusivity * dt`
        Can be a number, `phi.Tensor` or `phi.field.Field`.
        If a channel dimension is present, it will be interpreted as non-isotropic diffusion.
    dt: Time interval. `diffusion_amount = diffusivity * dt`
    substeps: number of iterations to use (Default value = 1)
    order: Spatial order of accuracy.
        Higher orders entail larger stencils and more computation time but result in more accurate results assuming a large enough resolution.
        Supported: 2 explicit, 4 explicit, 6 implicit (inherited from `phi.field.laplace()`).
        For FVM, the order is used when interpolating `v` and `prev_v` to cell faces if needed.
    implicit: When a `Solve` object is passed, performs a spatially implicit operation with the specified solver and tolerances.
        Otherwise, an explicit stencil is used.
    gradient: Only used by FVM at the moment. Approximate gradient of `u`, e.g. ∇u of the previous time step.
        If `None`, approximates the gradient as `(u_neighbor - u_self) / distance`.
    upwind: For unstructured meshes only. Whether to use upwind interpolation.
    correct_skew: If `True`, adds a correction term for cell skewness. This requires `gradient` to be passed.

Returns:
    Diffused field of same type as `field`.
```

### [Parameter] pde
```python
No docstring available.
```

### [Class] Field
```python
A `Field` represents a discretized physical quantity (like temperature field or velocity field).
The sample points and their relation are encoded in the `geometry` property and the corresponding values are stored as one `Tensor` in `values`.
The boundary conditions and values outside the geometry are determined by `boundary`.

Examples:
    Create a periodic 2D grid, initialized via noise fluctuations.
    >>> Field(UniformGrid(x=32, y=32), values=Noise(), boundary=PERIODIC)

    Create a field on an unstructured mesh loaded from a .gmsh file
    >>> mesh = phi.geom.load_gmsh('cylinder.msh', ('y-', 'x+', 'y+', 'x-', 'cyl+', 'cyl-'))
    >>> Field(mesh, values=vec(x=1, y=0), boundary={'x': ZERO_GRADIENT, 'y': 0, 'cyl': 0})

    Create two cubes and compute a scalar values for each.
    >>> Field(Cuboid(vec(x=[0, 2], y=0), x=1, y=1), values=lambda x,y: x)

See the `phi.field` module documentation at https://tum-pbs.github.io/PhiFlow/Fields.html
```

### [Parameter] boundary_condition
```python
No docstring available.
```

### [Function] laplace
```python
Spatial Laplace operator for scalar grid.

For grids, uses a finite difference scheme specified by `order` and `implicit`.
For unstructured meshes, the scheme is specified via `order` and `upwind`.

Args:
    u: n-dimensional grid or mesh.
    axes: The second derivative along these dimensions is summed over
    weights: (Optional) Multiply the axis terms by these factors before summation.
        Must be a `phi.math.Tensor` or `phi.field.Field` with a single channel dimension that lists all laplace axes by name.
    gradient: Only used by FVM at the moment. Approximate gradient of `u`, e.g. ∇u of the previous time step.
        If `None`, approximates the gradient as `(u_neighbor - u_self) / distance`.
    order: Spatial order of accuracy.
        Higher orders entail larger stencils and more computation time but result in more accurate results assuming a large enough resolution.
        Supported: 2 explicit, 4 explicit, 6 implicit (inherited from `phi.field.laplace()`).
        For FVM, the order is used when interpolating `v` and `prev_v` to cell faces if needed.
    implicit: When a `Solve` object is passed, performs an implicit operation with the specified solver and tolerances.
        Otherwise, an explicit stencil is used.
    implicitness: specifies the size of the implicit stencil in case an implicit treatment is used
    upwind: FVM only. Whether to use upwind interpolation.
    correct_skew: If `True`, adds a correction term for cell skewness. This requires `gradient` to be passed.

Returns:
    laplacian field as `CenteredGrid`
```

### [Class] Mesh
```python
Unstructured mesh, consisting of vertices and elements.

Use `phi.geom.mesh()` or `phi.geom.mesh_from_numpy()` to construct a mesh manually or `phi.geom.load_su2()` to load one from a file.
```

### [Method] boundary_connectivity
```python
No docstring available.
```

### [Function] finite_rk4
```python
Runge-Kutta-4 integrator with Euler fallback where velocity values are NaN. 
```

### [Function] divergence
```python
Computes the divergence of a grid using finite differences.

This function can operate in two modes depending on the type of `field`:

* `CenteredGrid` approximates the divergence at cell centers using central differences
* `StaggeredGrid` exactly computes the divergence at cell centers

Args:
    field: vector field as `CenteredGrid` or `StaggeredGrid`
    order: Spatial order of accuracy.
        Higher orders entail larger stencils and more computation time but result in more accurate results assuming a large enough resolution.
        Supported: 2 explicit, 4 explicit, 6 implicit.
    implicit: When a `Solve` object is passed, performs an implicit operation with the specified solver and tolerances.
        Otherwise, an explicit stencil is used.
    implicitness: specifies the size of the implicit stencil in case an implicit treatment is used
    upwind: For unstructured meshes only. Whether to use upwind interpolation.

Returns:
    Divergence field as `CenteredGrid`
```

### [Method] as_boundary
```python
Returns an `Extrapolation` representing this 'Field''s values as a Dirichlet (constant) boundary.
If this `Field` encloses the required boundaries, its values will be interpolated to the required boundaries.
If boundaries outside of this `Field`'s sampled domain are required, this `Field`'s boundary conditions will be applied to determine the boundary values.

Returns:
    `Extrapolation`
```

### [Class] Domain
```python
No docstring available.
```

### [Method] accessible_mask
```python
Unifies domain and Obstacle or Geometry objects into a binary StaggeredGrid mask which can be used
to enforce boundary conditions.

Args:
    not_accessible: blocked region(s) of space specified by geometries
    type: class of Grid to create, must be either CenteredGrid or StaggeredGrid
    extrapolation: (optional) grid extrapolation, defaults to Domain.boundaries['accessible']

Returns:
    Binary mask indicating valid fields w.r.t. the boundary conditions.
```

### [Function] fourier_laplace
```python
See `phi.math.fourier_laplace()` 
```

### [Method] _sample
```python
No docstring available.
```

### [Method] __init__
```python
The Domain specifies the grid resolution, physical size and boundary conditions of a simulation.

It provides convenience methods for creating Grids fitting the domain, e.g. `grid()`, `vector_grid()` and `staggered_grid()`.

Also see the `phi.physics` module documentation at https://tum-pbs.github.io/PhiFlow/Physics.html

Args:
  resolution: grid dimensions as Shape or sequence of integers. Alternatively, dimensions can be specified directly as kwargs.
  boundaries: specifies the extrapolation modes of grids created from this Domain.
    Default materials include OPEN, CLOSED, PERIODIC.
    To specify boundary conditions per face of the domain, pass a sequence of boundaries or boundary pairs (lower, upper)., e.g. [CLOSED, (CLOSED, OPEN)].
    See https://tum-pbs.github.io/PhiFlow/Physics.html#boundary-conditions .
  bounds: physical size of the domain. If not provided, the size is equal to the resolution (unit cubes).
```

---

## 2. GRAPH INTERCONNECTIONS & DEPENDENCIES

- [Class] Domain --(Has Method)--> [Method] accessible_mask
- [Class] Field --(Has Method)--> [Method] as_boundary
- [Class] Mesh --(Has Method)--> [Method] boundary_connectivity
- [Function] apply_boundary_conditions --(Has Description)--> [GeneratedDescription] Unknown
- [Function] curl --(Has Description)--> [GeneratedDescription] Unknown
- [Function] differential --(Has Description)--> [GeneratedDescription] Unknown
- [Function] explicit --(Has Description)--> [GeneratedDescription] Unknown
- [Function] fourier_laplace --(Has Description)--> [GeneratedDescription] Unknown
- [Function] fourier_poisson --(Has Description)--> [GeneratedDescription] Unknown
- [Function] get_coefficients --(Has Description)--> [GeneratedDescription] Unknown
- [Function] get_coefficients --(Has Parameter)--> [Parameter] boundary_condition
- [Function] incompressible_rk4 --(Has Description)--> [GeneratedDescription] Unknown
- [Function] incompressible_rk4 --(Has Parameter)--> [Parameter] pde
- [Function] laplace --(Has Description)--> [GeneratedDescription] Unknown
- [GeneratedDescription] Unknown --(Defines Class)--> [Class] Field
- [GeneratedDescription] Unknown --(Defines Function)--> [Function] advect
- [GeneratedDescription] Unknown --(Defines Function)--> [Function] apply_boundary_conditions
- [GeneratedDescription] Unknown --(Defines Function)--> [Function] curl
- [GeneratedDescription] Unknown --(Defines Function)--> [Function] differential
- [GeneratedDescription] Unknown --(Defines Function)--> [Function] divergence
- [GeneratedDescription] Unknown --(Defines Function)--> [Function] euler_step
- [GeneratedDescription] Unknown --(Defines Function)--> [Function] explicit
- [GeneratedDescription] Unknown --(Defines Function)--> [Function] finite_rk4
- [GeneratedDescription] Unknown --(Defines Function)--> [Function] implicit
- [GeneratedDescription] Unknown --(Defines Function)--> [Function] incompressible_rk4
- [GeneratedDescription] Unknown --(Defines Function)--> [Function] laplace
- [GeneratedDescription] Unknown --(Defines Function)--> [Function] mac_cormack
- [GeneratedDescription] Unknown --(Defines Function)--> [Function] make_incompressible
- [GeneratedDescription] Unknown --(Defines Function)--> [Function] masked_laplace
- [GeneratedDescription] Unknown --(Defines Function)--> [Function] semi_lagrangian
- [GeneratedDescription] Unknown --(Defines Function)--> [Function] step
- [Method] __init__ --(Has Description)--> [GeneratedDescription] Unknown
- [Method] _sample --(Has Description)--> [GeneratedDescription] Unknown
