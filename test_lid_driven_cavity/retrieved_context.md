# CODEBASE COMPONENT SPECIFICATIONS & API REFERENCE

## 1. PRIMARY PUBLIC API ENDPOINTS (PREFER USING THESE)

### [File] fluid.py
**Import Path:** `phi.flow.fluid.py`

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

### [Method] is_grid
**Import Path:** `phi.flow.Field.is_grid`

**Signature/Docstring:**
```python
A Field represents grid data if its `geometry` is a `phi.geom.UniformGrid` instance.
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

### [Method] boundary_elements
**Import Path:** `phi.flow.Geometry.boundary_elements`

**Signature/Docstring:**
```python
Slices on the primal dimensions to mark boundary elements.
Grids and meshes have no boundary elements and return `{}`.
Dynamic graphs can define boundary elements for obstacles and walls.

Returns:
    Map from `name` to slicing `dict`.
```

### [Method] boundary_faces
**Import Path:** `phi.flow.Geometry.boundary_faces`

**Signature/Docstring:**
```python
Slices on the dual dimensions to mark boundary faces.

Regular grids use the keys (dim, is_upper) to identify boundaries.
Unstructured meshes use string identifiers for the boundaries.
Dynamic graphs return slices along the dual dimensions.

Returns:
    Map from `name` to slicing `dict`.
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

### [Method] bounding_radius
**Import Path:** `phi.flow.UniformGrid.bounding_radius`

### [Method] corner_representation
**Import Path:** `phi.flow.UniformGrid.corner_representation`

### [Method] dx
**Import Path:** `phi.flow.UniformGrid.dx`

### [Method] face_areas
**Import Path:** `phi.flow.UniformGrid.face_areas`

### [Method] face_normals
**Import Path:** `phi.flow.UniformGrid.face_normals`

### [Method] face_shape
**Import Path:** `phi.flow.UniformGrid.face_shape`

### [Method] faces
**Import Path:** `phi.flow.UniformGrid.faces`

### [Method] interior
**Import Path:** `phi.flow.UniformGrid.interior`

### [Method] padded
**Import Path:** `phi.flow.UniformGrid.padded`

### [Method] position_of
**Import Path:** `phi.flow.UniformGrid.position_of`

### [Method] rotated
**Import Path:** `phi.flow.UniformGrid.rotated`

### [Method] shifted
**Import Path:** `phi.flow.UniformGrid.shifted`

### [Method] spatial_rank
**Import Path:** `phi.flow.UniformGrid.spatial_rank`

### [Method] upper
**Import Path:** `phi.flow.UniformGrid.upper`

### [Method] volume
**Import Path:** `phi.flow.UniformGrid.volume`

### [Method] voxel_at
**Import Path:** `phi.flow.UniformGrid.voxel_at`

### [Class] Mesh
**Import Path:** `phi.flow.Mesh`

**Usage:** `from phi.flow.Mesh import Mesh; Mesh(...)` or direct instantiation from phi.flow

**Signature/Docstring:**
```python
Unstructured mesh, consisting of vertices and elements.

Use `phi.geom.mesh()` or `phi.geom.mesh_from_numpy()` to construct a mesh manually or `phi.geom.load_su2()` to load one from a file.
```

### [Method] boundary_connectivity
**Import Path:** `phi.flow.Mesh.boundary_connectivity`

### [Method] boundary_faces
**Import Path:** `phi.flow.Mesh.boundary_faces`

### [Method] bounds
**Import Path:** `phi.flow.Mesh.bounds`

### [Method] cell_walk_towards
**Import Path:** `phi.flow.Mesh.cell_walk_towards`

**Signature/Docstring:**
```python
If `location` is not within the cell at index `from_cell_idx`, moves to a closer neighbor cell.

Args:
    location: Target location as `Tensor`.
    start_cell_idx: Index of starting cell. Must be a valid cell index.
    allow_exit: If `True`, returns an invalid index for points outside the mesh, otherwise keeps the current index.

Returns:
    index: Index of the neighbor cell or starting cell.
    leaves_mesh: Whether the walk crossed the mesh boundary. Then `index` is invalid. This is only possible if `allow_exit` is true.
    is_outside: Whether `location` was outside the cell at index `start_cell_idx`.
```

### [Method] sample_uniform
**Import Path:** `phi.flow.Mesh.sample_uniform`

### [Method] volume
**Import Path:** `phi.flow.Mesh.volume`

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

- [Class] Field --(Has Method)--> [Method] is_grid
- [Class] Geometry --(Has Method)--> [Method] boundary_elements
- [Class] Geometry --(Has Method)--> [Method] boundary_faces
- [Class] Mesh --(Has Method)--> [Method] boundary_connectivity
- [Class] Mesh --(Has Method)--> [Method] boundary_faces
- [Class] Mesh --(Has Method)--> [Method] bounds
- [Class] Mesh --(Has Method)--> [Method] cell_walk_towards
- [Class] Mesh --(Has Method)--> [Method] sample_uniform
- [Class] Mesh --(Has Method)--> [Method] volume
- [Class] UniformGrid --(Has Method)--> [Method] boundary_elements
- [Class] UniformGrid --(Has Method)--> [Method] boundary_faces
- [Class] UniformGrid --(Has Method)--> [Method] bounding_half_extent
- [Class] UniformGrid --(Has Method)--> [Method] bounding_radius
- [Class] UniformGrid --(Has Method)--> [Method] corner_representation
- [Class] UniformGrid --(Has Method)--> [Method] dx
- [Class] UniformGrid --(Has Method)--> [Method] face_areas
- [Class] UniformGrid --(Has Method)--> [Method] face_normals
- [Class] UniformGrid --(Has Method)--> [Method] face_shape
- [Class] UniformGrid --(Has Method)--> [Method] faces
- [Class] UniformGrid --(Has Method)--> [Method] interior
- [Class] UniformGrid --(Has Method)--> [Method] padded
- [Class] UniformGrid --(Has Method)--> [Method] position_of
- [Class] UniformGrid --(Has Method)--> [Method] rotated
- [Class] UniformGrid --(Has Method)--> [Method] shifted
- [Class] UniformGrid --(Has Method)--> [Method] spatial_rank
- [Class] UniformGrid --(Has Method)--> [Method] upper
- [Class] UniformGrid --(Has Method)--> [Method] volume
- [Class] UniformGrid --(Has Method)--> [Method] voxel_at
