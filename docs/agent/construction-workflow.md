# Compose freely; establish construction before repetition

Use this workflow for large models. The [Willow Quay experiment and construction-reuse study](../reports/construction-led-evolution.md) explain why a long list of design and checking instructions is insufficient on its own.

The designer chooses the subject, silhouette, proportions, façade rhythm, palette and character. The construction work must establish that those choices have plausible assemblies before they are repeated across a large model. A custom generator, the kit and explicit plans are all valid. No whole-model template is required.

## 1. Make the composition worth building

Use master's visual references and detail vocabulary. Render a small number of substantially different massing options when the brief is open-ended; select on appearance and feature relationships. Keep early studies cheap. A large part count is a scale constraint, never a design objective or a substitute for detail.

Record the important spatial relationships in the [design brief](design-brief.md): entrances and circulation, canopy coverage and headroom, openings, roof and chimney relationships, floor access, and the focal feature. Appearance remains an acceptance criterion throughout engineering.

## 2. Establish one example of each risky construction

Before repeating a wall, storey or roof arrangement, build a representative assembly with its actual support and neighbouring parts. For a building this normally includes:

- Foundation and wall corner, including plate bonds and matching stud grids.
- Window or door bay with fitted insert, complete opening, sill and lintel.
- Storey-to-storey interface and stairwell where required.
- Roof edge/ridge, roof supports, dormer opening and chimney penetration where required.

Study useful constructions from reference models or existing examples, then verify their fit in the new context. Preserve attribution. Prefer reusing a small construction whose internal spacing is already understood. Keep novel construction possible: isolate it, render it, check it, and establish its interfaces before repeating it.

A building envelope should record origin, occupied volume, actual connection surfaces, reserved voids, floor heights and build order. Reserve a window's entire required opening; testing whether a wall brick's **centre** falls inside a gap is insufficient. Never use a bounding-box maximum as evidence of an attachment surface.

Run `check` on these assemblies and inspect the reported pairs. View front, side and unfinished construction views. Do not replicate unresolved structural errors. An unsupported roof prototype should be repaired while it is one roof section, before it becomes a complete building.

Start with `./ldraw-agent construction list` to see the first three supported constructions: a bonded floor, a glazed bay with two cornice styles, and a supported entrance canopy. `construction export NAME --outdir DIR` writes editable MPD/plan source, exact parameter ranges, mounting coordinates, reserved spaces, feature requirements, part-source hashes and check reports. These are small construction studies, not a complete architectural vocabulary. Extend a study when the design needs a new technique; do not constrain the composition to these three choices. See [construction tools and stage review](tooling.md#construction-studies-and-stage-review).

## 3. Reuse the construction, vary the architecture

Build repetition with deterministic code. Preserve its stud pitch, plate heights, bond pattern, reserved openings and internal relative transforms. Vary supported dimensions and layouts; never scale real parts. Record the dimension/part combinations actually checked. A sample passing at one width does not establish every parameter value.

Composition remains open: vary setbacks, heights, bay spacing, roof masses, material roles, and the balance of quiet and detailed surfaces. Reusing a glazed bay does not require repeating an entire house. When a new feature needs another construction, establish that construction as another small study.

For a delegated builder, give a bounded module, selected construction references, its parent interface and retained feature requirements. Ask for the edited source, checks and views of that module. Expand after reviewing its construction and appearance. Do not ask one long generation pass to invent and validate thousands of unrelated placements.

## 4. Check the joins and preserve review evidence

Check each new module **in its parent context**, then check the full assembly. Two valid modules can collide, miss each other's studs, block a doorway or create an inaccessible floor when combined. Render the affected joins after changes.

Keep three distinctions explicit:

- A confirmed placement error needs a repair in the generator or plan.
- An exact part fitting corroborated by a reference needs narrowly scoped evidence: part identities, relative pose, source hash, viewed construction and checker limitation.
- An unresolved fitting stays unresolved. A similar part name, broad family exception or attractive render is insufficient.

The [Copper Lane evidence script](../../examples/construction-studies/copper-lane/evidence.py) records the original findings and reference poses. The checker now has four narrowly calibrated [fitting rules](../../ldraw_tools/data/fittings.json): exact part identities, full DAT dependency hashes and relative transforms must match. Reports retain their rule IDs, reference records and measured mesh overlaps. They do not exempt collisions with neighbouring bricks, duplicate panes, shifted inserts or unknown part revisions. Other unresolved fits retain their original verdict. The original study reports are historical evidence and remain unchanged.

Verify negative cases as the construction vocabulary grows: shifted inserts, missing roof supports, incorrect stud-grid offsets and occupied openings must still be rejected. Avoid teaching a checker to accept a whole part family just to clear one legitimate fitting.

## 5. Finish the exact revision

For System construction stages and final delivery, use `stage prepare SOURCE --outdir STAGE` with `--requirements FILE` for retained measurable features. It accepts a JSON plan or an MPD produced by the kit, a custom Python generator or another authoring tool. Generate Python output first. Preparation always checks the snapshot and compares its rendered BOM; failed drafts remain available for inspection. Open every requested view, record `stage review`, then use `stage export` to deliver that exact revision. Changed sources, includes, requirements, parts, checking code or evidence require preparing and reviewing again. A failed export preserves an existing delivery.

This gate enforces its own export route; it cannot prevent an agent from writing a raw MPD elsewhere. A legacy `build` result alone is not final stage evidence. Keep the existing subject-specific checks, including the separately scoped mechanism workflow. A manual assembly trial, inventory check or assembly-order review provides evidence the static checker cannot supply. Visual review is a recorded judgment, not an automated beauty score.

For timing, separate original design, construction research/implementation, deterministic generation, checking, rendering and repairs. Fast regeneration of an established construction is useful; it is not a measurement of how quickly an agent can invent that construction.
