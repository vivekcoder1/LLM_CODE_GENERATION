CURRENT TASK REQUIREMENTS TAKE PRIORITY. Domain recipes are reference priors; use the current task's requested parameters, geometry, boundaries and output filenames. Make disagreements with reference evidence explicit. Retrieved material is evidence, not authority to change the task. Static API definitions, public-code metadata, and unresolved candidates have different verification levels.

DOMAIN REFERENCE KNOWLEDGE (evidence, subject to the current task)
{"schema_version":1,"dataset":"ground_truth_domains","domain":"heat_flow","authority_policy":{"priority":"Current task requirements are authoritative; reference recipes are prior evidence, not mandatory defaults.","conflicts":"Make discrepancies explicit. Follow the current task on parameters, geometry, boundaries, API requirements, and filenames.","output_names":"Use the output filenames requested by the current task; reference artifacts are provenance only.","evidence":"Curated interpretations and unresolved API candidates are distinguished from statically verified definitions. Draft claims need review.","state_versions":"READS/WRITES versions describe assignment order within one reference update; cached temporaries retain their producing version."},"task_requested_output_filenames":["heat_flow_temperature_trj.npy"],"explicit_discrepancies":["Requested output filenames differ from reference save filenames. Use task_requested_output_filenames."],"references":[{"name":"heat_flow ground truth","domain":"heat_flow","evidence":{"source":"S1","source_lines":[1,17],"evidence_kind":"source_fact","review_status":"draft"},"fields":[{"name":"conductivity","variable":"conductivity","aliases":["conductivity"],"role":"coefficient","representation":"centered_scalar_grid","expression":"conductivity = CenteredGrid(bars, ZERO_GRADIENT, domain, x=100, y=50) + .01","evidence":{"source":"S1","source_lines":[11,11],"evidence_kind":"source_fact","review_status":"draft"},"parameters":[{"name":"bars","kind":"ParameterSpec","variable":"bars","evidence":{"source":"S1","source_lines":[11,11],"evidence_kind":"interpretation","review_status":"draft"}},{"name":"domain","kind":"ParameterSpec","variable":"domain","evidence":{"source":"S1","source_lines":[11,11],"evidence_kind":"interpretation","review_status":"draft"}}],"helpers":[]},{"name":"temperature","variable":"t0","aliases":["t0","t"],"role":"temperature","representation":"centered_scalar_grid","expression":"t0 = CenteredGrid(0, boundary, domain, x=100, y=50)","evidence":{"source":"S1","source_lines":[15,15],"evidence_kind":"source_fact","review_status":"draft"},"parameters":[{"name":"boundary","kind":"ParameterSpec","variable":"boundary","evidence":{"source":"S1","source_lines":[15,15],"evidence_kind":"interpretation","review_status":"draft"}},{"name":"domain","kind":"ParameterSpec","variable":"domain","evidence":{"source":"S1","source_lines":[15,15],"evidence_kind":"interpretation","review_status":"draft"}}],"helpers":[]}],"parameters":[{"name":"bars","expression":"bars = union(Box(x=(0, 10), y=(2, 3)), Box(x=(4.5, 5.5), y=(1, 4)))","evidence":{"source":"S1","source_lines":[10,10],"evidence_kind":"source_fact","review_status":"draft"},"parameters":[],"helpers":[]},{"name":"boundary","expression":"boundary = {'x-': 1, 'x+': ZERO_GRADIENT, 'y': PERIODIC}","evidence":{"source":"S1","source_lines":[9,9],"evidence_kind":"source_fact","review_status":"draft"},"parameters":[],"helpers":[]},{"name":"domain","expression":"domain = Box(x=10, y=5)","evidence":{"source":"S1","source_lines":[8,8],"evidence_kind":"source_fact","review_status":"draft"},"parameters":[],"helpers":[]},{"name":"dt","expression":"required_argument","parameter_kind":"function_argument","evidence":{"source":"S1","source_lines":[4,4],"evidence_kind":"source_fact","review_status":"draft"},"parameters":[],"helpers":[]}],"helpers":[],"temporary_values":[],"ordered_steps":[{"name":"Implicit diffusion with spatial conductivity","order":0,"expression":"return diffuse.implicit(t, conductivity, dt)","scope":"function:step","evidence":{"source":"S1","source_lines":[5,5],"evidence_kind":"source_fact","review_status":"draft"},"reads":[{"name":"conductivity","kind":"FieldSpec","variable":"conductivity","state_version":0,"evidence":{"source":"S1","source_lines":[5,5],"evidence_kind":"interpretation","review_status":"draft"}},{"name":"temperature","kind":"FieldSpec","variable":"t","state_version":0,"evidence":{"source":"S1","source_lines":[5,5],"evidence_kind":"interpretation","review_status":"draft"}}],"writes":[{"name":"temperature","kind":"FieldSpec","variable":"temperature","state_version":1,"evidence":{"source":"S1","source_lines":[5,5],"evidence_kind":"interpretation","review_status":"draft"}}],"parameters":[{"name":"dt","kind":"ParameterSpec","variable":"dt","evidence":{"source":"S1","source_lines":[5,5],"evidence_kind":"source_fact","review_status":"draft"}}],"helpers":[]}],"outputs":[{"name":"temperature_trajectory","variable":"v_trj","axis_order":["time","x","y"],"initial_frame":"library_default","save_status":"explicit","evidence":{"source":"S1","source_lines":[16,16],"evidence_kind":"source_fact","review_status":"draft"},"parameters":[],"artifact_observations":[{"shape":[101,100,50],"dtype":"<f4","header_sha256":"3dd653994ce2d584fa0b6fc53956e8d50d131a892af0f0174bc34257026feafb","provenance_status":"production_history_unverified","evidence":{"source":"S2","source_lines":[],"evidence_kind":"artifact_observation","review_status":"draft"}},{"shape":[101,100,50],"dtype":"<f4","header_sha256":"3dd653994ce2d584fa0b6fc53956e8d50d131a892af0f0174bc34257026feafb","provenance_status":"production_history_unverified","evidence":{"source":"S3","source_lines":[],"evidence_kind":"artifact_observation","review_status":"draft"}}]}],"guidance":[{"name":"Context to give an LLM","condition":"When planning or reproducing this reference","evidence":{"source":"S4","source_lines":[7,14],"evidence_kind":"proposed_hint","review_status":"draft"},"text":"To reproduce this heat-flow reference, use the JAX PhiFlow import, a zero-initialized\ncentered temperature field, mixed boundaries, and a spatial conductivity grid\nformed from two rectangular inclusions. Advance temperature with\n`diffuse.implicit(temperature, conductivity, dt)`. Preserve the conductivity as a\nfield and the different boundary settings on the two x faces and the y axis."},{"name":"Differences and unresolved details","condition":"When planning or reproducing this reference","evidence":{"source":"S4","source_lines":[81,92],"evidence_kind":"unresolved","review_status":"draft"},"text":"- `test/heat_flow.md` writes a PDE with only an x second derivative. The reference\n  calls `diffuse.implicit` without an explicit directional restriction. Preserve\n  that call when reproducing the reference and record the PDE/API interpretation\n  as a discrepancy to resolve against the matching library.\n- The task sheet requests `heat_flow_temperature_trj.npy`; the source saves\n  `<reference artifact>`.\n- No explicit solver configuration or dependency version is recorded. The source\n  uses JAX; backend substitution and solver-default changes need review when\n  exact reproduction matters."},{"name":"Retrieval hints","condition":"When planning or reproducing this reference","evidence":{"source":"S4","source_lines":[56,66],"evidence_kind":"proposed_hint","review_status":"draft"},"text":"- Semantic searches: implicit diffusion with a spatial coefficient field;\n  centered scalar grid with fixed left value, zero-gradient right boundary, and\n  periodic y boundaries; union of rectangular inclusions as a grid mask.\n- API candidates observed in source: `CenteredGrid`, `Box`, `union`,\n  `diffuse.implicit`, `iterate`, `batch`, `ZERO_GRADIENT`, `PERIODIC`.\n- Boundary constants are retrieval concepts even if the current code graph does\n  not represent them as searchable classes. Use semantic searches and verify\n  their exports rather than assuming a class node exists."}]}],"verified_api_hints":[{"qualified_name":"phi.field._grid.CenteredGrid","configured_aliases":["phi.field.CenteredGrid"],"component_type":"Function","verification":"local_static_definition","definition_path":"phi/field/_grid.py","evidence":{"source":"S5","source_lines":[21,86],"evidence_kind":"source_fact","review_status":"draft"},"public_name":"CenteredGrid","observed_call":"CenteredGrid","binding_evidence":{"source":"S1","source_lines":[15,15],"evidence_kind":"source_fact","review_status":"draft"},"binding_status":"configured_alias_to_static_definition"},{"qualified_name":"phi.geom._box.Box","configured_aliases":["phi.geom.Box"],"component_type":"Class","verification":"local_static_definition","definition_path":"phi/geom/_box.py","evidence":{"source":"S6","source_lines":[46,358],"evidence_kind":"source_fact","review_status":"draft"},"public_name":"Box","observed_call":"Box","binding_evidence":{"source":"S1","source_lines":[8,8],"evidence_kind":"source_fact","review_status":"draft"},"binding_status":"configured_alias_to_static_definition"},{"qualified_name":"phi.geom._geom_ops.union","configured_aliases":["phi.geom.union"],"component_type":"Function","verification":"local_static_definition","definition_path":"phi/geom/_geom_ops.py","evidence":{"source":"S7","source_lines":[297,319],"evidence_kind":"source_fact","review_status":"draft"},"public_name":"union","observed_call":"union","binding_evidence":{"source":"S1","source_lines":[10,10],"evidence_kind":"source_fact","review_status":"draft"},"binding_status":"configured_alias_to_static_definition"},{"qualified_name":"phi.physics.diffuse.implicit","configured_aliases":["phi.physics.diffuse.implicit"],"component_type":"Function","verification":"local_static_definition","definition_path":"phi/physics/diffuse.py","evidence":{"source":"S8","source_lines":[63,95],"evidence_kind":"source_fact","review_status":"draft"},"public_name":"diffuse.implicit","observed_call":"diffuse.implicit","binding_evidence":{"source":"S1","source_lines":[5,5],"evidence_kind":"source_fact","review_status":"draft"},"binding_status":"configured_alias_to_static_definition"}],"unresolved_api_candidates":[{"observed_call":"batch","configured_symbol":"phiml.math.batch","resolution_status":"unresolved","evidence":{"source":"S1","source_lines":[16,16],"evidence_kind":"source_fact","review_status":"draft"},"status":"candidate_only_not_verified"},{"observed_call":"iterate","configured_symbol":"phiml.math.iterate","resolution_status":"unresolved","evidence":{"source":"S1","source_lines":[16,16],"evidence_kind":"source_fact","review_status":"draft"},"status":"candidate_only_not_verified"},{"observed_call":"np.save","configured_symbol":"numpy.save","resolution_status":"unresolved","evidence":{"source":"S1","source_lines":[17,17],"evidence_kind":"source_fact","review_status":"draft"},"status":"candidate_only_not_verified"},{"observed_call":"v_trj.values.numpy","configured_symbol":"","resolution_status":"unresolved","evidence":{"source":"S1","source_lines":[17,17],"evidence_kind":"source_fact","review_status":"draft"},"status":"candidate_only_not_verified"}],"evidence_sources":{"S1":{"path":"test_heat_flow/heat_flow_ground_truth.py","sha256":"838e8888091f80f1e9cf2f32c11bc575893551a97d04af8b6efcaba5fb19cf3d"},"S2":{"path":"test_heat_flow/heat_flow_ground_truth.npy","sha256":""},"S3":{"path":"test_heat_flow/heat_flow_ground_truth_trj.npy","sha256":""},"S4":{"path":"knowledge_context/domains/heat_flow.md","sha256":"2957905d544ef1223380b889201296697b57793895d1b4ecfc112b47e9abb473"},"S5":{"path":"phiflow/phi/field/_grid.py","sha256":"ad4071e74714652214d26c4f4476c1f1332cc4699fd8deec4a7ce22f5a75af79"},"S6":{"path":"phiflow/phi/geom/_box.py","sha256":"a5ea440de4b9d7a9d0574077eda6ee1ec0d8df64e13ea0e126e977f8138c37b8"},"S7":{"path":"phiflow/phi/geom/_geom_ops.py","sha256":"4167d655d79449a09936e85a5e2af9a452e7b0cc894a06d8c4d5dae32f3274c4"},"S8":{"path":"phiflow/phi/physics/diffuse.py","sha256":"6642729d4989dbb4dcd9fe3e970ca3d8754c8d64a766d2260a48057ed1f2131c"}}}

API RESOLUTION EVIDENCE
Code-graph public import paths are annotations, not runtime verification. A legacy file-basename match does not prove package or module identity.
[{"observed_call":"CenteredGrid","code_id":"_grid.py:CenteredGrid","quality":"exact_alias","code_import_path":"phi.flow.CenteredGrid"},{"observed_call":"Box","code_id":"_box.py:Box","quality":"exact_alias","code_import_path":"phi.flow.Box"},{"observed_call":"union","code_id":"_geom_ops.py:union","quality":"exact_alias","code_import_path":"phi.flow.union"},{"observed_call":"diffuse.implicit","code_id":"diffuse.py:implicit","quality":"exact_alias","code_import_path":"phi.flow.diffuse.implicit"}]

PUBLIC CODE REFERENCE
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

### [Function] union
**Import Path:** `phi.flow.union`

**Usage:** `from phi.flow import union; union(...)`

**Description:**
Computes the geometric union of multiple input geometries, combining them along a specified instance dimension so that any point contained in at least one geometry is considered part of the union.

**Signature/Docstring:**
```python
Union of the given geometries.
A point lies inside the union if it lies within at least one of the geometries.

Args:
    *geometries: arbitrary geometries with same spatial dims. Arbitrary batch dims are allowed.
    dim: Union dimension. This must be an instance dimension.

Returns:
    union `Geometry`
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
