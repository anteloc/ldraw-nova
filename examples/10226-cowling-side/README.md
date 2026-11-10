# Biplane fuselage side wall: one-stud brick wall on a plate strip with hinge plates and a reinforced panel

A biplane fuselage side as a one-stud-thick wall: dark-tan 1×4 and 1×1 bricks on a 1×8 plate strip, two 1×4 hinge-plate pairs so the wall folds to the fuselage taper, a reinforced 1×4×3 panel as the cockpit side, and a 1×1×3 clip brick that anchors a rigging string. Rebuild the technique: a one-stud wall with hinge plates at the ends lets a plate-built fuselage taper in plan; use a reinforced panel where the wall needs to be thin but stiff.

Read [GUIDE.md](GUIDE.md) for the construction, what the parent supplies, how to read the board and the limits; [index.html](index.html) holds the build pages. Source: `10226-1.mpd` / `10226 - step34.ldr` (placed by `10226 - main.ldr`). Style: display SNOT biplane. Atlas: [examples/aircraft-atlas](../aircraft-atlas/README.md).

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "10226-cowling-side",
    "title": "Biplane fuselage side wall: one-stud brick wall on a plate strip with hinge plates and a reinforced panel",
    "scope": "inspiration",
    "kind": "detail",
    "aliases": [
      "aircraft:10226-cowling-side"
    ],
    "families": [
      "aircraft"
    ],
    "legacy_groups": [
      "details"
    ],
    "lesson": "A biplane fuselage side as a one-stud-thick wall: dark-tan 1×4 and 1×1 bricks on a 1×8 plate strip, two 1×4 hinge-plate pairs so the wall folds to the fuselage taper, a reinforced 1×4×3 panel as the cockpit side, and a 1×1×3 clip brick that anchors a rigging string. Rebuild the technique: a one-stud wall with hinge plates at the ends lets a plate-built fuselage taper in plan; use a reinforced panel where the wall needs to be thin but stiff.",
    "limits": "Inspiration only: the rigging-string child is LDCad segments with mirrored matrices and two plates overlap by 0.0001 LDU (assembly.nonrigid, assembly.library_internal, assembly.body_overlap), so source checks fail and export is blocked. The hinge angles were not checked. The source and renders teach a construction. They do not prove clutch, fit, clearance, travel or stability. Boards are rendered from synthetic inspection copies, and poses are rigid re-placements.",
    "subjects": [
      "Aircraft fuselage skin",
      "cowling",
      "fuselage"
    ],
    "techniques": [
      "snot"
    ],
    "style": "display SNOT biplane",
    "origin": {
      "model": "10226-1.mpd",
      "section": "10226 - step34.ldr",
      "parent": "10226 - main.ldr",
      "sha256": "2903c00bd3f1e0af46d47af2e09bd8ccb423eced0588947cc0fb9bd14ac20511",
      "discovery_id": "submodel-32ad4c86bdb0ac328ec1c956",
      "database_description": "Dark-tan brick-and-plate fuselage/cowling panel with hinge plates, a reinforced side panel and white clip bricks",
      "description_accuracy": "accurate"
    },
    "model": "examples/10226-cowling-side/source.mpd",
    "plan": "examples/10226-cowling-side/scene.plan.json",
    "manual": "examples/10226-cowling-side/index.html",
    "study_notes": "examples/10226-cowling-side/study-notes.json",
    "study_guide": "examples/10226-cowling-side/GUIDE.md",
    "preview": "examples/10226-cowling-side/renders/home.png",
    "board": "examples/10226-cowling-side/board/mosaic.png",
    "visual_review": "examples/10226-cowling-side/visual-review.json",
    "model_sha256": "12e77b3bb81eda929dbdb568cec0a25b134ab918f9f96c2f9198016ab2b2b3cd"
  }
]
```
