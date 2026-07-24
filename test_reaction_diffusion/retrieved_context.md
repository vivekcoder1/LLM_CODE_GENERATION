# CODEBASE COMPONENT SPECIFICATIONS & API REFERENCE

## 1. COMPONENT SIGNATURES & FUNCTIONAL DESCRIPTIONS

### [File] diffuse.py
**Signature/Docstring:**
```python
No docstring available.
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

### [Function] get_coefficients
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] fourier_poisson
**Signature/Docstring:**
```python
See `phi.math.fourier_poisson()` 
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

### [Function] fourier_laplace
**Signature/Docstring:**
```python
See `phi.math.fourier_laplace()` 
```

### [Function] implicit
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

### [Method] face_areas
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] differential
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

### [Function] curl
**Signature/Docstring:**
```python
Computes the finite-difference curl of the give 2D `StaggeredGrid`.

Args:
    field: `Field`
    at: Either `center` or `face`.
```

### [Function] sample_grid_at_faces
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] shifted
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

### [Function] rk4
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] _get_bounds
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] volume
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] face_shape
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] shifted
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] corner_representation
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

### [Function] euler
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

### [Method] boundary_elements
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] bounding_half_extent
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] perform_finite_difference_operation
**Signature/Docstring:**
```python
No docstring available.
```

### [Method] boundary_elements
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] sample_staggered_grid
**Signature/Docstring:**
```python
No docstring available.
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

### [Method] dx
**Signature/Docstring:**
```python
No docstring available.
```

### [Function] spatial_gradient
**Signature/Docstring:**
```python
Finite difference spatial_gradient.

This function can operate in two modes:

* `type=CenteredGrid` approximates the spatial_gradient at cell centers using central differences
* `type=StaggeredGrid` computes the spatial_gradient at face centers of neighbouring cells

Args:
    field: centered grid of any number of dimensions (scalar field, vector field, tensor field)
    boundary: Boundary conditions of the gradient field.
    at: Either `'face'` or `'center'`
    dims: Along which dimensions to compute the spatial gradient. Only supported when `type==CenteredGrid`.
    stack_dim: Dimension to be added. This dimension lists the spatial_gradient w.r.t. the spatial dimensions.
        The `field` must not have a dimension of the same name.
    order: Spatial order of accuracy.
        Higher orders entail larger stencils and more computation time but result in more accurate results assuming a large enough resolution.
        Supported: 2 explicit, 4 explicit, 6 implicit.
    implicit: When a `Solve` object is passed, performs an implicit operation with the specified solver and tolerances.
        Otherwise, an explicit stencil is used.
    implicitness: specifies the size of the implicit stencil in case an implicit treatment is used
    gradient_extrapolation: Alias for `boundary`.
    scheme: For unstructured meshes only. Currently only `'green-gauss'` is supported.
    upwind: For unstructured meshes only. Whether to use upwind interpolation.

Returns:
    spatial_gradient field of type `type`.
```

---

## 2. GRAPH INTERCONNECTIONS & DEPENDENCIES

- [Class] AngularVelocity --(Has Method)--> [Method] _sample
- [Class] Domain --(Has Method)--> [Method] grid
- [Class] Domain --(Has Method)--> [Method] staggered_grid
- [Class] SDFGrid --(Has Method)--> [Method] boundary_elements
- [Class] SDFGrid --(Has Method)--> [Method] boundary_faces
- [Class] SDFGrid --(Has Method)--> [Method] bounding_half_extent
- [Class] SDFGrid --(Has Method)--> [Method] shifted
- [Class] UniformGrid --(Has Method)--> [Method] boundary_elements
- [Class] UniformGrid --(Has Method)--> [Method] boundary_faces
- [Class] UniformGrid --(Has Method)--> [Method] bounding_half_extent
- [Class] UniformGrid --(Has Method)--> [Method] corner_representation
- [Class] UniformGrid --(Has Method)--> [Method] dx
- [Class] UniformGrid --(Has Method)--> [Method] face_areas
- [Class] UniformGrid --(Has Method)--> [Method] face_shape
- [Class] UniformGrid --(Has Method)--> [Method] shifted
- [Class] UniformGrid --(Has Method)--> [Method] upper
- [Class] UniformGrid --(Has Method)--> [Method] volume
- [File] diffuse.py --(Defines Function)--> [Function] StaggeredGrid
- [File] diffuse.py --(Defines Function)--> [Function] _get_bounds
- [File] diffuse.py --(Defines Function)--> [Function] apply_boundary_conditions
- [File] diffuse.py --(Defines Function)--> [Function] curl
- [File] diffuse.py --(Defines Function)--> [Function] differential
- [File] diffuse.py --(Defines Function)--> [Function] euler
- [File] diffuse.py --(Defines Function)--> [Function] euler_step
- [File] diffuse.py --(Defines Function)--> [Function] explicit
- [File] diffuse.py --(Defines Function)--> [Function] fourier_laplace
- [File] diffuse.py --(Defines Function)--> [Function] fourier_poisson
- [File] diffuse.py --(Defines Function)--> [Function] get_coefficients
- [File] diffuse.py --(Defines Function)--> [Function] implicit
- [File] diffuse.py --(Defines Function)--> [Function] laplace
- [File] diffuse.py --(Defines Function)--> [Function] perform_finite_difference_operation
- [File] diffuse.py --(Defines Function)--> [Function] rk4
- [File] diffuse.py --(Defines Function)--> [Function] sample_grid_at_faces
- [File] diffuse.py --(Defines Function)--> [Function] sample_staggered_grid
- [File] diffuse.py --(Defines Function)--> [Function] spatial_gradient
