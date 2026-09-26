# Turntable frame: manual steps 31–40

A reconstruction of the subassembly on the supplied instruction pages `/tmp/build-instructions/build-33-1.png` … `build-42-1.png` (steps 31–40). The pages show a Technic frame: two light bluish grey 11L beams, a 28-tooth turntable, and four black bent liftarms forming leg frames, linked at their feet by axle joiners.

- Model: [turntable-frame.mpd](turntable-frame.mpd). Root `turntable-frame.ldr` has one LDraw STEP per manual step. The sub-build from step 37 is `turntable-frame-axle-link.ldr`, used twice.
- Generator: [generate.py](generate.py) writes [turntable-frame.plan.json](turntable-frame.plan.json). `--write-mpd` also serializes the MPD (see "Checks").
- 32 physical placements. Axes: X runs along the beams, −Z is the front, −Y is up. Hole *n* of each 11L beam is at x = (n − 6)·20.

## Part identification

Each part was described from the callout boxes, then searched with Jev (`discover search parts --construction all`, model jev-1.13.0) and offline FTS (BM25). Reports and queries are in [search/](search/). Visual comparison boards are in [shortlist/](shortlist/).

| Step | Seen in manual | Qty | Chosen part | Evidence |
|---|---|---|---|---|
| 31, 35 | grey straight liftarm, "11" callout | 2 | 32525 Technic Beam 11, LBG | Jev #1 (0.82); FTS #4 |
| 31, 38–40 | short black pin with centre collar | 4+2+2+2 | 2780 Technic Pin with Friction and Slots, black | Jev #4 (0.70). #1–3 are other friction-pin moulds; 2780 is the black slotted friction pin |
| 31 | grey 3L pin with a perpendicular hole in its middle | 1 | 87082 Technic Pin Long with Pin Hole Type 1, LBG | Jev #4 (0.76). Axle variants 27940/5713 rejected: the manual shows pin ends |
| 32 | grey straight 3-hole block with 2 pins up and 2 down | 2 | 48989 Technic Cross Block 1×3 (Pin/Pin/Pin) with 4 Pins, LBG | Jev #2 (0.62). The board showed 55615 is the bent 90° version, so rejected |
| 33, 38 | blue 3L pin, collar ⅓ from one end | 2+2 | 6558 Technic Pin Long with Friction and Slot, blue | Jev #1 (0.58) after re-query; FTS #2. The first query's "stop bush" (32054) was wrong: the collar is a normal 3L-pin collar |
| 34 | grey turntable base with side pin holes | 1 | 99009 Technic Turntable 28 Tooth Bottom, LBG | Jev #1 (0.86) |
| 34 | black 28T turntable top with two raised pin-hole ears | 1 | 99010 Technic Turntable 28 Tooth Top, black | Jev #1 (0.91); FTS #1 |
| 36, 39 | black bent liftarm: ⊕+5 holes on the long arm, 2 holes+⊕ on the short arm | 2+2 | 6629 Technic Beam 4×6 Liftarm Bent 53.13, black | Jev #5 (0.72). Hole count checked on zoomed callouts (6-4, 9 holes) |
| 37 | red 2L axle | 4 | 32062 Technic Axle 2 Notched, red | Jev #1 (0.83) |
| 37 | black 3L axle joiner with a crossing pin hole and a moulded "2" | 2 | **Substitute:** 26287 Technic Axle Joiner 3L, black | No exact match. See below |
| 40 | grey straight liftarm, "7" callout | 1 | 32524 Technic Beam 7, LBG | Jev #1 (0.79) |

**Joiner substitution.** Zooming into the step-37 sub-build shows the red axles plug into both *ends* of the black part, along its length. It is an in-line 3L axle joiner with a pin hole across its middle.
- **32184 rejected.** Cross Block 1×3 (Axle/Pin/Axle), Jev 0.76, has its axle holes across the thickness, so it can't join coaxial axles.
- **No exact match.** A 3000-candidate Jev search and FTS found no in-line joiner with a centre pin hole in the installed library. The exhaustive `--candidates 0` search timed out after 240 s. The `Unofficial` folder is empty.
- **Substitute used.** 26287 Technic Axle Joiner 3L has the same length and the same axle-to-axle role. Only the unused centre pin hole is missing, since nothing in steps 31–40 attaches to it.

## Construction (from zoomed step pictures)

- **Step 31.** Rear beam B1 at z=+20. Black pins in holes 2, 4, 8, 10 point to the rear. The 87082 goes in hole 6, with its centre hole vertical in the 1L gap.
- **Step 32.** The 48989 blocks pin into holes 1+3 and 9+11 and set the 1L spacing. Their end holes are vertical and their centre hole faces front.
- **Step 33.** Blue 3L pins in holes 5 and 7. The 1L end is in B1; the 2L end passes through the gap into B2.
- **Step 34.** Turntable base at y=−20. Its two lugs (x=±20) sit in the gap on the blue pins. The top is turned 90° so its ears face front and rear, as drawn.
- **Step 35.** Front beam B2 at z=−20.
- **Step 36.** Rear bent arms on pins 2/4 and 8/10. The axle ends are at holes 5/7. Each bend overhangs one hole past the beam end (x=±120), and the short arms form legs dropping at 53.13°.
- **Step 37.** An axle link at each leg foot (x=±156, y=48). A red axle is 1L in the leg and 1L in the joiner.
- **Step 38.** Blue 3L pins in B2 holes 2 and 10 (2L forward). Black pins in holes 4 and 8.
- **Step 39.** Front bent arms mirror the rear ones and slide onto the link axles. A forward-facing black pin goes in each bend hole.
- **Step 40.** 7L beam at z=−60, carried by black pins in its end holes. The pins go into hole 3 of each front arm (x=±60), between the blue pin stubs.

## Checks

| Check | Result |
|---|---|
| `build` gate | Refused to write: 4 `technic.invalid_seating` errors ([turntable-frame.build.json](turntable-frame.build.json)) |
| `validate --geometry --contacts all` | Exit 1: the same 4 seating errors (listed twice) and 2 warnings ([turntable-frame.validation.json](turntable-frame.validation.json)) |
| `technic check` | Exit 1: the same 4 errors, plus warnings for unreviewed parts, restraint and access ([turntable-frame.technic-check.json](turntable-frame.technic-check.json)) |
| [verify_joints.py](verify_joints.py) | 28/28 intended joints coaxial with a full 20 LDU of engagement |
| [check_turntable_clearance.py](check_turntable_clearance.py) | 0 of 5478 turntable-base points inside either beam or the 87082 hub |
| `check-model.sh` | Passed, including the LeoCAD import/export smoke test ([check-model.log](check-model.log)) |
| `compare-bom` | Python and LeoCAD match: 32/32 placements ([turntable-frame.bom-comparison.json](turntable-frame.bom-comparison.json)) |

**About the 4 seating errors.** The rule reports any coaxial pin and hole whose spans overlap by ≥ −0.2 LDU without a recognised joint. So a pin end resting *flush* against the next layer's hole face counts as "almost-mated". All four cases are that flush abutment, which is exactly what the manual builds:
- The black pins in B2 holes 4 and 8 end at z=−50, against the back face of the 7L beam's holes 2 and 6.
- The 7L beam's pins end at z=−30, against B2's holes 3 and 9. The 48989 pins already fill those holes from behind.

Removing the findings would mean moving the 7L beam or the front arms off the manual's positions. So `generate.py --write-mpd` writes the MPD with the toolkit's own `build_plan` and `atomic_write`, bypassing only the build gate. Plan-level errors still abort, and the full validation above was run on that file.

**Connectivity warning (14 groups).** The toolkit's reviewed interface registry covers the beams and pins but not 48989, 87082, 6629, 99009/99010, 26287 or 32062. Their joints are therefore not in the "confirmed" graph. The generic contacts it reports between the 48989 pins and the bent arms are pin ends touching hole entries, not joints. `verify_joints.py` checks every intended joint from the same connector metadata instead.

**Collision review.** The 50 bounding-box candidates are:
- the verified pin/axle joints;
- pin ends flush against the 48989 centre holes (x=±80);
- the turntable base against the beams and the hub, which the point check resolved. Over the beams the base's lowest points are at exactly y=−10, so it rests on the beam tops. Below that level it occupies only the 1L gap.

## Visual review

Images opened: [home](review/home.png), [front](review/front.png), [top](review/top.png), [right](review/right.png), [bottom](review/bottom.png), and [manual-angle](review-manual-angle/home.png). The manual-angle view is a preview wrapper that turns the model −90° about Y to match the manual's camera; the delivered MPD is unchanged.

Against step 40 and the page-33 preview, the manual-angle view matches:
- the U-shaped left leg frame with its link;
- the 7L beam flanked by blue pin stubs;
- the forward pins in the bend holes;
- the turntable ears front and rear;
- the red axle end on the right leg.

The right view confirms that the legs drop to the links and that the ear holes face sideways. No missing, floating or misplaced parts were found.

## Remaining limitations

- The black joiner is a substitute without the centre pin hole.
- The turntable base is shown dropping in from above (step 34), but its lugs must slide onto the already-inserted blue pins along Z. Insertion paths weren't checked beyond the manual's order.
- Point sampling is not a full mesh-intersection proof. No strength, stability or colour-availability checks were done; `physical_validity` stays `not_proven`.
