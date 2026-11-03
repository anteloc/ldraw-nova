# Canopy cockpit

Read the registered construction lesson and its linked audit before adapting the source.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "canopy-cockpit",
    "title": "Octagonal cockpit enclosure and shaped closure",
    "scope": "construction",
    "kind": "detail",
    "aliases": [
      "spaceship:canopy-cockpit"
    ],
    "families": [
      "spaceship"
    ],
    "legacy_groups": [
      "details"
    ],
    "lesson": "Octagonal side halves frame a shaped central door spanning the top/front. Study enclosure and pilot envelope; the pilot and helmet are nested context, not separate recommended constructions. Hinge motion and clearance remain unverified.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/spaceship-audit.json",
    "subjects": [
      "cockpit"
    ],
    "model": "examples/spaceship-atlas/canopy-cockpit/source.mpd",
    "plan": "examples/spaceship-atlas/canopy-cockpit/scene.plan.json",
    "generator": "examples/spaceship-atlas/canopy-cockpit/generate.py",
    "preview": "examples/spaceship-atlas/canopy-cockpit/renders/home.png",
    "manual": "examples/spaceship-atlas/canopy-cockpit/index.html",
    "study_notes": "examples/spaceship-atlas/canopy-cockpit/study-notes.json",
    "visual_review": "examples/spaceship-atlas/canopy-cockpit/visual-review.json",
    "model_sha256": "6b882983b13fe53b055e127ecb3973b568e4aa535c1f8e151c0330414ead818d",
    "audit_pointer": "/items/1",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/spaceship-findings.md",
    "techniques": []
  }
]
```

## Audited section observations

These observations refer to the source hashes in the registrations. They correct earlier source descriptions and preserve static visual scope; existing numeric and export checks remain separate.

### Octagonal cockpit enclosure and shaped closure

| Source section | Opened-image observation |
|---|---|
| `study-81a8902a5014-00-6887---Spaceship---Cockpit.ldr` | Octagonal transparent side halves enclose seated pilot; hinged central glazing closes top/front. Actual parent places cockpit forward of craft. Correct rear-glazing wording. |
| `study-81a8902a5014-01-6887---Spaceship---Cockpit---Door.ldr` | Hinged central canopy closure has transparent shaped panel, cone pair and inward tool-holder detail. Extra right/back context views confirm top/front location, not a rear window. |
| `study-81a8902a5014-02-6887---Minifig.ldr` | Seated helmeted pilot with raised visor is inside the cockpit; retained as occupant-envelope context, not independent vehicle structure. |
| `study-81a8902a5014-03-6887---Minifig---Helmet.ldr` | Black helmet and green raised visor; inspected alone and on pilot. |
