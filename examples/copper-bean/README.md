# The Copper Bean

Three storeys of apartments over a corner coffee shop, with three people having
coffee under a parasol on the pavement terrace outside. One 32x32 stud
baseplate, 1022 physical placements across 24 FILE blocks.

[Generated MPD](copper-bean.mpd) · [Plan](copper-bean.plan.json) ·
[Generator](generate.py) · [Design brief](design-brief.json) ·
[Visual review](visual-review.md)

[Validation](copper-bean.validation.json) ·
[Full-scene inspection](copper-bean.inspection.json) ·
[BOM](copper-bean.bom.json) · [BOM comparison](copper-bean.bom-comparison.json)

Previews: [home](review/home.png) · [front](review/front.png) ·
[left](review/left.png) · [back](review/back.png) · [top](review/top.png) ·
[terrace](terrace-review/front.png) · [shopfront](shop-review/front.png)

## Rebuild

```sh
.venv/bin/python output/copper-bean/generate.py
./ldraw-agent build output/copper-bean/copper-bean.plan.json \
  --output output/copper-bean/copper-bean.mpd --detail summary --force \
  --report output/copper-bean/copper-bean.build.json
./ldraw-agent validate output/copper-bean/copper-bean.mpd --geometry --detail summary \
  --report output/copper-bean/copper-bean.validation.json
./ldraw-agent inspect output/copper-bean/copper-bean.mpd --contacts all --detail summary \
  --report output/copper-bean/copper-bean.inspection.json
./ldraw-agent render output/copper-bean/copper-bean.mpd --outdir output/copper-bean/review \
  --views home front left back top
./ldraw-agent compare-bom output/copper-bean/copper-bean.mpd \
  --csv output/copper-bean/review/leocad-bom.csv \
  --report output/copper-bean/copper-bean.bom-comparison.json
./check-model.sh output/copper-bean/copper-bean.mpd
```

Edit `generate.py`, not the JSON plan or the MPD; regenerating overwrites both.

## Module contracts

Every module has bottom Y=0 and faces -Z. Storeys stack through `attach`, each
one's `base` anchor onto the anchor `roof` of the storey below.

| Module | Envelope | `roof` anchor | Notes |
|---|---|---:|---|
| `bean-shop.ldr` | 16 x 12 studs | h 208 | 8 brick courses; glazing in courses 0-5, sign band 6-7 |
| `bean-flat-one.ldr` | 16 x 12 | h 160 | three front windows; its cornice carries the balcony |
| `bean-flat-two.ldr` | 16 x 12 | h 160 | French door onto that balcony |
| `bean-roof.ldr` | 16 x 12 | — | parapet, tiled terrace, studded service bay |
| `bean-terrace.ldr` | 12 x 10 | — | local origin is the parasol mast axis |

The cornice at each storey head projects two studs at the front and one stud on
the flanks and rear. Every cornice plate keeps at least one stud row over the
wall head and is clamped by the deck of the storey above, so nothing in the ring
is a free cantilever.

## Geometry notes worth keeping

- **Minifigure stack.** Measured from this library's own connector frames, not
  copied from a model: legs 12 LDU below the hips origin, torso 32 above, head
  57 above. Seated, the legs take a proper -90 degree rotation about the figure's
  X axis; the hips underside and the rotated thigh underside then share one
  bearing plane 20.75 LDU below the hips origin, which is the chair seat.
- **Left arm.** `973c01` and a plain `3819` cannot be used here: `3819` is a
  mirrored reference to `3818`, its shadow connection frames are rejected under
  reflection, and the assembly profile then fails on incomplete geometry. The
  figures use `43368`/`43369` (arm with integral hand), which each carry their
  own geometry.
- **Parasol parity.** `958c01`'s stand grips studs at (±20, 0, ±10), which pins
  the mast to a stud centre in X and a stud line in Z. No symmetric square table
  can then be stud-supported around it; hence a five-by-four top on legs at
  (±40, ±30) LDU, the only corner positions outside the 60 LDU round stand.
- **`3039` sockets** sit half a stud off the part origin in Z. The awning course
  is at `z = -d/2 - 0.5`; at `-d/2 - 1` the slopes rest on the cornice without
  engaging any stud.

## What the checks cover

`checks_passed` is true for the assembly profile with geometry analysis, and
LeoCAD's BOM matches the Python BOM exactly at 1022 placements over 103 distinct
(reference, colour) entries. `physical_validity` stays `not_proven`; see
[visual-review.md](visual-review.md) for what was looked at and what was not.

Full-scene `--contacts all` gives 2868 contacts and 64 connected groups. One
group of 942 parts holds the whole building, street, terrace furniture and
planting. The other 63 are accounted for:

| Group | Count | Why it is separate |
|---|---:|---|
| `60608` window panes | 44 | clip into their window frames; no connector metadata for pane-in-frame |
| `57895` display glass | 2 | same, inside the `60596` shopfront frames |
| Minifigure bodies | 3 | figures are deliberately separate objects resting on their chairs |
| Minifigure arms / hair | 9 | `43368`, `43369` and hair parts carry no connector metadata |
| Lamp lanterns and finials | 4 | the shared `lamp()` module's `6141`/`4589` tops carry only pin frames |
| Table posy | 1 | `6141` under the flower has no stud frame in the shadow library |

No group is a construction defect: each one was traced to a specific part's
metadata or to an intentionally separate object.

## Limits

Contacts, overlaps and connector graphs are evidence, not a buildability proof.
No detailed material-intersection pass was run on this model. Retail
availability of any part in any of these colours is not claimed, and this is an
original design, not a recreation of any set.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "copper-bean",
    "title": "Copper bean",
    "scope": "construction",
    "kind": "assembly",
    "aliases": [
      "standalone:copper-bean"
    ],
    "families": [
      "building"
    ],
    "legacy_groups": [
      "examples"
    ],
    "lesson": "Three-storey composition: green cafe beneath two tan apartment shells, roof terrace and planted pavement. Correct README which says three apartment storeys above cafe; retain facade/scene assembly scope. Glazed green shop with striped awning. Additional top view confirms rear counter, very abstract block espresso prop, two round pedestal tables and four small stools; no stair/circulation route.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/standalone-audit.json",
    "model": "examples/copper-bean/copper-bean.mpd",
    "plan": "examples/copper-bean/copper-bean.plan.json",
    "generator": "examples/copper-bean/generate.py",
    "model_sha256": "5a4aa4f553f1c21c30972880b0af819b0863828d50688712986d601f7ff0a504",
    "audit_pointer": "/items/1",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/standalone-findings.md",
    "techniques": [],
    "subjects": [
      "architecture"
    ]
  }
]
```

## Audited section observations

These observations refer to the source hashes in the registrations. They correct earlier source descriptions and preserve static visual scope; existing numeric and export checks remain separate.

### Copper bean

| Source section | Opened-image observation |
|---|---|
| `copper-bean.ldr` | Three-storey composition: green cafe beneath two tan apartment shells, roof terrace and planted pavement. Correct README which says three apartment storeys above cafe; retain facade/scene assembly scope. |
| `bean-shop.ldr` | Glazed green shop with striped awning. Additional top view confirms rear counter, very abstract block espresso prop, two round pedestal tables and four small stools; no stair/circulation route. |
| `display4-15.ldr` | Tall white display frame with clear pane; two actual shop-front instances. Retain fitted glazing lesson with matching part IDs. |
| `door4-15-15-glazed.ldr` | White glazed panel door and knob; reviewed in shop front and second-flat front. These are actual instances of same fitted door. |
| `door4-15-70-traditional.ldr` | Brown traditional four-light door in white frame, on shop rear wall. Keep as door-in-frame variant. |
| `window4-15-47.ldr` | White four-pane glazing/window frame, repeated across shop and both flat walls. All three distinct parents inspected; one lesson with occurrences. |
| `bean-flat-one.ldr` | First tan upper-floor shell has flowered front balustrade and perimeter glazing; empty studded room, no furniture, partitions or stairs. Scope to facade and stacking. |
| `bean-flat-two.ldr` | Second tan upper-floor shell has front glazed door and perimeter windows; empty studded room, no furniture, partitions or stairs. Scope to facade and stacking. |
| `bean-roof.ldr` | Flat tiled rooftop with parapet, rectangular chimney/service block and flower box. No stair access shown; roof treatment lesson only. |
| `flower-box-4.ldr` | Four red flowers along green round stems behind tan curb; actual pavement and rooftop occurrences reviewed. Colour variant of shared planter. |
| `bean-terrace.ldr` | Outdoor cafe seating group: three seated figures around square table pierced by green parasol pole. Verify chair/figure/table heights as explicit interfaces; no full furniture family claim. |
| `cafe-table.ldr` | Square studded table with central opening and four round white legs; actual parasol passes through opening. Keep constrained furniture recipe. |
| `cafe-chair.ldr` | Block-built white chair with brown tiled seat/back cap. Three occurrences support seated figures; minimal prop, not exemplar of detailed furnishing. |
| `bean-guest-left.ldr` | Seated dark-red figure with brown hair and bent legs, installed at left side of terrace. Same minifigure assembly family as other guests. |
| `bean-guest-right.ldr` | Seated blue figure with ponytail and bent legs, installed at opposite terrace chair. Pose/colour/hair variant, not separate construction lesson. |
| `bean-guest-front.ldr` | Seated orange figure with tousled hair and bent legs, installed at third terrace chair. Pose/colour/hair variant. |
| `street-tree-288-5.ldr` | Stylized round-trunk foliage tree on flowered square base; green and pink top foliage. Shared tree recipe, colour variant. |
| `street-tree-2-14.ldr` | Same round-trunk tree form with green/yellow foliage and yellow base flowers, beside front lamp. Shared recipe variant. |
| `fluted-lamp.ldr` | Fluted dark street lamp with transparent yellow round lantern and cone cap, two pavement occurrences. Record connection-check limits. |
| `bench-70.ldr` | Simple brown bench with studded seat and back over two dark block feet; two pavement occurrences. Minimal prop scope. |
| `flower-box-14.ldr` | Four yellow flowers behind tan curb; two pavement occurrences. Same planter family as red and pink. |
| `street-tree-2-4.ldr` | Shared round-trunk tree with green/red foliage and red base flowers at rear corner. Colour variant. |
| `street-tree-288-14.ldr` | Shared round-trunk tree with muted-green/yellow foliage and yellow base flowers, opposite rear planting. Colour variant. |
| `flower-box-5.ldr` | Four pink flowers behind tan curb at rear pavement. Same planter family, colour variant. |
