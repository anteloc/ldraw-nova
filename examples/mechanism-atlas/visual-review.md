# Mechanism atlas visual review

Reviewed on 2026-09-26 after the final rendering corrections. Every image listed in each study's `visual-review.json` was opened: **49 build-step views and six final home previews**. The records bind the current manual, source, operation notes, checks, plan and images by SHA-256.

| Study | Opened images | Observations |
| --- | ---: | --- |
| [Gear and axle module](gear-reduction/visual-review.json) | 5 steps × home/back/top + final = 16 | The beam and pins precede gear layers, joiners, upper clutch gear and mounts. Top separates shaft stacks; back separates gear faces. The parent gearbox is needed to explain the full power path. |
| [Worm drive](worm-drive/visual-review.json) | 3 steps × home/top + final = 7 | Home reveals the worm and driven gear before the thin front beam closes the stack. Top clarifies the shaft and transverse pins, but hides much of the worm. The parent supplies the winding assembly. |
| [Steering rack](steering-rack/visual-review.json) | 3 steps × home/top + final = 7 | Lower beam, mirrored axle mounts and toothed rack are distinct additions. The driving pinion is absent from this section and must come from its parent. |
| [Piston and crank](piston-crank/visual-review.json) | 4 steps × home/right + final = 9 | Cylinder fins and bore now render correctly. Mounts, bushes and closing beam remain readable. Step 2 adds crank, rod, piston and cylinder together, immediately hiding some internals; the part list and source are essential. |
| [Differential](differential/visual-review.json) | 4 steps × home/back + final = 9 | The carrier and outputs sit inside the initial frame; later steps add drive gears and exterior beams. Home exposes bevel gears through the carrier opening. Back clarifies the transverse axis but hides depth. |
| [Driven turntable](driven-turntable/visual-review.json) | 3 steps × home/bottom + final = 7 | Frame and drive gear precede the mounts and turntable halves. Home reveals the toothed ring and upper pins; bottom reveals the rails and underside drive. |

The first piston preview showed a placeholder instead of its embedded cylinder. Inspection found that assembly-only preview extraction had discarded embedded DAT dependencies. Preview generation now retains the entire dependency closure, and a regression test checks that the renderer adapter receives the embedded part and subpart. All affected piston pages were regenerated and opened. A matching BOM alone would not have revealed this problem.

Step cameras now use the completed assembly's bounds, keeping framing stable throughout each sequence. Every final step remains inside its image. Yellow outlines make new pieces visible while earlier pieces retain their colours. Some orthographic views intentionally hide depth; they supplement the home view.

The images support construction study and agreement with the source pose. They share the source's assumptions, do not show every insertion movement, and do not demonstrate operation. Analytical mechanism verification remains deferred. The supplied parent context and operation notes identify what must be carried into a new model.
