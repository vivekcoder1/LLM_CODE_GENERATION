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

### [Method] as_boundary
**Import Path:** `phi.flow.Field.as_boundary`

**Signature/Docstring:**
```python
Returns an `Extrapolation` representing this 'Field''s values as a Dirichlet (constant) boundary.
If this `Field` encloses the required boundaries, its values will be interpolated to the required boundaries.
If boundaries outside of this `Field`'s sampled domain are required, this `Field`'s boundary conditions will be applied to determine the boundary values.

Returns:
    `Extrapolation`
```

### [Method] boundary_names
**Import Path:** `phi.flow.Field.boundary_names`

### [Method] grid
**Import Path:** `phi.flow.Field.grid`

**Signature/Docstring:**
```python
Cast `self.geometry` to a `phi.geom.UniformGrid`.
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

### [Method] half_size
**Import Path:** `phi.flow.UniformGrid.half_size`

### [Method] interior
**Import Path:** `phi.flow.UniformGrid.interior`

### [Method] lower
**Import Path:** `phi.flow.UniformGrid.lower`

### [Method] padded
**Import Path:** `phi.flow.UniformGrid.padded`

### [Method] shape
**Import Path:** `phi.flow.UniformGrid.shape`

### [Method] shifted
**Import Path:** `phi.flow.UniformGrid.shifted`

### [Method] spatial_rank
**Import Path:** `phi.flow.UniformGrid.spatial_rank`

### [Method] staggered_cells
**Import Path:** `phi.flow.UniformGrid.staggered_cells`

### [Method] upper
**Import Path:** `phi.flow.UniformGrid.upper`

### [Method] volume
**Import Path:** `phi.flow.UniformGrid.volume`

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

### [Method] boundary_faces
**Import Path:** `phi.flow.Mesh.boundary_faces`

### [Method] get_boundary
**Import Path:** `phi.flow.Mesh.get_boundary`

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

- [Class] Box --(Has Method)--> [Method] boundary_elements
- [Class] Field --(Has Method)--> [Method] as_boundary
- [Class] Field --(Has Method)--> [Method] boundary_names
- [Class] Field --(Has Method)--> [Method] grid
- [Class] Field --(Has Method)--> [Method] is_grid
- [Class] Geometry --(Has Method)--> [Method] boundary_elements
- [Class] Geometry --(Has Method)--> [Method] boundary_faces
- [Class] Mesh --(Has Method)--> [Method] boundary_connectivity
- [Class] Mesh --(Has Method)--> [Method] boundary_elements
- [Class] Mesh --(Has Method)--> [Method] boundary_faces
- [Class] Mesh --(Has Method)--> [Method] get_boundary
- [Class] UniformGrid --(Has Method)--> [Method] boundary_elements
- [Class] UniformGrid --(Has Method)--> [Method] boundary_faces
- [Class] UniformGrid --(Has Method)--> [Method] bounding_half_extent
- [Class] UniformGrid --(Has Method)--> [Method] corner_representation
- [Class] UniformGrid --(Has Method)--> [Method] dx
- [Class] UniformGrid --(Has Method)--> [Method] face_areas
- [Class] UniformGrid --(Has Method)--> [Method] face_normals
- [Class] UniformGrid --(Has Method)--> [Method] face_shape
- [Class] UniformGrid --(Has Method)--> [Method] faces
- [Class] UniformGrid --(Has Method)--> [Method] half_size
- [Class] UniformGrid --(Has Method)--> [Method] interior
- [Class] UniformGrid --(Has Method)--> [Method] lower
- [Class] UniformGrid --(Has Method)--> [Method] padded
- [Class] UniformGrid --(Has Method)--> [Method] shape
- [Class] UniformGrid --(Has Method)--> [Method] shifted
- [Class] UniformGrid --(Has Method)--> [Method] spatial_rank
- [Class] UniformGrid --(Has Method)--> [Method] staggered_cells
- [Class] UniformGrid --(Has Method)--> [Method] upper
- [Class] UniformGrid --(Has Method)--> [Method] volume
