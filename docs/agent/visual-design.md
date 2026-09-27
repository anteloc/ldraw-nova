# Design models worth looking at

Geometric correctness is a constraint, not the design brief. An attractive model needs a recognizable subject, clear proportions, a controlled palette, depth, and details that belong to its story. A thousand repetitive bricks do not substitute for these decisions. Make a visual revision after opening the first render; do not end at the first valid assembly.

For [Technic structures](technic.md), choose the skeleton and body mounts together. Keep long members, bracing and repeated frames visually coherent; use a restrained palette and give exposed pins a clear purpose. A System body needs real, supported mounting interfaces. Review the bare skeleton and the covered model from the side and underside before adding surface detail. For mechanisms, use the [Stage 2 workflow](mechanisms.md): expose the useful moving forms, preserve space around them in the chosen pose, and adapt bodywork and mounts to the studied construction. Analytical mechanism verification is deferred.

For vehicles, use the [vehicle design workflow](vehicles.md) and its review criteria:
stance, wheel/arch balance, bonnet/cabin/tail proportions, continuous body lines,
glazing, clean surfaces and front/rear identity. `vehicle list`, `vehicle wheels`,
`vehicle details`, `vehicle plan` and `vehicle check --profile FAMILY` provide executable starting points and evidence.
Choose dedicated seats, controls, glazing, hulls, frames, wings and cargo fittings
before surrounding bodywork; compare their footprints and native attachment planes.
Architectural motifs below are examples for buildings, not a vehicle vocabulary.

For [spaceships](spaceships.md), design the silhouette, scale and internal support together. Use dedicated canopies, controls, wedges, cylindrical engines and grille/bar/clip details. Concentrate machinery in service bays beside quiet armour; inspect wing thickness, engine spacing, underside and display mounts. Read [build pages](build-manuals.md) for useful hidden constructions before adapting them.

## Start with composition

Write a short `design-brief.json` or Markdown brief outside the assembly plan. Record:

- **Identity:** what this place/object does and the mood it should convey. For example, a botanical bookshop beside a quieter townhouse.
- **Silhouette:** two or three major masses, height differences, roof shapes and a clear base. Make it recognizable at thumbnail size before adding small ornaments.
- **Focal hierarchy:** one primary feature (shop entrance/awning), two supporting features (dormer and neighbouring clock pediment), then small accents. Do not make every surface equally busy.
- **Palette roles:** dominant body colour, contrasting trim, roof, smaller accent, metal, glazing and planting. Repeat roles across related modules; use fewer colours on large surfaces.
- **Depth:** recessed glazing, projecting sills, a layered cornice, a canopy or bay, roof overhangs. Even one-stud offsets create useful shadows when they have real support.
- **Detail vocabulary:** choose a few consistent motifs—arches, masonry, flower boxes, brass fittings—and vary their use by function. Leave quiet wall and roof areas.
- **Scene/story:** readable entrance, a window display, books, a seat, planting, paving and appropriate lighting. Add intentional asymmetry and different plant heights without random scattering.

Use the current [Copper Lane brief](../../examples/modular-street/design-brief.json) and [review](../../examples/modular-street/visual-review.md) as an example. Adapt the principles to other subjects: vehicles need stance, wheel/arch proportions and readable functional details; animals need silhouette, pose and expressive features; interiors need a clear activity and appropriate furniture scale.

## Find a shape before memorizing a number

First consider whether the missing design idea is a whole-model precedent, a reusable construction or an individual part. Use [reference discovery](reference-discovery.md) for separate searches at those three levels and `examples --family reference` for curated sources. Open the candidate catalog, compare measured sizes and parent context, and select a few distinct constructions. A model can suggest proportions and palette; a submodel can reveal actual fittings and assembly techniques that a part-name search misses. Record whether each chosen source is copied, adapted or used only as inspiration.

Start with [Jev part discovery](tooling.md#jev-part-discovery) when you know the role or visual character but not the part name. Describe one part, such as `a wall decoration for a castle`; the reranker returns ten scored alternatives for that role. Run separate queries for different roles, inspect the returned real references, and compare a curated shortlist visually. Keep the model's scale and style in the query, then verify actual dimensions and attachment geometry with the tools below.

The supplied `data/categories/` tree has descriptive part symbols, colour definitions and dimension hints. The tooling reads those files as static metadata, preserving their notices; it does not import their optional `py4bricks` dependency or edit the generated files.

```sh
./ldraw-agent catalog categories
./ldraw-agent catalog parts 'arch 1 x 6' --category arches --limit 5 --measure
./ldraw-agent catalog parts 'embossed' --category bricks
./ldraw-agent catalog parts 'leaves' --category plants --limit 5
./ldraw-agent catalog colours 'sand'
./ldraw-agent part @arches.Arch1X6X2WithThickTopAndReinforcedUnderside
```

Results include an exact symbolic ref, actual filename, installed description/status, source file/line and cached dimensions. Normal results exclude missing, alias and internal entries; use `--include-unavailable` to investigate them explicitly. A category is not a manufacturing inventory or proof that a part is suitable at a particular scale.

`--max-size X Y Z` filters **cached** full dimensions in LDU. `--measure` measures the selected results against current library geometry and flags discrepancies. Some supplied dimensions disagree with the installed geometry; they are useful shortlist hints, not an authoritative fit API. Full bounds include studs and decoration. Never use `ldu_y`, `plates_y` or rounded `studs_*` as a stacking height or socket location. Use `part`, curated body profiles, and connector frames for placement.

Browse candidates visually before choosing:

```sh
./ldraw-agent part-board @plants.PlantLeaves6X5 @plants.PlantTreeOval4X4X6 \
  @arches.Arch1X6X2WithThickTopAndReinforcedUnderside \
  --colour @colours.Dark_Green --outdir output/part-shortlist
```

Open `index.html`; each card links an actual LeoCAD image, a small MPD and measured bounds. At most twelve candidates keep the board useful. Images are independently framed, so use the listed dimensions when comparing scale. A perfectly valid part may still have the wrong visual character: the updated example chose layered leaves over the ribbed one-piece trees after visual review.

## Generate with descriptive names

JSON placements accept category symbols and colour names directly:

```json
{"id":"window-arch", "ref":"@arches.Arch1X6X2WithThickTopAndReinforcedUnderside",
 "colour":"@colours.Tan", "at":[0,-128,0]}
```

The editable plan retains these symbols. `build` resolves them to current library filenames and numeric LDraw colours, then runs the usual validation. Misspelled symbols and absent files fail explicitly. Numeric refs/colours remain supported and work even without `data/categories/`; use `LDRAW_CATEGORIES` to point to another source tree. Current `LDConfig.ldr` supplies rendering colour data, including transparency; the generated category colour snapshot is not substituted for it.

## Reuse a detail, then adapt its role

```sh
./ldraw-agent design palettes
./ldraw-agent design palettes botanical-bookshop
./ldraw-agent design details
./ldraw-agent design details arched-window --palette rose-townhouse --output output/window.plan.json
./ldraw-agent build output/window.plan.json --output output/window.mpd
./ldraw-agent inspect output/window.mpd --contacts all
./ldraw-agent render output/window.mpd --outdir output/window-review
```

Palettes use named roles and composition guidance; they do not assert that every part was manufactured in those colours. Detail plans are ordinary editable assembly plans, usable through `includes` and named anchors. Put the exported plan in `includes`, then reference its first section name from a placement. To include two palette variants, give their sections distinct names and use those names in the containing model. Inherited placement colour does not override explicit palette colours inside a recipe; change its roles or generate a different palette variant. No private geometry format is required. The current recipe set includes:

| Recipe | Purpose and interface |
|---|---|
| `arched-window` | Six-stud bay with a projecting sill, two contrasting piers, matching window/panes, an arch and flower accents. Bottom support Y=0; top body plane -128; front -Z. |
| `striped-awning` | Eight-stud canopy. Rear underside stud row at Z=0 anchors to a cornice; the two-stud-deep beam supports actual slope sockets at Z=-20. Front extends to Z=-50. |
| `flower-planter` | Four-stud plinth, flower accents, a round trunk and four foliage layers. Bottom support Y=0; leaves overhang the base well above ground. |
| `book-sign` | Side-stud mounts hold a real gold BOOKS patterned tile. Bottom support Y=0; front -Z. |

Place details at an appropriate scale and where their attachment frames make sense. Do not paste a recipe through existing wall bricks. Reserve openings, remove conflicting core parts, and include decoration in the full model’s collision review. Copper Lane's dormer replaces the front roof slopes in its footprint; its arched bays replace wall cells rather than cover them. Each decorative storey advances 168 LDU between deck undersides (base +8, cornice -160).

## Review beauty separately from physical evidence

Render and open a whole-model home/front/top set, plus a close detail and a side/rear view when the design needs it. Ask concrete questions:

1. At thumbnail size, are the subject, silhouette and main feature recognizable?
2. Are the base, storeys, windows, entrance and roof in convincing proportion?
3. Does the main view have depth and useful shadows, including on the exposed sides?
4. Do colours organize the composition, with small accents rather than scattered patches?
5. Do repeated motifs have enough variation to distinguish functions and buildings?
6. Are there both quiet surfaces and deliberate details? Could an ornament be removed to clarify the design?
7. Are doors, glazing, displays and roof features visible, rather than hidden behind planting or lamps?
8. Did the details introduce hovering parts, collisions, unsupported overhangs or bad connections?

Write a short review naming the viewed images, specific problems found, and changes made. Do not invent an automated beauty score, claim visual review from a JSON report, or use a higher part count as a quality metric. The geometry checker still reports its own coverage limits. A beautiful render cannot clear an invalid assembly; a valid assembly cannot satisfy an aesthetic brief by itself.

LeoCAD review renders explicitly set full shading, antialiasing, line width, and disable saved step fading/highlighting. This keeps comparisons more consistent across application settings. Keep all changes in plans/generators and regenerate the exact final MPD, reports, BOM and previews.
