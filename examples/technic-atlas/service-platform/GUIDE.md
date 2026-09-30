# Service platform

A System equipment body and tiled deck mount on a Technic skeleton through eight stud-ended pins.

This is a static structural example. Parts are unscaled. Pin grips and the mounting pairs in `structure.json` are checked against the reviewed registry. `scene.plan.json` and `generate.py` reproduce the model. The contract uses physical occurrence indices in the generated source and binds to its model revision.

## Assembly order and access

Build the box chassis and fit its two rails. Insert the eight half pins from above, leaving their studs exposed. Press each deck plate onto its four mounts. Add the front deck tiles, equipment housing walls, roof, vents and lamps. The System grid is offset by 10 LDU in X/Z relative to the frame grid; preserve the supplied coordinates.

Keep pins in their retaining seats and support loose subassemblies while closing the frame. STEP checks verify connector-before-closure order. Insertion paths, hand access, manufacturing fit and loads still require a physical build or further manual inspection.

## Mounting and appearance

Use the measured hole ports, not the outside bounding box, to attach another module. Preserve both connections of each crossmember. The palette separates the grey structure, yellow reinforcement and black pins; white rails identify the body support plane where present. Blue pins identify the selected long-pin variant by convention only—the registry determines its type.

Inspect all seven views, especially the bottom and the hidden face of each mounting pair. Bracing checks use a conservative multiple-pin rule; strength, overturning stability and mechanism behavior are not certified. The tower may need a wider base for a real load.

## Current evidence

- Source SHA-256: `1a4da42ba87b08fa4c04ee29ed43227a654037229f264e04a14814c1f4d6c3b2`
- Physical placements: 55
- Reviewed mechanical contacts: 32
- Structural member groups after the multiple-pin rule: 1
- Required mounting pairs: 40
- Physical validity: **not proven**.

Run `./ldraw-agent technic check examples/technic-atlas/service-platform/service-platform.mpd --contract examples/technic-atlas/service-platform/structure.json` from the repository root. Also run normal `validate --geometry`; a seating check cannot waive unrelated solid intersections.
