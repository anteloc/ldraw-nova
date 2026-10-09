# Technic structures: construction, compatibility and tooling readiness

Research date: 2026-09-25. **Historical preparatory assessment of the tooling before stage 1.** The [Stage 1 implementation record](technic-stage1-implementation.md) describes the structural support now available. The user subsequently authorized [Stage 2 construction from mechanism examples](technic-stage2-implementation.md), with analytical mechanism verification deferred. The observations and evidence below preserve the original research baseline.

Technic support should begin with a small, verified vocabulary of structural joints and frames. The existing part library, renderer, discovery tools and assembly format provide a useful foundation. The current connection solver needs additional rules before an agent can rely on it to construct Technic structures.

The decisive distinction is **connected versus rigid**. Parts can be joined correctly while the assembly still folds, twists or slides. Compatibility depends on the actual interfaces, their placement and their restraint—not the set or theme the parts came from.

This study combines LEGO construction guidance, a designer's historical discussion of stressed connections, the supplied LDraw/LDCad specifications, source inspection and local probes of **36 parts, 13 small assemblies and 3 snap requests**. Measurements and observed failures are preserved in the [evidence snapshot](technic-structure-evidence.json); the [probe script](technic-structure-probe.py) reproduces them. No physical assembly or load testing was performed.

## 1. The two stages

| Stage | Scope | Completion decision |
| --- | --- | --- |
| 1: structures | Studded and studless frames, chassis, bracing, fixed supports, retained structural axles, body mounts and System–Technic interfaces. Check unintended rotation/sliding, seating and assembly access. | Present reviewed examples and limitations for the user to judge. |
| 2: mechanisms | Working steering, suspension, gear trains, transmissions, linkages, actuators and their motion/interference analysis. | Begin only after the user explicitly decides stage 1 is satisfactory and authorizes stage 2. |

Recognizing that a structural joint can move belongs in stage 1. Designing useful motion belongs in stage 2. Using an axle as a structural member does not by itself make a mechanism. Conversely, freezing a gearbox in one pose does not turn its validation into a solved structural problem.

## 2. What changes when building with Technic

### Build around hole centres and joints

System construction often grows by stacking and overlapping bricks and plates. Technic construction grows around beam centre lines, hole patterns, pin engagement, axial stacks and bracing in several directions. Both systems can build structures, and Technic includes both studded bricks and studless beams.

These are **nominal LDraw relationships and measurements of the installed definitions**, not manufacturing specifications:

| Relationship | LDraw measurement | Consequence |
| --- | --- | --- |
| Common stud/hole pitch | 20 LDU | Many System and Technic mounting patterns share a horizontal module. |
| Ordinary brick / plate body height | 24 / 8 LDU | Vertical stacking does not automatically follow the Technic hole grid. Studs are excluded from these body heights. |
| Thick / thin sampled beams | 20 / 10 LDU through the holes | A thin beam is not one plate thick. Pins and spacers must match the actual layer stack. |
| Three-hole beam `32523` | Hole centres at local Z = −20, 0, 20; body bounds 18 × 20 × 58 | Three holes span **two** modules between end centres. Nominal length is not the solid bounding-box length. |
| Technic brick `3700` | Hole centre at local [0, 10, 0]; body bottom at Y = 24 | The hole is not halfway through the brick's height. Its origin differs from a studless beam's. |
| Four-module axle `3705` | Nominal 80 LDU; measured solid length 79 | Use nominal engagement geometry and measured ends for their respective purposes. |

For example, two directly stacked Technic bricks have hole centres 24 LDU apart; the ends of a three-hole brace are 40 LDU apart. Adding **two plates** between the bricks gives 24 + 8 + 8 = 40. LEGO Education teaches this construction; the generated local probe reproduces it. At a larger spacing, five brick heights equal six modules. [LEGO Education, Engineering Design Notebook, PDF pages 6–7][notebook]

Hole-count parity, half-module layers and the direction of each hole matter. A diagonal also has to satisfy its endpoint geometry: a 6–8–10-module triangle uses centre distances, potentially the end holes of 7-, 9- and 11-hole members. This is a geometric starting point, not a complete recipe: corner connectors, layer offsets and insertion access still need resolving. Never force a diagonal into place by stretching a part or changing the pitch.

### Design rigidity explicitly

A single ordinary pin is a pivot, even when friction resists rotation. Two separated pins between the same rigid members can restrain relative rotation. Nevertheless, a rectangle with one pivot at each corner can still rack. Triangulation, suitable rigid corner connections and moulded frames offer different ways to prevent this. LEGO Education demonstrates the difference between an unbraced rectangle and a braced structure. [Structures lesson][structures]

Stage 1 must also consider twisting out of the plane: a stiff flat frame is not necessarily a stiff chassis. Use crossmembers, separated supporting planes and short, supported attachment paths. A body panel attached at one point can wobble even if the chassis itself is well braced. Friction, strength and stiffness are not established by a connected-component count.

### Select connector function, not just shape or colour

| Interface | Useful behavior | Structural check |
| --- | --- | --- |
| Friction pin → appropriate round pin hole | Retained pin connection with resistance to rotation | Full seating and correct grip length; do not equate friction with a rigid corner. |
| Smooth pin → appropriate round pin hole | Retained connection that can pivot more freely | Add another constraint wherever the design needs a fixed angle. |
| Cross axle → cross hole | Keyed angular alignment | Check axial positioning/retention and engagement; matching cross-sections alone do not fix translation. |
| Cross axle → suitable round Technic hole | Shaft support that permits rotation and axial travel | Treat as a bearing interface, not a keyed or automatically retained structural joint. |
| Axle-pin connector | Different mating interfaces at opposite ends | Model and select each end separately, including its shoulder. |
| Bush / stop / spacer | Establishes axial positions when assembled against other members | Check the complete stack and both escape directions. |
| Stud-ended half pin / Technic brick / dedicated mounting plate | Bridge to System construction | Check the actual stud or socket, offsets, engagement and supported mounting pattern. |

Part identity and variant are authoritative; colour is not a sufficient classifier. LEGO's own element inventories distinguish friction and non-friction connectors. Nominal beam and axle lengths are expressed in modules, and LEGO supplies a measurement chart. [Element survey][elements], [Technic building guidance][technic-tips]

Pins contain collars and flexible retaining lips; holes contain recesses. Equal centre lines and a matching diameter are insufficient. A lip must reach its intended recess and a collar must not sit inside the narrow bore. Assembly order matters too: leave a path to insert the pins or axles before closing a frame. A plausible final pose can be impossible to assemble without bending or disassembly.

## 3. Compatibility across models and construction systems

| Reuse | Assessment | What must travel with the reused parts or submodel |
| --- | --- | --- |
| One Technic set → another | High for shared, matching standard interfaces. There is no set-specific lock on a normal pin or beam. | Exact part IDs/variants, hole pattern, pin lengths, orientation, clearance and restraint. |
| Studded Technic ↔ studless Technic | Useful and extensive, with grid/layer adjustments. | Brick-height offsets, end-hole spacing, beam thickness and suitable connector lengths. |
| Technic ↔ ordinary System models | Very useful through dedicated bridges. A Technic skeleton can support a System body, building, spacecraft or sculpture. | Stud/anti-stud attachments, actual offsets, supported body mounts and accessible assembly steps. |
| Education or other themes using these interfaces | Evaluate the individual connection; a theme label neither permits nor forbids it. | Verified pin, axle, stud, bar or ball interface and surrounding geometry. |
| Different-sized ball/socket, wheel hub, electronics or other specialist systems | No blanket compatibility claim. Mechanical mounting, shaft attachment and electrical compatibility are separate questions. | Explicit interface definitions or a verified adapter; otherwise mark unsupported. |
| Complete submodel → a different model | Conditional, even if every internal part is standard. | Mounting contract, envelope, load/support direction, parent dependencies, exposed ports and build order. |

Do not derive compatibility from a raw `pin_hole` label alone. The sampled System bricks and plates also acquire such labels for internal cavities. Nor should every round opening accept every pin, stud or bar. Dedicated bridge elements are a better initial vocabulary than unreviewed diameter matches.

**LDraw alignment is not a manufacturing fit certificate.** Jamie Berard's 2006 presentation documents a small difference between the real side-stud and classic Technic-hole heights, as well as cases where incomplete seating or forced cross-system connections stress parts. It is historical designer evidence, not a current universal rulebook for every mould. Our local `3700` definition uses the simplified Y = 10 LDU hole position; do not convert that into a claim about exact physical mould tolerances. [Stressing the Elements, especially PDF pages 2 and 8–13][stress]

Submodels also need a semantic distinction between **self-supporting structure**, **a module that becomes rigid only in its parent**, and **a mechanism**. Reusing a frame without its parent's bracing can remove the feature that made it useful.

## 4. What the current tooling actually does

The probes use `pyldraw3==1.7.0`, the installed official parts and the repository's LDCad shadow library. All 36 sampled parts report complete geometry and complete connection metadata coverage. The following results show why that coverage label must not be interpreted as physical correctness.

| Probe / inspection | Observed result | Implication for stage 1 |
| --- | --- | --- |
| `3705` axle in `32064` cross hole | One confirmed contact; a 45° roll produces none | Useful existing keyed-orientation support. Preserve it. `32064` is an alias to `32064a` in this library. |
| Same axle through `3700` round hole | No contact; no snap candidate | Valid bearing interfaces are missing from the allowed kind pairs. |
| Round end of `43093` axle-pin in `3700` | No contact | The mixed profile is classified as one `axle` feature; it needs separately addressable engagement regions. |
| Pin collar centred inside a beam hole | Five reported contacts; one confirmed component | Shared profile sections and overlapping intervals do not establish a legal seated position. |
| Pin end only touching a hole entrance | Three reported contacts; one confirmed component | The axial-gap check admits zero engagement. Positive insertion and retention checks are needed. |
| Same pin moved fully clear | No contact | The negative control distinguishes touching from separation. |
| Ordinary pin in a cross hole | No contact | Preserve this rejection; do not “fix” bearing support by allowing all cylindrical pairs. |
| Two beams joined by one smooth pin | One confirmed component | Correct connection evidence still says nothing about the remaining pivot. |
| Two beams joined by two pins | Also one confirmed component | A connectivity count cannot express the difference in structural restraint. |
| `32523`, a three-hole beam | **26 raw features**; authored hole centres reduce to three distinct positions | Primitive inference and shadow inheritance introduce duplicate and misplaced features. Raw feature count is not a hole count. |
| `2780` friction pin versus `3673` smooth pin | Their main full-length shadow profiles are identical and both have `friction=false`; `2780` additionally inherits other features, some with `friction=true` | The complete feature lists are **not** identical. Current metadata gives conflicting levels of description, not a dependable friction classification. |
| Valid two-plate bridge and unspaced negative control | Both produce one optimistic component | Even partial attachment can connect the entire graph. Every **intended** brace joint must be checked independently. |

The default pin-to-beam snap places the pin centre at the hole centre and reports `confirmed`, while retaining `collision.status=review_required`. It is not silently certified buildable: the current tools already expose that limitation. The problem is that stage-1 generation must select a properly seated pose instead of treating this candidate as sufficient.

The relevant source behavior is explicit:

- [`connection_adapter.py`](../../ldraw_tools/connection_adapter.py) currently adapts stud and selected wheel interfaces. It does not provide Technic joint rules.
- [`connectivity.py`](../../ldraw_tools/connectivity.py) selects rigid transforms and tracks occupied feature IDs. Long shafts and multi-ended pins need occupancy by **engaged interval/port**, rather than a whole-feature occupied flag. Preserve provenance and conflict checks.
- The installed `ldraw.connection_types` accepts a cylindrical pair when at least one rigid section shares shape/radius. Its residual tests centreline alignment and axial gap, not full section-by-section containment, insertion depth or seating. `snap_transform` aligns feature origins and chooses one orientation; it does not search legal grip positions along an axle.
- The installed `ldraw.connection_metadata` derives `friction` from `not slide`. LDCad's `slide` controls editor snapping behavior; it is not a measured friction coefficient or a complete description of a physical joint. See the supplied [LDCad metadata specification](../LDCad-metas.pdf), `SNAP_CYL`.
- [`geometry.py`](../../ldraw_tools/geometry.py) and [`collision.py`](../../ldraw_tools/collision.py) retain broad bounds checks for irregular parts. A pin inside a hole normally has overlapping bounding boxes. The curated rectangular body checks cannot be extended to solid beam boxes without representing their holes.
- [`discovery.py`](../../ldraw_tools/discovery.py) defaults to System-oriented family and Technic-share filters. `--all-families` exposes Technic candidates today, but does not identify structural assemblies or exclude mechanisms.

## 5. Reference material already available locally

An explicit **offline FTS** query, `Technic frame chassis`, with `--all-families`, produced these useful research candidates from the annotated models. This was not a Jev availability test or a claim about semantic ranking quality.

| Source section | Physical placements | Potential lesson |
| --- | ---: | --- |
| `8838-1.mpd` / `8838 - Lower-Frame.ldr` | 17 | Studded frame mixing Technic members, ordinary plates, axles and bushes. |
| `42112-1.mpd` / `42112 - chassis.ldr` | 16 | Studless longitudinal members joined by pins, axles and connector blocks. |
| `5893-1_Truck.mpd` / `5893 - Truck frame.ldr` | 11 | Open-centre frame with friction pins and half pins; a promising body-mounting study. |
| `8865-1.mpd` / `8865 - Front Frame.ldr` | 63 | Layered studded reinforcement and perpendicular framing. |

These are measured candidates, **not approved structural recipes**. Inspect their parent context, attachment dependencies, source checks and build order before promoting them. A mechanism-bearing parent model may contain a useful static frame; do not reject or accept the whole parent theme as a substitute for inspecting that section.

The `42112` chassis was rendered and its home/top views opened. They show a long axial subassembly between the beams as well as exposed mounting connectors. Its structural versus moving role needs parent-context inspection; the word “chassis” alone cannot qualify the complete section for stage 1.

The existing discovery, extraction, attribution and seven-view catalog workflows can be reused. Extend the cards with mounting ports, nominal grid, dimensions, intended restraints, required parent support, insertion direction and review status. Include close-ups and an assembly sequence where exterior views hide seating. Screenshots provide inspection and inspiration; they cannot establish strength or prove fit.

## 6. Recommended first-stage implementation

Implement this in small, reviewable increments:

1. **Curate the structural interfaces.** Start with common straight/thin beams, studded Technic bricks, rectangular frames, friction/smooth pins, mixed axle-pins, axles, bushes and dedicated System bridges. Resolve aliases and variants. Store measured hole frames, section profiles, grip regions, stops, friction class, permitted mating classes and evidence. Distinguish authored connectors from inferred geometry, and report unknowns explicitly.
2. **Make placement respect the entire joint.** Deduplicate connectors without erasing separate physical ports. Support axle-in-round-hole as a bearing, segment mixed connectors, choose legal axial seating and key orientation, require sufficient engagement, and track occupied spans. Check every declared attachment in a multi-hole mount. Keep these rules narrowly scoped so System snapping does not regress.
3. **Add structural construction recipes.** Parameterize beam spans, crossmember spacing, layer stacks, braced corners, frames and System mounts. Reuse the existing MPD builder, proper rotations, module anchors, BOM and provenance machinery. Do not stretch parts, reinterpret `on` as a universal Technic placer, or generate a Python script for every discovered source submodel.
4. **Add conservative structural review.** Report unsecured axial travel, single-pivot supports, unbraced loops, missing intended joints, unsupported panels and inaccessible insertion steps. Begin with curated patterns and explicit review states, not a claim of a general rigidity or strength solver. Use local material/clearance checks for the supported interfaces; retain review requirements elsewhere.
5. **Teach discovery and visual design the new scope.** Add an explicit `technic-structure` construction mode while preserving System defaults and the Jev availability/offline fallback. Select static structures by their contents and intended role. Design the skeleton around the desired silhouette and body mounting needs, then use suitable panels, flex elements only in reviewed uses, or System cladding. Review proportion, clean beam lines, colour discipline and exposed connector clutter as well as geometry.
6. **Deliver an initial structural atlas for judgment.** Include a braced flat frame, a chassis with restraint in multiple planes, a tower/truss, and a System body mounted on a Technic skeleton. Each needs a reproducible generator/plan, interface contract, assembly order, BOM, final renders, geometry/joint evidence and a candid list of checks still requiring a physical build.

Prefer a repository-owned, version-pinned adapter/registry or a reviewed upstream fix over edits to the installed package or official library. Keep source geometry, original models and attribution intact.

## 7. What would count as a successful stage 1

Before presenting the atlas for the user's decision:

- Positive fixtures must cover pin seating, thin/thick stacks, keyed axles, retained structural axles, bearing classification and System bridges.
- Negative fixtures must catch collar interference, zero/insufficient insertion, wrong connector family, incorrect axle roll, double occupation, wrong layer length and a missing second mount.
- Structural review must distinguish a connected pivoting frame from a restrained structure, with explicit uncertainty where the rules do not decide.
- Discovery must distinguish structural reuse from mechanisms and retain useful static sections from mixed parent models.
- Examples must look deliberate and well proportioned, show concealed joints and remain reproducible. Physical strength and manufacturing fit stay unproven until actually tested.
- Existing System construction, snapping, vehicle examples and reference provenance must continue to pass their relevant checks.

The user evaluates those results. There is no automatic progression to mechanisms.

## Reproduction and inspection record

```sh
.venv/bin/python docs/reports/technic-structure-probe.py
./ldraw-agent render output/technic-research/system-technic-brace-two-plates.mpd \
  --outdir output/technic-research/bridge-views --views home front right
./ldraw-agent discover search submodels 'Technic frame chassis' \
  --engine fts --all-families --limit 4 --pool 16 --max-parts 250 \
  --report output/technic-research/structural-references.json
```

The script writes measurements, both valid and deliberately invalid diagnostic fixtures, full raw evidence and a compact summary under `output/technic-research/`. These diagnostic MPDs are not examples to copy into models. The tracked evidence is the compact summary from this research run; source-file hashes and the dependency version identify the sampled definitions.

After running the discovery command, rerun the probe to include the local shortlist in `summary.json`. The hashes cover each sampled top-level part file and referenced model; they are not a checksum of every transitive geometry primitive. Keep the library and shadow versions consistent when comparing runs.

The System–Technic bridge's home and right views were opened and checked for hole alignment, the two spacer plates, layer contact and pin orientation. The axle-pin probe's home view was also opened: its round end occupies the brick hole and its axle end projects outside. The notebook's spacing diagram and Berard's offset illustration were opened. The existing axle/clip integration checks passed: **2 passed, 25 deselected**. This is a baseline check, not validation of future Technic support.

[notebook]: https://assets.education.lego.com/v3/assets/blt293eea581807678a/bltb2ff88770e40583b/613ab1b40f12922b05ea6df0/Engineering_Design_Notebook_Build_to_Launch_Printers_Marks.pdf?locale=en-us
[structures]: https://education.lego.com/en-us/lessons/spm/structures/
[elements]: https://assets.education.lego.com/v3/assets/blt293eea581807678a/blt4166a91df0a6e452/5ebb9bc7570e5c524078217a/es-spm-elementsurvey.pdf?locale=es-es
[technic-tips]: https://www.lego.com/en-ae/service/help-topics/article/tips-for-building-with-lego-technic-elements
[stress]: https://bramlambrecht.com/tmp/jamieberard-brickstress-bf06.pdf
