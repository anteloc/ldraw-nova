# Vehicle atlas visual and construction review

Reviewed 2026-09-23. Opened **home, front, back, right, top and bottom** PNGs for
all three final models. Each model's `visual-review.json` records the exact MPD
hash and the viewed files. This is an image review, not an automated beauty score
or physical assembly test.

| Model | Physical placements | Visual focus |
|---|---:|---|
| Grand tourer | 97 | Deep green long bonnet, short rounded tan roof, inset dark glazing and quiet rear deck |
| Delivery van | 112 | Raked six-wide cab, pale cargo body over a restrained blue belt, visible seats and steering |
| Workshop pickup | 114 | Separate pale cab roof, long open bed, dark capped rails and wood-colour floor |

## Problems found and revisions made

The first tourer render had an overlong flat roof with large eaves, a sharp step
behind the curved bonnet and exposed stud rows interrupting the shoulders.
Shortened the roof and glazing arrangement, added double-curved roof strips,
raised the rear bonnet surface to meet the curves, and tiled the shoulders.
The true side view then revealed an open slot under the curved roof; a plate
at the measured raised underside socket plane fills and supports that space.

The first tourer and van previews also showed a busy grid of small roof/deck
tiles and conspicuous studded silver bumper caps. Replaced them with wider/longer
tiles and continuous caps. The pickup uses the same surface treatment, with
long dark tiles defining the bed rim and a deliberately quiet load floor.
The van and pickup have brick-built seat cushions/backs and steering controls;
their side apertures remain open as a simple town-model construction.

The first underbody construction used identical runs of short plates. A later
connection review showed that whole body sections remained disconnected despite
the plausible side view. Replaced the spine with long two-wide plates in
staggered layers. All non-wheel/non-lamp structure now belongs to one evidenced
connection group in each model. The regression suite explicitly requires this.

The wheel/rim research also exposed the pinned library's wrong inferred rim axis
for 6014a/b. The narrow query adapter correction restores rim/tyre contacts without
changing part geometry or adding fictitious connectors. The ordinary headlight
brick's recessed side stud was measured at Z=-6; the fascia plate face is at
Z=-14 so its 8-LDU underside meets that actual plane.

## Final observations

The three silhouettes remain distinct in side view. The coupe has a short low
glazed volume, the van has a continuous cargo roof, and the pickup has an open
bed below the cab. The top views show coherent body colours and deliberate large
surfaces. Front/rear views show symmetric white headlights, red tail lamps,
matching wheels and an organized grille/bumper treatment. Underbody views show
the narrow spine and reserved wheel areas. No obvious floating body sections or
body penetration through the wheels was visible in these views.

These are compact construction lessons. Broad side/rear surfaces are deliberately
quiet; specific commissions should add their own vehicle identity and details.
The pickup's rear cab studs remain available for a later supported cab extension.
No cargo, driver, opening doors, articulated steering or suspension is claimed.

## Evidence and remaining limits

All three final sources pass assembly validation and the vehicle layout check.
The checks find four road-contact tyres, paired transverse axles, correct supported
rim/tyre offsets, no below-road geometry and no curated rectangular body entering
the tested wheel envelopes. Python and LeoCAD BOMs agree by reference, colour and
quantity. The reports and render manifests carry the same SHA-256 as each MPD.

Each geometry report retains **nine optimistic connection groups**: one complete
studded body/chassis group, four rim/tyre pairs and four round lamp plates. The
missing wheel-pin and hollow round-plate contacts are not suppressed. Wheel
positions follow the inspected wheel-pin geometry and official rim/tyre shortcut;
lamp sockets meet the inspected headlight-brick side stud. Those observations
do not prove retention, clutch strength or free rolling.

Curved fenders, slopes, glazing and SNOT interfaces still have general material
collision limits. No physical build, full solid-intersection analysis, friction
test, minifigure fit test or retail colour inventory check was performed.
`physical_validity: not_proven` remains the correct status.
