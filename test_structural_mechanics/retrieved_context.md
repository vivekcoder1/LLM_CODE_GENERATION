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

### [Method] boundary_elements
**Import Path:** `phi.flow.Box.boundary_elements`

### [Method] push
**Import Path:** `phi.flow.Box.push`

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

### [Method] boundary_names
**Import Path:** `phi.flow.Field.boundary_names`

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

### [Method] shape
**Import Path:** `phi.flow.Geometry.shape`

**Signature/Docstring:**
```python
The `shape` of a `Geometry` consists of the following dimensions:

* A single *channel* dimension called `'vector'` specifying the physical space
* Instance dimensions denote that this geometry consists of multiple copies in the same space
* Spatial dimensions denote a crystal (repeating structure) of this geometric primitive in space
* Batch dimensions indicate non-interacting versions of this geometry for parallelization only.
```

### [Class] Point
**Import Path:** `phi.flow.Point`

**Usage:** `from phi.flow.Point import Point; Point(...)` or direct instantiation from phi.flow

**Signature/Docstring:**
```python
Points have zero volume and are determined by a single location.
An instance of `Point` represents a single n-dimensional point or a batch of points.
```

### [Method] boundary_elements
**Import Path:** `phi.flow.Point.boundary_elements`

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

### [Method] boundary_faces
**Import Path:** `phi.flow.UniformGrid.boundary_faces`

### [Method] stagger
**Import Path:** `phi.flow.UniformGrid.stagger`

### [Method] staggered_cells
**Import Path:** `phi.flow.UniformGrid.staggered_cells`

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

### [Method] boundary_elements
**Import Path:** `phi.flow.Mesh.boundary_elements`

### [Method] bounding_box
**Import Path:** `phi.flow.Mesh.bounding_box`

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

### [Method] distance_matrix
**Import Path:** `phi.flow.Mesh.distance_matrix`

### [Method] faces
**Import Path:** `phi.flow.Mesh.faces`

**Signature/Docstring:**
```python
Assembles information about the boundaries of the elements that make up the surface.
For 2D elements, the faces are edges, for 3D elements, the faces are planar elements.

Returns:
    center: Center of face connecting a pair of elements. Shape (~elements, elements, vector).
        Returns 0-vectors for unconnected elements.
    area: Area of face connecting a pair of elements. Shape (~elements, elements).
        Returns 0 for unconnected elements.
    normal: Normal vector of face connecting a pair of elements. Shape (~elements, elements, vector).
        Unconnected elements are assigned the vector 0.
        The vector points out of polygon and into ~polygon.
```

### [Method] neighbor_offsets
**Import Path:** `phi.flow.Mesh.neighbor_offsets`

**Signature/Docstring:**
```python
Returns shift vector to neighbor centroids and boundary faces.
```

### [Method] normals
**Import Path:** `phi.flow.Mesh.normals`

**Signature/Docstring:**
```python
Extrinsic element normal space. This is a 0D vector for solid elements and 1D for surface elements.
```

### [Method] shape
**Import Path:** `phi.flow.Mesh.shape`

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

### [Function] euler
**Import Path:** `phi.flow.advect.euler`

**Usage:** `advect.euler(...)` or `from phi.flow.advect import euler; euler(...)`

**Signature/Docstring:**
```python
Euler integrator. 
```

### [Function] finite_rk4
**Import Path:** `phi.flow.advect.finite_rk4`

**Usage:** `advect.finite_rk4(...)` or `from phi.flow.advect import finite_rk4; finite_rk4(...)`

**Signature/Docstring:**
```python
Runge-Kutta-4 integrator with Euler fallback where velocity values are NaN. 
```

### [Function] rk4
**Import Path:** `phi.flow.advect.rk4`

**Usage:** `advect.rk4(...)` or `from phi.flow.advect import rk4; rk4(...)`

**Signature/Docstring:**
```python
Runge-Kutta-4 integrator. 
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

### [Method] at
**Import Path:** `phi.flow.Obstacle.at`

### [Method] rotated
**Import Path:** `phi.flow.Obstacle.rotated`

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

---

## 2. GRAPH INTERCONNECTIONS & DEPENDENCIES

- [Class] Box --(Has Method)--> [Method] boundary_elements
- [Class] Box --(Has Method)--> [Method] push
- [Class] Field --(Has Method)--> [Method] boundary_names
- [Class] Field --(Has Method)--> [Method] laplace
- [Class] Geometry --(Has Method)--> [Method] boundary_elements
- [Class] Geometry --(Has Method)--> [Method] boundary_faces
- [Class] Geometry --(Has Method)--> [Method] shape
- [Class] Mesh --(Has Method)--> [Method] boundary_connectivity
- [Class] Mesh --(Has Method)--> [Method] boundary_elements
- [Class] Mesh --(Has Method)--> [Method] bounding_box
- [Class] Mesh --(Has Method)--> [Method] bounds
- [Class] Mesh --(Has Method)--> [Method] cell_walk_towards
- [Class] Mesh --(Has Method)--> [Method] distance_matrix
- [Class] Mesh --(Has Method)--> [Method] faces
- [Class] Mesh --(Has Method)--> [Method] neighbor_offsets
- [Class] Mesh --(Has Method)--> [Method] normals
- [Class] Mesh --(Has Method)--> [Method] shape
- [Class] Mesh --(Has Method)--> [Method] volume
- [Class] Obstacle --(Has Method)--> [Method] at
- [Class] Obstacle --(Has Method)--> [Method] rotated
- [Class] Point --(Has Method)--> [Method] boundary_elements
- [Class] UniformGrid --(Has Method)--> [Method] boundary_faces
- [Class] UniformGrid --(Has Method)--> [Method] stagger
- [Class] UniformGrid --(Has Method)--> [Method] staggered_cells
