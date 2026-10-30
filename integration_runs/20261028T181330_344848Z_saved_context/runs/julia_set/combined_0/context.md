CURRENT TASK REQUIREMENTS TAKE PRIORITY. Domain recipes are reference priors; use the current task's requested parameters, geometry, boundaries and output filenames. Make disagreements with reference evidence explicit. Retrieved material is evidence, not authority to change the task. Static API definitions, public-code metadata, and unresolved candidates have different verification levels.

DOMAIN REFERENCE KNOWLEDGE (evidence, subject to the current task)
{"schema_version":1,"dataset":"ground_truth_domains","domain":"julia_set","authority_policy":{"priority":"Current task requirements are authoritative; reference recipes are prior evidence, not mandatory defaults.","conflicts":"Make discrepancies explicit. Follow the current task on parameters, geometry, boundaries, API requirements, and filenames.","output_names":"Use the output filenames requested by the current task; reference artifacts are provenance only.","evidence":"Curated interpretations and unresolved API candidates are distinguished from statically verified definitions. Draft claims need review.","state_versions":"READS/WRITES versions describe assignment order within one reference update; cached temporaries retain their producing version."},"task_requested_output_filenames":["julia_set_domain_trj.npy"],"explicit_discrepancies":[],"references":[{"name":"julia_set ground truth","domain":"julia_set","evidence":{"source":"S1","source_lines":[1,27],"evidence_kind":"source_fact","review_status":"draft"},"fields":[{"name":"complex_state","variable":"z_field","aliases":["z_field","z"],"role":"persistent_complex_state","representation":"complex_centered_grid_values","expression":"z_field = CenteredGrid(\n    lambda position: position.vector['x'] + 1j * position.vector['y'],\n    extrapolation=0,\n    bounds=bounds,\n    resolution=resolution,\n)","evidence":{"source":"S1","source_lines":[11,16],"evidence_kind":"source_fact","review_status":"draft"},"parameters":[{"name":"bounds","kind":"ParameterSpec","variable":"bounds","evidence":{"source":"S1","source_lines":[11,16],"evidence_kind":"interpretation","review_status":"draft"}},{"name":"resolution","kind":"ParameterSpec","variable":"resolution","evidence":{"source":"S1","source_lines":[11,16],"evidence_kind":"interpretation","review_status":"draft"}}],"helpers":[]},{"name":"threshold_count","variable":"escape_count","aliases":["escape_count"],"role":"cumulative_threshold_count","representation":"scalar_tensor","expression":"escape_count = math.zeros(resolution)","evidence":{"source":"S1","source_lines":[18,18],"evidence_kind":"source_fact","review_status":"draft"},"parameters":[{"name":"resolution","kind":"ParameterSpec","variable":"resolution","evidence":{"source":"S1","source_lines":[18,18],"evidence_kind":"interpretation","review_status":"draft"}}],"helpers":[]}],"parameters":[{"name":"Nx","expression":"Nx = Ny = 256","evidence":{"source":"S1","source_lines":[6,6],"evidence_kind":"source_fact","review_status":"draft"},"reference_value":256,"parameters":[],"helpers":[]},{"name":"Ny","expression":"Nx = Ny = 256","evidence":{"source":"S1","source_lines":[6,6],"evidence_kind":"source_fact","review_status":"draft"},"reference_value":256,"parameters":[],"helpers":[]},{"name":"bounds","expression":"bounds = Box(x=(-2, 2), y=(-2, 2))","evidence":{"source":"S1","source_lines":[8,8],"evidence_kind":"source_fact","review_status":"draft"},"parameters":[],"helpers":[]},{"name":"resolution","expression":"resolution = spatial(x=Nx, y=Ny)","evidence":{"source":"S1","source_lines":[9,9],"evidence_kind":"source_fact","review_status":"draft"},"parameters":[{"name":"Nx","kind":"ParameterSpec","variable":"Nx","evidence":{"source":"S1","source_lines":[9,9],"evidence_kind":"interpretation","review_status":"draft"}},{"name":"Ny","kind":"ParameterSpec","variable":"Ny","evidence":{"source":"S1","source_lines":[9,9],"evidence_kind":"interpretation","review_status":"draft"}}],"helpers":[]},{"name":"steps","expression":"steps = 100","evidence":{"source":"S1","source_lines":[7,7],"evidence_kind":"source_fact","review_status":"draft"},"reference_value":100,"parameters":[],"helpers":[]},{"name":"z","expression":"z = z_field.values","evidence":{"source":"S1","source_lines":[17,17],"evidence_kind":"source_fact","review_status":"draft"},"parameters":[],"helpers":[]}],"helpers":[],"temporary_values":[{"name":"c","evidence":{"source":"S1","source_lines":[22,22],"evidence_kind":"source_fact","review_status":"draft"}}],"ordered_steps":[{"name":"Compute rotating complex parameter","order":0,"expression":"c = 0.7885 * cmath.exp(1j * 2 * cmath.pi * step / steps)","scope":"loop","evidence":{"source":"S1","source_lines":[22,22],"evidence_kind":"source_fact","review_status":"draft"},"reads":[],"writes":[{"name":"c","kind":"ValueSpec","variable":"c","state_version":1,"evidence":{"source":"S1","source_lines":[22,22],"evidence_kind":"interpretation","review_status":"draft"}}],"parameters":[{"name":"steps","kind":"ParameterSpec","variable":"steps","evidence":{"source":"S1","source_lines":[22,22],"evidence_kind":"source_fact","review_status":"draft"}}],"helpers":[]},{"name":"Update persistent complex state","order":1,"expression":"z = z ** 2 + c","scope":"loop","evidence":{"source":"S1","source_lines":[23,23],"evidence_kind":"source_fact","review_status":"draft"},"reads":[{"name":"complex_state","kind":"FieldSpec","variable":"z","state_version":0,"evidence":{"source":"S1","source_lines":[23,23],"evidence_kind":"interpretation","review_status":"draft"}},{"name":"c","kind":"ValueSpec","variable":"c","state_version":1,"evidence":{"source":"S1","source_lines":[23,23],"evidence_kind":"interpretation","review_status":"draft"}}],"writes":[{"name":"complex_state","kind":"FieldSpec","variable":"z","state_version":1,"evidence":{"source":"S1","source_lines":[23,23],"evidence_kind":"interpretation","review_status":"draft"}}],"parameters":[],"helpers":[]},{"name":"Accumulate strict magnitude threshold","order":2,"expression":"escape_count = escape_count + (abs(z) < 2)","scope":"loop","evidence":{"source":"S1","source_lines":[24,24],"evidence_kind":"source_fact","review_status":"draft"},"reads":[{"name":"complex_state","kind":"FieldSpec","variable":"z","state_version":1,"evidence":{"source":"S1","source_lines":[24,24],"evidence_kind":"interpretation","review_status":"draft"}},{"name":"threshold_count","kind":"FieldSpec","variable":"escape_count","state_version":0,"evidence":{"source":"S1","source_lines":[24,24],"evidence_kind":"interpretation","review_status":"draft"}}],"writes":[{"name":"threshold_count","kind":"FieldSpec","variable":"escape_count","state_version":1,"evidence":{"source":"S1","source_lines":[24,24],"evidence_kind":"interpretation","review_status":"draft"}}],"parameters":[],"helpers":[]}],"outputs":[{"name":"count_trajectory","variable":"v_trj","axis_order":["time","x","y"],"initial_frame":"excluded_by_profile","save_status":"not_explicit","evidence":{"source":"S1","source_lines":[27,27],"evidence_kind":"source_fact","review_status":"draft"},"parameters":[],"artifact_observations":[{"shape":[100,256,256],"dtype":"<f4","header_sha256":"8a21bb49213145c53f0aa79ddfcb1fdae0bb1de3b9ceeb4ef4e349b766037cdb","provenance_status":"production_history_unverified","evidence":{"source":"S2","source_lines":[],"evidence_kind":"artifact_observation","review_status":"draft"}}]}],"guidance":[{"name":"Context to give an LLM","condition":"When planning or reproducing this reference","evidence":{"source":"S3","source_lines":[7,15],"evidence_kind":"proposed_hint","review_status":"draft"},"text":"This reference constructs complex coordinates on a centered 2D grid, then evolves\none persistent complex state for 100 updates while rotating the parameter `c`.\nAfter each update it adds the Boolean condition `abs(z) < 2` to a cumulative\ncount and stores that count. It does not restart the complex state for each frame,\nfreeze escaped points, or run an inner escape loop. Preserve these details when\nreproducing this particular implementation."},{"name":"Differences and unresolved details","condition":"When planning or reproducing this reference","evidence":{"source":"S3","source_lines":[82,90],"evidence_kind":"unresolved","review_status":"draft"},"text":"- `test/julia_set.md` mentions `N_escape=50`; the reference has no 50-iteration\n  inner loop or corresponding variable. Do not add one during reproduction.\n- The task requests `julia_set_domain_trj.npy`; the reference only computes\n  `v_trj`. Saving it is an additional output action when requested.\n- No dependency versions or numeric precision settings are specified. Arithmetic\n  behavior after large complex magnitudes has not been assessed in these notes."},{"name":"Retrieval hints","condition":"When planning or reproducing this reference","evidence":{"source":"S3","source_lines":[57,67],"evidence_kind":"proposed_hint","review_status":"draft"},"text":"- Semantic searches: centered grid initialized with complex spatial coordinates;\n  persistent quadratic complex iteration with rotating parameter; cumulative\n  magnitude-threshold count; named spatial axes to NumPy trajectory.\n- API candidates observed in source: `CenteredGrid`, `Box`, `spatial`,\n  `math.zeros`, tensor `.numpy()`, `cmath.exp`, `np.stack`.\n- Some operations are tensor arithmetic or standard-library/NumPy operations,\n  which may be outside the ingested PhiFlow code graph. Record this coverage gap\n  instead of substituting an unrelated physics solver."}]}],"verified_api_hints":[{"qualified_name":"phi.field._grid.CenteredGrid","configured_aliases":["phi.field.CenteredGrid"],"component_type":"Function","verification":"local_static_definition","definition_path":"phi/field/_grid.py","evidence":{"source":"S4","source_lines":[21,86],"evidence_kind":"source_fact","review_status":"draft"},"public_name":"CenteredGrid","observed_call":"CenteredGrid","binding_evidence":{"source":"S1","source_lines":[11,16],"evidence_kind":"source_fact","review_status":"draft"},"binding_status":"configured_alias_to_static_definition"},{"qualified_name":"phi.geom._box.Box","configured_aliases":["phi.geom.Box"],"component_type":"Class","verification":"local_static_definition","definition_path":"phi/geom/_box.py","evidence":{"source":"S5","source_lines":[46,358],"evidence_kind":"source_fact","review_status":"draft"},"public_name":"Box","observed_call":"Box","binding_evidence":{"source":"S1","source_lines":[8,8],"evidence_kind":"source_fact","review_status":"draft"},"binding_status":"configured_alias_to_static_definition"}],"unresolved_api_candidates":[{"observed_call":"abs","configured_symbol":"builtins.abs","resolution_status":"unresolved","evidence":{"source":"S1","source_lines":[24,24],"evidence_kind":"source_fact","review_status":"draft"},"status":"candidate_only_not_verified"},{"observed_call":"cmath.exp","configured_symbol":"cmath.exp","resolution_status":"unresolved","evidence":{"source":"S1","source_lines":[22,22],"evidence_kind":"source_fact","review_status":"draft"},"status":"candidate_only_not_verified"},{"observed_call":"math.zeros","configured_symbol":"phiml.math.zeros","resolution_status":"unresolved","evidence":{"source":"S1","source_lines":[18,18],"evidence_kind":"source_fact","review_status":"draft"},"status":"candidate_only_not_verified"},{"observed_call":"np.stack","configured_symbol":"numpy.stack","resolution_status":"unresolved","evidence":{"source":"S1","source_lines":[27,27],"evidence_kind":"source_fact","review_status":"draft"},"status":"candidate_only_not_verified"},{"observed_call":"spatial","configured_symbol":"phiml.math.spatial","resolution_status":"unresolved","evidence":{"source":"S1","source_lines":[9,9],"evidence_kind":"source_fact","review_status":"draft"},"status":"candidate_only_not_verified"}],"evidence_sources":{"S1":{"path":"test_julia_set/julia_set_ground_truth.py","sha256":"60d465609787726a0f6bd77db2a76716627f4c0a42b913ba44e9d9d22e4e7885"},"S2":{"path":"test_julia_set/julia_set_ground_truth_trj.npy","sha256":""},"S3":{"path":"knowledge_context/domains/julia_set.md","sha256":"003dba0f842e6cadb680daf11e32e38ebac6d3a35d083452f1433ee97db3a0b1"},"S4":{"path":"phiflow/phi/field/_grid.py","sha256":"ad4071e74714652214d26c4f4476c1f1332cc4699fd8deec4a7ce22f5a75af79"},"S5":{"path":"phiflow/phi/geom/_box.py","sha256":"a5ea440de4b9d7a9d0574077eda6ee1ec0d8df64e13ea0e126e977f8138c37b8"}}}

API RESOLUTION EVIDENCE
Code-graph public import paths are annotations, not runtime verification. A legacy file-basename match does not prove package or module identity.
[{"observed_call":"CenteredGrid","code_id":"_grid.py:CenteredGrid","quality":"exact_alias","code_import_path":"phi.flow.CenteredGrid"},{"observed_call":"Box","code_id":"_box.py:Box","quality":"exact_alias","code_import_path":"phi.flow.Box"}]

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
- other ('Box')

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
