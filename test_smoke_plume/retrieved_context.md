# CODEBASE COMPONENT SPECIFICATIONS & API REFERENCE

## 1. PRIMARY PUBLIC API ENDPOINTS (PREFER USING THESE)

### [File] fluid.py
**Import Path:** `phi.flow.fluid.py`

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

### [Method] sample_uniform_surface
**Import Path:** `phi.flow.Box.sample_uniform_surface`

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

### [Method] at_centers
**Import Path:** `phi.flow.Field.at_centers`

**Signature/Docstring:**
```python
Interpolates the values to the cell centers.

See Also:
    `Field.at_faces()`, `Field.at()`, `resample`.

Args:
    **kwargs: Sampling arguments.

Returns:
    `CenteredGrid` sampled at cell centers.
```

### [Method] curl
**Import Path:** `phi.flow.Field.curl`

**Signature/Docstring:**
```python
Alias for `phi.field.curl`
```

### [Method] divergence
**Import Path:** `phi.flow.Field.divergence`

**Signature/Docstring:**
```python
Alias for `phi.field.divergence`
```

### [Method] gradient
**Import Path:** `phi.flow.Field.gradient`

**Signature/Docstring:**
```python
Alias for `phi.field.spatial_gradient`
```

### [Method] grid
**Import Path:** `phi.flow.Field.grid`

**Signature/Docstring:**
```python
Cast `self.geometry` to a `phi.geom.UniformGrid`.
```

### [Method] grid_scatter
**Import Path:** `phi.flow.Field.grid_scatter`

**Signature/Docstring:**
```python
Deprecated. Use `sample` with `scatter=True` instead.
```

### [Method] is_grid
**Import Path:** `phi.flow.Field.is_grid`

**Signature/Docstring:**
```python
A Field represents grid data if its `geometry` is a `phi.geom.UniformGrid` instance.
```

### [Method] laplace
**Import Path:** `phi.flow.Field.laplace`

**Signature/Docstring:**
```python
Alias for `phi.field.laplace`
```

### [Class] Geometry
**Import Path:** `phi.flow.Geometry`

**Usage:** `from phi.flow.Geometry import Geometry; Geometry(...)` or direct instantiation from phi.flow

**Signature/Docstring:**
```python
Abstract base class for N-dimensional shapes.

Main implementing classes:

* `Sphere`
* `Box`
* `Cylinder`
* `Graph`
* `Mesh`
* `Heightmap`
* `SDFGrid`
* `SDF`
* `SplineSheet`

All geometry objects support batching.
Thereby any parameter defining the geometry can be varied along arbitrary batch dims.
All batch dimensions are listed in Geometry.shape.

Property getters (`@property`, such as `shape`), save for getters, must not depend on any variables marked as *variable* via `__variable_attrs__()` as these may be `None` during tracing.
Equality checks must also take this into account.
```

### [Method] integrate_flux
**Import Path:** `phi.flow.Geometry.integrate_flux`

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

### [Class] UniformGrid
**Import Path:** `phi.flow.UniformGrid`

**Usage:** `from phi.flow.UniformGrid import UniformGrid; UniformGrid(...)` or direct instantiation from phi.flow

**Signature/Docstring:**
```python
An instance of UniformGrid represents all cells of a regular grid as a batch of boxes.
```

### [Method] boundary_elements
**Import Path:** `phi.flow.UniformGrid.boundary_elements`

### [Method] boundary_faces
**Import Path:** `phi.flow.UniformGrid.boundary_faces`

### [Method] bounding_half_extent
**Import Path:** `phi.flow.UniformGrid.bounding_half_extent`

### [Method] face_areas
**Import Path:** `phi.flow.UniformGrid.face_areas`

### [Method] position_of
**Import Path:** `phi.flow.UniformGrid.position_of`

### [Method] rotated
**Import Path:** `phi.flow.UniformGrid.rotated`

### [Method] shifted
**Import Path:** `phi.flow.UniformGrid.shifted`

### [Method] stagger
**Import Path:** `phi.flow.UniformGrid.stagger`

### [Method] upper
**Import Path:** `phi.flow.UniformGrid.upper`

### [Method] volume
**Import Path:** `phi.flow.UniformGrid.volume`

### [Method] voxel_at
**Import Path:** `phi.flow.UniformGrid.voxel_at`

### [Method] with_scaled_resolution
**Import Path:** `phi.flow.UniformGrid.with_scaled_resolution`

### [Class] Mesh
**Import Path:** `phi.flow.Mesh`

**Usage:** `from phi.flow.Mesh import Mesh; Mesh(...)` or direct instantiation from phi.flow

**Signature/Docstring:**
```python
Unstructured mesh, consisting of vertices and elements.

Use `phi.geom.mesh()` or `phi.geom.mesh_from_numpy()` to construct a mesh manually or `phi.geom.load_su2()` to load one from a file.
```

### [Method] sample_uniform
**Import Path:** `phi.flow.Mesh.sample_uniform`

### [Method] volume
**Import Path:** `phi.flow.Mesh.volume`

### [Class] Noise
**Import Path:** `phi.flow.Noise`

**Usage:** `from phi.flow.Noise import Noise; Noise(...)` or direct instantiation from phi.flow

**Signature/Docstring:**
```python
Generates random noise fluctuations which can be configured in physical size and smoothness.
Each time values are sampled from a Noise field, a new noise field is generated.

Noise is typically used as an initializer for CenteredGrids or StaggeredGrids.
```

### [Method] grid_sample
**Import Path:** `phi.flow.Noise.grid_sample`

### [Class] Sphere
**Import Path:** `phi.flow.Sphere`

**Usage:** `from phi.flow.Sphere import Sphere; Sphere(...)` or direct instantiation from phi.flow

**Signature/Docstring:**
```python
N-dimensional sphere.
Defined through center position and radius.
```

### [Method] sample_uniform
**Import Path:** `phi.flow.Sphere.sample_uniform`

### [Function] euler
**Import Path:** `phi.flow.advect.euler`

**Usage:** `advect.euler(...)` or `from phi.flow.advect import euler; euler(...)`

**Signature/Docstring:**
```python
Euler integrator. 
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

### [Class] Obstacle
**Import Path:** `phi.flow.Obstacle`

**Usage:** `from phi.flow.Obstacle import Obstacle; Obstacle(...)` or direct instantiation from phi.flow

**Signature/Docstring:**
```python
An obstacle defines boundary conditions inside a geometry.
It can also have a linear and angular velocity.
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

---

## 2. GRAPH INTERCONNECTIONS & DEPENDENCIES

- [Class] Box --(Has Method)--> [Method] sample_uniform_surface
- [Class] Field --(Has Method)--> [Method] at_centers
- [Class] Field --(Has Method)--> [Method] curl
- [Class] Field --(Has Method)--> [Method] divergence
- [Class] Field --(Has Method)--> [Method] gradient
- [Class] Field --(Has Method)--> [Method] grid
- [Class] Field --(Has Method)--> [Method] grid_scatter
- [Class] Field --(Has Method)--> [Method] is_grid
- [Class] Field --(Has Method)--> [Method] laplace
- [Class] Geometry --(Has Method)--> [Method] integrate_flux
- [Class] Mesh --(Has Method)--> [Method] sample_uniform
- [Class] Mesh --(Has Method)--> [Method] volume
- [Class] Noise --(Has Method)--> [Method] grid_sample
- [Class] Sphere --(Has Method)--> [Method] sample_uniform
- [Class] UniformGrid --(Has Method)--> [Method] boundary_elements
- [Class] UniformGrid --(Has Method)--> [Method] boundary_faces
- [Class] UniformGrid --(Has Method)--> [Method] bounding_half_extent
- [Class] UniformGrid --(Has Method)--> [Method] face_areas
- [Class] UniformGrid --(Has Method)--> [Method] position_of
- [Class] UniformGrid --(Has Method)--> [Method] rotated
- [Class] UniformGrid --(Has Method)--> [Method] shifted
- [Class] UniformGrid --(Has Method)--> [Method] stagger
- [Class] UniformGrid --(Has Method)--> [Method] upper
- [Class] UniformGrid --(Has Method)--> [Method] volume
- [Class] UniformGrid --(Has Method)--> [Method] voxel_at
- [Class] UniformGrid --(Has Method)--> [Method] with_scaled_resolution
