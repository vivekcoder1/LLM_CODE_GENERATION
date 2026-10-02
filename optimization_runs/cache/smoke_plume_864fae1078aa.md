# CODEBASE COMPONENT SPECIFICATIONS & API REFERENCE

## 1. PRIMARY PUBLIC API ENDPOINTS (PREFER USING THESE)

### [Function] masked_laplace
**Import Path:** `phi.flow.fluid.masked_laplace`

**Usage:** `fluid.masked_laplace(...)` or `from phi.flow.fluid import masked_laplace; masked_laplace(...)`

**Returns:** `CenteredGrid`

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

### [Function] explicit
**Import Path:** `phi.flow.diffuse.explicit`

**Usage:** `diffuse.explicit(...)` or `from phi.flow.diffuse import explicit; explicit(...)`

**Signature/Docstring:**
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

**Parameters:**
- pressure_solve

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

### [Function] differential
**Import Path:** `phi.flow.diffuse.differential`

**Usage:** `diffuse.differential(...)` or `from phi.flow.diffuse import differential; differential(...)`

**Signature/Docstring:**
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

### [Function] implicit
**Import Path:** `phi.flow.diffuse.implicit`

**Usage:** `diffuse.implicit(...)` or `from phi.flow.diffuse import implicit; implicit(...)`

**Signature/Docstring:**
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

### [Function] cylinder
**Import Path:** `phi.flow.cylinder`

**Usage:** `flow.cylinder(...)` or `from phi.flow import cylinder; cylinder(...)`

**Signature/Docstring:**
```python
Args:
    center: Cylinder center as `Tensor` with `vector` dimension.
        The spatial dimension order should be specified in the `vector` dimension via item names.
        Can be left empty to specify dimensions via kwargs.
    radius: Cylinder radius as `float` or `Tensor`.
    depth: Cylinder length as `float` or `Tensor`.
    rotation: Rotation angle(s) or rotation matrix.
    axis: The cylinder is aligned along this axis, perturbed by `rotation`.
        Specified either as the dim along which the cylinder is aligned or as a vector.
    variables: Which properties of the cylinder are variable, i.e. traced and optimizable. All by default.
    **center_: Specifies center when the `center` argument is not given. Center position by dimension, e.g. `x=0.5, y=0.2`.
```

### [Class] Field
**Import Path:** `phi.flow.Field`

**Usage:** `from phi.flow.Field import Field; Field(...)` or direct instantiation from phi.flow

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

### [Function] fourier
**Import Path:** `phi.flow.diffuse.fourier`

**Usage:** `diffuse.fourier(...)` or `from phi.flow.diffuse import fourier; fourier(...)`

**Signature/Docstring:**
```python
Exact diffusion of a periodic field in frequency space.

For non-periodic fields or non-constant diffusivity, use another diffusion function such as `explicit()`.

Args:
    field:
    diffusivity: Diffusion per time. `diffusion_amount = diffusivity * dt`
    dt: Time interval. `diffusion_amount = diffusivity * dt`

Returns:
    Diffused field of same type as `field`.
```

### [Function] advect
**Import Path:** `phi.flow.advect`

**Usage:** `flow.advect(...)` or `from phi.flow import advect; advect(...)`

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

### [Class] HardGeometryMask
**Import Path:** `phi.flow.HardGeometryMask`

**Usage:** `from phi.flow.HardGeometryMask import HardGeometryMask; HardGeometryMask(...)` or direct instantiation from phi.flow

**Signature/Docstring:**
```python
Deprecated since version 2.3. Use `phi.field.mask()` or `phi.field.resample()` instead.
```

### [Class] Mesh
**Import Path:** `phi.flow.Mesh`

**Usage:** `from phi.flow.Mesh import Mesh; Mesh(...)` or direct instantiation from phi.flow

**Signature/Docstring:**
```python
Unstructured mesh, consisting of vertices and elements.

Use `phi.geom.mesh()` or `phi.geom.mesh_from_numpy()` to construct a mesh manually or `phi.geom.load_su2()` to load one from a file.
```

### [Class] Scene
**Import Path:** `phi.flow.Scene`

**Usage:** `from phi.flow.Scene import Scene; Scene(...)` or direct instantiation from phi.flow

**Signature/Docstring:**
```python
Provides methods for reading and writing simulation data.

See the format documentation at https://tum-pbs.github.io/PhiFlow/Scene_Format_Specification.html .

All data of a `Scene` is located inside a single directory with name `sim_xxxxxx` where `xxxxxx` is the `id`.
The data of the scene is organized into NumPy files by *name* and *frame*.

To create a new scene, use `Scene.create()`.
To reference an existing scene, use `Scene.at()`.
To list all scenes within a directory, use `Scene.list()`.
```

### [Function] normalize
**Import Path:** `phi.flow.normalize`

**Usage:** `flow.normalize(...)` or `from phi.flow import normalize; normalize(...)`

**Signature/Docstring:**
```python
Multiplies the values of `field` so that its sum matches the source. 
```

### [Function] sharpen
**Import Path:** `phi.flow.diffuse.sharpen`

**Usage:** `diffuse.sharpen(...)` or `from phi.flow.diffuse import sharpen; sharpen(...)`

### [Class] Sphere
**Import Path:** `phi.flow.Sphere`

**Usage:** `from phi.flow.Sphere import Sphere; Sphere(...)` or direct instantiation from phi.flow

**Signature/Docstring:**
```python
N-dimensional sphere.
Defined through center position and radius.
```

### [Class] Box
**Import Path:** `phi.flow.Box`

**Usage:** `from phi.flow.Box import Box; Box(...)` or direct instantiation from phi.flow

**Signature/Docstring:**
```python
Simple cuboid defined by location of lower and upper corner in physical space.

Boxes can be constructed either from two positional vector arguments `(lower, upper)` or by specifying the limits by dimension name as `kwargs`.

Examples:
    >>> Box(x=1, y=1)  # creates a two-dimensional unit box with `lower=(0, 0)` and `upper=(1, 1)`.
    >>> Box(x=(None, 1), y=(0, None)  # creates a Box with `lower=(-inf, 0)` and `upper=(1, inf)`.

    The slicing constructor was updated in version 2.2 and now requires the dimension order as the first argument.

    >>> Box['x,y', 0:1, 0:1]  # creates a two-dimensional unit box with `lower=(0, 0)` and `upper=(1, 1)`.
    >>> Box['x,y', :1, 0:]  # creates a Box with `lower=(-inf, 0)` and `upper=(1, inf)`.
```

### [Function] Cuboid
**Import Path:** `phi.flow.Cuboid`

**Usage:** `flow.Cuboid(...)` or `from phi.flow import Cuboid; Cuboid(...)`

**Signature/Docstring:**
```python
Args:
    center: Center position
    half_size: Half-size of the cuboid as vector or scalar
    rotation: Rotation angle(s) or rotation matrix.
    is_open: Specify which faces are open, i.e. have infinite extent.
    variable_attrs: Which properties of the box are treated as variable.
    **size: Alternative way of specifying the size. If used, `half_size` must not be specified.
```

