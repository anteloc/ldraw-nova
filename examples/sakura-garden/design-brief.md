# Sakura Garden — design brief

## Subject and scope

A Japanese temple garden at the height of cherry-blossom season, at minifigure
scale on one 48×48 stud baseplate. A vermilion five-storey pagoda stands on a
stone platform at the back right. Visitors enter through a torii on a flagstone
axis, cross a koi pond on a humped bridge, and pass stone lanterns, a bamboo
grove, a cloud-pruned pine and a raked dry garden. Three figures give the scene
its story and scale: a visitor in a pink robe on the bridge crown, a monk on
the stepping-stone path and a gardener beside the raked gravel.

This is an original design. The official set 10315 *Tranquil Garden* was
studied for technique only (see References); no source geometry was copied.

## What should make it attractive

- **One unmistakable silhouette.** The pagoda is the only tall mass (944 LDU
  from the base to the spire tip), so it reads at thumbnail size. Its five roofs
  shrink by two studs per storey and its gilded nine-ring spire tapers to a rod.
- **Flared eaves, not boxes.** Each roof has a flat eave line that sweeps up
  into raised corners through 3-stud curved slopes, ending in gilded tips with
  hanging bells. The single-width roof slopes leave seams that read as tile rows.
- **Warm against cool.** Vermilion and gold against dark-grey roofs, set in
  green moss, blue water, white gravel and pink blossom.
- **Depth through layers.** The water sits a plate below the lawn, the platform
  and stair rise above it, the bridge arches over the pond, and the trees stand
  in stepped canopy tiers.
- **Quiet surfaces.** Raked gravel and a plain stone terrace surround the
  pagoda so its detail isn't competing with ground clutter.

## Silhouette and dimensions

| Item | Value |
|---|---|
| Footprint | 48×48 studs (960×960 LDU); all parts lie within ±480 LDU |
| Height | 944 LDU (the pagoda spire tip); terrain top at 24 LDU |
| Pagoda | platform 22×22; cores 12/12/10/8/6; roofs 18/16/14/12/10; storey pitch 104 LDU |
| Pond | about 19×15 studs, water surface 8 LDU below the lawn |
| Bridge | 4×16 studs, crown 32 LDU above the banks |
| Torii | 14 studs wide, 192 LDU tall, straddling the 4-stud path |

## Focal hierarchy

1. **Primary:** the five-storey pagoda: diminishing flared roofs, lattice
   windows, red corbels, gilded bells, tips and spire.
2. **Supporting:** the vermilion arched bridge over the koi pond, with its
   brown planked crown, handrail, giboshi posts and the pink-robed visitor.
3. **Supporting:** the torii on the main axis, which frames the pagoda from the
   front and carries a gilded plaque.
4. **Accents:** six stone lanterns with lit fire boxes, printed koi tiles, lily
   pads, irises, fallen petals, boulders, a stone basin and a timber bench.

## Palette roles

| Role | Colour (LDraw code) |
|---|---|
| Structure: posts, lattice, corbels, bridge, torii | Red (4) |
| Plaster panels | White (15) |
| Eave decks and screens behind the lattice | Dark Red (320) |
| Roofs, eaves, hips | Dark Bluish Grey (72) |
| Spire, bells, eave tips, finials, plaque | Pearl Gold (297) |
| Stone: platform, lanterns, footings | Light Bluish Grey (71) |
| Torii kasagi and plaque body | Black (0) |
| Lawn / moss / pine | Green (2) / Dark Green (288) |
| Blossom | Bright Pink (29), Pink (13), Dark Pink (5), White (15) petals |
| Water | Trans Medium Blue (41) over a Dark Blue (272) bed; koi tiles on Dark Azure (321) |
| Paths / gravel | Tan (19) flagstones; White (15) and Very Light Bluish Grey (151) raked rows |
| Trunks, bridge deck, bench | Reddish Brown (70) |
| Bamboo | Green (2), Bright Green (10) |
| Irises / monk / gardener | Medium Lavender (30) / Orange (25) / Dark Blue (272) |

Availability of every part in every colour is not claimed.

## Detail vocabulary

Curved flares, gilded tips and bells, and vermilion lattice on the architecture.
Round stone forms (dishes, round bricks) for the lanterns, basin and spire.
Stepped cloud canopies with petal clusters on the cherries, and the same
construction in dark green for the pine. Printed koi in the water.

## Physical subassemblies and build order

1. `garden-ground` — three plate layers over the baseplate. The water, koi and
   lily cells sink one plate; the bridge pier footing sits at water level.
2. `temple-plinth` — brick rings, a full deck, the terrace, a dark veranda and
   a lattice railing; it carries the pagoda at h = 32.
3. `pagoda-storey-0…4`, stacked by `attach` on the `next` anchor, then
   `pagoda-crown` and `pagoda-spire`.
4. `temple-steps`, `arched-bridge`, `torii-gate`, `stone-lantern` ×6.
5. Planting: `cherry-large/medium/small`, `garden-pine`, seven bamboo culms,
   boulders, the basin and the bench.
6. Water details (koi, lily pads), irises, fallen petals, then the figures.

## Module checklist

All modules have their bottom at h = 0 and face −Z; X/Z are in studs.

| Module | Local origin | Envelope | Anchors / interface | Review |
|---|---|---|---|---|
| garden-ground | board centre | 48×48, top h=24 | tiles/studs per terrain map | built, overlaps triaged |
| temple-plinth | platform centre | 22×22, deck h=32, terrace h=40 | `entry` (front centre) | contacts: main + finial group |
| pagoda-storey-k | core centre, wall foot | roof R×R, 104 high | `base`, `next` (deck top) | contacts in scene; screens fixed |
| pagoda-crown / spire | apex | 4×4 / 2×2 | `apex` | spire rings pair after the 85861 swap |
| temple-steps | stair centre | 6×5, treads 8…40 | meets terrace at 40 | built |
| arched-bridge | span centre | 4×16 (+end posts), crown h=32 | tips on bank studs, legs on footing (−8) | crest profile measured |
| torii-gate | path centre | 14×2, 192 high | pillars on 2×2 studs at x = ±3 | single component |
| stone-lantern | 2×2 stud centre | 3×3 roof, 132 high | base on 2×2 studs | dish roof: metadata limit |
| cherry-* / garden-pine | trunk centre | up to 14 studs wide | root flare on 4×4 studs | single component each |
| bamboo culm | stud centre | 1 stud + leaf fans | leaf headings solved in code | leaf clearance measured |
| figures | between the foot studs | 2×1 | feet on studs (1.2 LDU correction) | bodies connect; arms have no metadata |

## Measured part frames used by the generator

- Slopes `3039/3040b/3298/4286/3045/3675/3665b`: origin on the high stud row,
  low edge toward local −Z; footprint centres are listed in `LOCAL`.
- `11477`, `54200`: origin at the bottom; high end toward +Z.
  `50950`, `61678`: origin at the high top; high end toward +Z.
- `50967` arch slope (measured surface profile): the tip socket is at
  y = +24 and the feet beside the tip and the central legs reach y = +32. The
  flat crown between the two crests spans only z = ±35 LDU of a mirrored pair,
  so crown parts use the inner studs.
- `3185/3633` fences: origin on top, bottom at +48/+24.
- `42284` rock shell: sockets at +8, rim at +32. It sits on a hidden round
  2×2 brick; a square brick clips the sloping inner ceiling (checked by surface
  sampling).
- `43898`, `4740`, `3960` dishes: centre socket 8/8/16 LDU below the origin.
- `30176` bamboo leaves: three blades reaching 52 LDU, lying 1–18 LDU below the
  node top.
- `11211` side studs: 10 LDU below the top on the −Z face. The upright plaque
  tile sits at top −10 and 18 LDU forward.
- Minifigure stack (from `examples/copper-bean`): hips 40 LDU above the stud
  surface. Feet sockets (`3816c/3817c`) sit 1.2 LDU behind the leg origin,
  so the figure is shifted +1.2 LDU to seat them on the studs.

## References and part discovery

- **Whole-model precedent:** `10315-1.mpd` *Tranquil Garden* (source SHA-256
  prefix `821df9d16555bac9`, 1,341 physical placements). I studied its lantern
  (cone + 1×1 brick + dish), its cherry blossom cluster (frond + 1×1 petal
  plates), its rock piece and its pine. I adapted the techniques and rebuilt
  them at this scale with this model's own interfaces; nothing was extracted.
- **Jev part discovery** (`research/jev/*.json`, one query per role) surfaced
  koi tiles `3069bp0p/q` (used), bamboo brick `30176` (used), curved-top arches
  and `50967` (bridge, used), the `73682/99301/75538` concave pieces (rejected:
  wrong scale or corner-only), lattice fences `3185/3633` (used) and rock
  `42284` (used). Part boards are in `research/board-*.png`.
