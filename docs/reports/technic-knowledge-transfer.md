# Technic knowledge transfer from ldraw-mecha

Date: **2026-10-08**. Scope: reuse Technic construction knowledge from the
sibling's documentation and examples to improve model generation here.

## Delivered knowledge

- [Technic design guide](../agent/technic-design.md): function-led briefs,
  a pattern index, construction/review workflow and six new subject prompts.
- [Transmission patterns](../agent/technic-patterns/transmissions.md): parallel
  and bevel gearing, worm adjustment, differentials, Cardan shafts and selectors.
- [Engine patterns](../agent/technic-patterns/engines.md): actual W16 inventory,
  paired rods, repeated banks, source phase and cam followers.
- [Suspension and steering](../agent/technic-patterns/suspension-steering.md):
  measured interfaces, shocks, missing mounts and combined-corner design.
- [Lifts and linkages](../agent/technic-patterns/lifts-and-linkages.md): four-bar
  geometry, pawl/stepper limitations and surrounding construction.
- [Source reuse](../agent/technic-patterns/source-reuse.md): selection frames,
  occurrence identity, part boundaries, incomplete evidence and attribution.
- [Five worked studies](../../examples/technic-studies/README.md), three unchanged
  source previews, a 53-file provenance ledger and 21 retained report observations.

The main instructions, project README, Technic/mechanism guides and both existing
atlases now lead to this material. Existing commands, registries and atlas export
gates are unchanged. The design prompts are explicitly unbuilt ideas, while the
studies preserve the source's measurements and qualifications.

## Source selection and limits

Selected cases: 42083 W16, 42110 drivetrain/controls, standalone 42110 suspension,
42083 independent mechanisms, and the Technic parts of the 10265 discovery audit.
Minifigures, plants, general movable-object scenes, Blender lifecycle logic,
animation drivers and runtime code were outside this transfer.

The source revision was `a1182a3f87e323003b64fe79d4f32f040668a95d`, with local
changes affecting 21 of the selected files. The
[manifest](../../examples/technic-studies/sources.json) hashes the working-tree
bytes; it does not pretend the Git revision contains all those changes.

Particular qualifications preserved: W16 annotation versus actual inventory;
parallel double-bevel use; incomplete suspension supports; full-droop source pose;
animation-only spring scaling; approximate hub spin; assumed cam/selector laws;
static winch rope and pawl; fixed wing upper pivot; independent paddle/shift
controls; two reconstruction gears in the Chiron gearbox; unresolved Mustang
crank-to-frame contact. These remain local to their source cases.

## Checks performed for this transfer

- Matched all 53 source-file hashes and all 21 JSON-pointer observations against
  the retained sibling files. Checked the three copied PNGs are byte-identical.
- Confirmed that the local 42083, 42110 and 10265 B-model MPDs have identical
  bytes to their sibling counterparts; resolved the exact named source sections.
- Counted physical leaves using Nova/pyldraw3: W16 223 parts, including 16 pistons
  and 16 rods; standalone suspension 259; reconstructed gearbox 397.
- Exercised the documented W16 `mechanism prepare` command with `--no-render`
  in `output/technic-knowledge-transfer/w16-smoke`. Exit 0, source checks passed,
  223 physical placements, analytical verification deferred. A rendered BOM
  comparison and new manual visual review remain pending for that scratch study.
- Opened all three retained previews. They show the W16 cutaway, a suspension
  corner and the wing lift; their captions state the omitted structure/context.
- Checked local Markdown targets/anchors introduced by this change, JSON parsing
  and patch whitespace. [Check results](technic-knowledge-transfer.json) record
  the counts and actual coverage.

No new model, animation, mechanical solver or physical certification is claimed.
No motion/Blender checks were rerun, and the existing mechanism atlas was not
regenerated. This is a documentation and source-evidence change; no runtime code
changed, so application tests were not needed. The sibling project and supplied
resource data were read without modification.
