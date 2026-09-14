# CODEBASE COMPONENT SPECIFICATIONS & API REFERENCE

## 1. PRIMARY PUBLIC API ENDPOINTS (PREFER USING THESE)

### [Function] masked_laplace
**Import Path:** `phi.flow.fluid.masked_laplace`

**Usage:** `fluid.masked_laplace(...)` or `from phi.flow.fluid import masked_laplace; masked_laplace(...)`

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

### [Function] apply_boundary_conditions
**Import Path:** `phi.flow.fluid.apply_boundary_conditions`

**Usage:** `fluid.apply_boundary_conditions(...)` or `from phi.flow.fluid import apply_boundary_conditions; apply_boundary_conditions(...)`

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

### [Function] points
**Import Path:** `phi.flow.advect.points`

**Usage:** `advect.points(...)` or `from phi.flow.advect import points; points(...)`

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

### [Function] make_incompressible
**Import Path:** `phi.flow.fluid.make_incompressible`

**Usage:** `fluid.make_incompressible(...)` or `from phi.flow.fluid import make_incompressible; make_incompressible(...)`

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

### [Function] CenteredGrid
**Import Path:** `phi.flow.CenteredGrid`

**Usage:** `flow.CenteredGrid(...)` or `from phi.flow import CenteredGrid; CenteredGrid(...)`

**Signature/Docstring:**
```python
Create an n-dimensional grid with values sampled at the cell centers.
A centered grid is defined through its `CenteredGrid.values` `phi.math.Tensor`, its `CenteredGrid.bounds` `phi.geom.Box` describing the physical size, and its `CenteredGrid.extrapolation` (`phi.math.extrapolation.Extrapolation`).

Centered grids support batch, spatial and channel dimensions.

See Also:
    `StaggeredGrid`,
    `Grid`,
    `Field`,
    `Field`,
    module documentation at https://tum-pbs.github.io/PhiFlow/Fields.html

Args:
    values: Values to use for the grid.
        Has to be one of the following:

        * `phi.geom.Geometry`: sets inside values to 1, outside to 0
        * `Field`: resamples the Field to the staggered sample points
        * `Number`: uses the value for all sample points
        * `tuple` or `list`: interprets the sequence as vector, used for all sample points
        * `phi.math.Tensor` compatible with grid dims: uses tensor values as grid values
        * Function `values(x)` where `x` is a `phi.math.Tensor` representing the physical location.
            The spatial dimensions of the grid will be passed as batch dimensions to the function.

    extrapolation: The grid extrapolation determines the value outside the `values` tensor.
        Allowed types: `float`, `phi.math.Tensor`, `phi.math.extrapolation.Extrapolation`.
    bounds: Physical size and location of the grid as `phi.geom.Box`.
        If the resolution is determined through `resolution` of `values`, a `float` can be passed for `bounds` to create a unit box.
    resolution: Grid resolution as purely spatial `phi.math.Shape`.
        If `bounds` is given as a `Box`, the resolution may be specified as an `int` to be equal along all axes.
    **resolution_: Spatial dimensions as keyword arguments. Typically either `resolution` or `spatial_dims` are specified.
    convert: Whether to convert `values` to the default backend.
```

### [Function] incompressible_rk4
**Import Path:** `phi.flow.fluid.incompressible_rk4`

**Usage:** `fluid.incompressible_rk4(...)` or `from phi.flow.fluid import incompressible_rk4; incompressible_rk4(...)`

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

### [Function] euler
**Import Path:** `phi.flow.advect.euler`

**Usage:** `advect.euler(...)` or `from phi.flow.advect import euler; euler(...)`

**Signature/Docstring:**
```python
Euler integrator. 
```

### [Class] Obstacle
**Import Path:** `phi.flow.Obstacle`

**Usage:** `from phi.flow.Obstacle import Obstacle; Obstacle(...)` or direct instantiation from phi.flow

**Signature/Docstring:**
```python
An obstacle defines boundary conditions inside a geometry.
It can also have a linear and angular velocity.
```

### [Function] differential
**Import Path:** `phi.flow.advect.differential`

**Usage:** `advect.differential(...)` or `from phi.flow.advect import differential; differential(...)`

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

### [Function] StaggeredGrid
**Import Path:** `phi.flow.StaggeredGrid`

**Usage:** `flow.StaggeredGrid(...)` or `from phi.flow import StaggeredGrid; StaggeredGrid(...)`

**Signature/Docstring:**
```python
N-dimensional grid whose vector components are sampled at the respective face centers.
A staggered grid is defined through its values tensor, its bounds describing the physical size, and its extrapolation.

Staggered grids support batch and spatial dimensions but only one channel dimension for the staggered vector components.

See Also:
    `CenteredGrid`,
    `Grid`,
    `Field`,
    `Field`,
    module documentation at https://tum-pbs.github.io/PhiFlow/Fields.html

Args:
    values: Values to use for the grid.
        Has to be one of the following:

        * `phi.geom.Geometry`: sets inside values to 1, outside to 0
        * `Field`: resamples the Field to the staggered sample points
        * `Number`: uses the value for all sample points
        * `tuple` or `list`: interprets the sequence as vector, used for all sample points
        * `phi.math.Tensor` with staggered shape: uses tensor values as grid values.
          Must contain a `vector` dimension with each slice consisting of one more element along the dimension they describe.
          Use `phi.math.stack()` to manually create this non-uniform tensor.
        * Function `values(x)` where `x` is a `phi.math.Tensor` representing the physical location.
            The spatial dimensions of the grid will be passed as batch dimensions to the function.

    boundary: The grid extrapolation determines the value outside the `values` tensor.
        Allowed types: `float`, `phi.math.Tensor`, `phi.math.extrapolation.Extrapolation`.
    bounds: Physical size and location of the grid as `phi.geom.Box`.
        If the resolution is determined through `resolution` of `values`, a `float` can be passed for `bounds` to create a unit box.
    resolution: Grid resolution as purely spatial `phi.math.Shape`.
        If `bounds` is given as a `Box`, the resolution may be specified as an `int` to be equal along all axes.
    convert: Whether to convert `values` to the default backend.
    **resolution_: Spatial dimensions as keyword arguments. Typically either `resolution` or `spatial_dims` are specified.
```

### [Function] mac_cormack
**Import Path:** `phi.flow.advect.mac_cormack`

**Usage:** `advect.mac_cormack(...)` or `from phi.flow.advect import mac_cormack; mac_cormack(...)`

**Signature/Docstring:**
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

### [Function] finite_rk4
**Import Path:** `phi.flow.advect.finite_rk4`

**Usage:** `advect.finite_rk4(...)` or `from phi.flow.advect import finite_rk4; finite_rk4(...)`

**Signature/Docstring:**
```python
Runge-Kutta-4 integrator with Euler fallback where velocity values are NaN. 
```

### [Class] Noise
**Import Path:** `phi.flow.Noise`

**Usage:** `from phi.flow.Noise import Noise; Noise(...)` or direct instantiation from phi.flow

**Signature/Docstring:**
```python
Generates random noise fluctuations which can be configured in physical size and smoothness.
Each time values are sampled from a Noise field, a new noise field is generated.

Noise is typically used as an initializer for CenteredGrids or StaggeredGrids.
```

### [Function] boundary_push
**Import Path:** `phi.flow.fluid.boundary_push`

**Usage:** `fluid.boundary_push(...)` or `from phi.flow.fluid import boundary_push; boundary_push(...)`

**Signature/Docstring:**
```python
Enforces boundary conditions by correcting possible errors of the advection step and shifting particles out of
obstacles or back into the domain.

Args:
    particles: PointCloud holding particle positions as elements
    obstacles: List of `Obstacle` or `Geometry` objects where any particles inside should get shifted outwards
    separation: Minimum distance between particles and domain boundary / obstacle surface after particles have been shifted.

Returns:
    PointCloud where all particles are inside the domain / outside of obstacles.
```

### [Class] UniformGrid
**Import Path:** `phi.flow.UniformGrid`

**Usage:** `from phi.flow.UniformGrid import UniformGrid; UniformGrid(...)` or direct instantiation from phi.flow

**Signature/Docstring:**
```python
An instance of UniformGrid represents all cells of a regular grid as a batch of boxes.
```

### [Function] semi_lagrangian
**Import Path:** `phi.flow.advect.semi_lagrangian`

**Usage:** `advect.semi_lagrangian(...)` or `from phi.flow.advect import semi_lagrangian; semi_lagrangian(...)`

**Signature/Docstring:**
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

### [Function] mask
**Import Path:** `phi.flow.mask`

**Usage:** `flow.mask(...)` or `from phi.flow import mask; mask(...)`

**Signature/Docstring:**
```python
Returns a `Field` that masks the inside (or non-zero values when `obj` is a grid) of a physical object.
The mask takes the value 1 inside the object and 0 outside.
For `CenteredGrid` and `StaggeredGrid`, the mask labels non-zero non-NaN entries as 1 and all other values as 0

Returns:
    `Grid` type or `PointCloud`
```

### [Function] rk4
**Import Path:** `phi.flow.advect.rk4`

**Usage:** `advect.rk4(...)` or `from phi.flow.advect import rk4; rk4(...)`

**Signature/Docstring:**
```python
Runge-Kutta-4 integrator. 
```

