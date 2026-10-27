# Build and review an LDraw model

Deliver reproducible source, an editable MPD, checks, matching BOMs and inspected
previews. Keep new work in `output/`. Use one loop: **edit the plan → review →
open the images → repair**.

## 1. Choose a starter

Run `./ldraw-agent doctor`. Use `./setup.sh` if needed, adding `--with-lsynth` for
flexible parts. Set `LDRAW_DIR` to the installed library; LeoCAD supplies previews.
Write down the requested silhouette, dimensions, palette and working features.

```sh
./ldraw-agent examples --family technic
./ldraw-agent part 3700
```

Choose the matching family: `building`, `vehicle`, `spaceship`, `technic` or
`mechanism`. For a frame, retained drive, pneumatic station or complete machine,
copy a [workshop starter](examples/workshop/README.md). Its ordinary JSON plan
includes supports, named joint checks and routes. Start with the smallest useful
assembly, preserving its documented mechanical dimensions.

**Spaceships use SNOT by default.** Follow the [Halcyon](examples/snot/halcyon/README.md):
a supported core, attached sideways skins, axial engines, smooth contours and
thin wing edges. Adapt its construction to the requested silhouette and scale.

## 2. Assemble supports

Edit the JSON plan. Use placement IDs such as `conveyor/drive-axle` to name parts
inside modules; keep required joints beside the section's geometry. Names survive
reordering. Include only intended joints, not every observed contact. Keep
`scope: joints` on moving assemblies in a static pose; fixed frames retain their
rigidity contracts. Preserve required axial stops and insertion STEPs.

```sh
cp examples/workshop/workshop/model.plan.json output/machine.plan.json
./ldraw-agent review output/machine.plan.json --section chain-drive.ldr --no-render
```

A scoped review checks that section and its dependencies; it excludes surrounding
interfaces. Use it to repair locally, then review the complete assembly.

Negative Y is up. Stud pitch is 20 LDU; brick and plate bodies are 24 and 8 LDU
high. Prefer `on` for upright stacking. Inspect real part origins and interfaces;
bounding-box height is not stacking height. Use proper rotations, never stretched
or reflected rigid parts. Colour 16 needs an explicit ancestor; 24 is for edges.

## 3. Route services

Place actual fittings or supported wheels first. Add a flex placement in the
same plan STEP with its own ID, explicit colour, and named endpoints:

```json
{"id":"supply", "colour":0, "flex":{
  "method":"TECHNIC_PNEUMATIC_HOSE_BEVELED",
  "from":{"part":"controls/pump", "port":"outlet", "lead":22},
  "to":{"part":"controls/valve", "port":"inlet", "lead":22},
  "checks":{"min_radius":15, "tube_radius":5, "min_separation":10}
}}
```

Those limits belong to the pneumatic starter, not every material. `part PART`
lists measured nozzle names. Moving or rotating a fitting updates its endpoint;
edit `via` only when the passage needs repair. Closed routes use existing wheels,
for example `"wheels":["drive-gear","idler-gear"]`. Routing copies are hidden.

Read [named authoring](docs/agent/authoring.md) for fields, diagnostics and supported
parts. It links to deeper family details. Existing external `.ldr` constraints,
prebuilt assets and Python helpers remain available. Python is useful for loops
or calculations; it should emit the same plans. Use LSynth for curves and the
existing pyldraw3 builder/parser; do not invent another solver or checking script.

## 4. Add bodywork

Attach System bodywork to actual studs, sockets or reviewed mounts. Reserve room
for bearings, retaining bushes, fitting sleeves and hose passages. Bond seams,
keep interfaces accessible, and inspect the underside and rear. Change colour,
shape and equipment arrangement to suit the brief without silently substituting
unsupported mechanical parts.

## 5. Review and deliver

```sh
./ldraw-agent review output/machine.plan.json --views home front back top bottom
```

Review builds the plan, checks declared joints and actual synthesized geometry,
measures inline route interactions, writes the BOM, renders with LeoCAD and
compares its BOM. Read `review.json` and `validation.json`, then **open the images**.
Failures identify the stage, source and named placement when available. Fix the
first failed prerequisite. Inspect warned obstacles in context; fitting bounding
boxes include empty space. After two unsuccessful corrections, isolate the
module or route and reconsider its available space while retaining the checks.

Rerun with `--force` after edits. Intermediate `--no-render` or `--section` results
are incomplete delivery evidence. Finish with a rendered whole-model review and
fresh image inspection. Exit 0 means selected checks passed; 1 means failed checks
or mismatching BOMs; 2 means input, dependency or execution failure. Contacts skip
automatically above 500 placements: review modules or use `--contacts all`.
Source-derived mechanism studies use their documented `--contacts none` scope.

Keep visual notes beside the source, outside generated review folders. Record
images opened, defects repaired and unresolved limits. Deliver source, MPD,
review/validation, asset manifests, BOMs, previews and notes from the final
revision. Checks do not prove physical strength, manufactured hose length,
complete collision freedom or general motion correctness. For semantic GLB
handoff, use `./prepare-glb.sh --file MODEL.mpd MODEL.glb`.

## References when needed

- [Plan format](docs/agent/plans.md), [modules](docs/agent/complex-models.md),
  [snapping](docs/agent/snapping.md), [geometry](docs/agent/geometry.md).
- [Visual design](docs/agent/visual-design.md), [SNOT](docs/agent/snot.md),
  [vehicles](docs/agent/vehicles.md), [spaceships](docs/agent/spaceships.md).
- [Technic details](docs/agent/technic.md), [design patterns](docs/agent/technic-design.md),
  [mechanisms](docs/agent/mechanisms.md), [advanced mechanisms](docs/agent/advanced-mechanisms.md),
  [parts catalog](docs/agent/technic-catalog.md), [flex families](docs/agent/flex-constraints.md).
- [Validation](docs/agent/validation.md), [CLI options](docs/agent/tooling.md),
  [build-step views](docs/agent/build-manuals.md), [LDraw reference](docs/agent/ldraw-reference.md).
- [Discovery](docs/agent/reference-discovery.md): check Jev availability once;
  if unavailable, report why and use FTS/catalogs/examples. Preserve attribution
  and extraction manifests. Search the local specification with `spec QUERY`.
