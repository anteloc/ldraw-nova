# Final visual review

Final assembly: `frame-drive.mpd`, SHA-256 `6b4befd5a661dda9aab3ee65e404ec12605af36ec210ce9baa0fe97eb2207669`. This is byte-identical to `scene-review/model.mpd`. It contains 57 physical placements, including 24 rigid chain links.

All seven final contextual previews were opened with the image tool after the last geometry edit: `scene-review/previews/home.png`, `front.png`, `back.png`, `right.png`, `left.png`, `top.png`, and `bottom.png`.

- Home: the grey frame, four yellow crossmembers, blue bearing rails, chain and red hand control form one mounted assembly. The chain plane clears the outboard rail; no unsupported juxtaposed module is visible.
- Bottom and top: both shafts cross the paired rails; the output also passes through the aligned moulded-frame side holes. Bushes meet the outside bearing faces. The extra half bush outside the hand knob is visible in the final revision. The crossmembers remain seated on their pin pairs.
- Right: the two equal sprockets and both straight chain runs are visible. The loop wraps both wheels without an obvious large gap or crossing. Exact link engagement, seam fit and tension are not established by this image.
- Left: the keyed red knob is accessible outside the left bearing rail; the opposite output tip remains exposed. Two spaced mounting pins are visible in each rail's frame region.
- Front and back: the axial stacks and separation between the chain plane and frame are visible. No obvious wheel/rail material intersection appears.

The fixed module's `frame-review/previews/home.png`, `bottom.png` and `left.png` were also opened. Its geometry and source hash were unchanged by the subsequent drive-only correction, so these views remain current.

All eight final frame manual pages were opened: `frame-manual/manual/00/step-001-home.png` through `step-004-home.png`, and the corresponding four `bottom` views. The final `frame-manual/renders/home.png` was opened too. The pages show the moulded frame, twelve independent pins, the four closing crossmembers, then the two closing rails. Pins project toward the later members; the rails each use two separated sideways pin axes. The documented manual-review command records these exact nine images and binds them to the final manual's hashes.

One visual-review-to-source correction was made: revision 1 lacked an outside stop for the hand knob. Revision 2 adds that half bush and moves the complete chain plane inward by 10 LDU, with revised adjacent bushes and shaft centring. Sprocket dimensions and their 120-LDU separation are preserved. All final contextual images were reopened after this edit.

Automatic geometry, flexible-source/synthesis checks, 24 fixed mounting joints, 12 connector-before-closure constraints, and a separate 32-required-joint shaft seating/retention witness pass. The witness's two bearing-rotation warnings are intended freedoms. The full moving assembly follows the documented `--contacts none` mechanism workflow; its general connector contacts are therefore not computed. Frame and shaft-support modules use automatic/all contacts respectively.

Physical validity remains **not proven**: these checks and images do not certify motion, strength, manufacturing fit, complete material collision freedom, swept insertion paths, dynamic chain engagement, tension or retail colour availability. This is a construction-only delivery, with analytical motion verification deferred.
