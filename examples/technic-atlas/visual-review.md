# Technic atlas visual review

Reviewed on 2026-09-26. All **28 images** were opened: home, front, back, right, left, top and bottom for each of the four examples. Each model's `visual-review.json` records its source SHA-256 and the hashes of the actual images inspected. Python and LeoCAD BOMs match for all four models.

The views were checked for silhouette, aligned holes and layer stacks, visible pin seating, body mounts, unsupported decoration and apparent intersections. Opposite views are intentionally similar on the symmetric structural examples. These are visual observations, not physical assembly or load tests.

## Reinforced frame

[Home](reinforced-frame/home.png) · [Bottom](reinforced-frame/bottom.png) · [Review record](reinforced-frame/visual-review.json)

The four yellow crossmembers read clearly against the grey moulded frame. Each has two spaced pins; the underside shows the retaining ends and the members sit against the frame without a visible gap. The compact outline leaves the construction easy to inspect.

## Box chassis

[Home](box-chassis/home.png) · [Bottom](box-chassis/bottom.png) · [Review record](box-chassis/visual-review.json)

Perpendicular frames form a readable three-dimensional skeleton. Paired connections are visible at the corners and beneath the two white body rails. The rail overhangs are intentional mounting space; their strength under load has not been assessed. Side views retain an open centre for later module placement.

## Frame tower

[Home](frame-tower/home.png) · [Bottom](frame-tower/bottom.png) · [Review record](frame-tower/visual-review.json)

Two box cells share a consistent width and alignment. External yellow beams bridge the deliberate 20-LDU gap between cells; blue long pins occupy the three-layer joints. Views from both sides and below show the bridge members meeting their supports without apparent penetration. A loaded physical tower may need a wider base; the restrained-member result does not establish overturning stability.

## Service platform

[Home](service-platform/home.png) · [Bottom](service-platform/bottom.png) · [Review record](service-platform/visual-review.json)

The white equipment body, yellow roof, black vents and clear lamps give the skeleton a visible purpose. The front tiled deck provides a quiet surface. The bottom view exposes the rail-to-deck mounts: eight stud-ended half pins support the two plates. The deck's 10-LDU X/Z offset is intentional registration between the System and Technic grids; its asymmetry is not placement drift.

During construction, the front tiles, roof vents and lamps were lowered to their actual seating heights. The retained images and source hashes describe the corrected version. No floating decoration or obvious solid intersection was seen in these views.

## Evidence and remaining checks

All four models pass their generated mounting and STEP-order contracts and form one member group under the conservative multiple-pin rule. The seven views complement those checks; they cannot show every internal surface. Swept insertion paths, hand access, manufacturing fit, strength, stiffness and loaded stability remain unproven. Follow each model's assembly guide and keep normal geometry validation alongside `technic check`.

Rebuilding an unchanged source preserves its review only when all seven image hashes also match. A changed model or replaced image makes the generator mark the review pending and remove its current-review catalog link. Open the new views before writing a new review record. The retained JSON records remain evidence of their stated revisions.
