# Validation of the supported gear drive

Reviewed 2026-10-25. Source SHA-256:
`7dc910cff77cb212741f9dee7bacb6d61afa0c56c35e566108c11b7797885399`.
The generator and retained Nova/Mecha MPDs reproduce these same bytes.

| Check | Observed result |
|---|---|
| Source, transforms, references and BOM | Passed; 23 physical parts, 9 distinct references; Python and LeoCAD BOMs agree |
| Catalog coverage | All 9 references installed and have connector evidence; evidence is not an automatic motion profile |
| Scope | One control, two moving bodies of 6 parts each, 11 fixed support parts |
| Mechanical checks | 25 checks: 14 finite coaxial fits, 10 keyed rigid relations, 1 signed 8:24 phase relation |
| Pure motion | 97 positions across -6π…6π plus 0.731 radians; ratio `output = -input/3` |
| Blender 5.2.2 LTS | Six diagnostic poses and 33 evaluated timeline positions passed, then passed again in a fresh process |
| Lifecycle | Rebuild without leaks, two isolated copies, translated/rotated root, control clamps and source-pose restoration passed |
| Whole-model surface diagnostic | No new crossings in 41 positions, using 0.4-LDU inward shrink; same-body and touching pairs excluded |
| Gear tooth surfaces | No surface crossings in 1,019 samples over -6π…6π at 0.037-radian increments, with **zero** inward shrink |

Opened and inspected Nova home, front and top views and Blender views at input
angles 0.731 and -2.27 radians. The fixed rails remain outside the tooth band,
the large gear clears the base, shafts pass through the round holes, and bushes
remain with their shafts. The two rail caps bind the adjacent bearing bricks;
their one-stud end overhangs are intentional. No visible defect required a
source revision. The animated frames are checked numerically as well as these
selected views being inspected.

The source hierarchy intentionally describes the fixed frame and two rigid
shafts. Parts and colours are preserved in the motion manifest; there is no
regrouping during rigging. A separate adversarial Blender fixture verifies that
tampering with a keyed gear is detected with animation active and that checking
restores time, action and controls.

Limits: automatic source contact discovery is skipped; the starter declares
its complete 23-part scope directly, so Mecha reports missing discovery coverage.
The whole-model diagnostic excludes same-body pairs and touching contacts
`0/5–1/4` and `0/6–2/4`. The separate tooth test includes the actual gear pair.
Surface tests do not establish containment, manufactured fit, load capacity or
continuous collision freedom between samples. Axial and tooth backlash, bush
friction and small hub clearance are not simulated; the 24-tooth hub has
nominal clearance between the half-bush stops.

Reproduce source review with the commands in [README](README.md). In Mecha,
use `scripts/gear_drive.py`, strict `check`, and `rig --animate --reopen`.
For the extra diagnostics, run Blender in the background with the saved blend:

```sh
blender --background output/gear-drive/rigged.blend --python-exit-code 1 \
  --python scripts/blender/check_clearance.py -- \
  --plan output/gear-drive/plan.json --controls drive --steps 41 \
  --report output/gear-drive/clearance.json
blender --background output/gear-drive/rigged.blend --python-exit-code 1 \
  --python scripts/blender/sweep_contact.py -- \
  --plan output/gear-drive/plan.json --control drive --pair 1/1 2/1 \
  --range -18.84955592153876 18.84955592153876 0.037 --shrink 0 \
  --report output/gear-drive/tooth-clearance.json
```

The inspected run lives under `output/gear-drive-demo/` in Mecha and
`output/gear-drive-review/` in Nova. Generated output can be removed without
losing the maintained source, recipe or these validation limits.
