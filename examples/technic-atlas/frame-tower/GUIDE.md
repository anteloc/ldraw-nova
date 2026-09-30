# Frame tower

Repeated box cells joined with overlapping beams and shared three-layer pins.

This is a static structural example. Parts are unscaled. Pin grips and the mounting pairs in `structure.json` are checked against the reviewed registry. `scene.plan.json` and `generate.py` reproduce the model. The contract uses physical occurrence indices in the generated source and binds to its model revision.

## Assembly order and access

Build each box cell from one side frame, the horizontal frames and the opposite side frame. Use the specified long pins where a bridge beam adds a third layer; their unused ends must face that beam. Bring neighboring cells to their final spacing, then fit the external bridge beams onto their projecting pins. The STEP constraints describe subassembly order; keep the cells supported during assembly.

Keep pins in their retaining seats and support loose subassemblies while closing the frame. STEP checks verify connector-before-closure order. Insertion paths, hand access, manufacturing fit and loads still require a physical build or further manual inspection.

## Mounting and appearance

Use the measured hole ports, not the outside bounding box, to attach another module. Preserve both connections of each crossmember. The palette separates the grey structure, yellow reinforcement and black pins; white rails identify the body support plane where present. Blue pins identify the selected long-pin variant by convention only—the registry determines its type.

Inspect all seven views, especially the bottom and the hidden face of each mounting pair. Bracing checks use a conservative multiple-pin rule; strength, overturning stability and mechanism behavior are not certified. The tower may need a wider base for a real load.

## Current evidence

- Source SHA-256: `570e01297b7ed08d6379e7145d528bfb6b67481c856b8376f1793d40992be892`
- Physical placements: 36
- Reviewed mechanical contacts: 56
- Structural member groups after the multiple-pin rule: 1
- Required mounting pairs: 56
- Physical validity: **not proven**.

Run `./ldraw-agent technic check examples/technic-atlas/frame-tower/frame-tower.mpd --contract examples/technic-atlas/frame-tower/structure.json` from the repository root. Also run normal `validate --geometry`; a seating check cannot waive unrelated solid intersections.
