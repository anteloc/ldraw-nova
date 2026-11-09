# Integration notes (orchestrator)

## r0 — 18:15, mid-work snapshots (H5 final, H1–H4 partial)
Images opened: integration/r0-whole/panels/01-home-view.png, 02-front-view.png.
- Build: checks_passed, 1397 parts, no cross-module overlap errors. Anchor stacking correct (roof top Y≈-684).
- Bounds min Z -338: something protrudes 18 LDU beyond the baseplate front edge (-320) — likely tree canopy (H5 noted).
- street: the two lamp posts stand directly in front of the café shopfront (X≈±4, Z -13) and hide door/display glazing in the front view → move lamps outward (|X| ≥ 8).
- floor2: bay window reads as a blank white box with one small window; weak focal point (H2 still working).
- ground: shopfront largely hidden behind awning in the front view; fascia/sign centre shows a white gap.
- floor3: balcony + railing + French doors read well; tan cornice good.
- roof: pergola, stair-house, chimney, planters present; good crown.

## r1 — 18:19–18:22, all five modules final (phase B)
Build: checks_passed, 1361 parts, no cross-module overlap/duplicate errors; anchors exact.
Contacts (--contacts all): 76 groups, main 1211 (89 %). Outside main group:
- analyzer blind spots (accepted): clipped glass panes 60608/3854/60797c04 (~32), round plates/flowers on tiles.
- REAL: floor2 + floor3 centre column of 3034 slab plates (X 0, rows Z -5..+3) rest on nothing — the
  storey below only has a perimeter ring; plus everything standing on them (rug, furniture).
- REAL: floor3 front strip plates 3460/3710 at local Z -6.5 unsupported.
- REAL: street props stand on tiles (no studs): 2 trees, 2 lamps, planters, bench, bins, hydrants.
Images opened: r1/whole/panels 01-home, 02-front, 03-back, 04-right.
Visual:
- ground: shopfront reads weak — grey wall with two small windows + door; no large display glazing, no
  visible sign, flat awning; white gap in the green fascia above the door.
- floor2: bay window reads as a flat white panel with one small window, not a glazed bay.
- floor3: balcony + French doors + flanking tall windows good; side walls have no windows.
- roof: grey deck-slab edge shows as a grey band under the white cornice on all sides; parapet is a plain
  red band; pergola / stair-house / chimney good.
- street: both lamps stand directly in front of the café, hiding door/glazing; tree canopy pokes past
  plot front edge (bounds Z -338 < -320).
→ Phase D round 1: repair messages to H1–H5 (parallel).

## r2 — 18:29–18:32, after D1
Build checks_passed, 1401 parts; contacts 47 groups, main 1355 (96.7 %). Outside main: only glass panes
(60608/3854/60797c04), 6141 stool seats / urn caps, 2 lamp finials — all analyzer blind spots or trivial.
Slab plates, props, awning, sign: all now in the main group.
Images opened: r2/whole/panels 01-home, 02-front, 03-back, 04-right.
Visual:
- ground: big improvement — green glazed shopfront, yellow sign band, sloped green/white striped awning.
- roof: dentil course + central pediment + urns; front deck edge white. Thin grey strip still visible on sides/back under the parapet.
- floor3: side + rear windows added; good.
- floor2: bay now a white box with three narrow slit windows — still the weakest element.
- street: props seated, trees inside plot, BUT lamps rebuilt as heavy black 2x2 stacked columns that read as bollards/chimneys — visual regression vs the original fluted lamp(). Back fence reads as an odd open brown frame from the back.
→ D2 (final round): H2 bay glazing, H5 lamps + back fence, H4 grey strip.
