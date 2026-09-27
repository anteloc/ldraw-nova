# Shadow connections and snapping

The toolkit loads the supplied `data/offLibShadow/` automatically through pyldraw3. Agents can inspect connector IDs and occupancy, request checked placements, move a complete submodel through one of its leaf connectors, and store snaps in reproducible JSON plans.

For [stage-1 Technic structures](technic.md), a geometry-fingerprinted registry supplies reviewed `technic:` ports in place of raw mechanical inferences. Pin grips, mixed connector ends, keyed axles and round-hole bearings use seating and occupied-span checks. Invalid seating blocks application. Existing stud/clip/wheel behavior remains available; unsupported Technic interfaces need review and curation.

## Configuration and coverage

```sh
./ldraw-agent doctor
./ldraw-agent part 3001 --limit 40
./ldraw-agent --no-shadow part 3001
./ldraw-agent --shadow ./data/offLibShadow --shadow ./my-shadow part 3001
```

`get_parts()` uses `LDRAW_SHADOW` (paths separated by the platform path separator) when set, otherwise the repository's `data/offLibShadow/` if present. Explicit repeated `--shadow` arguments replace those defaults and preserve registration order; later sources can clear or replace earlier features. `--no-shadow` or Python `get_parts(shadows=[])` disables external shadows. Inline part metadata remains active. Directories, ZIPs and CSLs are supported; an explicit missing or invalid path fails. `doctor.shadow_sources` lists the selected paths. The original library and shadow files are read only.

`part.connection_metadata` and each inspection instance's `connection_metadata` expose coverage, source and record counts, and parsing diagnostics. `complete` means metadata was consumed without reported gaps, including an intentional clear-to-empty result. It does not mean every physical connection has been modeled. `partial` and `none` distinguish weaker evidence; unsupported or invalid commands remain visible. Geometry completeness and connection coverage are separate fields.

## Discover and preview

```sh
./ldraw-agent inspect output/shadow-snap.mpd --limit 20
./ldraw-agent connectors output/shadow-snap.mpd --occurrence 1 --limit 20
./ldraw-agent snap output/shadow-snap.mpd --moving 1 --fixed 0 --limit 5
```

Use the same `--section` and `--colour` selection for all three commands. Occurrence indices identify physical leaves, including embedded DATs; `placement_path` identifies type-1 placement ordinals from root to leaf. Source line paths remain available in inspection reports. `connectors` returns original world-space frames, profiles, stable `feature_id`, source/provenance, native occupancy and observed contacts. `mating_kind` / `mating_source` identify the interpretation used by the adapter described below. Pagination uses `--offset` and `--limit`.

`snap --moving N` searches all stationary leaves; `--fixed M` narrows the search. `--moving-feature ID` and `--fixed-feature ID` select exact connector IDs from `connectors`. Quote IDs as shell arguments. Indices and feature IDs are scoped to the current model/library revision.

Each distinct candidate includes:

- `position` / `matrix`: the selected moving leaf's resulting world pose.
- `delta`: the rigid world transform applied to all `moving_instances`.
- `local_placement`: `ref`, `at`, and `matrix` for the actual part/submodel reference being moved, already converted through the parent inverse.
- Original moving/fixed features, `residual_before`, verified `contact_status`, and a bounded collision report against stationary parts.

By default only the leaf moves. `--moving-depth 0` moves its outermost placement as a rigid submodel; depth 1 moves the next reference along its path, and so on. Choose a leaf containing the intended mating interface. All descendants of the selected ancestor move together, and all are checked against the stationary scene. Existing contacts within that submodel remain occupied. Fixed connectors used by stationary parts are excluded; cross-boundary contacts of the moving object can detach. `--allow-occupied` explicitly permits reuse, for example multiple clips on a long bar, and still runs collision checks.

Reviewed Technic shafts reserve engaged intervals instead of their entire feature. Separate bushes or supports can share an axle when their intervals do not overlap. `--allow-occupied` cannot bypass conflicting occupation of a reviewed hole/span. Read `collision.interface_errors` as well as the ordinary body-overlap report. Thin layers sharing a pin grip must complete its retaining seat; move them as an assembled module when a single layer would leave an incomplete grip.

Candidates are ordered by body-collision status, unresolved overlap count, contact confidence, then leaf translation distance. Free roll is preserved; the search does not enumerate every hinge angle, roll or sliding position. `--max-candidates` defaults to 100 distinct poses to check; `--limit` defaults to five returned candidates. Read `search_truncated`, `candidates_truncated`, `checked_candidates`, and rejection counts. Searches exceeding 100,000 feature pairs fail with a scoping suggestion. `--max-instances` bounds model expansion. No eligible verified candidates returns exit 1; invalid selectors return structured JSON and exit 2.

## Apply to an MPD copy

```sh
./ldraw-agent snap output/shadow-snap.mpd --moving 1 --fixed 0 \
  --moving-depth 0 --candidate 0 --output output/repositioned.mpd
```

The output must differ from the input. `--force` permits replacing an existing output after successful checks. Candidate indices are zero-based within the returned list. The tool refuses a candidate with a detected body overlap, validates the serialized result and checks the complete resulting assembly before writing atomically. General overlap review warnings can remain: read the candidate's collision report and final geometry diagnostics. With `--section`, the output contains the selected dependency closure, including its preview wrapper when `--colour` was supplied.

Editing a nested leaf clones the section ancestors on that occurrence's path as needed, preserving their headers and other placements. Other instances of a shared section keep their original poses. Python `apply_snap(model, report, candidate=0)` returns a copy and rejects reports from another model revision; callers must validate and review that copy before writing it.

## Reproducible plans

Build the supplied example:

```sh
./ldraw-agent build examples/shadow-snap.plan.json --output output/shadow-snap.mpd
```

Use `snap` as the fourth placement mode alongside `at`, `on`, and `attach`:

```json
{"id":"cap", "ref":"cap.ldr", "colour":1,
 "snap":{"to":"base", "near":[0,-8,0], "moving_leaf":0, "fixed_leaf":0}}
```

`to` names an earlier placement in the same section. `near` is an initial position in that section's coordinates and guides ranking; it defaults to the support's position. Optional `yaw` or `matrix` supplies the initial orientation. The solver determines the final pose. `moving_leaf` and `fixed_leaf` default to zero and select physical leaves within the moving and supporting references. Both can refer to complete submodels; the entire moving reference is repositioned rigidly. Modules are built in dependency order, while the first declared section remains the MPD root.

Optional `moving_feature`, `fixed_feature`, and `candidate` make interface selection explicit. A plan snap checks up to 100 distinct candidates. It fails for absent interfaces, invalid leaf indices or a selected body collision. `snap` cannot coexist with `at`, `on`, `attach`, `offset_studs`, or `repeat`. Ordinary plan validation still applies. Keep edits in the plan when rebuilding generated models.

Python entry points are `connection_report`, `snap_report`, and `apply_snap` in `ldraw_tools.connectivity`. The existing `ldraw_tools.geometry.snap` remains a list-returning convenience wrapper; use `snap_report` to retain coverage and search-limit information.

## Collision interpretation

Shadow data describes mating interfaces, not complete solid volumes. Inspection uses resolved pyldraw3 geometry for AABBs, a 15-axis separating-axis test for oriented bounds, and curated rectangular brick/plate body envelopes in arbitrary rigid orientations. Submodels expand to physical leaves for all these checks.

| Result | Meaning |
|---|---|
| `rectangular_body_overlap` | Curated body envelopes penetrate beyond 0.00001 LDU. An assembly error; a matching connector never cancels it. |
| `oriented_bounds_separated` | AABB overlap was eliminated by oriented boxes. |
| `stud_zone_overlap_review_connections` | Body envelopes are separate; stud-inclusive bounds overlap. Check reported connection evidence. |
| `review_oriented_bounds` / `review_aabb_only` | Remaining envelope overlap requires material review, particularly for hollow or irregular parts. |

A snap's aggregate status is `blocked`, `review_required`, or `no_collision_found`. The last means no collision was found by these checks; `physical_validity` remains `not_proven`. General material intersection, containment, legal articulation, insertion clearance, strength and stability still require further review. Internal relationships of a rigidly moved module are unchanged during candidate checks; the CLI checks the full model before writing.

## pyldraw3 1.7 compatibility notes and sources

The [API reference](https://hbmartin.github.io/pyldraw3/api/), [local README](../pyldraw3-README.md), [LDCad shadow guide](../LDCad-Shadow-library.pdf), and [LDCad meta reference](../LDCad-metas.pdf) describe metadata loading, profiles, source precedence, contacts and rigid snapping. The supplied shadow's [license](../../data/offLibShadow/LICENSE.md) remains with its source files.

The installed version's generic snap solver aligns connector axes, while its strict stud contact check expects opposing axes. LDCad female cylinders point inward; inferred primitive sockets point outward. `connection_adapter.py` adapts temporary query frames for these two calls, retaining the original reported frames and IDs. Regression tests include ordinary and sideways stacking.

The supplied library also describes some brick/slope undersides as closed square cavities of radius 6 LDU. pyldraw3 1.7 classifies longer examples as pin holes and rejects their round-stud pairing. A narrow query-only projection models an inscribed round stud for these sockets, marks it **potential / heuristic** evidence, and retains the original square profile in reports. Other square, axle, pin and generic interfaces keep pyldraw3's compatibility rules. Retest these adaptations when updating the dependency pin; do not interpret complete metadata coverage as complete solver support.
