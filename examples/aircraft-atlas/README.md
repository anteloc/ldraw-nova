# Aircraft compatibility index

Reviewed aircraft constructions from real sets, one package per lesson under `examples/<package>/`. [Browse the generated index](index.html), or use:

```sh
./ldraw-agent examples --family aircraft
./ldraw-agent examples --family aircraft --details 'landing gear'
./ldraw-agent knowledge search 'propeller hub gear' --family aircraft
./ldraw-agent knowledge show aircraft:KEY
```

Read the [aircraft guide](../../docs/agent/guides/aircraft.md) first: it maps the brief to a construction style, the airframe roles to these packages, and lists what each package does and does not prove. The package README owns the lesson, scope and limits; its `GUIDE.md` explains the construction, what the parent supplies, how to read the inspection board and the corrected database description. Whole-aircraft studies (`kind: assembly`) show proportions and module layout in completed-model views; detail studies (`kind: detail`) have build pages and a board. Inspiration entries keep source errors (string segments, spring meshes, mirrored or skewed parts, an unclassified embedded part); rebuild their technique instead of exporting them.

## Sources

| Set | Source | Style | Packages |
|---|---|---|---|
| 10159 City Airport | `10159-1.mpd` | classic City studs-up | `10159-city-airliner` (inspiration: embedded printed tail lacks a part classification) |
| 6392 Airport | `6392-1.mpd` | classic City studs-up | `6392-hinged-cabin-roof`; its airplane is the same design as 10159 and keeps five plate overlaps |
| 7893 Passenger Plane | `7893-1.mpd` | special-part System airliner | `7893-airliner`, `7893-jet-nacelle`, `7893-wheel-bogie`, `7893-cockpit-interior`, `7893-boarding-stairs` |
| 5892 Sonic Boom | `5892-1.mpd` | Creator hybrid: Technic frame, System skin, SNOT nose | `5892-sonic-jet`, `5892-snot-nose`, `5892-retracting-nose-gear`, `5892-slope-tail-fin`, `5892-plate-wing` |
| 10226 Sopwith Camel | `10226-1.mpd` | display SNOT biplane with rigging | `10226-sopwith-camel`, `10226-geared-propeller`, `10226-wedge-tailplane`, `10226-towball-aileron`, `10226-socket-wing`, `10226-towball-landing-gear`, `10226-cowling-side`, plus the earlier `10226-striped-rudder` |
| 8855 Prop Plane | `8855-1.mpd` | studded Technic (1988) floatplane | `8855-prop-plane`, `8855-universal-joint-wings`, `8855-piston-engine`, `8855-tail-boom`, `8855-pontoons` |
| 42040 Fire Plane | `42040-1.mpd` | studless Technic | `42040-fire-plane`, `42040-piston-engine`, `42040-geared-tail` |
| 9394 Jet Plane (B model) | `9394-1_Propeller-Plane.mpd` | studless Technic with LSynth flex axles | `9394-technic-airframe` |

## Packages

Scope `construction` packages pass source checks with a matching LeoCAD BOM and can be exported; `inspiration` packages keep source errors and are for study only.

| Package | Kind | Scope | Source section | Style |
|---|---|---|---|---|
| [10159-city-airliner](../10159-city-airliner/README.md) | whole aircraft | inspiration | `10159-1.mpd` / `10159 - airplane.ldr` | classic City studs-up |
| [7893-airliner](../7893-airliner/README.md) | whole aircraft | construction | `7893-1.mpd` / `7893 - plane.ldr` | special-part System airliner |
| [5892-sonic-jet](../5892-sonic-jet/README.md) | whole aircraft | construction | `5892-1.mpd` / `5892 - Airplane.ldr` | Creator hybrid (Technic frame, System skin) |
| [42040-fire-plane](../42040-fire-plane/README.md) | whole aircraft | inspiration | `42040-1.mpd` / `42040 - Fire Plane.ldr` | studless Technic |
| [8855-prop-plane](../8855-prop-plane/README.md) | whole aircraft | inspiration | `8855-1.mpd` / `8855 - Prop Plane.ldr` | studded Technic (1988) |
| [9394-technic-airframe](../9394-technic-airframe/README.md) | whole aircraft | inspiration | `9394-1_Propeller-Plane.mpd` / `9394 - 9394-2.ldr` | studless Technic |
| [10226-sopwith-camel](../10226-sopwith-camel/README.md) | whole aircraft | inspiration | `10226-1.mpd` / `10226 - main.ldr` | display SNOT biplane |
| [5892-snot-nose](../5892-snot-nose/README.md) | aircraft nose | construction | `5892-1.mpd` / `5892 - Nose section.ldr` | Creator hybrid |
| [5892-retracting-nose-gear](../5892-retracting-nose-gear/README.md) | aircraft landing gear | construction | `5892-1.mpd` / `5892 - Nose gear.ldr` | Creator hybrid |
| [5892-slope-tail-fin](../5892-slope-tail-fin/README.md) | aircraft tail | construction | `5892-1.mpd` / `5892 - Tail fin.ldr` | Creator hybrid |
| [5892-plate-wing](../5892-plate-wing/README.md) | aircraft wing | construction | `5892-1.mpd` / `5892 - Left wing.ldr` | Creator hybrid |
| [10226-geared-propeller](../10226-geared-propeller/README.md) | aircraft propeller | construction | `10226-1.mpd` / `10226 - step69.ldr` | display SNOT biplane |
| [10226-towball-landing-gear](../10226-towball-landing-gear/README.md) | aircraft landing gear | inspiration | `10226-1.mpd` / `10226 - step58.ldr` | display SNOT biplane |
| [10226-socket-wing](../10226-socket-wing/README.md) | aircraft wing | inspiration | `10226-1.mpd` / `10226 - step53.ldr` | display SNOT biplane |
| [10226-wedge-tailplane](../10226-wedge-tailplane/README.md) | aircraft tail | construction | `10226-1.mpd` / `10226 - step47.ldr` | display SNOT biplane |
| [10226-towball-aileron](../10226-towball-aileron/README.md) | aircraft control surface | construction | `10226-1.mpd` / `10226 - step59.ldr` | display SNOT biplane |
| [10226-cowling-side](../10226-cowling-side/README.md) | aircraft fuselage skin | inspiration | `10226-1.mpd` / `10226 - step34.ldr` | display SNOT biplane |
| [7893-jet-nacelle](../7893-jet-nacelle/README.md) | aircraft engine | construction | `7893-1.mpd` / `7893 - engine.ldr` | special-part System airliner |
| [7893-wheel-bogie](../7893-wheel-bogie/README.md) | aircraft landing gear | construction | `7893-1.mpd` / `7893 - wheels.ldr` | special-part System airliner |
| [7893-cockpit-interior](../7893-cockpit-interior/README.md) | aircraft cockpit | construction | `7893-1.mpd` / `7893 - cabin.ldr` | special-part System airliner |
| [6392-hinged-cabin-roof](../6392-hinged-cabin-roof/README.md) | aircraft cockpit | construction | `6392-1.mpd` / `6392 - airplane - subpart.ldr` | classic City studs-up |
| [42040-piston-engine](../42040-piston-engine/README.md) | aircraft engine | construction | `42040-1.mpd` / `42040 - motor.ldr` | studless Technic |
| [42040-geared-tail](../42040-geared-tail/README.md) | aircraft tail | construction | `42040-1.mpd` / `42040 - tail.ldr` | studless Technic |
| [8855-universal-joint-wings](../8855-universal-joint-wings/README.md) | aircraft wing | construction | `8855-1.mpd` / `8855 - Wings.ldr` | studded Technic (1988) |
| [8855-pontoons](../8855-pontoons/README.md) | aircraft floats | inspiration | `8855-1.mpd` / `8855 - Pontoons.ldr` | studded Technic (1988) |
| [8855-piston-engine](../8855-piston-engine/README.md) | aircraft engine | construction | `8855-1.mpd` / `8855 - Engine block.ldr` | studded Technic (1988) |
| [8855-tail-boom](../8855-tail-boom/README.md) | aircraft tail | construction | `8855-1.mpd` / `8855 - Tail.ldr` | studded Technic (1988) |
| [7893-boarding-stairs](../7893-boarding-stairs/README.md) | airport ground equipment | construction | `7893-1.mpd` / `7893 - stairs.ldr` | special-part System airliner |

`measurements.json` holds the measured extents, part counts, Technic shares, stud directions and tyre/engine stations of the whole-aircraft sources; `measure.py` regenerates it and prints the table used in the guide:

```sh
.venv/bin/python examples/aircraft-atlas/measure.py --markdown
```

## Promote a new lesson

`selections.json` is the seed list and `recipes/` holds the ldraw-xray board recipes; `generate.py` is a thin command over `ldraw_tools.atlas`. Studies are prepared outside the repository, reviewed from the actual images, then installed:

```sh
.venv/bin/python examples/aircraft-atlas/generate.py --scaffold seeds.json          # append seeds with computed identity
.venv/bin/python examples/aircraft-atlas/generate.py --probe --name KEY             # source checks only: adapt or inspiration?
.venv/bin/python examples/aircraft-atlas/generate.py --candidates --name KEY        # build pages and boards into output/aircraft-atlas/KEY
.venv/bin/python examples/aircraft-atlas/generate.py --refresh-notes --name KEY     # after writing notes/guide fields from the images
./ldraw-agent manual review output/aircraft-atlas/KEY --images ... --note '...'     # list every image actually opened
.venv/bin/python examples/aircraft-atlas/generate.py --install --name KEY           # copy into examples/<package>/ and register
```

Install refuses a folder without a current review, an `adapt` row whose source checks or BOM comparison fail, and an `inspiration` row whose checks pass. Changing a recipe, the notes or the source invalidates the review; prepare and review again. `--install --force` replaces an installed package after a re-render. Extraction repairs four-decimal rounded rotation matrices (deviation between 1e-6 and 0.002) to exact rotations and records each repair in `extraction.json`; the structural check in `./ldraw-agent build` needs that precision. To refresh browsing from current registrations:

```sh
.venv/bin/python -c "from ldraw_tools.knowledge import write_compat_catalog; write_compat_catalog('aircraft', 'examples/aircraft-atlas')"
```
