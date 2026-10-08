# Build Technic structures

Stage 1 supports **static structural assemblies**: frames, chassis, supports, retained structural axles and mounts for System bodies. Stage 2 is now authorized through the [mechanism workflow](mechanisms.md): study source assemblies and build pages, then reuse or adapt them. Analytical mechanism verification is deferred at the user's request. Keep this guide's fixed-member contracts scoped to the stationary structure.

Use this guide with [instructions.md](../../instructions.md), the [Technic atlas](../../examples/technic-atlas/README.md) and the [research assessment](../reports/technic-structure-readiness.md). Keep the normal design, validation, BOM and visual review loop.

For more varied subjects and functional layouts, use the [Technic design guide](technic-design.md) and [Mecha construction studies](../../examples/technic-studies/README.md). They connect these fixed-frame techniques to engines, transmissions, suspension and lifts, including the real mounts that an isolated source study may omit.

The [Technic atlas mechanism studies](../../examples/technic-atlas/README.md#mechanisms-from-ldraw-mecha) provide six editable constructions with build pages and operation notes. Query `examples --family technic --limit 20` for both structures and mechanisms. Use their directory with `mechanism export`; fixed structural contracts apply to their supports only.

## Start from the structure and its mounting points

Record the silhouette, support/load direction, dimensions, palette and body attachment locations. Design the skeleton and visible body together; filling the body first can leave inaccessible joints.

```sh
./ldraw-agent technic list
./ldraw-agent technic parts 64179
./ldraw-agent technic parts 2780
./ldraw-agent examples --family technic
./ldraw-agent technic plan box-chassis --output output/chassis.plan.json
./ldraw-agent build output/chassis.plan.json --output output/chassis.mpd
./ldraw-agent validate output/chassis.mpd --geometry
./ldraw-agent technic check output/chassis.mpd \
  --contract output/chassis.plan.structure.json --report output/chassis.structure-review.json
./ldraw-agent render output/chassis.mpd --outdir output/chassis-review \
  --views home front back right left top bottom
./ldraw-agent compare-bom output/chassis.mpd --csv output/chassis-review/leocad-bom.csv
```

`technic plan` exports a normal assembly plan and a sibling `.structure.json` contract. Use `--force` to replace either. `--colour` and `--accent` change the palette; `--levels 1|2|3` changes the tower. [technic_recipes.py](../../ldraw_tools/technic_recipes.py) exposes placements and mounting pairs for adaptation. These constructions teach techniques; they do not limit the subjects an agent can build.

## Use measured ports and real lengths

The initial registry covers **34 definitions plus aliases**: common Technic bricks, straight beams, a thin beam, a rectangular frame, an axle/pin cross block, ordinary and long pins, axle-pins, a stud-ended half pin, axles and bushes. `technic parts` lists exact IDs, nominal ports, part roles and `geometry_matches`. Coordinates are **local LDU**.

Each entry fingerprints its expanded geometry. Changed or unreviewed definitions do not receive curated ports. Do not update a hash without measuring and reviewing the new part. Additional connector blocks, bent/flexible members, panels and hubs need interface curation before a strict structural contract can rely on them.

- Hole pitch is normally 20 LDU. Brick/plate body heights are 24/8. Two plates between studded Technic bricks produce a 40-LDU hole separation.
- Three beam holes span 40 LDU between their end centres. Solid bounds are not nominal placement dimensions.
- Sampled thick/thin beams are 20/10 LDU thick. Two thin layers can share a 20-LDU pin grip; one alone does not complete its retaining seat.
- Origins, axes and keyed roll vary. Use port frames and proper rotations. Never stretch or reflect a physical part to close a frame.
- Cross holes constrain axle roll; suitable round holes act as bearings. Neither establishes axial retention by itself.

Pins have separate grips; mixed connectors have separate pin and axle ends. Friction comes from reviewed part identity, not colour or LDCad's editor `slide` flag. This repository-owned registry remains active when external shadows are disabled.

## Seat the joints before closing the frame

```sh
./ldraw-agent connectors output/chassis.mpd --occurrence 0
./ldraw-agent snap output/chassis.mpd --moving 1 --fixed 0 --limit 5
```

Reviewed mechanical port IDs begin with `technic:`. `connectors`, `snap` and geometry inspection use them for supported geometry. `part` still exposes raw library metadata for comparison. Existing stud interfaces remain available; the half pin also supplies its missing System stud interface.

Snapping aligns a grip with its receiving bore, considers axial positions and preserves keyed orientation. Read `collision.status`, `interface_errors`, truncation and remaining review items. Blocked candidates cannot be applied. `--allow-occupied` cannot permit overlapping occupation of a reviewed hole or shaft span. Distinct axle intervals remain available for other members and bushes.

Normal `validate --geometry` and `inspect` report invalid seating, incomplete grips and conflicting occupation when contacts are computed. Large models still need module checks or explicit `--contacts all`; the normal automatic limit is 500 placements. General material intersections need the ordinary geometry checks and visual inspection too.

Insert pins into a supported member before bringing the closing member onto their exposed ends. Add shaft spacers and supports before installing the final retainer. Check both escape directions of a retaining stack. A correct final pose does not prove that the parts can be inserted with every surrounding member already present.

## Check intended joints and restraint

`technic check` defaults to 500 occurrences; select a module with `--section` or deliberately increase `--max-instances`. Occurrence indices and contracts belong to the same selection. Read coverage and warnings even when `checks_passed` is true.

A [structure contract](../../ldraw_tools/data/structure.schema.json) is a separate JSON file:

```json
{
  "version": 1,
  "require_rigid": true,
  "required_joints": [{"between": [1, 0]}, {"between": [1, 2]}],
  "assembly": [{"connector": 1, "before": [2]}]
}
```

Occurrence 1 must connect both members and appear in an earlier LDraw STEP than closing member 2. Generated contracts also bind to `model_sha256`. After changing or reordering a model, regenerate and review the contract; do not reuse stale indices or discard a revision mismatch. Hand-authored development contracts may omit the hash.

The checker reports receiving-hole engagement, thin-layer completion, duplicate occupation, missing mounts, unretained axles and bearings that still rotate. It checks connector-before-closure STEP constraints and groups members joined by at least two separated parallel pin axes. One pin remains a pivot; loops of such joints receive an unbraced-loop warning.

**This is a conservative restraint rule, not a general rigidity solver.** A valid diagonal truss or another pattern may require manual review or an additional reviewed recipe. `require_rigid` fails when the rule cannot join the structural members or their interfaces are unreviewed. Declare System body mounts individually too: one successful attachment cannot satisfy a four-point mounting design.

Swept insertion paths, hand access, arbitrary solid collisions, strength, stiffness, overturning stability and manufacturing tolerances remain outside the automated proof. Open hidden faces and the underside, review the build sequence, and report remaining physical checks.

## Find structural references and finish the appearance

First perform the [Jev availability check](reference-discovery.md#check-jev-availability-before-searching). When available:

```sh
./ldraw-agent discover search submodels 'a compact braced chassis frame' \
  --construction technic-structure --engine jev --limit 5
```

When unavailable, use `--engine fts`, the local catalogs and examples. Identify offline keyword ranking explicitly. The construction filter considers the selected description and actual BOM, excludes obvious mechanism contents, and allows static sections from mechanism-bearing parents. It does not prove every axle in a “chassis” is structural. Inspect parent support, mounting interfaces and build order; preserve attribution and extraction manifests.

Keep the skeleton's main lines clear, control its palette and reserve real mounts for panels or System cladding. Expose structure where it explains the subject; organize connector clutter elsewhere. Compare all seven views and a thumbnail. Fix proportions and unsupported mounts before adding decoration. Deliver the MPD, plan/generator, contract, checks, BOM comparison and visual review of the final revision.
