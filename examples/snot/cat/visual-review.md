# Review of the prepared cat

Reviewed 2026-10-21 with pyldraw3 1.7.0, the configured official library, supplied LDCad shadows and LeoCAD. The three JSON plans are the editable sources. All original 55 parts and colours are retained, allowing the construction to be studied independently of a redesign.

## Checks

| Evidence | Head | Leg | Complete cat |
|---|---:|---:|---:|
| Physical placements | 16 | 3 | 55 |
| Source/geometry errors | 0 | 0 | 0 |
| Geometry resolved | All | All | All |
| Python/LeoCAD BOM | Match | Match | Match |
| Automatic optimistic groups | 1 | 1 | 4 |

Review artifacts are in `output/snot-cat-head/`, `output/snot-cat-leg/` and `output/snot-cat-cat/`. The MPDs beside this note are byte-identical to their reviewed outputs. All eight head construction stages were also rendered into `output/snot-cat-head-steps/index.html`.

## Images actually inspected

- Source cat: `output/cat-snot-assessment/previews/home.png` and `right.png`.
- Comparison model: `output/boombox-review/previews/home.png`, alongside its design brief, generator and review notes.
- Prepared head: `output/snot-cat-head/previews/{home,top,bottom}.png`.
- Prepared leg: `output/snot-cat-leg/previews/{home,bottom}.png`.
- Prepared cat: `output/snot-cat-cat/previews/{home,front,back,right,top,bottom}.png`.
- Head stages: all eight `output/snot-cat-head-steps/manual/00/step-NNN-home.png` images and `step-001-bottom.png`.
- Both pages of LEGO's [official instruction sheet](https://www.lego.com/cdn/product-assets/product.bi.core.pdf/6310454.pdf), including head steps 11–18 and limb/tail construction.

The stage views expose the ear pivots before the eyes cover them. The head underside shows the neck ball and rear curve. The complete model's side and bottom views show the four paw bars, hip positions, shallow head and tail contour. The small seating corrections preserve the supplied silhouette; no aesthetic redesign was attempted.

## Design lessons

The cat is useful even when its style is unsuitable for the next model. Its large eyes make the face legible at small size, the orange/tan ear contrast clarifies a simple diagonal, and the curved tail reads well from the side. Those are transferable choices.

Its side view also exposes the compromises: the face is thin compared with its broad front silhouette, gray hip joints dominate the small body, and the straight repeated legs give this pose a stiff appearance. For a model intended to look more organic, plan head depth as well as width, use body shaping to visually integrate the joints while leaving articulation clearance, and review the stance from the side. Enlarging the eyes or adding more surface detail alone will not address those proportions.

For non-animal models, transfer the angled trim, layered focal detail and joint-based module placement. The boombox already demonstrates large perpendicular panels and repeated stud grids; the cat contributes smaller shapes and interfaces rather than a replacement workflow. The guide links these specific lessons without treating the cat's styling as a quality target.

## Why the automatic graph has four groups

The groups contain 48 parts, the four-part belly, the central tail axle, and the two-part upper tail. The [supplemental evidence](interface-evidence.json) records six interfaces:

| Interface | Evidence | Automatic coverage gap |
|---|---|---|
| Two `32803` belly curves to four `14417` hip plates | Four coincident stud/socket entries, opposed axes | The socket is at local Y=8; the ball extends the same part's box to Y=12. pyldraw's extreme-box-face test rejects this recessed entry. |
| `32062` axle to both `25214` elbows | Shared entry centre, aligned axes and keyed roll; nominal hole intervals `[-20,0]` and `[0,20]` | The axle has a reviewed Technic port; the elbow is outside that registry. Mixed reviewed/unreviewed mechanical pairs intentionally do not generate automatic contacts. |

These inspected relationships join the reported graph into one group if added as reference-specific evidence. They are not added to automatic validation. The elbow's authored profile has a 4 LDU round lead-in followed by a 16 LDU keyed span; the evidence uses nominal connector dimensions, not a manufacturing fit measurement.

Tests recompute the diagonal stud seating, six ball centres, four clip/bar centres and supplemental interfaces, check every prepared transform against the source, and detect a detached ear. The prepared ankle centres coincide exactly; the approximately 0.19 LDU source mismatch is recorded rather than hidden behind a larger tolerance.

`physical_validity` remains `not_proven`. Irregular-part material clearances, retention strength, available colours and allowed articulation ranges are not certified by these checks. The model is a reviewed construction reference, not a mechanism simulation.
