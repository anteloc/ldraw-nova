# Reinforced mounting frame

Four crossmembers, each attached at two separated points, reinforce a moulded frame.

This is a static structural example. Parts are unscaled. Pin grips and the mounting pairs in `structure.json` are checked against the reviewed registry. `scene.plan.json` and `generate.py` reproduce the model. The contract uses physical occurrence indices in the generated source and binds to its model revision.

## Assembly order and access

Insert the pins into the moulded frame first. Bring each crossmember onto its two projecting pins. Keep both holes aligned and seat the member against the frame; never bend a crossmember to close a mismatch.

Keep pins in their retaining seats and support loose subassemblies while closing the frame. STEP checks verify connector-before-closure order. Insertion paths, hand access, manufacturing fit and loads still require a physical build or further manual inspection.

## Mounting and appearance

Use the measured hole ports, not the outside bounding box, to attach another module. Preserve both connections of each crossmember. The palette separates the grey structure, yellow reinforcement and black pins; white rails identify the body support plane where present. Blue pins identify the selected long-pin variant by convention only—the registry determines its type.

Inspect all seven views, especially the bottom and the hidden face of each mounting pair. Bracing checks use a conservative multiple-pin rule; strength, overturning stability and mechanism behavior are not certified. The tower may need a wider base for a real load.

## Current evidence

- Source SHA-256: `5adb4bec0c0bb444afe9ee8936e905b9bbc5f80eaebaf3cab2cb2143a646c31a`
- Physical placements: 13
- Reviewed mechanical contacts: 16
- Structural member groups after the multiple-pin rule: 1
- Required mounting pairs: 16
- Physical validity: **not proven**.

Run `./ldraw-agent technic check examples/technic-atlas/reinforced-frame/reinforced-frame.mpd --contract examples/technic-atlas/reinforced-frame/structure.json` from the repository root. Also run normal `validate --geometry`; a seating check cannot waive unrelated solid intersections.
