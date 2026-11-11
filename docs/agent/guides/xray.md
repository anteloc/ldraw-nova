# Inspect models with ldraw-xray

Use `bin/ldraw-xray` installed by [setup](../../setup.md); use a PATH installation
only when the local tool is absent. This guide adapts the upstream
[README](https://github.com/anteloc/ldraw-xray/blob/v0.5.0/README.md) and
[agent instructions](https://github.com/anteloc/ldraw-xray/blob/v0.5.0/AGENTS.md).
The [recipe reference](https://github.com/anteloc/ldraw-xray/blob/v0.5.0/docs/reference.md)
covers advanced layers and cameras. A sibling checkout is not required.

Set `LDRAW_DIR`, `LDRAW_XRAY_CACHE` and, when necessary, `LEOCAD` as in setup.
Run `bin/ldraw-xray doctor`: `renders: true` means rendering is available.
Read `errors` otherwise. `sections`, `palette` and `mosaic` do not need LeoCAD.
Use current `--help` when selecting options.

For a particular part, obtain its exact filename through the [part-information workflow](part-information.md)
before rendering. Never open or parse library `.dat` contents to identify shapes
or reconstruct geometry; use the tool's images and structured evidence.

## Inspect the assembly and its mounting

From this project's root, substitute your source and exact section names:

```sh
bin/ldraw-xray sections output/task/model.mpd
bin/ldraw-xray board overview output/task/model.mpd --section 'wing.ldr' \
  --output output/task/xray/overview
bin/ldraw-xray render output/task/model.mpd --section 'wing.ldr' \
  --parent --highlight section --ghost --view front \
  --output output/task/xray/mount
bin/ldraw-xray render output/task/model.mpd --section 'wing.ldr' \
  --stud-map --view home --view bottom --output output/task/xray/studs
```

Read the JSON's `images`, `notes` and `warnings`, then open `mosaic.png` and the
individual PNGs. An empty selection can succeed with a warning. List sections
first: `--section` needs the exact name. Bare `--parent` needs a unique parent;
otherwise name one explicitly. Inspect all distinct parent placements. In a
parent view, selectors apply to the parent, so `section` highlights the child
assembly as a whole. Stud maps are especially useful for this project's SNOT
default; they show orientation, not a verified mating connection.

| Question | Command/options |
| --- | --- |
| Hidden parts | `render MODEL --xray 'colour:15' --highlight 'part:3647' -o OUT` |
| Build sequence | `render MODEL --section NAME --steps 3,7-9 -o OUT` |
| Shell cross-section | `board cutaway MODEL --section NAME --view front --depths 0.35 0.5 0.65 -o OUT` |
| Candidate pivots | `axes MODEL --section NAME` |
| Contacts and groups | `connections MODEL --section NAME` |
| Replay inspection | `board run recipe.json -o NEW_OUT` |

Quote selectors: `all`, `section`, `line:12,20-24`, `step:3-5`, `part:3001*`,
`colour:15,4`, `ref:wing.ldr`. `|` unions; `!` removes, with removals applied last.
Only removals starts from all placements. Line and step numbers belong to the
source, including empty source steps.

`--ghost` requires `--highlight`. `--steps` cannot combine with `--parent`,
`--highlight` or `--ghost`. `--stud-map` and `--xray` are mutually exclusive.
More than 12 panels needs `--no-mosaic`. Existing results require a new output
directory or an intentional `--force`.

For motion, get candidate axes with `axes`, then use `board pivot` with explicit
`--point X Y Z --direction X Y Z --moving 'SELECTOR' --angles ...`. Coordinates
are in the section frame, negative Y up. Choose mechanically plausible angles;
a rendered pose does not establish clearance or allowable travel. Pivot panels
share a camera; other views are framed independently, so their apparent sizes
are not directly comparable.

## Evidence and limits

Keep `recipe.json`, `manifest.json`, mosaics and panels under `output/<task>/`.
Record which images you opened and what they establish. Reuse only evidence
whose source hash and selections match the current model. Source models and the
parts library are read-only to xray.

Magenta marks highlights/new steps, pale grey is ghosted context, and synthetic
axes are visualization aids. Contacts, groups and box-overlap candidates are
clues: connector coverage is incomplete (including Technic pin/axle pairing),
and rotated bounding boxes can overestimate collisions. They do not prove
strength, clutch, fit or motion. Pair visual findings with Nova's validation
and BOM review; report skipped checks.

Commands emit one JSON object; errors use stderr. Exit 2 means bad input/setup;
exit 1 means execution failure. Preserve the exit status when saving reports.
