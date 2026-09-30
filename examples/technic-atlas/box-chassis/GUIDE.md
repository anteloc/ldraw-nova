# Box chassis

Perpendicular frames and two long rails establish structure in three dimensions.

This is a static structural example. Parts are unscaled. Pin grips and the mounting pairs in `structure.json` are checked against the reviewed registry. `scene.plan.json` and `generate.py` reproduce the model. The contract uses physical occurrence indices in the generated source and binds to its model revision.

## Assembly order and access

Prepare the left side frame with its inward-facing pins. Add the upper and lower horizontal frames from the side. Insert the opposite pins, then bring the right side frame onto all four ends together. Insert the upper rail pins before lowering the two rails into place.

Keep pins in their retaining seats and support loose subassemblies while closing the frame. STEP checks verify connector-before-closure order. Insertion paths, hand access, manufacturing fit and loads still require a physical build or further manual inspection.

## Mounting and appearance

Use the measured hole ports, not the outside bounding box, to attach another module. Preserve both connections of each crossmember. The palette separates the grey structure, yellow reinforcement and black pins; white rails identify the body support plane where present. Blue pins identify the selected long-pin variant by convention only—the registry determines its type.

Inspect all seven views, especially the bottom and the hidden face of each mounting pair. Bracing checks use a conservative multiple-pin rule; strength, overturning stability and mechanism behavior are not certified. The tower may need a wider base for a real load.

## Current evidence

- Source SHA-256: `939934608f422cd4cab8aecb1232f392f33d39282eb51da04c2c3672e84fd708`
- Physical placements: 18
- Reviewed mechanical contacts: 24
- Structural member groups after the multiple-pin rule: 1
- Required mounting pairs: 24
- Physical validity: **not proven**.

Run `./ldraw-agent technic check examples/technic-atlas/box-chassis/box-chassis.mpd --contract examples/technic-atlas/box-chassis/structure.json` from the repository root. Also run normal `validate --geometry`; a seating check cannot waive unrelated solid intersections.
