---
name: connectors-and-snapping
description: 'Connector evidence and snapping: LDCad shadow-library connectors loaded through pyldraw3, discovering and previewing connector IDs and occupancy, snap and connectors commands, applying a snap to an MPD copy, interpreting collisions, and measured wheel assemblies. Use when a placement needs a connector that on, under or join do not cover, or when diagnosing why parts do or do not connect.'
---

# Connectors and snapping

Inspect connector evidence on placed parts and move a part or whole submodel onto a real connector when `on`, `under` and `join` do not cover the interface (hinges, clips, wheels, bars). The toolkit loads the LDCad shadow library in `data/offLibShadow/` automatically through pyldraw3. In a plan, the same search is the `snap` position mode ([write-plans](../../write-plans/SKILL.md)).

## Configuration and coverage

```sh
./ldraw-agent doctor
./ldraw-agent part 3001 --limit 40
./ldraw-agent --no-shadow part 3001
./ldraw-agent --shadow ./data/offLibShadow --shadow ./my-shadow part 3001
```

- Default shadows: `LDRAW_SHADOW` (platform path separator) if set, else `data/offLibShadow/`. Repeated `--shadow` replaces the defaults in order (later sources can clear or replace features); `--no-shadow` or Python `get_parts(shadows=[])` disables them. Directories, ZIPs and CSLs work; a missing path fails. `doctor.shadow_sources` lists the selection.
- `connection_metadata` (on `part` and each inspected instance) reports coverage, sources, record counts and parse diagnostics. `complete` means metadata was consumed without gaps, **not** that every physical connection is modelled; `partial` and `none` mark weaker evidence.
- Reviewed Technic ports (`technic:`) replace raw inferences for Technic structures ([ports-and-contracts](../../technic/ports-and-contracts/SKILL.md)).

## Discover and preview

```sh
./ldraw-agent inspect output/shadow-snap.mpd --limit 20
./ldraw-agent connectors output/shadow-snap.mpd --occurrence 1 --limit 20
./ldraw-agent snap output/shadow-snap.mpd --moving 1 --fixed 0 --limit 5
```

Use the same `--section`/`--colour` selection for all three. Occurrence indices identify physical leaves (including embedded DATs); `placement_path` gives type-1 ordinals from root to leaf. `connectors` returns world frames, profiles, stable `feature_id`, provenance, occupancy, observed contacts and `mating_kind`/`mating_source`.

| `snap` option | Meaning |
|---|---|
| `--moving N` (required) | occurrence to move |
| `--fixed M` | narrow the search to one stationary leaf (omitted: all) |
| `--moving-feature ID`, `--fixed-feature ID` | exact connector IDs from `connectors` (quote them) |
| `--moving-depth D` | move an ancestor: 0 = outermost placement as a rigid submodel, 1 = next along the path; omitted moves the leaf |
| `--allow-occupied` | deliberately reuse occupied interfaces (several clips on one bar); collisions still checked |
| `--max-candidates` | distinct poses checked (default 100) |
| `--limit` | candidates returned (default 5) |
| `--candidate K`, `--output FILE`, `--force` | apply a candidate to a new MPD |

Each candidate gives `position`/`matrix` (the moving leaf's world pose), `delta` (rigid transform applied to all `moving_instances`), `local_placement` (`ref`, `at`, `matrix` for the moved reference in its parent frame), original features, `residual_before`, `contact_status` and a collision report against stationary parts.

- Candidates are ordered by body-collision status, unresolved overlaps, contact confidence, then translation distance. Free roll is preserved; the search does not enumerate every hinge angle, roll or slide.
- Read `search_truncated`, `candidates_truncated`, `checked_candidates` and rejection counts. Searches over 100,000 feature pairs fail with a scoping suggestion.
- No eligible verified candidate → exit 1; invalid selectors → structured JSON and exit 2.
- Reviewed Technic shafts reserve engaged intervals; `--allow-occupied` cannot bypass conflicting occupation of a reviewed hole/span. Read `collision.interface_errors` too.
- Indices and feature IDs are scoped to the current model/library revision.

## Apply to an MPD copy

```sh
./ldraw-agent snap output/shadow-snap.mpd --moving 1 --fixed 0 \
  --moving-depth 0 --candidate 0 --output output/repositioned.mpd
```

The output must differ from the input. The tool refuses candidates with a body overlap, validates the serialized result and checks the whole assembly before writing atomically. Editing a nested leaf clones the section ancestors on its path; other instances of a shared section keep their poses. Python: `connection_report`, `snap_report`, `apply_snap(model, report, candidate=0)` in `ldraw_tools.connectivity` (validate the returned copy before writing). Prefer recording the snap in the plan so rebuilds keep it:

```json
{"id":"cap", "ref":"cap.ldr", "colour":1,
 "snap":{"to":"base", "near":[0,-8,0], "moving_leaf":0, "fixed_leaf":0}}
```

Workflow for hinges, axles, wheels and clips: inspect both parts' connector frames and occupancy → put them in a small test MPD → `inspect` for occurrence indices → `connectors --occurrence N` for feature IDs → `snap` → review collisions, apply, rerun assembly checks.

## Collision interpretation

Shadow data describes mating interfaces, not solid volumes. Checks use AABBs, a 15-axis separating-axis test for oriented bounds, and curated rectangular brick/plate envelopes.

| Result | Meaning |
|---|---|
| `rectangular_body_overlap` | Curated body envelopes penetrate beyond 0.00001 LDU. An assembly error; a matching connector never cancels it. |
| `oriented_bounds_separated` | AABB overlap was eliminated by oriented boxes. |
| `stud_zone_overlap_review_connections` | Body envelopes are separate; stud-inclusive bounds overlap. Check reported connection evidence. |
| `review_oriented_bounds` / `review_aabb_only` | Remaining envelope overlap requires material review, particularly for hollow or irregular parts. |

A snap's status is `blocked`, `review_required` or `no_collision_found`; the last still leaves `physical_validity: not_proven`. Material intersection, legal articulation, insertion clearance, strength and stability need review.

## Adapter notes (pyldraw3 1.7)

- The generic snap solver aligns connector axes while the strict stud check expects opposing axes; `connection_adapter.py` adapts temporary query frames and keeps the reported frames and IDs.
- Some brick/slope undersides are closed square cavities of radius 6; a query-only projection models an inscribed round stud for them, marked **potential / heuristic**.
- Deep round underside sockets of `22885`/`67329` (R 6, length 36) and `47457` (R 6, length 12) are projected to potential stud receptacles. Other recessed sockets can still be missed. Retest these adaptations when the dependency pin changes.

## Measured wheel assemblies

`ldraw_tools.vehicles.axle()` places tyres and rims as separate physical leaves:

| Package | Holder / rim / tyre | Actual tyre envelope | Interface |
|---|---|---|---|
| `classic` | 4600 / 4624 / 3641 | Diameter 36, width 16 LDU; track 60 | Co-located rim/tyre from `4624c01`; holder pins at local Y=5, stud body plane Y=0 |
| `touring` | 6157 / 6014b / 6015 | Diameter approximately 50, width 28 LDU; track 92 | Tyre at rim-local Z=-6 from `6014bc01`; holder pins at local Y=5, stud body plane Y=8 |

Touring on the road: holder origin Y=-30, wheel axis Y=-25, holder stud plane Y=-22, first plate top Y=-30, second plate Y=-38; fenders at Y=-62, X=±20, facing out. `vehicle wheels` reports current installed bounds; changing the wheel package requires rechecking the whole chassis and body.

## Source docs

Verbatim copies, for details not covered above:

- [docs/agent/reference/connections.md](references/docs-agent-reference-connections.md)
