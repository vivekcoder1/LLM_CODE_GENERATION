# CODEBASE COMPONENT SPECIFICATIONS & API REFERENCE

## 1. PRIMARY PUBLIC API ENDPOINTS (PREFER USING THESE)

### [File] fluid.py
**Import Path:** `phi.flow.fluid.py`

### [Type] StaggeredGrid
**Import Path:** `phi.flow.StaggeredGrid`

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

### [Method] gradient
**Import Path:** `phi.flow.Field.gradient`

**Signature/Docstring:**
```python
Alias for `phi.field.spatial_gradient`
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

### [Method] bounding_radius
**Import Path:** `phi.flow.UniformGrid.bounding_radius`

### [Method] center
**Import Path:** `phi.flow.UniformGrid.center`

### [Method] center_representation
**Import Path:** `phi.flow.UniformGrid.center_representation`

### [Method] corner_representation
**Import Path:** `phi.flow.UniformGrid.corner_representation`

### [Method] face_areas
**Import Path:** `phi.flow.UniformGrid.face_areas`

### [Method] face_centers
**Import Path:** `phi.flow.UniformGrid.face_centers`

### [Method] face_normals
**Import Path:** `phi.flow.UniformGrid.face_normals`

### [Method] face_shape
**Import Path:** `phi.flow.UniformGrid.face_shape`

### [Method] faces
**Import Path:** `phi.flow.UniformGrid.faces`

### [Method] interior
**Import Path:** `phi.flow.UniformGrid.interior`

### [Method] lower
**Import Path:** `phi.flow.UniformGrid.lower`

### [Method] normal
**Import Path:** `phi.flow.UniformGrid.normal`

### [Method] position_of
**Import Path:** `phi.flow.UniformGrid.position_of`

### [Method] rotated
**Import Path:** `phi.flow.UniformGrid.rotated`

### [Method] shifted
**Import Path:** `phi.flow.UniformGrid.shifted`

### [Method] spatial_rank
**Import Path:** `phi.flow.UniformGrid.spatial_rank`

### [Method] stagger
**Import Path:** `phi.flow.UniformGrid.stagger`

### [Method] staggered_cells
**Import Path:** `phi.flow.UniformGrid.staggered_cells`

### [Method] upper
**Import Path:** `phi.flow.UniformGrid.upper`

### [Method] volume
**Import Path:** `phi.flow.UniformGrid.volume`

### [Method] voxel_at
**Import Path:** `phi.flow.UniformGrid.voxel_at`

### [Method] with_scaled_resolution
**Import Path:** `phi.flow.UniformGrid.with_scaled_resolution`

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

- [Class] Field --(Has Method)--> [Method] gradient
- [Class] UniformGrid --(Has Method)--> [Method] boundary_elements
- [Class] UniformGrid --(Has Method)--> [Method] boundary_faces
- [Class] UniformGrid --(Has Method)--> [Method] bounding_half_extent
- [Class] UniformGrid --(Has Method)--> [Method] bounding_radius
- [Class] UniformGrid --(Has Method)--> [Method] center
- [Class] UniformGrid --(Has Method)--> [Method] center_representation
- [Class] UniformGrid --(Has Method)--> [Method] corner_representation
- [Class] UniformGrid --(Has Method)--> [Method] face_areas
- [Class] UniformGrid --(Has Method)--> [Method] face_centers
- [Class] UniformGrid --(Has Method)--> [Method] face_normals
- [Class] UniformGrid --(Has Method)--> [Method] face_shape
- [Class] UniformGrid --(Has Method)--> [Method] faces
- [Class] UniformGrid --(Has Method)--> [Method] interior
- [Class] UniformGrid --(Has Method)--> [Method] lower
- [Class] UniformGrid --(Has Method)--> [Method] normal
- [Class] UniformGrid --(Has Method)--> [Method] position_of
- [Class] UniformGrid --(Has Method)--> [Method] rotated
- [Class] UniformGrid --(Has Method)--> [Method] shifted
- [Class] UniformGrid --(Has Method)--> [Method] spatial_rank
- [Class] UniformGrid --(Has Method)--> [Method] stagger
- [Class] UniformGrid --(Has Method)--> [Method] staggered_cells
- [Class] UniformGrid --(Has Method)--> [Method] upper
- [Class] UniformGrid --(Has Method)--> [Method] volume
- [Class] UniformGrid --(Has Method)--> [Method] voxel_at
- [Class] UniformGrid --(Has Method)--> [Method] with_scaled_resolution
