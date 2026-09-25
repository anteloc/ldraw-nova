# Sakura Garden — visual review

Every image listed here was opened and inspected. Standard review views come
from `ldraw-agent render` (LeoCAD, full shading, line width 1). The hero shots
come from `render_hero.py`, which uses LeoCAD's automated edge colouring so
small parts keep their colour. Earlier renders are kept in `iterations/` and
`proto/`.

## 1. Pagoda prototype — `proto/pagoda-review/home.png`, `front.png`

- **Problem:** the roofs read as flat grey trays. The 2-stud curved flare
  (`11477`) barely lifted the corners, and the solid 2×2 slopes (`3039`) were
  featureless.
- **Change:** 3-stud curved flares (`50950`) on a plate, rising 24 LDU into
  four-plate corner stacks with gilded round tiles. The slope ring became
  single-width `3040b` so the seams read as tile rows. A gilded 1×1 cone now
  hangs under every eave corner as a bell.
- **Result:** the front view shows swept eaves, bells and the nine-ring spire.
  I kept this design.

## 2. Bridge technique — `proto/bridge-test/right.png`, `home.png`

Two mirrored `50967` arch slopes form a humped two-span bridge with a central
pier. The image was needed to understand the part. Surface sampling later gave
the exact crest and foot heights (see design brief).

## 3. First full scene — `iterations/first-pass/home.png`, `top.png`, `front.png`, `right.png`

- **Works:** composition. The pond, bridge and torii sit in the foreground,
  the pagoda at the back right, and the torii frames the pagoda on the axis
  (front view).
- **Problems:** the cherry canopies were sparse, pale and flat; the water
  (Trans Light Blue) read as ice; the pine read as a white palm.
- **Changes:** water to Trans Medium Blue over Dark Blue; cherry and pine
  canopies redesigned (below).

## 4. Tree iterations — `proto/cherry-review/*.png`, `proto/pine-review/front.png`, `proto/cherry-large/*.png`, `proto/garden-pine/*.png`

- **Brown square hubs:** looked like tabletops.
- **Stacked frond spine:** read as a Christmas tree. Checking the geometry
  also showed that diagonal fronds at 70 LDU radius would cross their
  neighbours' back bars.
- **Final:** stepped cloud tiers (round pink discs on round-brick cores, a
  sprig ring on risers, petal carpets). Wider than tall, pink mass, no
  intersecting fronds. Pink risers replaced brown ones so the cloud doesn't
  break up.
- **Pine:** moved from upward serrated leaves (read as a palm) to thin tiers
  (too sparse) to cloud-pruned pads carpeted with dark green rosettes.

## 5. Rendering legibility — `iterations/pass3/home.png` vs `iterations/pass3-hero/*.png`

With the default edge lines, the whole-scene home view washes the colours out
to grey. I added the hero renders with automated edge colour, and in them the
palette reads clearly. The raked gravel (white grille tiles) rendered dark grey
because of the slots.

**Change:** plain tile rows alternating White and Very Light Bluish Grey.

## 6. Physical corrections driven by the triage, then re-rendered — `iterations/pass4-hero/hero-pond.png`, `hero-high.png`

- Boulder shells had sunk 24 LDU into the ground; they now stand on hidden
  round bricks with their rims on tiles.
- The bridge feet had sunk into the bank and footing; the footing now sits at
  water level, and the crown uses only the flat inner studs.
- Bamboo leaves were striking neighbouring culms; each leaf heading is now
  chosen with clearance checks.

After these fixes the gravel reads bright and the rocks sit naturally.

**Remaining weakness:** no life or scale.

## 7. Life and crowns — `iterations/pass5-hero/*.png`, `iterations/pass6-hero/*.png`

- **Added:** a pink-robed visitor on the bridge crown, a monk, a gardener in a
  rice hat, lavender irises on the banks, and fallen petals.
- **Problem:** the 4×4 dish crowns looked like flat pink hats, and the torii
  plaque was a plain black block.
- **Change:** petal-covered frond crowns, and a gilded plaque tile on
  side-stud brick `11211`.

## 8. Close-ups — `iterations/pass7-hero/hero-bridge.png`, `hero-torii.png`

These confirmed the koi, irises, fallen petals, lanterns, the plaque and the
upswept kasagi. The overlap triage then showed the visitor's forward-reaching
hands passing through the west handrail, so she moved one stud east (1 LDU
clearance).

## 9. Final — `review/home.png`, `front.png`, `back.png`, `left.png`, `right.png`, `top.png`; `hero/hero-pond.png`, `hero-axis.png`, `hero-high.png`, `hero-pagoda.png`, `hero-bridge.png`, `hero-torii.png`

- **Scene bounds:** they showed foliage overhanging the base (the pine by
  about 5 studs, the two edge cherries by 1–2 studs). The pine moved inward,
  and the edge trees dropped the sprigs pointing off the board, so they lean
  into the garden. The small cherry's crown was turned by 90°. Every part now
  lies within ±480 LDU.
- **Bamboo:** five of ten culms had come out bare because they were packed
  too tightly. The grove was re-spaced to seven culms, 3–4 studs apart, and
  all 20 nodes carry leaves.
- **Final views:** the back and left views confirm that the pagoda's lattice,
  corbels and bells continue on every face, and that the terrain edge is a
  clean three-plate section. The top view confirms the pond outline, the
  stepping-stone route and the tree spacing.

## Remaining aesthetic limits

- The upper two storeys are all red, because their narrow cores leave no room
  for white panels beside the 4-wide lattice.
- The lawn is studded green. That is deliberate texture, but it is busier than
  a tiled lawn.
- The bench is a simple slab.
