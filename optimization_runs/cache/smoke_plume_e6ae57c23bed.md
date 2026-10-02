# CODEBASE COMPONENT SPECIFICATIONS & API REFERENCE

## 1. PRIMARY PUBLIC API ENDPOINTS (PREFER USING THESE)

### [Function] masked_laplace
**Import Path:** `phi.flow.fluid.masked_laplace`

**Usage:** `fluid.masked_laplace(...)` or `from phi.flow.fluid import masked_laplace; masked_laplace(...)`

**Returns:** `CenteredGrid`

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

### [Class] Noise
**Import Path:** `phi.flow.Noise`

**Usage:** `from phi.flow.Noise import Noise; Noise(...)` or direct instantiation from phi.flow

**Signature/Docstring:**
```python
Generates random noise fluctuations which can be configured in physical size and smoothness.
Each time values are sampled from a Noise field, a new noise field is generated.

Noise is typically used as an initializer for CenteredGrids or StaggeredGrids.
```

### [Class] Mesh
**Import Path:** `phi.flow.Mesh`

**Usage:** `from phi.flow.Mesh import Mesh; Mesh(...)` or direct instantiation from phi.flow

**Signature/Docstring:**
```python
Unstructured mesh, consisting of vertices and elements.

Use `phi.geom.mesh()` or `phi.geom.mesh_from_numpy()` to construct a mesh manually or `phi.geom.load_su2()` to load one from a file.
```

### [Class] UniformGrid
**Import Path:** `phi.flow.UniformGrid`

**Usage:** `from phi.flow.UniformGrid import UniformGrid; UniformGrid(...)` or direct instantiation from phi.flow

**Signature/Docstring:**
```python
An instance of UniformGrid represents all cells of a regular grid as a batch of boxes.
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

### [Function] make_incompressible
**Import Path:** `phi.flow.fluid.make_incompressible`

**Usage:** `fluid.make_incompressible(...)` or `from phi.flow.fluid import make_incompressible; make_incompressible(...)`

**Signature/Docstring:**
```python
Projects the given velocity field by solving for the pressure and subtracting its spatial_gradient.

This method is similar to :func:`field.divergence_free()` but differs in how the boundary conditions are specified.

Args:
    velocity: Vector field sampled on a grid.
    obstacles: `Obstacle` or `phi.geom.Geometry` or tuple/list thereof to specify boundary conditions inside the domain.
    solve: `Solve` object specifying method and tolerances for the implicit pressure solve.
    active: (Optional) Mask for which cells the pressure should be solved.
        If given, the velocity may take `NaN` values where it does not contribute to the pressure.
        Also, the total divergence will never be subtracted if active is given, even if all values are 1.
    order: spatial order for derivative computations.
        For Higher-order schemes, the laplace operation is not conducted with a stencil exactly corresponding to the one used in divergence calculations but a smaller one instead.
        While this disrupts the formal correctness of the method it only induces insignificant errors and yields considerable performance gains.
        supported: explicit 2/4th order - implicit 6th order (obstacles are only supported with explicit 2nd order)

Returns:
    velocity: divergence-free velocity of type `type(velocity)`
    pressure: solved pressure field, `CenteredGrid`
```

