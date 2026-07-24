# CODEBASE COMPONENT SPECIFICATIONS & API REFERENCE

## 1. COMPONENT SIGNATURES & FUNCTIONAL DESCRIPTIONS

### [Class] UniformGrid
**Signature/Docstring:**
```python
An instance of UniformGrid represents all cells of a regular grid as a batch of boxes.
```

### [Method] boundary_faces
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] boundary_elements
**Signature/Docstring:**
```python
No docstring available.
```

### [File] _field_math.py
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] fourier_poisson
**Signature/Docstring:**
```python
See `phi.math.fourier_poisson()` 
```

### [Function] get_coefficients
**Signature/Docstring:**
```python
No docstring available.
```

### [Parameter] boundary_condition
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

### [Function] _create_boundary_conditions
**Signature/Docstring:**
```python
Construct mixed boundary conditions from from a sequence of boundary conditions.

Args:
  obj: single boundary condition or sequence of boundary conditions

Returns:
  Mixed boundary conditions as `dict`.
```

### [Class] SDFGrid
**Signature/Docstring:**
```python
Grid-based signed distance field.
```

### [Method] boundary_faces
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] boundary_elements
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] fourier_laplace
**Signature/Docstring:**
```python
See `phi.math.fourier_laplace()` 
```

### [Method] interior
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

### [Class] Domain
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

### [Function] explicit
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

### [Method] upper
**Signature/Docstring:**
```python
No docstring available.
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

### [Method] boundary_names
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] face_areas
**Signature/Docstring:**
```python
No docstring available.
```

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

### [Function] _get_bounds
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

### [Method] volume
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] create_similar_grid
**Signature/Docstring:**
```python
No docstring available.
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

### [Method] corner_representation
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

### [Method] boundary_faces
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] accessible_mask
**Signature/Docstring:**
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

### [Method] vector_potential
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

### [Parameter] v_boundary
**Signature/Docstring:**
```python
No docstring available.
```

### [Class] Heatmap2D
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] can_plot
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] sample_grid_at_faces
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] at_faces
**Signature/Docstring:**
```python
No docstring available.
```

### [Parameter] boundary
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] with_boundary
**Signature/Docstring:**
```python
Returns a copy of this field with the `boundary` replaced. 
```

### [Parameter] boundary
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] gradient
**Signature/Docstring:**
```python
Alias for `phi.field.spatial_gradient`
```

### [Parameter] boundary
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] CenteredGrid
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

### [Parameter] boundary
**Signature/Docstring:**
```python
No docstring available.
```

---

## 2. GRAPH INTERCONNECTIONS & DEPENDENCIES

- [Class] AngularVelocity --(Has Method)--> [Method] _sample
- [Class] Domain --(Has Method)--> [Method] accessible_mask
- [Class] Domain --(Has Method)--> [Method] grid
- [Class] Domain --(Has Method)--> [Method] staggered_grid
- [Class] Domain --(Has Method)--> [Method] vector_potential
- [Class] Field --(Has Method)--> [Method] boundary_names
- [Class] Geometry --(Has Method)--> [Method] boundary_elements
- [Class] Heatmap2D --(Has Method)--> [Method] can_plot
- [Class] Mesh --(Has Method)--> [Method] boundary_faces
- [Class] SDFGrid --(Has Method)--> [Method] boundary_elements
- [Class] SDFGrid --(Has Method)--> [Method] boundary_faces
- [Class] UniformGrid --(Has Method)--> [Method] boundary_elements
- [Class] UniformGrid --(Has Method)--> [Method] boundary_faces
- [Class] UniformGrid --(Has Method)--> [Method] corner_representation
- [Class] UniformGrid --(Has Method)--> [Method] face_areas
- [Class] UniformGrid --(Has Method)--> [Method] interior
- [Class] UniformGrid --(Has Method)--> [Method] upper
- [Class] UniformGrid --(Has Method)--> [Method] volume
- [File] _field_math.py --(Defines Function)--> [Function] StaggeredGrid
- [File] _field_math.py --(Defines Function)--> [Function] _create_boundary_conditions
- [File] _field_math.py --(Defines Function)--> [Function] _get_bounds
- [File] _field_math.py --(Defines Function)--> [Function] apply_boundary_conditions
- [File] _field_math.py --(Defines Function)--> [Function] create_similar_grid
- [File] _field_math.py --(Defines Function)--> [Function] curl
- [File] _field_math.py --(Defines Function)--> [Function] explicit
- [File] _field_math.py --(Defines Function)--> [Function] fourier_laplace
- [File] _field_math.py --(Defines Function)--> [Function] fourier_poisson
- [File] _field_math.py --(Defines Function)--> [Function] get_coefficients
- [File] _field_math.py --(Defines Function)--> [Function] sample_grid_at_faces
- [Function] CenteredGrid --(Has Parameter)--> [Parameter] boundary
- [Function] get_coefficients --(Has Parameter)--> [Parameter] boundary_condition
- [Function] masked_laplace --(Has Parameter)--> [Parameter] v_boundary
- [Method] at_faces --(Has Parameter)--> [Parameter] boundary
- [Method] gradient --(Has Parameter)--> [Parameter] boundary
- [Method] with_boundary --(Has Parameter)--> [Parameter] boundary
