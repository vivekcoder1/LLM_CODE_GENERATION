# CODEBASE COMPONENT SPECIFICATIONS & API REFERENCE

## 1. PRIMARY PUBLIC API ENDPOINTS (PREFER USING THESE)

### [Function] CenteredGrid
**Import Path:** `phi.flow.CenteredGrid`

**Usage:** `from phi.flow import CenteredGrid; CenteredGrid(...)`

**Description:**
Constructs an n-dimensional grid where field values are sampled at cell centers, accepting flexible input types (geometries, fields, numbers, tensors, or functions) and defining the grid's physical bounds, resolution, and boundary extrapolation behavior.

**Parameters:**
- boundary (Any)
- bounds (Box or float)
- convert
- extrapolation (Any)
- resolution (int or Shape)
- values (Any)

**Returns:** `Field`

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

### [Class] Noise
**Import Path:** `phi.flow.Noise`

**Usage:** `from phi.flow import Noise; Noise(...)`

**Description:**
Generates random noise fields with configurable spatial scale and smoothness, using FFT-based frequency filtering to produce spatially correlated random fluctuations. It is primarily used to initialize CenteredGrids or StaggeredGrids with realistic random perturbations.

**Signature/Docstring:**
```python
Generates random noise fluctuations which can be configured in physical size and smoothness.
Each time values are sampled from a Noise field, a new noise field is generated.

Noise is typically used as an initializer for CenteredGrids or StaggeredGrids.
```

### [Class] Box
**Import Path:** `phi.flow.Box`

**Usage:** `from phi.flow import Box; Box(...)`

**Description:**
The Box class represents an axis-aligned or rotatable cuboid geometry defined by lower and upper corner coordinates, supporting construction via positional vectors, keyword dimension limits, or slice notation.

It provides extensive geometric operations including volume/area computation, point containment testing, signed distance calculations

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

### [Function] semi_lagrangian
**Import Path:** `phi.flow.advect.semi_lagrangian`

**Usage:** `from phi.flow import advect; advect.semi_lagrangian(...)`

**Description:**
Advects a scalar or vector field defined on a grid backward through a given velocity field over time step dt, using an ODE integrator to trace lookup points and resampling the field at those locations to compute updated values.

**Parameters:**
- field (Field)
- velocity (Field)
- dt (float)
- integrator

**Returns:** `Field`

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

### [Function] implicit
**Import Path:** `phi.flow.diffuse.implicit`

**Usage:** `from phi.flow import diffuse; diffuse.implicit(...)`

**Description:**
Performs implicit Euler diffusion by constructing and solving a linear system representing the diffusion equation over a time interval, returning a diffused version of the input field.

**Parameters:**
- field (Field)
- diffusivity (Tensor)
- dt (Tensor)
- solve
- gradient (Field)
- upwind (Field)
- correct_skew
- gradient_for_diffusivity

**Returns:** `Field`

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

### [Method] grid_sample
**Import Path:** `phi.flow.Noise.grid_sample`

**Usage:** On an initialized `Noise` instance, call `instance.grid_sample(...)`.

**Description:**
Generates a sampled grid of noise values at the specified resolution and size, shaped according to the given shape parameter for use in noise generation.

**Parameters:**
- resolution
- size
- shape

### [Method] approximate_closest_surface
**Import Path:** `phi.flow.Box.approximate_closest_surface`

**Usage:** On an initialized `Box` instance, call `instance.approximate_closest_surface(...)`.

**Description:**
Computes an approximate closest point or distance on the surface of the Box relative to the given location, likely used for spatial queries or collision detection.

**Parameters:**
- location (Tensor)

**Returns:** `Tuple[Tensor, Tensor, Tensor, Tensor, Tensor]`

### [Method] approximate_signed_distance
**Import Path:** `phi.flow.Box.approximate_signed_distance`

**Usage:** On an initialized `Box` instance, call `instance.approximate_signed_distance(...)`.

**Description:**
Computes the signed L-infinity distance from a given location to the nearest side of the Box, returning positive values outside the box and negative values inside it.

**Parameters:**
- location (Tensor)

**Signature/Docstring:**
```python
Computes the signed L-infinity norm (manhattan distance) from the location to the nearest side of the box.
For an outside location `l` with the closest surface point `s`, the distance is `max(abs(l - s))`.
For inside locations it is `-max(abs(l - s))`.

Args:
  location: float tensor of shape (batch_size, ..., rank)

Returns:
  float tensor of shape (*location.shape[:-1], 1).
```

### [Method] at
**Import Path:** `phi.flow.Box.at`

**Usage:** On an initialized `Box` instance, call `instance.at(...)`.

**Description:**
Sets or returns the center point of the Box, likely used to reposition the box at a specified coordinate.

**Parameters:**
- center (Tensor)

**Returns:** `'Box'`

### [Method] boundary_elements
**Import Path:** `phi.flow.Box.boundary_elements`

**Usage:** On an initialized `Box` instance, call `instance.boundary_elements(...)`.

**Description:**
Returns the boundary elements of the Box instance, likely representing its edges, faces, or surfaces that define its outer limits.

**Returns:** `Dict[Any, Dict[str, slice]]`

### [Method] boundary_faces
**Import Path:** `phi.flow.Box.boundary_faces`

**Usage:** On an initialized `Box` instance, call `instance.boundary_faces(...)`.

**Description:**
Returns the set of faces representing the boundary of the Box object, likely used for rendering or geometric boundary extraction.

**Returns:** `Dict[Any, Dict[str, slice]]`

### [Method] bounding_half_extent
**Import Path:** `phi.flow.Box.bounding_half_extent`

**Usage:** On an initialized `Box` instance, call `instance.bounding_half_extent(...)`.

**Description:**
Returns half the extent (size) of the box along its dominant axis, representing the bounding radius from the box's center to its farthest point.

**Returns:** `Tensor`

---

## 2. GRAPH INTERCONNECTIONS & DEPENDENCIES

- [Class] Box --(Has Method)--> [Method] approximate_closest_surface
- [Class] Box --(Has Method)--> [Method] approximate_signed_distance
- [Class] Box --(Has Method)--> [Method] at
- [Class] Box --(Has Method)--> [Method] boundary_elements
- [Class] Box --(Has Method)--> [Method] boundary_faces
- [Class] Box --(Has Method)--> [Method] bounding_half_extent
- [Class] Noise --(Has Method)--> [Method] grid_sample
