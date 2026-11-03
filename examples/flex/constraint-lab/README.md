# Learn constraints by measuring actual LSynth output

These small geometry experiments make the effects of marker choices visible.
They are not mounted mechanisms. Use the [pneumatic press](../pneumatic-press/README.md)
for an assembly with real fittings and supports, and the
[constraint guide](../../../docs/agent/guides/flex.md) for the authoring and repair process.

```sh
.venv/bin/python examples/flex/constraint-lab/generate.py --outdir output/flex-lab
./ldraw-agent review output/flex-lab/corner-32/asset.mpd \
  --outdir output/flex-lab/corner-32/review --contacts none
```

Open the generated views. The corner and return layouts use shared `corner_waypoints` and
`return_waypoints` helpers from `ldraw_tools.flex_authoring`; `offset_waypoints`
translates a control layout for a parallel route. These helpers do not predict
the synthesized radius. Each experiment retains its constraints, generated
asset and manifest, constraint report and actual-geometry report. `results.json`
collects the measurements. Use a new output directory, or explicitly `--force`
to overwrite generated experiment files. An expected failed geometric check
remains in the results; it does not prevent inspecting the generated shape.

| Experiment | Question |
| --- | --- |
| Straight | Are endpoint directions and the 22 LDU leads correct? |
| Corners with nominal radii 6, 24, 32, 48 | What bend does the real output produce? Nominal geometry and output radius differ. |
| Corner 32 with a midpoint | Does an extra marker help? In this fixture it tightens the bend. |
| Two parallel corners | Do routes 12 LDU apart stay separated? |
| Return loop | Can a deliberate loop reverse travel without a local hairpin? |

| Tight corner: rejected | Larger corner: accepted geometric limit |
| --- | --- |
| ![Tight corner](corner-6.png) | ![Larger corner](corner-32.png) |

| Return loop | Parallel pair |
| --- | --- |
| ![Return loop](return.png) | ![Parallel pair](bundle.png) |

These home images were opened, along with the top views. The top views look
edge-on at these XY-plane routes and cannot show the bends properly. Source,
asset and image hashes are retained in [visual-review.json](visual-review.json).
Normal source/BOM review passes even for the tight corner; the separate bend
check correctly rejects it. This distinction is part of the lesson.

The test criterion is a **geometric** minimum radius of 15 LDU and a round tube
radius of 5 LDU for the beveled pneumatic definition. These are not universal
LEGO material limits. The 6 LDU corner must fail. The larger baseline fixtures
pass those criteria; inspect their actual appearance too. Tests exercise rigidly
rotated/transformed versions and deliberately invalid input separately.

To exercise every installed synthesis definition:

```sh
.venv/bin/python examples/flex/constraint-lab/generate.py \
  --outdir output/flex-families --families
```

This generates straight hose fixtures and simple loop fixtures. It is a smoke
test for definition discovery, authoring, packaging and measurement, **not**
approval of wheel compatibility, manufactured lengths, motion or all shapes in
a family. Errors are retained explicitly. BRICK_ARC in the tested 3.1.0 engine
emits reflected physical bricks; source validation rejects those placements.
Do not relax the validator to make its example pass.

For agent evaluation, start from the guide and these sources, then request an
unseen rotated fitting, changed passage or second nearby route. Require the
actual generated output, checks and opened contextual previews. Record repair
count, elapsed active time and any expert intervention. Passing the software
tests establishes tool behaviour; independent agent competence must still be
measured on these adaptation tasks.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "flex-constraints#straight",
    "title": "Straight",
    "scope": "diagnostic",
    "kind": "detail",
    "aliases": [
      "constraint-lab:straight"
    ],
    "families": [
      "flex"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Straight cylindrical route with enlarged sleeves at each end; no bend.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/constraint-lab-findings.md",
    "generator": "examples/flex/constraint-lab/generate.py",
    "techniques": [
      "flex"
    ],
    "subjects": []
  },
  {
    "id": "flex-constraints#corner-6",
    "title": "Corner 6",
    "scope": "diagnostic",
    "kind": "detail",
    "aliases": [
      "constraint-lab:corner-6"
    ],
    "families": [
      "flex"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Tight L-shaped route with visibly abrupt inner bend; preserve expected failure.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/constraint-lab-findings.md",
    "generator": "examples/flex/constraint-lab/generate.py",
    "techniques": [
      "flex"
    ],
    "subjects": []
  },
  {
    "id": "flex-constraints#corner-24",
    "title": "Corner 24",
    "scope": "diagnostic",
    "kind": "detail",
    "aliases": [
      "constraint-lab:corner-24"
    ],
    "families": [
      "flex"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Rounded right-angle route with straight end approaches; accepted narrowly above fixture minimum.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/constraint-lab-findings.md",
    "generator": "examples/flex/constraint-lab/generate.py",
    "techniques": [
      "flex"
    ],
    "subjects": []
  },
  {
    "id": "flex-constraints#corner-32",
    "title": "Corner 32",
    "scope": "diagnostic",
    "kind": "detail",
    "aliases": [
      "constraint-lab:corner-32"
    ],
    "families": [
      "flex"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Broader rounded corner in existing home view; sampled radius differs from nominal helper radius.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/constraint-lab-findings.md",
    "generator": "examples/flex/constraint-lab/generate.py",
    "techniques": [
      "flex"
    ],
    "subjects": []
  },
  {
    "id": "flex-constraints#corner-48",
    "title": "Corner 48",
    "scope": "diagnostic",
    "kind": "detail",
    "aliases": [
      "constraint-lab:corner-48"
    ],
    "families": [
      "flex"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Broad smooth corner with long end approaches; greatest sampled radius among corner baselines.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/constraint-lab-findings.md",
    "generator": "examples/flex/constraint-lab/generate.py",
    "techniques": [
      "flex"
    ],
    "subjects": []
  },
  {
    "id": "flex-constraints#corner-32-midpoint",
    "title": "Corner 32 midpoint",
    "scope": "diagnostic",
    "kind": "detail",
    "aliases": [
      "constraint-lab:corner-32-midpoint"
    ],
    "families": [
      "flex"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Extra midpoint produces a more angular, tighter two-stage bend than baseline 32; preserve as counterexample to more markers being better.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/constraint-lab-findings.md",
    "generator": "examples/flex/constraint-lab/generate.py",
    "techniques": [
      "flex"
    ],
    "subjects": []
  },
  {
    "id": "flex-constraints#bundle",
    "title": "Bundle",
    "scope": "diagnostic",
    "kind": "detail",
    "aliases": [
      "constraint-lab:bundle"
    ],
    "families": [
      "flex"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Two distinct parallel red corners, both individually visible with separate sleeves and a gap; same-frame comparison fixture, no supporting hardware.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/constraint-lab-findings.md",
    "generator": "examples/flex/constraint-lab/generate.py",
    "techniques": [
      "flex"
    ],
    "subjects": []
  },
  {
    "id": "flex-constraints#return",
    "title": "Return",
    "scope": "diagnostic",
    "kind": "detail",
    "aliases": [
      "constraint-lab:return"
    ],
    "families": [
      "flex"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "U-shaped return with deliberate broad loop and separate ends; reversal has real routing space, not an instantaneous tangent flip.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/constraint-lab-findings.md",
    "generator": "examples/flex/constraint-lab/generate.py",
    "techniques": [
      "flex"
    ],
    "subjects": []
  }
]
```