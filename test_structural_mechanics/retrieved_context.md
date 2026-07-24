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

### [File] integrate.py
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] euler
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] get_coefficients
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] _create_boundary_conditions
**Signature/Docstring:**
```python
Construct mixed boundary conditions from from a sequence of boundary conditions.

Args:
  obj: single boundary condition or sequence of boundary conditions

Returns:
  Mixed boundary conditions as `dict`.
```

### [Function] build_faces
**Signature/Docstring:**
```python
Given a list of vertices, elements and boundary edges, computes the element connectivity matrix  and corresponding edge properties.

Args:
    vertices: `Tensor` representing list (instance) of vectors (channel)
    elements: Sparse matrix listing all elements (instance). Each entry represents a vertex (dual) belonging to an element.
    boundaries: Named sequences of edges (vertex pairs).
    element_rank: Spatial rank of the elements (currently only 2 is supported)
    periodic: Which dims are periodic.
    vertex_mean: Mean vertex position for each element.
    face_format: Sparse matrix format to use for the element-element matrices.
```

### [Class] SplineSolid
**Signature/Docstring:**
```python
Internal coordinates (u,v) are in the range [0, N] where N is the number of points along that axis.
```

### [Method] _central_point_tangents
**Signature/Docstring:**
```python
No docstring available.
```

### [Class] Cylinder
**Signature/Docstring:**
```python
N-dimensional cylinder.
Defined by center position, radius, depth, alignment axis, rotation.

For cylinders whose bottom and top lie outside the domain or are otherwise not needed, you may use `infinite_cylinder` instead, which simplifies computations.
```

### [Method] boundary_elements
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] volume
**Signature/Docstring:**
```python
No docstring available.
```

### [Class] Obstacle
**Signature/Docstring:**
```python
An obstacle defines boundary conditions inside a geometry.
It can also have a linear and angular velocity.
```

### [Function] StaggeredGrid
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

### [Function] solve_resolution_with_margin_cells
**Signature/Docstring:**
```python
No docstring available.
```

### [Class] Geometry
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
**Signature/Docstring:**
```python
Slices on the primal dimensions to mark boundary elements.
Grids and meshes have no boundary elements and return `{}`.
Dynamic graphs can define boundary elements for obstacles and walls.

Returns:
    Map from `name` to slicing `dict`.
```

### [Class] Box
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

### [Method] push
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] euler
**Signature/Docstring:**
```python
Euler integrator. 
```

### [Function] rk4
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] eval_nurbs_bases
**Signature/Docstring:**
```python
Compute all NURBS basis functions.
This simplifies to B-spline basis functions if `weights=None` and knots are uniform.

Args:
    t: Parameter value where to evaluate the basis functions.
    knots: Knot matrix of shape (~bases:d, support:s=degree+2).
    weights: NURBS weight per control point. Shape (~bases:d,)
    eps: Value smaller than 1/n, ensuring that the upper end t=1.0 is handled correctly.

Returns:
    Basis function values at `t` of all basis function listed along `bases_dim`.
```

### [Function] euler_step
**Signature/Docstring:**
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

### [Method] _central_tangents
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] perform_finite_difference_operation
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

### [Method] boundary_connectivity
**Signature/Docstring:**
```python
No docstring available.
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

### [Class] Domain
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] vector_grid
**Signature/Docstring:**
```python
Creates a vector grid matching the resolution and bounds of the domain.
The grid is created from the given `value` which must be one of the following:

* Number (int, float, complex or zero-dimensional tensor): all grid values will be equal to `value`. This has a near-zero memory footprint.
* Field: the given value is resampled to the grid cells of this Domain.
* Tensor with spatial dimensions matcing the domain resolution: grid values will equal `value`.
* Geometry: grid values are determined from the volume overlap between grid cells and geometry. Non-overlapping = 0, fully enclosed grid cell = 1.
* function(location: Tensor) returning one of the above.

The returned grid will have a vector dimension with size equal to the rank of the domain.

Args:
  value: constant, Field, Tensor or function specifying the grid values
  type: class of Grid to create, must be either CenteredGrid or StaggeredGrid
  extrapolation: (optional) grid extrapolation, defaults to Domain.boundaries['vector']

Returns:
  Grid of specified type
```

### [Function] build_mesh
**Signature/Docstring:**
```python
Build a mesh for a given domain, respecting obstacles.

Args:
    bounds: Bounds for uniform cells.
    resolution: Base resolution
    obstacles: Single `Geometry` or `dict` mapping boundary name to corresponding `Geometry`.
    method: Meshing algorithm. Only `quad` is currently supported.
    cell_dim: Dimension along which to list the cells. This should be an instance dimension.
    face_format: Sparse storage format for cell connectivity.
    max_squish: Smallest allowed cell size compared to the smallest regular cell.
    **resolution_: For uniform grid, pass resolution as `int` and specify `bounds`.
        Or pass a sequence of floats for each dimension, specifying the vertex positions along each axis.
        This allows for variable cell stretching.

Returns:
    `Mesh`
```

### [Class] Sphere
**Signature/Docstring:**
```python
N-dimensional sphere.
Defined through center position and radius.
```

### [Method] boundary_elements
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] staggered_grid
**Signature/Docstring:**
```python
Creates a staggered grid matching the resolution and bounds of the domain.
This is equal to calling `vector_grid()` with `type=StaggeredGrid`.

The grid is created from the given `value` which must be one of the following:

* Number (int, float, complex or zero-dimensional tensor): all grid values will be equal to `value`. This has a near-zero memory footprint.
* Field: the given value is resampled to the grid cells of this Domain.
* Tensor with spatial dimensions matcing the domain resolution: grid values will equal `value`.
* Geometry: grid values are determined from the volume overlap between grid cells and geometry. Non-overlapping = 0, fully enclosed grid cell = 1.
* function(location: Tensor) returning one of the above.

The returned grid will have a vector dimension with size equal to the rank of the domain.

Args:
  value: constant, Field, Tensor or function specifying the grid values
  extrapolation: (optional) grid extrapolation, defaults to Domain.boundaries['vector']

Returns:
  Grid of specified type
```

### [Method] distance_matrix
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] _surface_point_tangents
**Signature/Docstring:**
```python
No docstring available.
```

### [Class] UniformGrid
**Signature/Docstring:**
```python
An instance of UniformGrid represents all cells of a regular grid as a batch of boxes.
```

### [Method] staggered_cells
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] mesh
**Signature/Docstring:**
```python
Create a mesh from vertex positions and vertex lists.

Args:
    vertices: `Tensor` with one instance and one channel dimension `vector`.
    elements: Lists of vertex indices as 2D tensor.
        The elements must be listed along an instance dimension, and the vertex indices belonging to the same polygon must be listed along a spatial dimension.
    boundaries: Pass a `str` to assign one name to all boundary faces.
        For multiple boundaries, pass a `dict` mapping group names `str` to lists of faces, defined by their vertices.
        The last entry can be `None` to group all boundary faces not explicitly listed before.
        The `boundaries` `dict` maps boundary names to a list of edges (point pairs) in 2D and faces (3 or more points) in 3D (not yet supported).
    face_format: Storage format for cell connectivity, must be one of `csc`, `coo`, `csr`, `dense`.

Returns:
    `Mesh`
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

### [Function] build_quadrilaterals
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

### [Method] _central_point_normals
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] boundary_faces
**Signature/Docstring:**
```python
Slices on the dual dimensions to mark boundary faces.

Regular grids use the keys (dim, is_upper) to identify boundaries.
Unstructured meshes use string identifiers for the boundaries.
Dynamic graphs return slices along the dual dimensions.

Returns:
    Map from `name` to slicing `dict`.
```

### [Method] approximate_signed_distance
**Signature/Docstring:**
```python
No docstring available.
```

---

## 2. GRAPH INTERCONNECTIONS & DEPENDENCIES

- [Class] AngularVelocity --(Has Method)--> [Method] _sample
- [Class] Box --(Has Method)--> [Method] push
- [Class] Cylinder --(Has Method)--> [Method] boundary_elements
- [Class] Domain --(Has Method)--> [Method] grid
- [Class] Domain --(Has Method)--> [Method] staggered_grid
- [Class] Domain --(Has Method)--> [Method] vector_grid
- [Class] Geometry --(Has Method)--> [Method] boundary_elements
- [Class] Geometry --(Has Method)--> [Method] boundary_faces
- [Class] HardGeometryMask --(Has Method)--> [Method] _sample
- [Class] Mesh --(Has Method)--> [Method] boundary_connectivity
- [Class] Mesh --(Has Method)--> [Method] distance_matrix
- [Class] Sphere --(Has Method)--> [Method] boundary_elements
- [Class] SplineSolid --(Has Method)--> [Method] _central_point_normals
- [Class] SplineSolid --(Has Method)--> [Method] _central_point_tangents
- [Class] SplineSolid --(Has Method)--> [Method] _central_tangents
- [Class] SplineSolid --(Has Method)--> [Method] _surface_point_tangents
- [Class] SplineSolid --(Has Method)--> [Method] approximate_signed_distance
- [Class] SplineSolid --(Has Method)--> [Method] volume
- [Class] UniformGrid --(Has Method)--> [Method] staggered_cells
- [File] integrate.py --(Defines Class)--> [Class] Obstacle
- [File] integrate.py --(Defines Function)--> [Function] StaggeredGrid
- [File] integrate.py --(Defines Function)--> [Function] _create_boundary_conditions
- [File] integrate.py --(Defines Function)--> [Function] apply_boundary_conditions
- [File] integrate.py --(Defines Function)--> [Function] build_faces
- [File] integrate.py --(Defines Function)--> [Function] build_mesh
- [File] integrate.py --(Defines Function)--> [Function] build_quadrilaterals
- [File] integrate.py --(Defines Function)--> [Function] euler
- [File] integrate.py --(Defines Function)--> [Function] euler_step
- [File] integrate.py --(Defines Function)--> [Function] eval_nurbs_bases
- [File] integrate.py --(Defines Function)--> [Function] get_coefficients
- [File] integrate.py --(Defines Function)--> [Function] mesh
- [File] integrate.py --(Defines Function)--> [Function] perform_finite_difference_operation
- [File] integrate.py --(Defines Function)--> [Function] rk4
- [File] integrate.py --(Defines Function)--> [Function] solve_resolution_with_margin_cells
