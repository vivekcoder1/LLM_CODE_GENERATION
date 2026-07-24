# CODEBASE COMPONENT SPECIFICATIONS & API REFERENCE

## 1. COMPONENT SIGNATURES & FUNCTIONAL DESCRIPTIONS

### [File] _grid.py
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] _get_bounds
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

### [Function] fourier_laplace
**Signature/Docstring:**
```python
See `phi.math.fourier_laplace()` 
```

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

### [Function] grid
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

### [Function] curl
**Signature/Docstring:**
```python
Computes the finite-difference curl of the give 2D `StaggeredGrid`.

Args:
    field: `Field`
    at: Either `center` or `face`.
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

### [Method] face_areas
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] corner_representation
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] sample_grid_at_faces
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] create_similar_grid
**Signature/Docstring:**
```python
No docstring available.
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

### [Method] interior
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] stagger
**Signature/Docstring:**
```python
Creates a new grid by evaluating `face_function` given two neighbouring cells.
One layer of missing cells is inferred from the extrapolation.

This method returns a Field of type `type` which must be either StaggeredGrid or CenteredGrid.
When returning a StaggeredGrid, the new values are sampled at the faces of neighbouring cells.
When returning a CenteredGrid, the new grid has the same resolution as `field`.

Args:
    field: Grid
    face_function: function mapping (value1: Tensor, value2: Tensor) -> center_value: Tensor
    boundary: extrapolation mode of the returned grid. Has no effect on the values.
    at: Where the result should be sampled, one of 'face', 'center'
    dims: Which dimensions to stagger. Defaults to all spatial axes.

Returns:
    Grid sampled either at centers or faces depending on `at`.
```

### [Class] SDFGrid
**Signature/Docstring:**
```python
Grid-based signed distance field.
```

### [Method] bounds
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] _dyadic_interpolate
**Signature/Docstring:**
```python
Samples a sub-grid from `grid` with an offset of half a grid cell in directions defined by `interpolation_dirs`.

Args:
    grid: `Tensor` to be resampled.
    interpolation_dirs: List which defines for every spatial dimension of `grid` if interpolation should be performed,
        in positive direction `1` / negative direction `-1` / no interpolation`0`
        len(interpolation_dirs) == len(grid.shape.spatial.names) is assumed
        Example: With `grid.shape.spatial.names=['x', 'y']` and `interpolation_dirs: [1, -1]`
                 grid will be interpolated half a grid cell in positive x direction and half a grid cell in negative y direction
    padding: Extrapolation used for the needed out of Domain values
    order: finite difference `Scheme` used for interpolation

Returns:
  Sub-grid as `Tensor`
```

### [Method] at
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] expand_staggered
**Signature/Docstring:**
```python
Add missing spatial dimensions to `values` 
```

### [Method] boundary_faces
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] bake_extrapolation
**Signature/Docstring:**
```python
Pads `grid` with its current extrapolation.
For `StaggeredGrid`s, the resulting grid will have a consistent shape, independent of the original extrapolation.

Args:
    grid: `CenteredGrid` or `StaggeredGrid`.

Returns:
    Padded grid with extrapolation `phi.math.extrapolation.NONE`.
```

### [Function] laplace
**Signature/Docstring:**
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

### [Function] _create_boundary_conditions
**Signature/Docstring:**
```python
Construct mixed boundary conditions from from a sequence of boundary conditions.

Args:
  obj: single boundary condition or sequence of boundary conditions

Returns:
  Mixed boundary conditions as `dict`.
```

### [Method] bounding_radius
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] finite_fill
**Signature/Docstring:**
```python
Extrapolates values of `grid` which are marked by nonzero values in `valid` using `phi.math.masked_fill().
If `values` is a StaggeredGrid, its components get extrapolated independently.

Args:
    grid: Grid holding the values for extrapolation and possible non-finite values to be filled.
    distance: Number of extrapolation steps, i.e. how far a cell can be from the closest finite value to get filled.
    diagonal: Whether to extrapolate values to their diagonal neighbors per step.

Returns:
    grid: Grid with extrapolated values.
    valid: binary Grid marking all valid values after extrapolation.
```

### [Method] lies_inside
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] green_gauss_gradient
**Signature/Docstring:**
```python
Computes the Green-Gauss gradient of a field at the centroids.
```

### [Parameter] boundary
**Signature/Docstring:**
```python
No docstring available.
```

### [Parameter] boundary
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

### [Parameter] boundary
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] __call__
**Signature/Docstring:**
```python
No docstring available.
```

### [Parameter] boundary
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

---

## 2. GRAPH INTERCONNECTIONS & DEPENDENCIES

- [Class] Domain --(Has Method)--> [Method] grid
- [Class] Domain --(Has Method)--> [Method] staggered_grid
- [Class] SDFGrid --(Has Method)--> [Method] at
- [Class] SDFGrid --(Has Method)--> [Method] boundary_faces
- [Class] SDFGrid --(Has Method)--> [Method] bounds
- [Class] SDFGrid --(Has Method)--> [Method] lies_inside
- [Class] UniformGrid --(Has Method)--> [Method] boundary_elements
- [Class] UniformGrid --(Has Method)--> [Method] boundary_faces
- [Class] UniformGrid --(Has Method)--> [Method] bounding_half_extent
- [Class] UniformGrid --(Has Method)--> [Method] bounding_radius
- [Class] UniformGrid --(Has Method)--> [Method] corner_representation
- [Class] UniformGrid --(Has Method)--> [Method] face_areas
- [Class] UniformGrid --(Has Method)--> [Method] interior
- [Class] UniformGrid --(Has Method)--> [Method] upper
- [File] _grid.py --(Defines Function)--> [Function] _create_boundary_conditions
- [File] _grid.py --(Defines Function)--> [Function] _dyadic_interpolate
- [File] _grid.py --(Defines Function)--> [Function] _get_bounds
- [File] _grid.py --(Defines Function)--> [Function] apply_boundary_conditions
- [File] _grid.py --(Defines Function)--> [Function] bake_extrapolation
- [File] _grid.py --(Defines Function)--> [Function] create_similar_grid
- [File] _grid.py --(Defines Function)--> [Function] curl
- [File] _grid.py --(Defines Function)--> [Function] expand_staggered
- [File] _grid.py --(Defines Function)--> [Function] finite_fill
- [File] _grid.py --(Defines Function)--> [Function] fourier_laplace
- [File] _grid.py --(Defines Function)--> [Function] fourier_poisson
- [File] _grid.py --(Defines Function)--> [Function] get_coefficients
- [File] _grid.py --(Defines Function)--> [Function] grid
- [File] _grid.py --(Defines Function)--> [Function] laplace
- [File] _grid.py --(Defines Function)--> [Function] sample_grid_at_faces
- [File] _grid.py --(Defines Function)--> [Function] stagger
- [Function] StaggeredGrid --(Has Parameter)--> [Parameter] boundary
- [Function] green_gauss_gradient --(Has Parameter)--> [Parameter] boundary
- [Function] stagger --(Has Parameter)--> [Parameter] boundary
- [Method] __call__ --(Has Parameter)--> [Parameter] boundary
- [Method] at_faces --(Has Parameter)--> [Parameter] boundary
