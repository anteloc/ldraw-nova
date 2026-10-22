# Flexible parts with LSynth

Use **lsynth-nova** to shape hoses, cables, strings, flexible axles, rubber bands and treads, or to lay out separate chain links. Keep the constraints as editable source, generate an MPD asset, then use the normal plan and review commands. The adapter uses the Python port's CLI; it does not implement another curve or belt solver.

## Install and try

Keep the `lsynth-nova` checkout beside this repository:

```sh
./setup.sh --with-lsynth
./ldraw-agent flex types
./ldraw-agent flex build examples/flex/hose.ldr --output output/flex/hose.mpd
./ldraw-agent review output/flex/hose.mpd --contacts none
```

Open the review's previews. [Small examples](../../examples/flex/README.md) cover a hose, a rubber band and a chain. Copy a constraint file into your own `output/` directory before editing it. `doctor` reports whether the optional package is installed. `LSYNTH_SOURCE=/path/to/lsynth-nova ./setup.sh --with-lsynth` accepts another checkout location. Ordinary setup and builds do not require LSynth; `uv sync` may remove this optional installation, so use the setup flag again afterward.

Only synthesis needs LSynth installed. Generated assets embed the required LSynth geometry and work with the ordinary LDraw library, including in LeoCAD. Do not run `lsynth --install-parts` for this workflow: the adapter leaves the parts library unchanged.

## Describe a path

A hose uses at least two visible constraints, in path order, inside an ordinary LDR or MPD:

```text
0 SYNTH BEGIN TECHNIC_PNEUMATIC_HOSE_BEVELED 4
1 4 -60 0 0 0 -1 0 1 0 0 0 0 1 LS01.dat
1 4 0 -40 0 0 -1 0 1 0 0 0 0 1 LS01.dat
1 4 60 0 0 0 -1 0 1 0 0 0 0 1 LS01.dat
0 SYNTH END
```

Coordinates are LDU. Each marker's local **−Y axis points along the path**: away from the start, into the end. These matrices point along +X. Move markers to route the hose, and rotate them to control its direction. Use enough clearance for the actual cross section, and inspect bends and endpoints after every change. `flex types` lists supported methods, product aliases and marker parts. Product aliases are hints, not proof that the resulting pose has the correct manufactured length.

A band uses actual pulley, wheel or gear placements as constraints, in loop order. Choose only parts listed under `band_constraints`; their configured radii determine the wrap. `0 SYNTH INSIDE`, `OUTSIDE` and `CROSS` control the route. Start with two separated, coplanar pulleys and inspect a simple loop before adding crossings. Put each wheel in the source once. Visible wheel constraints remain real placements in the generated asset; `SYNTH HIDE` suppresses them when the wheels already belong to another assembly.

Use explicit colours in each SYNTH BEGIN. Keep the original visible constraints even if using `SYNTH HIDE`: LSynth comments markers out in its output, which cannot reliably reconstruct the source on a later run. The adapter rejects already synthesized inputs. Multiple SYNTH blocks and ordinary MPD submodels are supported; blocks must stay within one FILE section. Keep source section names unique when importing several assets, or use the existing `extract --namespace` command to rename a dependency closure.

## Generate and reuse

```sh
./ldraw-agent flex build output/my-hose.ldr --output output/my-hose.mpd
# After changing the original constraints:
./ldraw-agent flex build output/my-hose.ldr --output output/my-hose.mpd --force
```

This writes the MPD and a `.manifest.json` with source/configuration hashes, engine version, source credits, embedded geometry provenance, each synthesized block and any recorded compatibility repairs. Unknown types, warnings from LSynth, empty synthesis and assembly validation errors fail without replacing an existing asset. `--timeout` bounds the subprocess. `--namespace` changes the generated part prefix; it defaults to the output filename stem. The source is never overwritten.

Import it through the existing plan format. Place the `root` returned by `flex build`:

```json
{
  "version": 1,
  "author": "Your name",
  "assets": ["my-hose.mpd"],
  "sections": [{
    "name": "main.ldr",
    "description": "Assembly containing a posed hose",
    "steps": [[{"id": "hose", "ref": "my-hose.ldr", "colour": 4, "at": [0, 0, 0]}]]
  }]
}
```

Asset paths are relative to the plan. Regenerate after moving endpoints relative to one another; a rigid placement only moves the completed pose. The generated colour remains explicit. Use the normal `build` and `review` commands for the complete assembly, and deliver the constraint source and manifest with it.

## What the checks mean

Continuous hoses, cables, bands and one-piece rubber treads become **one posed embedded part per block**. LSynth's stretched cross sections belong inside that part's geometry, and are not independent BOM items. Separate Technic chain/tread links and BRICK_ARC bricks stay ordinary rigid physical placements. Minifigure chains are supplied as a complete item and stay one posed part. Posed part IDs describe geometry; they are not an inventory or retail part-number claim.

The normal prohibition on stretching, shearing or mirroring complete parts remains in force. For generated rigid links only, the adapter can recover rounding from LSynth's four-decimal output when each corrected matrix coefficient differs by at most 0.00005. Every such repair is recorded. It never applies this repair to input placements or to stretched hose/band geometry. Larger defects fail validation.

Check every route's bend radius as well as its endpoints. Fixed-segment types such as `TECHNIC_RIBBED_HOSE` place separate rigid rings about 5.5 LDU apart, and those rings open visible gaps once neighbours turn more than about 7°. LSynth's stiff curves can also form near-hairpins when waypoints sit close together. Stretched types such as pneumatic hose stay continuous, but can still bend too tightly or cross another hose.

The [pneumatic press](../../examples/flex/pneumatic-press/README.md) places hose ends on the nozzle frames from each part's shadow data. Its test measures sleeve seating, minimum bend radius, tube-to-tube distance and part clearance; reuse those checks for new routes.

Start flex studies with `review --contacts none`. Bounds, source checks, previews and BOM comparison still run, but connectivity and material clearance are not established. Posed parts have no verified connector metadata, stock length, tension, minimum bend radius or elasticity. Inspect the route, endpoint seating, obstructions and link engagement in the actual assembly; generic AABB overlaps cannot certify these. `physical_validity` stays `not_proven`.

The tested port is **lsynth-nova 3.1.0**, with its bundled definitions. This adapter currently uses default resolution: that version reads the wrong argument positions for `HOSE_RES` and `BAND_RES`, so custom resolution records are rejected. GHOST inputs are also unsupported. The standalone LSynth CLI remains available for other workflows; its raw output needs separate review before reuse here.

Legacy compatibility is confined to embedded copies: LS22's Latin-1 author header becomes UTF-8, and LS50/LS51's invalid `BFC CERTIFY INVERTNEXT` becomes `BFC INVERTNEXT`. Original hashes and changes are recorded; authorship, licence notices and geometry remain. Some bundled examples also contain missing legacy parts, nonrigid source placements or impossible pulley routes. A successful LSynth exit alone does not make those assemblies valid.
