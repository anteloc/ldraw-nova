# Studs-forward retro boombox: design brief

**Identity.** A 1980s portable stereo. The black case is built upright, but the silver front is built studs-forward and the battery door studs-backward. The SNOT is functional: woofers, cassette, meters and tuner all sit on sideways stud grids, and the whole fascia lies flush inside the case frame.

**Scale and silhouette.** Case footprint 26 × 6 studs (520 × 120 LDU); lid top 280 LDU above the ground. The rounded handle rises to 344 LDU and the aerial tip to 464. Three masses read at thumbnail size: two large round woofers, a narrow central control column, and a long, low box under a bar handle. The aerial adds the one asymmetric accent.

**Palette roles.**

| Role | Colour |
|---|---|
| Case, lid, bezels, recess floors, hidden fill | Black 0 |
| Fascia skin, keys, collars, handle grip | Pearl Silver 179 |
| Woofer cones, vent grilles, battery door | Dark Bluish Grey 72 |
| Dust caps, nameplate, aerial | Chrome Silver 383 |
| Knobs, tweeter grilles | Light Bluish Grey 71 |
| Record key, tuner needle, cassette label | Red 4 |
| Tuner scale (over white backing) | Trans Orange 57 |
| Tape-counter digits | Medium Azure 322 |
| Power / record LEDs | Trans Green 34 / Trans Red 36 |

**Focal hierarchy.** Primary: the pair of woofers, each a 6 × 6 inverted dish floating in a raised square bezel. Secondary: the cassette bay with its tape-reel tile, and the backlit tuner with its red needle. Accents: VU meters, counter, LEDs, knobs, slider pairs, tweeters, piano keys and nameplate. The bottom band, the outer columns of the top strip and the lid stay quiet.

**Depth (fascia, from the base-plate top).** Exposed base studs in the recesses sit at 0–4. The woofer rim is at 8 and the cassette and tuner at 16. The skin tiles are at 32, flush with the case frame. Bezels, tweeters and sliders stand at 40 and knobs at 48.

## Modules and interfaces

| Section | Local origin | Interface |
|---|---|---|
| `boombox.ldr` | Ground centre; front faces −Z | Case: feet, base, SNOT walls, lid, top controls |
| `boombox-fascia.ldr` | Base-plate top, 24 × 12 cells, studs −Y, up +Z | Four 12 × 6 base plates. Undersides at local Y=8 meet the 22885 studs at world Z=−20 (placed with Rx 90° at [0,−24,−28]) |
| `boombox-rear.ldr` | Same convention | Undersides meet the 30414 studs at world Z=40 (Ry 180°·Rx 90° at [0,−24,48]). Engages panel rows 1 and 7 |
| `boombox-speaker.ldr` | 8 × 8 centre on the base-plate top | Bezel ring and two 4032a spacers. The dish sockets sit on the upper spacer at −16, so the rim (−8) clears the base stud tops (−4) |
| `boombox-tweeter.ldr`, `boombox-knob.ldr` | 2 × 2 centre on the base-plate top | Round brick on four base studs |

**Grid reconciliation.** 22885 and 32952 are 40 LDU high, which is 5 plates or 2 stud pitches. Six running-bond courses therefore give a continuous 20 LDU forward grid: all 288 fascia cells have a stud behind them. The back wall uses 24 LDU bricks. Only courses 1 and 6 are 30414, because 5 × 24 = 6 × 20 places both stud rows on the panel grid. The fascia's 40 LDU thickness (plate + brick + tile) also equals 2 studs. This makes it exactly flush with the frame, so the lid plates cover its top edge and a tiled sill carries its bottom edge. The side walls carry an outward 11211 in course 8, holding `2432` strap lugs: a third SNOT direction (±X).

**Build order.** Feet and base → wall plates and smooth sills → six 22885 courses → side walls with lug mounts → back wall with two 30414 courses → fascia → rear panel → lid → keys and lid tiles → handle and aerial.

**Reference and discovery.** The SNOT method follows `docs/agent/snot.md` and the parrot head. The Jev availability check passed (`stats.api_calls` > 0). Jev part discovery was used for handle candidates, which were compared on part boards (`output/boombox-handles/`, `output/boombox-shortlist/`). No source model was copied.
