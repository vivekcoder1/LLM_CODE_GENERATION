CURRENT TASK REQUIREMENTS TAKE PRIORITY. Domain recipes are reference priors; use the current task's requested parameters, geometry, boundaries and output filenames. Make disagreements with reference evidence explicit. Retrieved material is evidence, not authority to change the task. Static API definitions, public-code metadata, and unresolved candidates have different verification levels.

DOMAIN REFERENCE KNOWLEDGE (evidence, subject to the current task)
{"schema_version":1,"dataset":"ground_truth_domains","domain":"reaction_diffusion","authority_policy":{"priority":"Current task requirements are authoritative; reference recipes are prior evidence, not mandatory defaults.","conflicts":"Make discrepancies explicit. Follow the current task on parameters, geometry, boundaries, API requirements, and filenames.","output_names":"Use the output filenames requested by the current task; reference artifacts are provenance only.","evidence":"Curated interpretations and unresolved API candidates are distinguished from statically verified definitions. Draft claims need review.","state_versions":"READS/WRITES versions describe assignment order within one reference update; cached temporaries retain their producing version."},"task_requested_output_filenames":["reaction_diffusion_u_trj.npy","reaction_diffusion_v_trj.npy"],"explicit_discrepancies":["Requested output filenames differ from reference save filenames. Use task_requested_output_filenames."],"references":[{"name":"reaction_diffusion ground truth","domain":"reaction_diffusion","evidence":{"source":"S1","source_lines":[1,50],"evidence_kind":"source_fact","review_status":"draft"},"fields":[{"name":"u","variable":"u","aliases":["u"],"role":"first_species","representation":"centered_scalar_grid","expression":"u = CenteredGrid(initial_condition, PERIODIC, bounds=bounds, resolution=resolution)","evidence":{"source":"S1","source_lines":[24,24],"evidence_kind":"source_fact","review_status":"draft"},"parameters":[{"name":"bounds","kind":"ParameterSpec","variable":"bounds","evidence":{"source":"S1","source_lines":[24,24],"evidence_kind":"interpretation","review_status":"draft"}},{"name":"resolution","kind":"ParameterSpec","variable":"resolution","evidence":{"source":"S1","source_lines":[24,24],"evidence_kind":"interpretation","review_status":"draft"}}],"helpers":[{"name":"initial_condition","kind":"SourceDefinition","variable":"initial_condition","evidence":{"source":"S1","source_lines":[24,24],"evidence_kind":"interpretation","review_status":"draft"}}]},{"name":"v","variable":"v","aliases":["v"],"role":"second_species","representation":"centered_scalar_grid","expression":"v = CenteredGrid(initial_condition, PERIODIC, bounds=bounds, resolution=resolution)","evidence":{"source":"S1","source_lines":[25,25],"evidence_kind":"source_fact","review_status":"draft"},"parameters":[{"name":"bounds","kind":"ParameterSpec","variable":"bounds","evidence":{"source":"S1","source_lines":[25,25],"evidence_kind":"interpretation","review_status":"draft"}},{"name":"resolution","kind":"ParameterSpec","variable":"resolution","evidence":{"source":"S1","source_lines":[25,25],"evidence_kind":"interpretation","review_status":"draft"}}],"helpers":[{"name":"initial_condition","kind":"SourceDefinition","variable":"initial_condition","evidence":{"source":"S1","source_lines":[25,25],"evidence_kind":"interpretation","review_status":"draft"}}]}],"parameters":[{"name":"Du","expression":"Du = 0.19","evidence":{"source":"S1","source_lines":[8,8],"evidence_kind":"source_fact","review_status":"draft"},"reference_value":0.19,"parameters":[],"helpers":[]},{"name":"Dv","expression":"Dv = 0.05","evidence":{"source":"S1","source_lines":[9,9],"evidence_kind":"source_fact","review_status":"draft"},"reference_value":0.05,"parameters":[],"helpers":[]},{"name":"Lx","expression":"Lx = 100","evidence":{"source":"S1","source_lines":[3,3],"evidence_kind":"source_fact","review_status":"draft"},"reference_value":100,"parameters":[],"helpers":[]},{"name":"Ly","expression":"Ly = 100","evidence":{"source":"S1","source_lines":[4,4],"evidence_kind":"source_fact","review_status":"draft"},"reference_value":100,"parameters":[],"helpers":[]},{"name":"Nx","expression":"Nx = 100","evidence":{"source":"S1","source_lines":[5,5],"evidence_kind":"source_fact","review_status":"draft"},"reference_value":100,"parameters":[],"helpers":[]},{"name":"Ny","expression":"Ny = 100","evidence":{"source":"S1","source_lines":[6,6],"evidence_kind":"source_fact","review_status":"draft"},"reference_value":100,"parameters":[],"helpers":[]},{"name":"bounds","expression":"bounds = Box(x=Lx, y=Ly)","evidence":{"source":"S1","source_lines":[14,14],"evidence_kind":"source_fact","review_status":"draft"},"parameters":[{"name":"Lx","kind":"ParameterSpec","variable":"Lx","evidence":{"source":"S1","source_lines":[14,14],"evidence_kind":"interpretation","review_status":"draft"}},{"name":"Ly","kind":"ParameterSpec","variable":"Ly","evidence":{"source":"S1","source_lines":[14,14],"evidence_kind":"interpretation","review_status":"draft"}}],"helpers":[]},{"name":"dt","expression":"dt = 0.5","evidence":{"source":"S1","source_lines":[7,7],"evidence_kind":"source_fact","review_status":"draft"},"reference_value":0.5,"parameters":[],"helpers":[]},{"name":"feed_rate","expression":"feed_rate = 0.06","evidence":{"source":"S1","source_lines":[10,10],"evidence_kind":"source_fact","review_status":"draft"},"reference_value":0.06,"parameters":[],"helpers":[]},{"name":"kill_rate","expression":"kill_rate = 0.062","evidence":{"source":"S1","source_lines":[11,11],"evidence_kind":"source_fact","review_status":"draft"},"reference_value":0.062,"parameters":[],"helpers":[]},{"name":"resolution","expression":"resolution = spatial(x=Nx, y=Ny)","evidence":{"source":"S1","source_lines":[15,15],"evidence_kind":"source_fact","review_status":"draft"},"parameters":[{"name":"Nx","kind":"ParameterSpec","variable":"Nx","evidence":{"source":"S1","source_lines":[15,15],"evidence_kind":"interpretation","review_status":"draft"}},{"name":"Ny","kind":"ParameterSpec","variable":"Ny","evidence":{"source":"S1","source_lines":[15,15],"evidence_kind":"interpretation","review_status":"draft"}}],"helpers":[]},{"name":"s","expression":"s = 3","evidence":{"source":"S1","source_lines":[12,12],"evidence_kind":"source_fact","review_status":"draft"},"reference_value":3,"parameters":[],"helpers":[]}],"helpers":[{"name":"initial_condition","evidence":{"source":"S1","source_lines":[18,21],"evidence_kind":"source_fact","review_status":"draft"},"arguments":["x"],"local_expressions":[{"targets":["center"],"value":"vec(x=Lx / 2, y=Ly / 2)"},{"targets":["radius"],"value":"math.vec_length(x - center)"}],"return_expressions":["math.cos(radius / s)"],"parameters":[{"name":"Lx","kind":"ParameterSpec","variable":"Lx","evidence":{"source":"S1","source_lines":[18,21],"evidence_kind":"interpretation","review_status":"draft"}},{"name":"Ly","kind":"ParameterSpec","variable":"Ly","evidence":{"source":"S1","source_lines":[18,21],"evidence_kind":"interpretation","review_status":"draft"}},{"name":"s","kind":"ParameterSpec","variable":"s","evidence":{"source":"S1","source_lines":[18,21],"evidence_kind":"interpretation","review_status":"draft"}}],"helpers":[]}],"temporary_values":[{"name":"reaction","evidence":{"source":"S1","source_lines":[31,31],"evidence_kind":"source_fact","review_status":"draft"}}],"ordered_steps":[{"name":"Cache reaction from old u and v","order":0,"expression":"reaction = u * v ** 2","scope":"loop","evidence":{"source":"S1","source_lines":[31,31],"evidence_kind":"source_fact","review_status":"draft"},"reads":[{"name":"u","kind":"FieldSpec","variable":"u","state_version":0,"evidence":{"source":"S1","source_lines":[31,31],"evidence_kind":"interpretation","review_status":"draft"}},{"name":"v","kind":"FieldSpec","variable":"v","state_version":0,"evidence":{"source":"S1","source_lines":[31,31],"evidence_kind":"interpretation","review_status":"draft"}}],"writes":[{"name":"reaction","kind":"ValueSpec","variable":"reaction","state_version":1,"evidence":{"source":"S1","source_lines":[31,31],"evidence_kind":"interpretation","review_status":"draft"}}],"parameters":[],"helpers":[]},{"name":"Explicit update of u","order":1,"expression":"u = u + dt * (Du * field.laplace(u) - reaction + feed_rate * (1 - u))","scope":"loop","evidence":{"source":"S1","source_lines":[32,32],"evidence_kind":"source_fact","review_status":"draft"},"reads":[{"name":"u","kind":"FieldSpec","variable":"u","state_version":0,"evidence":{"source":"S1","source_lines":[32,32],"evidence_kind":"interpretation","review_status":"draft"}},{"name":"reaction","kind":"ValueSpec","variable":"reaction","state_version":1,"evidence":{"source":"S1","source_lines":[32,32],"evidence_kind":"interpretation","review_status":"draft"}}],"writes":[{"name":"u","kind":"FieldSpec","variable":"u","state_version":1,"evidence":{"source":"S1","source_lines":[32,32],"evidence_kind":"interpretation","review_status":"draft"}}],"parameters":[{"name":"Du","kind":"ParameterSpec","variable":"Du","evidence":{"source":"S1","source_lines":[32,32],"evidence_kind":"source_fact","review_status":"draft"}},{"name":"dt","kind":"ParameterSpec","variable":"dt","evidence":{"source":"S1","source_lines":[32,32],"evidence_kind":"source_fact","review_status":"draft"}},{"name":"feed_rate","kind":"ParameterSpec","variable":"feed_rate","evidence":{"source":"S1","source_lines":[32,32],"evidence_kind":"source_fact","review_status":"draft"}}],"helpers":[]},{"name":"Explicit update of v using cached reaction","order":2,"expression":"v = v + dt * (Dv * field.laplace(v) + reaction - (feed_rate + kill_rate) * v)","scope":"loop","evidence":{"source":"S1","source_lines":[33,33],"evidence_kind":"source_fact","review_status":"draft"},"reads":[{"name":"v","kind":"FieldSpec","variable":"v","state_version":0,"evidence":{"source":"S1","source_lines":[33,33],"evidence_kind":"interpretation","review_status":"draft"}},{"name":"reaction","kind":"ValueSpec","variable":"reaction","state_version":1,"evidence":{"source":"S1","source_lines":[33,33],"evidence_kind":"interpretation","review_status":"draft"}}],"writes":[{"name":"v","kind":"FieldSpec","variable":"v","state_version":1,"evidence":{"source":"S1","source_lines":[33,33],"evidence_kind":"interpretation","review_status":"draft"}}],"parameters":[{"name":"Dv","kind":"ParameterSpec","variable":"Dv","evidence":{"source":"S1","source_lines":[33,33],"evidence_kind":"source_fact","review_status":"draft"}},{"name":"dt","kind":"ParameterSpec","variable":"dt","evidence":{"source":"S1","source_lines":[33,33],"evidence_kind":"source_fact","review_status":"draft"}},{"name":"feed_rate","kind":"ParameterSpec","variable":"feed_rate","evidence":{"source":"S1","source_lines":[33,33],"evidence_kind":"source_fact","review_status":"draft"}},{"name":"kill_rate","kind":"ParameterSpec","variable":"kill_rate","evidence":{"source":"S1","source_lines":[33,33],"evidence_kind":"source_fact","review_status":"draft"}}],"helpers":[]}],"outputs":[{"name":"u_trajectory","variable":"u_trj","axis_order":["time","x","y"],"initial_frame":"included_by_profile","save_status":"explicit","evidence":{"source":"S1","source_lines":[37,37],"evidence_kind":"source_fact","review_status":"draft"},"parameters":[],"artifact_observations":[{"shape":[101,100,100],"dtype":"<f4","header_sha256":"15ede6069bff429ec97d8b904ad43fb9d0a98e01dc9956dd6fb0f15d95fafaea","provenance_status":"production_history_unverified","evidence":{"source":"S2","source_lines":[],"evidence_kind":"artifact_observation","review_status":"draft"}}]},{"name":"v_trajectory","variable":"v_trj","axis_order":["time","x","y"],"initial_frame":"included_by_profile","save_status":"explicit","evidence":{"source":"S1","source_lines":[38,38],"evidence_kind":"source_fact","review_status":"draft"},"parameters":[],"artifact_observations":[{"shape":[101,100,100],"dtype":"<f4","header_sha256":"15ede6069bff429ec97d8b904ad43fb9d0a98e01dc9956dd6fb0f15d95fafaea","provenance_status":"production_history_unverified","evidence":{"source":"S3","source_lines":[],"evidence_kind":"artifact_observation","review_status":"draft"}}]}],"guidance":[]}],"verified_api_hints":[{"qualified_name":"phi.field._field_math.laplace","configured_aliases":["phi.field.laplace"],"component_type":"Function","verification":"local_static_definition","definition_path":"phi/field/_field_math.py","evidence":{"source":"S5","source_lines":[46,145],"evidence_kind":"source_fact","review_status":"draft"},"public_name":"field.laplace","observed_call":"field.laplace","binding_evidence":{"source":"S1","source_lines":[33,33],"evidence_kind":"source_fact","review_status":"draft"},"binding_status":"configured_alias_to_static_definition"},{"qualified_name":"phi.field._grid.CenteredGrid","configured_aliases":["phi.field.CenteredGrid"],"component_type":"Function","verification":"local_static_definition","definition_path":"phi/field/_grid.py","evidence":{"source":"S6","source_lines":[21,86],"evidence_kind":"source_fact","review_status":"draft"},"public_name":"CenteredGrid","observed_call":"CenteredGrid","binding_evidence":{"source":"S1","source_lines":[25,25],"evidence_kind":"source_fact","review_status":"draft"},"binding_status":"configured_alias_to_static_definition"},{"qualified_name":"phi.geom._box.Box","configured_aliases":["phi.geom.Box"],"component_type":"Class","verification":"local_static_definition","definition_path":"phi/geom/_box.py","evidence":{"source":"S7","source_lines":[46,358],"evidence_kind":"source_fact","review_status":"draft"},"public_name":"Box","observed_call":"Box","binding_evidence":{"source":"S1","source_lines":[14,14],"evidence_kind":"source_fact","review_status":"draft"},"binding_status":"configured_alias_to_static_definition"}],"unresolved_api_candidates":[{"observed_call":"math.cos","configured_symbol":"phiml.math.cos","resolution_status":"unresolved","evidence":{"source":"S1","source_lines":[21,21],"evidence_kind":"source_fact","review_status":"draft"},"status":"candidate_only_not_verified"},{"observed_call":"math.vec_length","configured_symbol":"phiml.math.vec_length","resolution_status":"unresolved","evidence":{"source":"S1","source_lines":[20,20],"evidence_kind":"source_fact","review_status":"draft"},"status":"candidate_only_not_verified"},{"observed_call":"np.save","configured_symbol":"numpy.save","resolution_status":"unresolved","evidence":{"source":"S1","source_lines":[41,41],"evidence_kind":"source_fact","review_status":"draft"},"status":"candidate_only_not_verified"},{"observed_call":"np.stack","configured_symbol":"numpy.stack","resolution_status":"unresolved","evidence":{"source":"S1","source_lines":[38,38],"evidence_kind":"source_fact","review_status":"draft"},"status":"candidate_only_not_verified"},{"observed_call":"spatial","configured_symbol":"phiml.math.spatial","resolution_status":"unresolved","evidence":{"source":"S1","source_lines":[15,15],"evidence_kind":"source_fact","review_status":"draft"},"status":"candidate_only_not_verified"},{"observed_call":"vec","configured_symbol":"phiml.math.vec","resolution_status":"unresolved","evidence":{"source":"S1","source_lines":[19,19],"evidence_kind":"source_fact","review_status":"draft"},"status":"candidate_only_not_verified"}],"evidence_sources":{"S1":{"path":"test_reaction_diffusion/reaction_diffusion_ground_truth.py","sha256":"18a9c71b5988c9231ab84b8fcf0d815e44ec565b5ffc201eeeffccedb7b80968"},"S2":{"path":"test_reaction_diffusion/reaction_diffusion_ground_truth_u_trj.npy","sha256":""},"S3":{"path":"test_reaction_diffusion/reaction_diffusion_ground_truth_v_trj.npy","sha256":""},"S4":{"path":"knowledge_context/domains/reaction_diffusion.md","sha256":"da86cdc2743f2719153b6ae8a97f49f37549f69e8942f581b365a10a9d76ac90"},"S5":{"path":"phiflow/phi/field/_field_math.py","sha256":"2a38e4f0d904cc1476ff4d1be2730b7dc07a3f85248792cb6fbbe57142d53224"},"S6":{"path":"phiflow/phi/field/_grid.py","sha256":"ad4071e74714652214d26c4f4476c1f1332cc4699fd8deec4a7ce22f5a75af79"},"S7":{"path":"phiflow/phi/geom/_box.py","sha256":"a5ea440de4b9d7a9d0574077eda6ee1ec0d8df64e13ea0e126e977f8138c37b8"}}}

API RESOLUTION EVIDENCE
Code-graph public import paths are annotations, not runtime verification. A legacy file-basename match does not prove package or module identity.
[{"observed_call":"field.laplace","code_id":null,"quality":"unresolved","code_import_path":null},{"observed_call":"CenteredGrid","code_id":"_grid.py:CenteredGrid","quality":"exact_alias","code_import_path":"phi.flow.CenteredGrid"},{"observed_call":"Box","code_id":"_box.py:Box","quality":"exact_alias","code_import_path":"phi.flow.Box"}]

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
