# Constraint lab: preserve a measured tutorial

All eight fixtures (nine routes, including both bundle members) were visually inspected. Four existing images were reused after source/output/image hash checks; four missing views were rendered with global `ldraw-xray`. Constraints and assets for every case match the stored synthesis manifests and results. No regeneration or numeric test rerun was needed.

| Case | Observed lesson | Recorded sampled radius / result |
|---|---|---|
| Straight | Straight route with distinct end sleeves | No bend; pass |
| Corner 6 | Abrupt tight L bend | 5.829 LDU; expected fail |
| Corner 24 | Rounded bend, limited margin | 15.736 LDU; pass |
| Corner 32 | Broader baseline corner | 20.593 LDU; pass |
| Corner 48 | Broadest baseline corner | 38.678 LDU; pass |
| Corner 32 + midpoint | Extra marker tightens and changes bend shape | 16.642 LDU; pass |
| Parallel pair | Both separate routes and sleeves visible | 38.678 LDU each; pass |
| Return | Deliberate U loop reverses direction | 38.678 LDU; pass |

These results use a chosen geometric minimum radius of 15 LDU and round tube radius of 5 LDU. They are not universal material specifications. The tutorial should contrast the 32 baseline with its midpoint variant and keep the 6 failure prominent. Source/BOM success alone does not accept a bend.

Keep one tutorial package with eight small variants, not eight independent ranked design recommendations. Retain generator, constraints, generated result, measurements and purposeful images together. Link it from the flex authoring guide and mounted examples. Generated DAT route sections are posed parts; LS22/LS23 embedded primitives are dependencies, not curated assemblies. These fixtures contain no mounting hardware or physical parent beyond their display wrapper; do not advertise nozzle seating or mechanism clearance.

Fresh front views use LeoCAD fallback framing because embedded route bounds are unavailable. The curves are visible; edge-adjacent sleeves and independently fitted images are unsuitable for visual dimension comparison. Measurements above come from stored hash-matched reports, not screenshot scaling. [Per-case evidence](constraint-lab-audit.json).
