# CODEBASE COMPONENT SPECIFICATIONS & API REFERENCE

## 1. COMPONENT SIGNATURES & FUNCTIONAL DESCRIPTIONS

### [Class] AngularVelocity
**Signature/Docstring:**
```python
Model of a single vortex or set of vortices.
The falloff of the velocity magnitude can be controlled.

Without a specified falloff, the velocity increases linearly with the distance from the vortex center.
This is the case with rotating rigid bodies, for example.
```

### [Method] _sample
**Signature/Docstring:**
```python
No docstring available.
```

### [File] fluid.py
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] masked_laplace
**Signature/Docstring:**
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

### [Function] fourier_poisson
**Signature/Docstring:**
```python
See `phi.math.fourier_poisson()` 
```

### [Function] incompressible_rk4
**Signature/Docstring:**
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

### [Parameter] pressure_solve
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] apply_boundary_conditions
**Signature/Docstring:**
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

### [Class] Cylinder
**Signature/Docstring:**
```python
N-dimensional cylinder.
Defined by center position, radius, depth, alignment axis, rotation.

For cylinders whose bottom and top lie outside the domain or are otherwise not needed, you may use `infinite_cylinder` instead, which simplifies computations.
```

### [Method] sample_uniform
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] curl
**Signature/Docstring:**
```python
Computes the finite-difference curl of the give 2D `StaggeredGrid`.

Args:
    field: `Field`
    at: Either `center` or `face`.
```

### [Class] HardGeometryMask
**Signature/Docstring:**
```python
Deprecated since version 2.3. Use `phi.field.mask()` or `phi.field.resample()` instead.
```

### [Method] _sample
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] points
**Signature/Docstring:**
```python
Advects the sample points of a point cloud using a simple Euler step.
Each point moves by an amount equal to the local velocity times `dt`.

Args:
    points: Points to be advected. Can be provided as position `Tensor`, `Geometry` or `Field`.
    velocity: velocity sampled at the same points as the point cloud
    dt: Euler step time increment
    integrator: ODE integrator for solving the movement.

Returns:
    Advected points, same type as `points`.
```

### [Function] sample_grid_at_centers
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] fourier_laplace
**Signature/Docstring:**
```python
See `phi.math.fourier_laplace()` 
```

### [Class] Noise
**Signature/Docstring:**
```python
Generates random noise fluctuations which can be configured in physical size and smoothness.
Each time values are sampled from a Noise field, a new noise field is generated.

Noise is typically used as an initializer for CenteredGrids or StaggeredGrids.
```

### [Method] grid_sample
**Signature/Docstring:**
```python
No docstring available.
```

### [Parameter] pressure_order
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] _balance_divergence
**Signature/Docstring:**
```python
No docstring available.
```

### [Parameter] pressure
**Signature/Docstring:**
```python
No docstring available.
```

### [Parameter] pressure
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] sample_grid_at_faces
**Signature/Docstring:**
```python
No docstring available.
```

### [Class] Mesh
**Signature/Docstring:**
```python
Unstructured mesh, consisting of vertices and elements.

Use `phi.geom.mesh()` or `phi.geom.mesh_from_numpy()` to construct a mesh manually or `phi.geom.load_su2()` to load one from a file.
```

### [Method] sample_uniform
**Signature/Docstring:**
```python
No docstring available.
```

### [Class] UniformGrid
**Signature/Docstring:**
```python
An instance of UniformGrid represents all cells of a regular grid as a batch of boxes.
```

### [Method] volume
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] sample_staggered_grid
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] create_similar_grid
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] volume
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] boundary_faces
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] grid_scatter
**Signature/Docstring:**
```python
Approximately samples this field on a regular grid using math.scatter().

Args:
    outside_handling: `str` passed to `phi.math.scatter()`.
    bounds: physical dimensions of the grid
    resolution: grid resolution

Returns:
    `CenteredGrid`
```

### [Class] Field
**Signature/Docstring:**
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

### [Method] divergence
**Signature/Docstring:**
```python
Alias for `phi.field.divergence`
```

### [Function] make_incompressible
**Signature/Docstring:**
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

### [Class] Domain
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] grid
**Signature/Docstring:**
```python
Creates a grid matching the resolution and bounds of the domain.
The grid is created from the given `value` which must be one of the following:

* Number (int, float, complex or zero-dimensional tensor): all grid values will be equal to `value`. This has a near-zero memory footprint.
* Field: the given value is resampled to the grid cells of this Domain.
* Tensor with spatial dimensions matching the domain resolution: grid values will equal `value`.
* Geometry: grid values are determined from the volume overlap between grid cells and geometry. Non-overlapping = 0, fully enclosed grid cell = 1.
* function(location: Tensor) returning one of the above.

Args:
  value: constant, Field, Tensor or function specifying the grid values
  type: type of Grid to create, must be either CenteredGrid or StaggeredGrid
  extrapolation: (optional) grid extrapolation, defaults to Domain.boundaries['scalar']

Returns:
    Grid of specified type
```

### [Method] boundary_elements
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] upper
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] bounding_half_extent
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] _accessible_extrapolation
**Signature/Docstring:**
```python
Determine whether outside cells are accessible based on the velocity extrapolation. 
```

### [Function] euler
**Signature/Docstring:**
```python
Euler integrator. 
```

### [Parameter] velocity
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] finite_rk4
**Signature/Docstring:**
```python
Runge-Kutta-4 integrator with Euler fallback where velocity values are NaN. 
```

### [Parameter] velocity
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] advect
**Signature/Docstring:**
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

### [Parameter] velocity
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] differential
**Signature/Docstring:**
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

### [Parameter] velocity
**Signature/Docstring:**
```python
No docstring available.
```

---

## 2. GRAPH INTERCONNECTIONS & DEPENDENCIES

- [Class] AngularVelocity --(Has Method)--> [Method] _sample
- [Class] Cylinder --(Has Method)--> [Method] sample_uniform
- [Class] Cylinder --(Has Method)--> [Method] volume
- [Class] Domain --(Has Method)--> [Method] grid
- [Class] Field --(Has Method)--> [Method] divergence
- [Class] HardGeometryMask --(Has Method)--> [Method] _sample
- [Class] Mesh --(Has Method)--> [Method] sample_uniform
- [Class] Noise --(Has Method)--> [Method] grid_sample
- [Class] UniformGrid --(Has Method)--> [Method] boundary_elements
- [Class] UniformGrid --(Has Method)--> [Method] boundary_faces
- [Class] UniformGrid --(Has Method)--> [Method] bounding_half_extent
- [Class] UniformGrid --(Has Method)--> [Method] upper
- [Class] UniformGrid --(Has Method)--> [Method] volume
- [File] fluid.py --(Defines Function)--> [Function] _accessible_extrapolation
- [File] fluid.py --(Defines Function)--> [Function] _balance_divergence
- [File] fluid.py --(Defines Function)--> [Function] apply_boundary_conditions
- [File] fluid.py --(Defines Function)--> [Function] create_similar_grid
- [File] fluid.py --(Defines Function)--> [Function] curl
- [File] fluid.py --(Defines Function)--> [Function] fourier_laplace
- [File] fluid.py --(Defines Function)--> [Function] fourier_poisson
- [File] fluid.py --(Defines Function)--> [Function] grid_scatter
- [File] fluid.py --(Defines Function)--> [Function] make_incompressible
- [File] fluid.py --(Defines Function)--> [Function] masked_laplace
- [File] fluid.py --(Defines Function)--> [Function] points
- [File] fluid.py --(Defines Function)--> [Function] sample_grid_at_centers
- [File] fluid.py --(Defines Function)--> [Function] sample_grid_at_faces
- [File] fluid.py --(Defines Function)--> [Function] sample_staggered_grid
- [Function] advect --(Has Parameter)--> [Parameter] velocity
- [Function] differential --(Has Parameter)--> [Parameter] velocity
- [Function] euler --(Has Parameter)--> [Parameter] velocity
- [Function] finite_rk4 --(Has Parameter)--> [Parameter] velocity
- [Function] incompressible_rk4 --(Has Parameter)--> [Parameter] pressure
- [Function] incompressible_rk4 --(Has Parameter)--> [Parameter] pressure_order
- [Function] incompressible_rk4 --(Has Parameter)--> [Parameter] pressure_solve
- [Function] masked_laplace --(Has Parameter)--> [Parameter] pressure
