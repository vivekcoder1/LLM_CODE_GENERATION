# CODEBASE COMPONENT SPECIFICATIONS & API REFERENCE

## 1. PRIMARY PUBLIC API ENDPOINTS (PREFER USING THESE)

### [Class] UniformGrid
**Import Path:** `phi.flow.UniformGrid`

**Usage:** `from phi.flow.UniformGrid import UniformGrid; UniformGrid(...)` or direct instantiation from phi.flow

**Signature/Docstring:**
```python
An instance of UniformGrid represents all cells of a regular grid as a batch of boxes.
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

### [Function] finite_rk4
**Import Path:** `phi.flow.advect.finite_rk4`

**Usage:** `advect.finite_rk4(...)` or `from phi.flow.advect import finite_rk4; finite_rk4(...)`

**Signature/Docstring:**
```python
Runge-Kutta-4 integrator with Euler fallback where velocity values are NaN. 
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

### [Function] euler
**Import Path:** `phi.flow.advect.euler`

**Usage:** `advect.euler(...)` or `from phi.flow.advect import euler; euler(...)`

**Signature/Docstring:**
```python
Euler integrator. 
```

### [Function] show
**Import Path:** `phi.flow.show`

**Usage:** `flow.show(...)` or `from phi.flow import show; show(...)`

**Signature/Docstring:**
```python
Args:
    See `plot()`.
```

### [Function] rk4
**Import Path:** `phi.flow.advect.rk4`

**Usage:** `advect.rk4(...)` or `from phi.flow.advect import rk4; rk4(...)`

**Signature/Docstring:**
```python
Runge-Kutta-4 integrator. 
```

### [Function] plot
**Import Path:** `phi.flow.plot`

**Usage:** `flow.plot(...)` or `from phi.flow import plot; plot(...)`

**Signature/Docstring:**
```python
Creates one or multiple figures and sub-figures and plots the given fields.

To show the figures, use `show()`.

The arguments `row_dims`, `col_dims`, `animate` and `overlay` control how data is presented.
Each accepts dimensions as a `str`, `Shape`, tuple, list or type function.
In addition to the dimensions present on the data to be plotted, the dimensions `args` is created if multiple arguments are passed,
and `tuple`, `list`, `dict` are generated for corresponding objects to be plotted.

Args:
    fields: Fields or Tensors to plot.
    lib: Plotting library name or reference. Valid names are `'matplotlib'`, `'plotly'` and `'console'`.
    row_dims: Batch dimensions along which sub-figures should be laid out vertically.
        `Shape` or comma-separated names as `str`, `tuple` or `list`.
    col_dims: Batch dimensions along which sub-figures should be laid out horizontally.
        `Shape` or comma-separated names as `str`, `tuple` or `list`.
    title: `str` for figures with a single subplot.
        For subplots, pass a string `Tensor` matching the content dimensions, i.e. `row_dims` and `col_dims`.
        Passing a `tuple`, `list` or `dict`, will create a tensor with these names internally.
    size: Figure size in inches, `(width, height)`.
    same_scale: Whether to use the same axis limits for all sub-figures.
    log_dims: Dimensions for which the plot axes should be scaled logarithmically.
        Can be given as a comma-separated `str`, a sequence of dimension names or a `Shape`.
        Use `'_'` to scale unnamed axes logarithmically, e.g. the y-axis of scalar functions.
    show_color_bar: Whether to display color bars for heat maps.
    color: `Tensor` of line / marker colors.
        The color can be specified either as a cycle index (int tensor) or as a hex code (str tensor).
        The color of different lines and markers can vary.
    alpha: Opacity as `float` or `Tensor`.
        This affects all elements, not only line plots.
        Opacity can vary between lines and markers.
    err: Expected deviation from the value given in `fields`.
        For supported plots, adds error bars of size *2·err*.
        If the plotted data is the mean of some distribution, a good choice for `err` is the standard deviation along the mean dims.
    animate: Time dimension to animate.
        If not present in the data, will produce a regular plot instead.
    overlay: Dimensions along which elements should be overlaid in the same subplot.
        The default is only the `overlay` dimension which is created by `overlay()`.
    frame_time: Interval between frames in the animation.
    repeat: Whether the animation should loop.

Returns:
    `Tensor` of figure objects.
    The tensor contains those dimensions of `fields` that were not reduced by `row_dims`, `col_dims` or `animate`.
    Currently, only single-figure plots are supported.

    In case of an animation, a displayable animation object will be returned instead of a `Tensor`.
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

### [Function] resample
**Import Path:** `phi.flow.resample`

**Usage:** `flow.resample(...)` or `from phi.flow import resample; resample(...)`

**Signature/Docstring:**
```python
Samples a `Field`, `Geometry` or value at the sample points of the field `to`.
The result will approximate `value` on the data structure of `to`.
Unlike `sample()`, this method returns a `Field` object, not a `Tensor`.

Aliases:
    `value.at(to)`, (and the deprecated `value @ to`).

See Also:
    `sample()`, `reduce_sample()`, `Field.at()`, [Resampling overview](https://tum-pbs.github.io/PhiFlow/Fields.html#resampling-fields).

Args:
    value: Object containing values to resample.
        This can be
    to: `Field` (`CenteredGrid`, `StaggeredGrid` or `PointCloud`) object defining the sample points.
        The current values of `to` are ignored.
    keep_boundary: Only available if `self` is a `Field`.
        If True, the resampled field will inherit the extrapolation from `self` instead of `representation`.
        This can result in non-compatible value tensors for staggered grids where the tensor size depends on the extrapolation type.
    **kwargs: Sampling arguments, e.g. to specify the numerical scheme.
        By default, linear interpolation is used.
        Grids also support 6th order implicit sampling at mid-points.

Returns:
    Field object of same type as `representation`

Examples:
    >>> grid = CenteredGrid(x=64, y=32)
    >>> field.resample(Noise(), to=grid)
    CenteredGrid[(xˢ=64, yˢ=32), size=(x=64, y=32), extrapolation=float64 0.0]
    >>> field.resample(1, to=grid)
    CenteredGrid[(xˢ=64, yˢ=32), size=(x=64, y=32), extrapolation=float64 0.0]
    >>> field.resample(Box(x=1, y=2), to=grid)
    CenteredGrid[(xˢ=64, yˢ=32), size=(x=64, y=32), extrapolation=float64 0.0]
    >>> field.resample(grid, to=grid) == grid
    True
```

### [Class] Mesh
**Import Path:** `phi.flow.Mesh`

**Usage:** `from phi.flow.Mesh import Mesh; Mesh(...)` or direct instantiation from phi.flow

**Signature/Docstring:**
```python
Unstructured mesh, consisting of vertices and elements.

Use `phi.geom.mesh()` or `phi.geom.mesh_from_numpy()` to construct a mesh manually or `phi.geom.load_su2()` to load one from a file.
```

### [Function] control
**Import Path:** `phi.flow.control`

**Usage:** `flow.control(...)` or `from phi.flow import control; control(...)`

**Signature/Docstring:**
```python
Mark a variable as controllable by any GUI created via `view()`.

Example:
>>> dt = control(1.0, (0.1, 10), name="Time increment (dt)")

This will cause a control component (slider, checkbox, text field, drop-down, etc.) to be generated in the user interface.
Changes to that component will immediately be reflected in the Python variable assigned to the control.
The Python variable will always hold a primitive type, such as `int`, `float´, `bool` or `str`.

Args:
    value: Initial value. Must be either `int`, `float`, `bool` or `str`.
    range: (Optional) Specify range of possible values as `(min, max)`. Only for `int`, `float` and `str` values.
    description: Human-readable description.
    **kwargs: Additional arguments to determine the appearance of the GUI component,
        e.g. `rows` for text fields or `log=False` for float sliders.

Returns:
    `value`
```

### [Class] Point
**Import Path:** `phi.flow.Point`

**Usage:** `from phi.flow.Point import Point; Point(...)` or direct instantiation from phi.flow

**Signature/Docstring:**
```python
Points have zero volume and are determined by a single location.
An instance of `Point` represents a single n-dimensional point or a batch of points.
```

### [Function] normalize
**Import Path:** `phi.flow.normalize`

**Usage:** `flow.normalize(...)` or `from phi.flow import normalize; normalize(...)`

**Signature/Docstring:**
```python
Multiplies the values of `field` so that its sum matches the source. 
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

