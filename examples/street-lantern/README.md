# Street Lantern

A stud-mounted lantern with a thin round-brick post, a transparent light, an open-stud collar and an inverted-dish shade.

Run from the repository root:

```sh
.venv/bin/python examples/street-lantern/generate.py --height 5 --render --outdir output/street-lantern
```

`--height` accepts 2–10 brick courses. `--colour` changes the structure; `--accent` changes the cornice rounds or lantern collar. Parts keep their real geometry and proper rotations. The editable [plan](scene.plan.json) exposes a positioning frame at the base underside, Y=0. It is not an inferred mechanical connector.

Both the default and changed-height forms were checked for geometry errors and a single optimistic connection group. This is computational evidence; stability, clutch strength and fit in a larger scene remain unproven. Inspect [validation.json](validation.json) and [render.json](render.json), and preserve the source credit in the plan. Compare the [home view](renders/home.png) and other saved views before placing it.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "street-lantern",
    "title": "Street Lantern recipe",
    "scope": "construction",
    "kind": "assembly",
    "aliases": [
      "reference:street-lantern"
    ],
    "families": [
      "reference"
    ],
    "legacy_groups": [
      "examples",
      "details"
    ],
    "lesson": "Fresh home view shows narrow round-brick post, open collar, translucent yellow lamp, inverted dish cap and square foot. Keep adjustable-height recipe.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/reference-audit.json",
    "scale": "minifigure",
    "subjects": [
      "parameterized construction"
    ],
    "model": "examples/street-lantern/street-lantern.mpd",
    "plan": "examples/street-lantern/scene.plan.json",
    "generator": "examples/street-lantern/generate.py",
    "preview": "examples/street-lantern/renders/home.png",
    "model_sha256": "f471460690ce9202147f9e27f6319a7ab3588e0dba900ff723b043617350a240",
    "audit_pointer": "/recipes/1",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/reference-findings.md",
    "techniques": []
  }
]
```