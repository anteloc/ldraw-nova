# Boombox: sideways panels on a supported shell

Flat-built fascia and rear panel rotate onto the case’s side-stud grids. Two speaker bays, controls, handle and aerial make a recognizable object. Rear battery-door motif is decorative; knobs are printed dial tiles, not domes.

## Reproduce and adapt

Run from the repository root. Write a new plan/output so the reviewed source stays available:

```sh
.venv/bin/python examples/boombox/generate.py --plan output/boombox.plan.json
./ldraw-agent review output/boombox.plan.json
```

Keep the original source credit in the plan and MPD. Read the [design brief](design-brief.md) for local frames, actual interfaces and palette roles. Adapt the interface or module that serves the new brief; the whole silhouette is not a template. Geometry changes require new checks and isolated/parent review of the affected sections.

## Evidence and limits

392 placements; one optimistic versus 185 confirmed connection groups. Recessed speaker socket pairing needs the documented upper spacer; generic lower-spacer pairing is misleading. Panel clutch, one-stud handle attachments and retail colours remain unverified. No operating audio or door claim.

The [visual audit](evidence/visual-audit.json) records opened isolated sections and their actual parents. [Relocation records](evidence/relocation.json) map unchanged images, native recipes/manifests and reports to this package by SHA-256. Internal paths in those historical artifacts identify their original locations. The [original visual notes](history/visual-review.md) preserve revisions and coverage; exploratory outputs remain outside the package. No new physical acceptance is implied by promotion.

## Section entry points

These are addressable sections of one package. Repeated colours and logical groups do not become separate recommended models.

| Source section | Audited role |
|---|---|
| `boombox.ldr` | Recognizable portable stereo: two large round speakers, central cassette/control strip, carry handle and aerial. Retain as scoped SNOT panel-and-shell exemplar, not universal model template. |
| `boombox-fascia.ldr` | Front panel composed flat in local coordinates and mounted vertically facing outward; two speaker bays, cassette tile, meters, orange tuner strip, controls and azure printed display. |
| `boombox-rear.ldr` | Flat rear panel with central dark battery-door motif, vents and white label. Actual back view confirms placement; no opening door or hinge shown. |
| `boombox-speaker.ldr` | Raised square bezel around round inverted dish and central cap, used twice in fascia. Preserve recessed socket/upper spacer evidence and do not rely on checker lower-spacer pairing. |
| `boombox-tweeter.ldr` | Small round brick and printed grille tile form tweeter; two upper fascia instances. |
| `boombox-knob.ldr` | Flat printed dial tile on round brick/collar stack; two centre fascia instances. Not a domed knob. |

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "boombox",
    "title": "Boombox: sideways panels on a supported shell",
    "scope": "construction",
    "kind": "assembly",
    "subjects": [
      "object",
      "audio"
    ],
    "techniques": [
      "snot",
      "system"
    ],
    "families": [
      "snot",
      "object"
    ],
    "aliases": [
      "replacement:boombox"
    ],
    "legacy_groups": [
      "examples"
    ],
    "lesson": "Flat-built fascia and rear panel rotate onto the case’s side-stud grids. Two speaker bays, controls, handle and aerial make a recognizable object. Rear battery-door motif is decorative; knobs are printed dial tiles, not domes.",
    "limits": "392 placements; one optimistic versus 185 confirmed connection groups. Recessed speaker socket pairing needs the documented upper spacer; generic lower-spacer pairing is misleading. Panel clutch, one-stud handle attachments and retail colours remain unverified. No operating audio or door claim.",
    "model": "examples/boombox/boombox.mpd",
    "model_sha256": "0f7d917aa9e53d46f522e17ff184c1ff620919326fee236f01dd4792b4122e2f",
    "plan": "examples/boombox/boombox.plan.json",
    "generator": "examples/boombox/generate.py",
    "visual_review": "examples/boombox/evidence/visual-audit.json",
    "audit": "examples/boombox/evidence/visual-audit.json",
    "preview": "examples/boombox/evidence/root/home.png"
  }
]
```
