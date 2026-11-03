# An-225 Mriya — visual and construction review

This review was made from opened LeoCAD renders; it is not an automated beauty score.
Each pass below names the images that were opened, what they showed, and what changed.
The final images are in `review/` (whole-model views) and `review/closeups/` (regional
views framed by `closeup.py`). Earlier passes are kept in `iterations/`.

## Pass 1 — first silhouette (`iterations/review-v1/`: home, right, top, front)

- The model already read as a long, swept high-wing jet with six engines. Main-gear and
  nose-gear wheels were visible in the right view.
- **Problems.**
  - The wing top was a single fully studded grey slab.
  - The nose was an open box because the visor was missing.
  - The tail was missing.
  - The belly upsweep showed as a coarse staircase.
- **Changes.**
  - The upper wing layer became a tile field. It is bond-packed so every tile bridges the
    plate joints below.
  - Added the H-tail with 54094 endplate fins.
  - Added the hinged visor, the ramp, microscale containers, upper-deck windows and
    Buran mounting posts.
  - Added trans-red and trans-green wingtip lights.

## Pass 2 — whole aircraft (`iterations/review-v2/`: home, left, front, top, back, right; close-ups of nose, tail, gear and engines)

- **What worked.**
  - The top and front views read as the Mriya: six nacelles, a twin-fin H-tail, and a
    long fuselage with a blue/yellow cheatline.
  - The orange and sand-green containers and the yellow-edged ramp make the hold the
    colour focus.
- **Problems.**
  - The visor looked ribbed, because it was built from 1-wide slopes.
  - The tail cone ended bluntly.
  - The sponsons were plain boxes.
  - Close-ups showed the belly steps as scallops.
- **Structural problems found alongside this pass.** The full contact analysis split the
  model into 21 groups:
  - The port wing had a continuous joint at its root in both layers.
  - Each keel sponson strip had the same footprint in all three layers.
  - Each nacelle's studs sat half a stud off its pylon sockets.
  - The wing and tail tip tile patches were unbonded.
  - The round Buran caps and the round-plate lamps had no connection evidence.
- **Changes.**
  - Wrote a bond-aware packer: an upper piece prefers to bridge at least two lower pieces.
  - Added tie plates in the middle keel layer.
  - Aligned the nacelles.
  - Tiled all full tip cells, including the wedges' full cells.
  - Changed the lamps to 1×1 tiles and removed the Buran caps.
  - Rebuilt the visor from 2-wide slopes (3660b, 3039, 3298) in rings that overlap by one
    row, so the shelves bond them.

## Pass 3 — revised shape (`iterations/review-v3/`: home, left, front, top; close-ups of nose, tail, aft and sponson)

- **What worked.**
  - The top view shows a clear An-225 planform: 1:2 swept leading edge, 1:4 trailing
    edge, six engines ahead of the wing, and the H-tail with fins at the stabiliser tips.
  - The full contact graph became one group.
- **Visor.** Seen from the front and side it still reads as a stepped brick shell.
- **Decision on the visor.**
  - A larger rebuild was considered, using 22390/32084 nose rings and 41761 hull wedges.
  - I kept the validated ring construction and refined its colour and hinge instead.
  - The rebuild would have changed the proven hinge and shelf interfaces for a marginal
    gain at this scale.
- **Aft belly.** Scalloped: each step is a 13547 curve with a 4-LDU riser. It still reads
  as a continuous upsweep at thumbnail size, so it was accepted as a stated LEGO-style
  simplification.

## Pass 4 — hinges (`iterations/review-v4/closeups/nose/`: home, left)

- The mesh check (`mesh_clearance.py`) found that at −70° the plates on the 3938 hinge
  tops cut the 3937 bases' square top-rear edge.
- `hinge_study.py` showed:
  - At yaw 0 the plated top cuts the base from 15° to 85°.
  - At yaw 180 it is clear at every angle.
- Both hinge parts are now yawed 180°.
- The ramp's click hinges have toothed detents every 22.5°. The ramp now sits at the
  22.5° detent, lengthened to 7 studs so its toe is 6 LDU above the ground.
- The left close-up confirms a gentler, believable loading ramp.

## Pass 5 — palette and finish (`iterations/review-v5/`: all seven views; every close-up)

- **Changes.**
  - Yellow and blue flag caps on the fin tips give the tail a Ukrainian identity (tail
    close-up).
  - A light-grey visor chin continues the belly line and reads as the radome when the
    visor is raised.
- **Problems.**
  - The bottom and back views showed the blue cheatline plates exposed under the tail
    cone.
  - The engines' front close-up showed that the sponson ends were open hollow boxes.
- **Changes after this pass.**
  - The ceiling and pinstripe turn white aft of s=96, so the stripe ends cleanly before
    the tail.
  - The sponson ends are closed with bricks in their inner column.

## Final images (`review/`)

- **Opened:** `home.png`, `front.png`, `back.png`, `left.png`, `right.png`, `top.png`,
  `bottom.png`, and the nose (home, left, front), tail, gear, engines, aft and sponson
  close-ups.
- **Thumbnail.** The home view is recognisable as the An-225: six engines, twin fins and
  the long white fuselage with a blue/yellow line. The raised visor and ramp mark the
  front.
- **Front.** The hold is framed by the raised visor above and the ramp below; the
  containers carry the colour accent. The engines hang evenly, and the wing is flat.
- **Side (left/right).** A straight top line and a stepped aft upsweep. The sponson is
  closed and all 14 main wheels line up under it. The nose leg sits under the hold, and
  the fins rise above the roof line.
- **Top.** Symmetric swept wing and stabiliser. Tiled surfaces are quiet, and studded
  wedge bands mark the edges. The roof tiles, curved edges and Buran posts all sit on
  the centreline.
- **Bottom.** The light-grey keel sits between the gear beams. Engines, bogies and the
  nose leg are all symmetric. No stray colour remains under the tail.

## Remaining visual limitations

- **Visor:** a stepped brick shell, not a smooth radome.
- **Aft belly:** scalloped steps, not a straight upsweep.
- **Tail cone:** blunt.
- **Wing:** flat, with no anhedral.
- **Model colour:** predominantly white and grey, by design.
- **Edge bands:** the studded wedge bands on the leading and trailing edges are
  deliberate but busier than the tiled field.
- **Render framing:** at the renderer's whole-model framing the aircraft is small in
  frame, because the wingspan sets the bounding sphere. The close-ups carry the detail
  review.
