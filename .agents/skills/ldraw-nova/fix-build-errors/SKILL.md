---
name: fix-build-errors
description: 'Reads and acts on build, review and validate diagnostics: checks_passed, errors with their placement paths, warnings by code, next. Lists the fix for each code (plan.schema, plan.authoring, assembly.body_overlap, assembly.duplicate, assembly.floating_group, assembly.became_floating, appearance.deep_overlap, appearance.exposed_side_studs, appearance.glass_obstructed, part.alias_or_internal, technic.*, coverage.*) and what validation does and does not cover. Use when a build fails or prints warnings, or when deciding whether a geometry report proves anything.'
---

# Fix build errors

Read the summary that `build`, `review` and `validate` print and turn each diagnostic into a concrete change to the plan. Also: what the checks cover and what a pass does not prove. The overall build loop is in the root [ldraw-nova](../SKILL.md) skill.

## Read the summary

Every run prints:

- `checks_passed`;
- `errors`, each with the placement paths it concerns in `at`;
- `warnings`, grouped by code with example placements;
- `next`, the step to take.

**Fix the first error, rebuild and repeat.** `--quiet` prints one line; `--report FILE` saves the complete report. A failed `build` writes `NAME.draft.mpd` beside the plan (keeping any earlier `NAME.mpd`), and `review --draft` renders the failing model so you can see the problem. `review --no-render` runs checks only; `--section NAME` checks one module's dependency closure.

If two repairs of the same interface fail, rebuild that interface alone in a small plan, check it, then put it back.

## Fix by code (plan builds)

| Code | What to do |
|---|---|
| `plan.schema` | Fix the field at `pointer`; `example` shows a valid value. |
| `plan.authoring` | A placement could not be built. The message names it and lists the faces, studs, sockets or Technic ports that exist; a failed Technic seat names the fit rule. |
| `assembly.body_overlap` | Two bricks or plates share space. Move the second placement by `separation` (the first by the opposite), or rebuild the joint. |
| `assembly.duplicate` | The same part twice in one place: delete one. |
| `assembly.floating_group` | These placements touch nothing in the main model. `gap` is how far their box is from the nearest main part, named in `nearest`; seat them on studs. When it says the parts have no connector data, check the render instead. |
| `assembly.became_floating` | Your last edit disconnected these placements. Restore their support rather than deleting them. |
| `appearance.deep_overlap` | Two parts are probably inside each other. Look at a close-up, then move one. |
| `appearance.exposed_side_studs` | Bare sideways studs show. Cover them with tiles unless they are intended. |
| `appearance.glass_obstructed` | A part sits right behind or in front of a window pane, so the window looks blocked. |
| `part.alias_or_internal` | The part number has moved: use `replacement`. |
| `technic.*` | A Technic rule failed: see the fix table in [technic](../technic/SKILL.md). |
| `coverage.*` | Something a check could not cover. Not an error, but look at those parts in the images. |

Warnings do not fail a build. Every `appearance.*` and `assembly.*` warning still names parts a person will notice: check them in the render before delivering ([review-and-deliver](../review-and-deliver/SKILL.md)).

## Fix by family (MPD and lower-level validation)

| Diagnostic family | Action |
|---|---|
| `syntax.*`, `parse.*`, `number.*` | Go to the indicated source line. Rebuild the record with all fields; replace nonfinite coordinates; remove prose from operational records. |
| `model.unknown_part`, `mpd.unresolved_submodel` | Search the real library ([find-constructions-and-parts](../find-constructions-and-parts/SKILL.md)); match the exact FILE name and include transitive submodels. Never invent an ID. |
| `mpd.cycle`, `mpd.duplicate_section`, `mpd.library_shadow` | Unique assembly names, acyclic references, main block first, no library filenames. |
| `matrix.singular`, `assembly.nonrigid` | Recompute a proper rotation (`orient`, `matrix`). Do not "repair" a mirrored part via colour or BFC. |
| `colour.*`, `model.unknown_colour` | Use a real palette code (`colours QUERY`); give the root an explicit colour instead of 16. Colour 24 is for edges. |
| `geometry.*` | Fix the primitive geometry or unresolved dependency. Incomplete bounds/contacts cannot justify a pass. |
| `assembly.body_overlap`, `assembly.duplicate` | `separation` is the shortest translation moving the second body out; recalculate position, origin or stacking height (body height, not bounds), or rebuild the joint. |
| `assembly.disconnected_evidence`, `assembly.floating_group` | Up to five placements, the nearest main part and the `gap`. Check stud parity, upper-body height, mating axes and missing metadata (`connector_data: false`). Explain intentionally separate objects in delivery notes. Never hide the diagnostic. |
| `coverage.contacts_skipped` | Select a module and compute contacts, or request `--contacts all`. Skipped analysis gives no connectivity conclusion. |
| `coverage.*` | Simplify to the supported construction, or perform and document the missing checks. |
| `header.*`, `mpd.unreachable`, `part.alias_or_internal` | Add accurate headers, remove unused assemblies, inspect the alias/replacement; keep original attribution. |

If a complex connection stays uncertain, replace it with a simpler inspected assembly and rerun. If it cannot be resolved, deliver it as a specific stated limitation; never claim the validator guarantees correctness.

## Appearance checks in detail

These use part bounds, vertices and connector positions, not images: confirm each in a close-up before changing the model.

| Warning | Rule |
|---|---|
| `appearance.deep_overlap` | Each part of a pair has at least two vertices more than 2 LDU inside the other's body (vertex box without stud cylinders). Excluded: recognised contacts, male-in-coaxial-female, glazing in frames, doors, hinge halves, figure parts, Technic pins and axles, tyres on wheels, flexible parts, foliage on foliage. A part inside a hollow shell can trip it. |
| `appearance.exposed_side_studs` | A sideways stud (radius 6, not up or down) with no mated part whose outward ray clears every other part's box for 400 LDU. |
| `appearance.glass_obstructed` | A transparent glass/pane/window/windscreen/door part with an opaque part covering half or more of either face within 16 LDU. Frames, seats, figures and enclosing shells do not count. |

## What validation covers, and what it does not

`checks_passed` means no reported errors in the selected profile; **it never means a model is proven buildable**. Every report says `physical_validity: not_proven`.

| Check | Boundary |
|---|---|
| Records, encoding, MPD structure | Types 0–5 field checks; UTF-8 without BOM (builder emits CRLF); first main block, case-insensitive duplicates, cycles, unresolved and unused sections. |
| Matrices | Physical placements need determinant > 0 and `M.T @ M` within 1e-4 of identity. No global grid restriction: SNOT and off-grid placements are legal. |
| Colours | Palette lookup and inheritance; edge colour rejected on parts. Real inventory availability not certified. |
| Duplicates | Same reference and world transform at 1e-6, across submodels, any colour. |
| Collision | Curated rectangular body envelopes in rigid orientations, AABB refined by oriented boxes. **No general material intersection proof.** |
| Connections | Typed connectors with shadows; confirmed/optimistic graphs. Auto mode computes contacts through 500 placements, then reports skipped coverage. |
| `!TEXMAP`, `!DATA`, `0 !:`, local `!COLOUR`, `CLEAR` | Explicit `coverage.*` errors; unsupported is not invalid LDraw. Use palette colours and real parts. |
| Technic | Invalid seating, incomplete grips, conflicting occupation; `technic check --contract` for mounts, retention, STEP order and restraint. No motion simulation, insertion access or strength. |

- `rectangular_body_overlap` is an error for curated bricks/plates. `review_oriented_bounds` / `review_aabb_only` pairs are candidates only (hollow parts overlap boxes without touching). `stud_zone_overlap_review_connections` is expected for correct stacks.
- `confirmed_components` / `optimistic_components` describe connector evidence, not real fit. Several groups can mean floating parts, missing metadata or deliberately separate objects: document which you verified. One group does not prove strength or stability.
- `--contacts none` records skipped connectivity, not acceptance. For mechanisms, scope rigidity contracts to stationary supports and use joint scope for moving mounts.
- Filenames with single spaces work; repeated spaces/tabs are flagged. Embed `.ldr` submodels rather than relying on loose external paths.

## Source docs

Verbatim copies, for details not covered above:

- [docs/agent/cards/checks.md](references/docs-agent-cards-checks.md)
- [docs/agent/reference/validation.md](references/docs-agent-reference-validation.md)
