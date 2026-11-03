# Arcade Bay

A four-stud architectural bay with a real arch, adjustable brick piers and an articulated cornice.

Run from the repository root:

```sh
.venv/bin/python examples/reference-atlas/recipes/arcade-bay/generate.py --height 5 --render --outdir output/arcade-bay
```

`--height` accepts 2–10 brick courses. `--colour` changes the structure; `--accent` changes the cornice rounds or lantern collar. Parts keep their real geometry and proper rotations. The editable [plan](scene.plan.json) exposes a positioning frame at the base underside, Y=0. It is not an inferred mechanical connector.

Both the default and changed-height forms were checked for geometry errors and a single optimistic connection group. This is computational evidence; stability, clutch strength and fit in a larger scene remain unproven. Inspect [validation.json](validation.json) and [render.json](render.json), and preserve the source credit in the plan. Compare the [home view](renders/home.png) and other saved views before placing it.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "classical-arch-bay#adjustable-recipe",
    "title": "Arcade Bay recipe",
    "scope": "construction",
    "kind": "detail",
    "aliases": [
      "reference:arcade-bay"
    ],
    "families": [
      "reference"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Fresh home view shows narrow tan arch, tall piers, round spacers and cornice. Keep adjustable-height recipe beside classical-arch-bay source; articulated means architectural detail, not motion.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/reference-audit.json",
    "scale": "display",
    "subjects": [
      "parameterized construction"
    ],
    "model": "examples/reference-atlas/recipes/arcade-bay/arcade-bay.mpd",
    "plan": "examples/reference-atlas/recipes/arcade-bay/scene.plan.json",
    "generator": "examples/reference-atlas/recipes/arcade-bay/generate.py",
    "preview": "examples/reference-atlas/recipes/arcade-bay/renders/home.png",
    "model_sha256": "4f60baebbd9cb3552ef7c68a0448985bfb00100c27645fa797aa35874a1d969d",
    "audit_pointer": "/recipes/0",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/reference-findings.md",
    "techniques": []
  }
]
```