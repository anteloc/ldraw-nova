# Linden Row House — module contracts

An original 3-storey urban townhouse on a 32×32 baseplate: a café on the ground floor, two apartments
above and a roof terrace. Classic city-terrace character: rusticated dark-grey stone base with a green
shopfront, dark-red brick upper storeys with white window frames, white cornices, black ironwork.

Palette (see `common.PALETTE`): brick 320 dark red · stone 72 dark bluish grey · trim 15 white ·
accent 19 tan · shop 288 dark green · door/timber/floor 70 reddish brown · glass 47 · metal 0 black ·
roof deck 72 · paving 71 · foliage 2 · flowers 5/14/1.

## Scene layout (orchestrator, studs; baseplate X -16..16, Z -16..16, top surface Y=0)
- Building footprint: X -12..12, Z -6..10 → each storey module is placed at scene (0, 0, +2 studs) = [0,0,40] LDU.
  So module-local Z -8 (front wall face) = scene Z -6.
- Stack: ground at Y=0; floor2 attach ground.next; floor3 attach floor2.next; roof attach floor3.next.
  Pitch 160 LDU. Roof base at Y=-480.
- Street owns everything on the baseplate outside the footprint.

## ground.ldr — worker H1 (café / bakery)
- Storey contract. Walls body colour 72 (stone), with tan (19) accents allowed.
- Front (-Z): shopfront in dark green 288: large display glazing (e.g. `display4()` units, 144 LDU tall)
  either side of a central recessed or framed entrance door (door leaf 70 or glazed door in 288).
  Fascia band above the shopfront with a sign (e.g. tiles in 15 or 14 on 288, or printed tile).
- Awning: striped 288/15 (slopes/tiles) projecting forward to local Z -11 at most, its underside no
  lower than h=104, top no higher than h=156. Must be supported by the wall (brackets or interlocking
  plates) — no floating parts.
- Sides/back: a few windows (window4) and a back door.
- Interior: counter with cash register / cakes (round tiles/plates), 2 small tables with stools, a shelf.
  Keep the interior below h=150 and clear of the 4-stud doorway.
- Projection zone: Z -12..-8 (awning, step, door surround, planters). Nothing beyond local Z -12.
- Anchors: base, next (h=160).

## floor2.ldr — worker H2 (apartment, bay window)
- Storey contract. Walls dark red brick 320 (use `material='masonry'` or embossed bricks for texture where
  sensible), white 15 window frames; tan 19 sills / string course allowed.
- Front: a centred projecting **bay window** about 8 studs wide, projecting up to 2 studs (local Z -10..-8),
  supported from below by its own corbel/brackets on this storey (its bottom h ≥ 8 so it does not hit the
  awning below; the awning top is ≤ h 156 of the storey below, i.e. below this storey). Bay top ≤ h=160.
  Flanking windows (window4) left and right with window boxes (flowers) under them.
- Sides/back: windows.
- Interior: living room — sofa, coffee table, bookshelf, lamp, rug (tiles).
- Projection zone: Z -10..-8 only, and only for the bay + window boxes.
- Anchors: base, next (h=160).

## floor3.ldr — worker H3 (apartment, balcony)
- Storey contract. Walls dark red brick 320, white trim; include a white/tan **cornice/string course** at
  the bottom (h 8..32 band) on the front face, may project 1 stud (Z -9..-8).
- Front: centred pair of tall French doors (door4 glazed style or 1x4x6 frames + glass) opening onto a
  **balcony** about 12 studs wide, deck at h=8 projecting to local Z -11 (3 studs), black 0 railing (fence
  / bars / 1x4 railings, ~40 LDU high). The deck must be supported: interlock with the slab (plates that
  span from inside the wall line outward) and/or brackets under it. Deck underside ≥ h 0 (never below the
  storey's own Y=0, the bay window below rises to h 160 of floor2).
  Flanking windows either side of the doors.
- Interior: bedroom — bed, wardrobe, nightstand, lamp.
- Projection zone: Z -11..-8 only (balcony, cornice).
- Anchors: base, next (h=160).

## roof.ldr — worker H4 (roof terrace)
- Local origin footprint centre, bottom Y=0, front -Z. It sits on floor3's top ring.
- Full 24×16 deck slab at h 0..8 (plates), roof deck surface: tiles 72/71 or a wooden deck area (70 tiles).
- Front **parapet** with a white 15 cornice projecting 1 stud (Z -9..-8) at the bottom, brick 320 parapet
  ~2–3 bricks high with white coping; lower parapet/railing on sides and back.
- Features: a timber **pergola** (70/19) over part of the deck with a table and chairs, planters with
  plants/flowers, a brick **chimney stack** (320 with 72 cap) near one side wall, a stair hatch / small
  stair-house (door4, 72 roof) at the back, a skylight (trans-clear panes), maybe a small water tank or
  antenna. Height up to h ≈ 200.
- Projection zone: Z -9..-8 for the cornice only.
- Anchors: base only (`next` optional).

## street.ldr — worker H5 (plot and street scene)
- Local origin = baseplate centre; baseplate 32×32 (`3811`, colour 2 green or 72) at [0,0,0], top surface Y=0.
  This section is placed at scene origin.
- **Reserved: footprint X -12..12, Z -6..10 must remain bare baseplate studs** (the ground storey sits there).
- Sidewalk: Z -16..-6 full width, light bluish grey 71 tiles (one plate-height: tiles at h=8 on plates? —
  use a single layer of tiles directly on the baseplate, h=8 meaning `at Y=-8`? Check `./ldraw-agent part 3068b`:
  a tile's origin is at its top face; a tile on the baseplate is placed at Y=-8), with a 1-stud dark grey 72 kerb
  line at Z -16..-15. **Note**: the café door is at scene X 0, Z -6: keep a 4-stud wide clear walkway
  from X -2..2 at Z -8..-6 (no props).
- Tall props (higher than 100 LDU: lamp post, tree) must stand at scene Z ≤ -12 (near the kerb) **or** at
  |X| ≥ 13 (side strips), because balconies/awning overhang Z -11..-6 at mid-height.
- Props: 1–2 street lamps (`lamp()`), a tree in a raised planter (`tree()`), a bench, a bike rack with a bike
  if feasible, a fire hydrant, a post box or bin, café sidewalk table with 2 chairs at X 7..11 Z -11..-8
  (low only, ≤ 60 LDU).
- Side strips X -16..-12 and 12..16 (Z -6..16): left = side alley paved 72 with bins; right = small garden
  path/hedge. Back yard Z 10..16: small garden: grass (baseplate), a fence along the back edge, a shed or tree.
- Anchors: base only.
