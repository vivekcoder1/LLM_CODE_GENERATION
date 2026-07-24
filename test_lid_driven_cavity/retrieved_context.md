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

### [File] fluid.py
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

### [Method] face_areas
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] _get_bounds
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

### [Function] get_coefficients
**Signature/Docstring:**
```python
No docstring available.
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

### [Method] volume
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] fourier_poisson
**Signature/Docstring:**
```python
See `phi.math.fourier_poisson()` 
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

### [Method] boundary_elements
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

### [Method] bounding_half_extent
**Signature/Docstring:**
```python
No docstring available.
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

### [Method] bounding_radius
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] shifted
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] bounding_half_extent
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

### [Function] fourier_laplace
**Signature/Docstring:**
```python
See `phi.math.fourier_laplace()` 
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

### [Method] faces
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] enclosing_grid
**Signature/Docstring:**
```python
Constructs a `UniformGrid` which fully encloses the `geometries`.
The grid voxels are chosen to have approximately the same size along each axis.

Args:
    *geometries: `Geometry` objects `Tensor` of points which should lie within the grid.
    voxel_count: Approximate number of total voxels.
    rel_margin: Relative margin, i.e. empty space on each side as a fraction of the bounding box size of `geometries`.
    abs_margin: Absolute margin, i.e. empty space on each side.
    margin_cells: Number of cell layers to fit outside the bounding box around `geometries`. This is cumulative with `rel_margin` and `abs_margin`.

Returns:
    `UniformGrid`
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

### [Function] curl
**Signature/Docstring:**
```python
Computes the finite-difference curl of the give 2D `StaggeredGrid`.

Args:
    field: `Field`
    at: Either `center` or `face`.
```

### [Method] lies_inside
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] voxel_at
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] bounds
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] bounding_half_extent
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] dx
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] bounding_radius
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

### [Method] spatial_rank
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] boundary_elements
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

---

## 2. GRAPH INTERCONNECTIONS & DEPENDENCIES

- [Class] AngularVelocity --(Has Method)--> [Method] _sample
- [Class] Cylinder --(Has Method)--> [Method] bounding_half_extent
- [Class] Domain --(Has Method)--> [Method] accessible_mask
- [Class] Domain --(Has Method)--> [Method] grid
- [Class] Domain --(Has Method)--> [Method] staggered_grid
- [Class] Mesh --(Has Method)--> [Method] boundary_faces
- [Class] SDFGrid --(Has Method)--> [Method] boundary_elements
- [Class] SDFGrid --(Has Method)--> [Method] boundary_faces
- [Class] SDFGrid --(Has Method)--> [Method] bounding_half_extent
- [Class] SDFGrid --(Has Method)--> [Method] bounding_radius
- [Class] SDFGrid --(Has Method)--> [Method] bounds
- [Class] SDFGrid --(Has Method)--> [Method] lies_inside
- [Class] UniformGrid --(Has Method)--> [Method] boundary_elements
- [Class] UniformGrid --(Has Method)--> [Method] boundary_faces
- [Class] UniformGrid --(Has Method)--> [Method] bounding_half_extent
- [Class] UniformGrid --(Has Method)--> [Method] bounding_radius
- [Class] UniformGrid --(Has Method)--> [Method] dx
- [Class] UniformGrid --(Has Method)--> [Method] face_areas
- [Class] UniformGrid --(Has Method)--> [Method] faces
- [Class] UniformGrid --(Has Method)--> [Method] shifted
- [Class] UniformGrid --(Has Method)--> [Method] spatial_rank
- [Class] UniformGrid --(Has Method)--> [Method] upper
- [Class] UniformGrid --(Has Method)--> [Method] volume
- [Class] UniformGrid --(Has Method)--> [Method] voxel_at
- [File] fluid.py --(Defines Function)--> [Function] StaggeredGrid
- [File] fluid.py --(Defines Function)--> [Function] _get_bounds
- [File] fluid.py --(Defines Function)--> [Function] apply_boundary_conditions
- [File] fluid.py --(Defines Function)--> [Function] curl
- [File] fluid.py --(Defines Function)--> [Function] enclosing_grid
- [File] fluid.py --(Defines Function)--> [Function] explicit
- [File] fluid.py --(Defines Function)--> [Function] fourier_laplace
- [File] fluid.py --(Defines Function)--> [Function] fourier_poisson
- [File] fluid.py --(Defines Function)--> [Function] get_coefficients
- [File] fluid.py --(Defines Function)--> [Function] laplace
- [File] fluid.py --(Defines Function)--> [Function] masked_laplace
