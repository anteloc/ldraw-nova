# Linden Row House (SNOT edition) — module and submodel contracts

The same original 3-storey urban townhouse as run 1 (café ground floor, two apartments, roof terrace, 32×32
plot), now in **SNOT style**: structure stays System (slabs, wall cores, rings), while **façades and details
are SNOT** — cladding panels, sign, cornices, pilasters, dentils, kerb face, nameplates — mounted on
side-stud bricks (30414 / 11211 / 87087) and headlight bricks (4070). Classic city-terrace character:
rusticated dark-grey stone base with a green shopfront; dark-red brick upper storeys with white surrounds;
white cornices; black ironwork.

Palette (`common.PALETTE`): brick 320 · stone 72 · trim 15 · accent 19 tan · shop 288 · door/timber/floor 70 ·
glass 47 · metal 0 · roof 72 · paving 71 · foliage 2 · flowers 5/14/1.

## What is new in this run: the submodel tree is part of the contract
Each module's root section (`<module>.ldr`) may contain **only** the submodels listed below (plus its
anchors). Every part you place belongs to exactly one contracted submodel (helper sections such as
`window4()` may be used inside a submodel; they inherit its ownership). Section names are fixed: create a
`Module('<name>', ...)` per row (the `export()` prefix is your module name, so a submodel named
`ground-sign` must be a Module named `ground-sign` — do **not** add a second prefix; helper modules get
the prefix automatically). `contract_check.py` verifies every row (existence, placement count, envelope,
connection, SNOT interface contacts, colours, duplicates, symmetry, forbidden zones).

Coordinates in the tables: module-local, X/Z in **studs**, h in **LDU upward** (h = -Y), front = -Z.
Envelopes are where every part of that submodel must lie (all placements together for ×2/×3 rows); the top limit tolerates the 4 LDU of exposed studs.
"✦" = SNOT submodel: it must have a declared interface and pass its contact count.

## Scene layout (orchestrator)
- Baseplate X -16..16, Z -16..16, top surface Y=0. Building footprint X -12..12, Z -6..10 → storey modules are
  placed at scene [0,0,40] (module-local Z -8 = scene Z -6).
- Stack: ground at Y=0; floor2 `attach` ground.next; floor3 `attach` floor2.next; roof `attach` floor3.next.
  Pitch 160 LDU. Module scene origins: street [0,0,0], ground [0,0,40], floor2 [0,-160,40], floor3 [0,-320,40], roof [0,-480,40].
- **Storey contract** (ground, floor2, floor3): slab underside h=0; anchors `base` [0,0,0] and `next` at h=160;
  complete perimeter plate ring with top at h=160; nothing else above h=160 inside the footprint.
- Projection zones beyond the front wall (Z < -8): SNOT cladding everywhere down to Z -9; ground awning to
  Z -12; floor2 bay + window boxes to Z -10.5; floor3 balcony to Z -11; roof cornice/dentils/pediment face to Z -9.
- Street owns the plot outside the footprint; tall props only at Z ≤ -12 or |X| ≥ 13; café walkway X -2..2,
  Z -8..-6 clear.

## Rules learned in run 1 (all modules)
1. Floor slabs: plates must rest on the ring of the storey below — use 6x16 plates **3027 running
   front-to-back** (Z -8..8) so both ends sit on the front/back ring. No free-floating centre plates.
2. Every prop/furniture item stands on **studs** (plates), never on smooth tiles.
3. Round caps on top of things: **98138** round tile (has a stud receptacle); never 6141 on 3062b or a 4589
   cone as a floating cap.
4. Chairs/sofas face their table: check each backrest direction vector.
5. Left/right counterparts are mirror-symmetric (colour patterns too: dentils, stripes, slats).
6. LeoCAD's top view is a perspective camera — never call an envelope violation from a render; use
   `contract_check.py` (envelope by owning part).
7. Ground display glazing ≥ 96 LDU tall; awning in the band h 100..134 below the sign.
8. Rear façades must read finished (windows with surrounds, a door, details), not blank.
9. Every element must **read as what it is** (plants look like plants, a bay looks glazed, a sign looks
   like a sign). Design-level findings must be **fixed**, not just recorded.
10. Keep the cafe front visible: nothing tall in front of the shopfront.

## Submodel tables

### street.ldr — worker H5 (scene origin [0, 0, 0] LDU)

| # | submodel (section) | ×| parent | envelope X / Z studs, h LDU | build frame | interfaces (mount/part ≥min) | purpose / inspection duties |
|---|---|---|---|---|---|---|---|
| 1 | `street-base.ldr` | 1 | street | [-16, 16] / [-16, 16] / [-4, 16] | upright, studs up | — | 32x32 baseplate 3811, sidewalk paving (tiles), alley/garden paving; PLATE pads (not tiles) under every prop. **Check:** footprint bare; pads under props; no tile under any prop; forbid house footprint (must stay bare baseplate studs) |
| 2 | `street-kerb.ldr` ✦ | 1 | street | [-16, 16] / [-17, -14] / [0, 32] | built FLAT in its own frame (studs up), turned with panel_R(face) and seated with seat(); final studs face OUT (-Z) | street-base/* ≥4 | kerb: dark grey 72 kerb course along the front edge with a SNOT tile face pointing -Z (sideways tiles on side-stud bricks). **Check:** stud-map of the section in parent; contact count on its interface; seams flush; no gap behind panel |
| 3 | `street-lamp.ldr` | 2 | street | [-16, 16] / [-16, -12] / [0, 262] | upright, studs up | — | slim fluted lamp post (architecture lamp() style; cap 98138 not 4589/6141). **Check:** seated base; slim; |X|>=6; not hiding the shopfront; mirror-symmetric |
| 4 | `street-tree.ldr` | 2 | street | [-16, 16] / [-16, -8] / [0, 262] | upright, studs up | — | street tree in a raised planter. **Check:** canopy inside the plot; clear of awning (ground awning spans X -10..10, Z -12..-8 of the house = scene Z -10..-6, h 100..132); mirror-symmetric |
| 5 | `street-furniture.ldr` | 1 | street | [-16, 16] / [-16, -6] / [0, 80] | upright, studs up | — | bench, fire hydrant, litter bin, post box. **Check:** every item seated on studs; facing the street/sidewalk sensibly; forbid cafe doorway walkway |
| 6 | `street-cafe-terrace.ldr` | 1 | street | [3, 11] / [-12, -7] / [0, 60] | upright, studs up | — | cafe sidewalk table with 2 chairs facing it, maybe a parasol <=60 tall. **Check:** chairs face the table (check backrest direction vector) |
| 7 | `street-alley.ldr` | 1 | street | [-16, -12] / [-6, 16] / [0, 80] | upright, studs up | — | side alley (left): paving 72, bins, a side gate. **Check:** seated, inside envelope, reads as what it is |
| 8 | `street-garden.ldr` | 1 | street | [-16, 16] / [-6, 16] / [0, 120] | upright, studs up | — | right hedge strip X 12..16 + back garden Z 10..16: closed fence/wall along the back edge, tidy shed with door and roof. **Check:** seated, inside envelope, reads as what it is; forbid house footprint |
| 9 | `street-house-plaque.ldr` ✦ | 1 | street-garden | [-16, 16] / [-6, 16] / [0, 120] | built FLAT in its own frame (studs up), turned with panel_R(face) and seated with seat(); final studs face OUT | street-garden/* ≥2 | house name/number plaque mounted SIDEWAYS on the garden wall or a gate pier (flat-built tile panel on side studs). **Check:** stud-map of the section in parent; contact count on its interface; seams flush; no gap behind panel |

### ground.ldr — worker H1 (scene origin [0, 0, 40] LDU)

| # | submodel (section) | ×| parent | envelope X / Z studs, h LDU | build frame | interfaces (mount/part ≥min) | purpose / inspection duties |
|---|---|---|---|---|---|---|---|
| 1 | `ground-slab.ldr` | 1 | ground | [-12, 12] / [-8, 8] / [0, 8] | upright, studs up | — | floor slab 24x16 of plates on the baseplate, top h=8. **Check:** full coverage; plates only |
| 2 | `ground-walls.ldr` | 1 | ground | [-12, 12] / [-8.3, 8.3] / [8, 152] | upright, studs up | — | stone (72) wall core, 1 stud thick; front: piers X -12..-10 and 10..12, openings X -10..10 for the shopfront; side-stud bricks (30414/11211, studs -Z) in the pier courses and in the fascia course (top h=152) for the SNOT panels; side windows (window4) and back openings. **Check:** openings match ground-shopfront/rear exactly; side-stud bricks exactly where the panels need them |
| 3 | `ground-rustication.ldr` ✦ | 2 | ground | [-12.5, 12.5] / [-9, -7.5] / [8, 128] | built FLAT in its own frame (studs up), turned with panel_R(face) and seated with seat(); final studs face OUT (-Z) | ground-walls/* ≥4 | rusticated stone cladding panel for ONE front pier (2 wide, banded 72/19 tiles), placed twice (left pier, right pier). **Check:** stud-map of the section in parent; contact count on its interface; seams flush; no gap behind panel; both piers identical; mirror-symmetric |
| 4 | `ground-shopfront.ldr` | 1 | ground | [-10, 10] / [-8.5, -6] / [8, 128] | upright, studs up | — | two display windows >=96 LDU tall glazing (e.g. 1x4x5 frames 2493b + glass 2494, or 1x4x6 + glass) in 288 green, plus central door (X -2..2) in a 288 surround. **Check:** glazing >= 96 LDU tall; symmetric about X=0; door centred |
| 5 | `ground-sign.ldr` ✦ | 1 | ground | [-10, 10] / [-9, -7.5] / [128, 156] | built FLAT in its own frame (studs up), turned with panel_R(face) and seated with seat(); final studs face OUT (-Z) | ground-walls/* ≥4 | fascia SIGN: 288 board with a lettering-like pattern of 14/15 tiles, built FLAT, mounted on the fascia side-stud course. **Check:** stud-map of the section in parent; contact count on its interface; seams flush; no gap behind panel; reads as a sign; centred |
| 6 | `ground-awning.ldr` | 1 | ground | [-10, 10] / [-12, -8] / [100, 134] | upright, studs up | ground-walls/* ≥2 | sloped striped awning 288/15 over the shopfront, projecting to Z -12, underside >= h100, top <= h134. **Check:** every slope seated; stripes regular and symmetric; no floating valance |
| 7 | `ground-rear.ldr` ✦ | 1 | ground | [-12, 12] / [6, 9] / [8, 152] | mixed; SNOT parts face +Z | ground-walls/* ≥2 | rear facade details: back door, 2 windows, SNOT lintels/sills (tiles on side studs pointing +Z), a lamp. **Check:** stud-map of the section in parent; contact count on its interface; seams flush; no gap behind panel; rear must read as finished, not blank |
| 8 | `ground-interior.ldr` | 1 | ground | [-11, 11] / [-7, 7] / [8, 150] | upright, studs up | — | cafe interior: counter with till/cakes, 2 tables with stools, shelf; clear of the doorway. **Check:** every item seated; stools around tables; nothing in the 4-stud door path |
| 9 | `ground-ring.ldr` | 1 | ground | [-12, 12] / [-8, 8] / [152, 160] | upright, studs up | — | top interface: complete perimeter plate ring, top at h=160 (white 15). **Check:** complete ring; top exactly h=160 |

### floor2.ldr — worker H2 (scene origin [0, -160, 40] LDU)

| # | submodel (section) | ×| parent | envelope X / Z studs, h LDU | build frame | interfaces (mount/part ≥min) | purpose / inspection duties |
|---|---|---|---|---|---|---|---|
| 1 | `floor2-slab.ldr` | 1 | floor2 | [-12, 12] / [-10, 8] / [0, 8] | upright, studs up | — | floor slab: FOUR 6x16 plates 3027 running front-to-back (each rests on the front and back ring of the storey below) + bay floor plates to Z -10. **Check:** every slab plate rests on ring cells or is clutched by a plate that does |
| 2 | `floor2-walls.ldr` | 1 | floor2 | [-12, 12] / [-8.3, 8.3] / [8, 152] | upright, studs up | — | dark-red 320 brick wall core with window openings; side-stud bricks (studs -Z) where floor2-facade panels mount; headlight bricks 4070 for the window boxes. **Check:** seated, inside envelope, reads as what it is |
| 3 | `floor2-facade.ldr` ✦ | 1 | floor2 | [-12, 12] / [-9, -7.5] / [8, 152] | built FLAT in its own frame (studs up), turned with panel_R(face) and seated with seat(); final studs face OUT (-Z) | floor2-walls/* ≥8 | front SNOT cladding: white window surrounds / tan sill bands / masonry texture panels around the two flanking windows (X -10..-6 and 6..10). **Check:** stud-map of the section in parent; contact count on its interface; seams flush; no gap behind panel; symmetric; mirror-symmetric |
| 4 | `floor2-bay.ldr` | 1 | floor2 | [-4, 4] / [-10, -8] / [8, 160] | upright, studs up | floor2-slab/* ≥2 | glazed bay window, 8 wide, projecting to Z -10: >=60% glass, corbels below, sloped/tiled cap <= h160. **Check:** reads as a glazed bay; supported; symmetric; mirror-symmetric |
| 5 | `floor2-window-box.ldr` ✦ | 2 | floor2 | [-11, 11] / [-10.5, -7.5] / [8, 56] | box upright; front face on 4070 side studs | floor2-walls/4070 ≥4 | flower box under each flanking window, front face SNOT-mounted on headlight bricks; flowers on studs. **Check:** stud-map of the section in parent; contact count on its interface; seams flush; no gap behind panel; mirror-symmetric |
| 6 | `floor2-rear.ldr` ✦ | 1 | floor2 | [-12, 12] / [6, 9] / [8, 152] | SNOT parts face +Z | floor2-walls/* ≥2 | rear facade: 2 windows with SNOT white surrounds (+Z), a drainpipe or balconette. **Check:** stud-map of the section in parent; contact count on its interface; seams flush; no gap behind panel; rear reads finished |
| 7 | `floor2-interior.ldr` | 1 | floor2 | [-11, 11] / [-7, 7] / [8, 150] | upright, studs up | — | living room: sofa facing a coffee table/TV, bookshelf, lamp, rug, plant. **Check:** every item seated on studs; sofa faces the table |
| 8 | `floor2-ring.ldr` | 1 | floor2 | [-12, 12] / [-8, 8] / [152, 160] | upright, studs up | — | top interface ring, top h=160. **Check:** seated, inside envelope, reads as what it is |

### floor3.ldr — worker H3 (scene origin [0, -320, 40] LDU)

| # | submodel (section) | ×| parent | envelope X / Z studs, h LDU | build frame | interfaces (mount/part ≥min) | purpose / inspection duties |
|---|---|---|---|---|---|---|---|
| 1 | `floor3-slab.ldr` | 1 | floor3 | [-12, 12] / [-11, 8] / [0, 8] | upright, studs up | — | floor slab of 3027 6x16 plates front-to-back; balcony deck integrated (centre plates extend to Z -11). **Check:** every slab plate rests on ring cells or is clutched; deck underside >= h0 |
| 2 | `floor3-walls.ldr` | 1 | floor3 | [-12, 12] / [-8.3, 8.3] / [8, 152] | upright, studs up | — | dark-red 320 brick core; openings for French doors (X -2..2) and two tall flanking windows; side-stud courses for cornice and pilasters; side windows. **Check:** seated, inside envelope, reads as what it is |
| 3 | `floor3-cornice.ldr` ✦ | 1 | floor3 | [-12, 12] / [-9, -7.5] / [8, 40] | built FLAT in its own frame (studs up), turned with panel_R(face) and seated with seat(); final studs face OUT (-Z) | floor3-walls/* ≥6 | SNOT string course across the whole front: tan/white sideways plates + tiles (a 2-tone band). **Check:** stud-map of the section in parent; contact count on its interface; seams flush; no gap behind panel; continuous across the front except the door opening; mirror-symmetric |
| 4 | `floor3-pilaster.ldr` ✦ | 2 | floor3 | [-4, 4] / [-9, -7.5] / [8, 152] | built FLAT in its own frame (studs up), turned with panel_R(face) and seated with seat(); final studs face OUT (-Z) | floor3-walls/* ≥4 | white SNOT pilaster flanking the French doors (one section placed twice: X -3..-2 and 2..3). **Check:** stud-map of the section in parent; contact count on its interface; seams flush; no gap behind panel; mirror-symmetric |
| 5 | `floor3-french-doors.ldr` | 1 | floor3 | [-2, 2] / [-8.5, -6] / [8, 152] | upright, studs up | — | pair of glazed French doors (white 15) in the X -2..2 opening. **Check:** seated, inside envelope, reads as what it is |
| 6 | `floor3-balcony-rail.ldr` | 1 | floor3 | [-6, 6] / [-11, -8] / [8, 56] | upright, studs up | floor3-slab/* ≥4 | black 0 balcony railing ~40 tall around the deck edge, with 2 small planters. **Check:** continuous rail; posts seated; symmetric; mirror-symmetric |
| 7 | `floor3-windows.ldr` | 1 | floor3 | [-12, 12] / [-8.5, 8.5] / [8, 152] | upright, studs up | — | all window units of the storey (front flanking tall windows, 1 per side wall, 2 rear). **Check:** frames seated in openings; glass in frames |
| 8 | `floor3-rear.ldr` ✦ | 1 | floor3 | [-12, 12] / [6, 9] / [8, 152] | SNOT parts face +Z | floor3-walls/* ≥2 | rear facade: SNOT window surrounds (+Z) and a string course matching the front. **Check:** stud-map of the section in parent; contact count on its interface; seams flush; no gap behind panel |
| 9 | `floor3-interior.ldr` | 1 | floor3 | [-11, 11] / [-7, 7] / [8, 150] | upright, studs up | — | bedroom: bed, wardrobe, nightstand + lamp, rug. **Check:** seated; bed against a wall |
| 10 | `floor3-ring.ldr` | 1 | floor3 | [-12, 12] / [-8, 8] / [152, 160] | upright, studs up | — | top interface ring, top h=160. **Check:** seated, inside envelope, reads as what it is |

### roof.ldr — worker H4 (scene origin [0, -480, 40] LDU)

| # | submodel (section) | ×| parent | envelope X / Z studs, h LDU | build frame | interfaces (mount/part ≥min) | purpose / inspection duties |
|---|---|---|---|---|---|---|---|
| 1 | `roof-deck.ldr` | 1 | roof | [-12, 12] / [-8, 8] / [0, 16] | upright, studs up | — | deck slab (plates spanning to the perimeter) + surface tiles; white 15 outer edge; plate pads under everything standing on it. **Check:** slab plates supported; nothing stands on tiles |
| 2 | `roof-parapet-front.ldr` | 1 | roof | [-12, 12] / [-8.3, -6.5] / [16, 96] | upright, studs up | — | front parapet core (320) with side-stud courses for cornice and dentils; white coping. **Check:** continuous; coping 1 deep (Z -8..-7) |
| 3 | `roof-front-cornice.ldr` ✦ | 1 | roof | [-12, 12] / [-9, -7.5] / [0, 40] | built FLAT in its own frame (studs up), turned with panel_R(face) and seated with seat(); final studs face OUT (-Z) | roof-parapet-front/* ≥6 | white SNOT cornice band across the front at the base of the parapet. **Check:** stud-map of the section in parent; contact count on its interface; seams flush; no gap behind panel; the only roof part allowed to reach Z -9 besides dentils/pediment face; mirror-symmetric |
| 4 | `roof-dentils.ldr` ✦ | 1 | roof | [-12, 12] / [-9, -7.5] / [40, 88] | upright, studs up | roof-parapet-front/* ≥6 | dentil course: alternating 98138 / 1x1 tiles on headlight bricks or a flat-built strip on side studs. **Check:** stud-map of the section in parent; contact count on its interface; seams flush; no gap behind panel; mirror-symmetric pattern; mirror-symmetric |
| 5 | `roof-pediment.ldr` ✦ | 1 | roof | [-4, 4] / [-9, -6.5] / [88, 150] | core upright; nameplate built FLAT in its own frame (studs up), turned with panel_R(face) and seated with seat(); final studs face OUT | roof-parapet-front/* ≥2 | central pediment over the parapet with a SNOT nameplate (flat-built tile panel) and a stepped/triangular top. **Check:** stud-map of the section in parent; contact count on its interface; seams flush; no gap behind panel; symmetric; reads as a pediment; mirror-symmetric |
| 6 | `roof-parapets.ldr` | 1 | roof | [-12, 12] / [-8.3, 8.3] / [16, 64] | upright, studs up | — | side and back parapets: one brick course + white coping; gap where the stair-house meets the back wall. **Check:** seated, inside envelope, reads as what it is |
| 7 | `roof-corner-pier.ldr` | 2 | roof | [-12, 12] / [-9, -6] / [16, 120] | upright, studs up | — | white corner pier with urn (cap 98138), front corners; placed twice. **Check:** urn seated (98138, not 6141); mirror-symmetric |
| 8 | `roof-stair-house.ldr` | 1 | roof | [-6, 6] / [2, 8] / [16, 196] | upright, studs up | — | stair-house with door4 facing front, lintel, roof (top <= 196). **Check:** door faces the deck; closed walls; roof complete |
| 9 | `roof-skylight.ldr` | 1 | roof-stair-house | [-6, 6] / [2, 8] / [180, 200] | upright, studs up | roof-stair-house/* ≥2 | skylight on the stair-house roof, flush tiles, top <= h200. **Check:** seated, inside envelope, reads as what it is; max_h 200 |
| 10 | `roof-chimney.ldr` | 1 | roof | [7, 12] / [-3, 5] / [16, 190] | upright, studs up | — | 2x2 brick chimney stack with cap and pots, against the right parapet. **Check:** seated, inside envelope, reads as what it is |
| 11 | `roof-pergola.ldr` | 1 | roof | [-11, -1] / [-6, 4] / [16, 140] | upright, studs up | — | timber pergola: 4 posts on pads, beams, evenly spaced slats. **Check:** 4 posts seated; slats evenly spaced and centred |
| 12 | `roof-bistro-set.ldr` | 1 | roof | [-10, -2] / [-5, 3] / [16, 64] | upright, studs up | — | bistro table + 4 chairs FACING the table, under the pergola. **Check:** chair backrests point AWAY from the table |
| 13 | `roof-planter.ldr` | 3 | roof | [-12, 12] / [-8, 8] / [16, 80] | upright, studs up | — | planter box with plants that read as plants (leaves/flowers, not 2x2 round bricks); placed 3 times. **Check:** seated, inside envelope, reads as what it is |
