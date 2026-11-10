# Biplane upper wing: plate spar, 1×3 tile planking, socket plates for the ailerons and suspension-arm struts

The upper wing of the biplane: a sandwich of 2×16 plates and 6×10 plates as the spar, rows of dark-green 1×3 tiles with gaps as the planked fabric-and-rib surface, 6×6 tiles as the aileron bays, two socket plates per side that take the ailerons' towballs, and four 1×9 suspension arms pinned underneath as the interplane struts. Rebuild the technique: tile rows with one-stud gaps read as ribbed fabric on any vintage wing, socket plates give snap-in control surfaces, and suspension arms make slim interplane struts. The rigging strings are LDCad segments; add them last with the flex workflow.

Read [GUIDE.md](GUIDE.md) for the construction, what the parent supplies, how to read the board and the limits; [index.html](index.html) holds the build pages. Source: `10226-1.mpd` / `10226 - step53.ldr` (placed by `10226 - main.ldr`). Style: display SNOT biplane. Atlas: [examples/aircraft-atlas](../aircraft-atlas/README.md).

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "10226-socket-wing",
    "title": "Biplane upper wing: plate spar, 1×3 tile planking, socket plates for the ailerons and suspension-arm struts",
    "scope": "inspiration",
    "kind": "detail",
    "aliases": [
      "aircraft:10226-socket-wing"
    ],
    "families": [
      "aircraft"
    ],
    "legacy_groups": [
      "details"
    ],
    "lesson": "The upper wing of the biplane: a sandwich of 2×16 plates and 6×10 plates as the spar, rows of dark-green 1×3 tiles with gaps as the planked fabric-and-rib surface, 6×6 tiles as the aileron bays, two socket plates per side that take the ailerons' towballs, and four 1×9 suspension arms pinned underneath as the interplane struts. Rebuild the technique: tile rows with one-stud gaps read as ribbed fabric on any vintage wing, socket plates give snap-in control surfaces, and suspension arms make slim interplane struts. The rigging strings are LDCad segments; add them last with the flex workflow.",
    "limits": "Inspiration only: the two rigging-string children are LDCad segments with mirrored matrices (assembly.nonrigid, assembly.library_internal), so source checks fail and export is blocked. Strut engagement and socket clutch were not checked. The source and renders teach a construction. They do not prove clutch, fit, clearance, travel or stability. Boards are rendered from synthetic inspection copies, and poses are rigid re-placements.",
    "subjects": [
      "Aircraft wing",
      "wing",
      "biplane"
    ],
    "techniques": [
      "system",
      "snot"
    ],
    "style": "display SNOT biplane",
    "origin": {
      "model": "10226-1.mpd",
      "section": "10226 - step53.ldr",
      "parent": "10226 - main.ldr",
      "sha256": "2903c00bd3f1e0af46d47af2e09bd8ccb423eced0588947cc0fb9bd14ac20511",
      "discovery_id": "submodel-34866be8accf6ba1b07c9f2f",
      "database_description": "Large dark-green plank-and-tile main wing on a tan plate base with socket joints, towball pins and wedge wings",
      "description_accuracy": "accurate"
    },
    "model": "examples/10226-socket-wing/source.mpd",
    "plan": "examples/10226-socket-wing/scene.plan.json",
    "manual": "examples/10226-socket-wing/index.html",
    "study_notes": "examples/10226-socket-wing/study-notes.json",
    "study_guide": "examples/10226-socket-wing/GUIDE.md",
    "preview": "examples/10226-socket-wing/renders/home.png",
    "board": "examples/10226-socket-wing/board/mosaic.png",
    "visual_review": "examples/10226-socket-wing/visual-review.json",
    "model_sha256": "06e7ed9ddc2c5d166161610d783bc716bc0f5b5d97da4ce555f37fbaa7523e29"
  }
]
```
