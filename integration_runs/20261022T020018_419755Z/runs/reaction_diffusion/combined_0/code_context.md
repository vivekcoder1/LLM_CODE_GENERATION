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

### [Method] bounding_radius
**Import Path:** `phi.flow.Box.bounding_radius`

**Usage:** On an initialized `Box` instance, call `instance.bounding_radius(...)`.

**Description:**
Calculates and returns the radius of a sphere that would fully enclose the Box instance, likely derived from its dimensions.

### [Method] center
**Import Path:** `phi.flow.Box.center`

**Usage:** On an initialized `Box` instance, call `instance.center(...)`.

**Description:**
Returns or calculates the center point of the Box instance, likely based on its position and dimensions.

### [Method] center_representation
**Import Path:** `phi.flow.Box.center_representation`

**Usage:** On an initialized `Box` instance, call `instance.center_representation(...)`.

**Description:**
Returns the coordinate representation of the box centered at its midpoint, likely converting from a corner-based or origin-based format to a center-based format.

**Returns:** `'Cuboid'`

### [Method] contains
**Import Path:** `phi.flow.Box.contains`

**Usage:** On an initialized `Box` instance, call `instance.contains(...)`.

**Description:**
Determines whether another box (other) is entirely enclosed within the bounds of this box.

**Parameters:**
- other

**Signature/Docstring:**
```python
Tests if the other box lies fully inside this box. 
```

---

## 2. GRAPH INTERCONNECTIONS & DEPENDENCIES

- [Class] Box --(Has Method)--> [Method] approximate_closest_surface
- [Class] Box --(Has Method)--> [Method] approximate_signed_distance
- [Class] Box --(Has Method)--> [Method] at
- [Class] Box --(Has Method)--> [Method] boundary_elements
- [Class] Box --(Has Method)--> [Method] boundary_faces
- [Class] Box --(Has Method)--> [Method] bounding_half_extent
- [Class] Box --(Has Method)--> [Method] bounding_radius
- [Class] Box --(Has Method)--> [Method] center
- [Class] Box --(Has Method)--> [Method] center_representation
- [Class] Box --(Has Method)--> [Method] contains
