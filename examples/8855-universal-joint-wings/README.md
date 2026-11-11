# Studded Technic wing: Technic-brick spars, wing-brick ribs, universal-joint roots and plate flaps

A studded Technic wing: two 1×16 Technic bricks as leading and trailing spars on 10-long axles, 1×4 wing-front and 1×6 wing-back bricks as ribs, 1×8 plates as skin strips; each root is a universal joint with a towball so the wing can be tilted, and the flaps are 4×10 plates on a Technic-plate hinge with toggle joints. Use the spar-and-rib pattern for any studded Technic wing: Technic-brick spars give the span and pin holes, wing bricks give the profile, plates the skin. Drop the universal joints unless the wing must tilt, and hinge flaps on a Technic plate.

Read [GUIDE.md](GUIDE.md) for the construction, what the parent supplies, how to read the board and the limits; [index.html](index.html) holds the build pages. Source: `8855-1.mpd` / `8855 - Wings.ldr` (placed by `8855 - Prop Plane.ldr`). Style: studded Technic (1988). Atlas: [examples/aircraft-atlas](../aircraft-atlas/README.md).

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "8855-universal-joint-wings",
    "title": "Studded Technic wing: Technic-brick spars, wing-brick ribs, universal-joint roots and plate flaps",
    "scope": "construction",
    "kind": "detail",
    "aliases": [
      "aircraft:8855-universal-joint-wings"
    ],
    "families": [
      "aircraft"
    ],
    "legacy_groups": [
      "details"
    ],
    "lesson": "A studded Technic wing: two 1×16 Technic bricks as leading and trailing spars on 10-long axles, 1×4 wing-front and 1×6 wing-back bricks as ribs, 1×8 plates as skin strips; each root is a universal joint with a towball so the wing can be tilted, and the flaps are 4×10 plates on a Technic-plate hinge with toggle joints. Use the spar-and-rib pattern for any studded Technic wing: Technic-brick spars give the span and pin holes, wing bricks give the profile, plates the skin. Drop the universal joints unless the wing must tilt, and hinge flaps on a Technic plate.",
    "limits": "Wing tilt travel, flap travel and the universal joints' retention were not checked. `./ldraw-agent build` of the exported plan reports `technic.invalid_seating` for the two 6-long axles passing through the 1×2 hole bricks at the root as drawn; `manual export`, the plan rebuild and the BOM comparison pass. The source and renders teach a construction. They do not prove clutch, fit, clearance, travel or stability. Boards are rendered from synthetic inspection copies, and poses are rigid re-placements.",
    "subjects": [
      "Aircraft wing",
      "wing"
    ],
    "techniques": [
      "technic"
    ],
    "style": "studded Technic (1988)",
    "origin": {
      "model": "8855-1.mpd",
      "section": "8855 - Wings.ldr",
      "parent": "8855 - Prop Plane.ldr",
      "sha256": "98bb90e07be0a121c13018abd5fc51a2c0a7b1a4a94871b7c4bb92f3a3f04f8f",
      "discovery_id": "submodel-de73e9b073136323402217e8",
      "database_description": "The main wings constructed from wing-front and wing-back Technic bricks, long plates, gears, and translucent indicator lights.",
      "description_accuracy": "partly accurate"
    },
    "model": "examples/8855-universal-joint-wings/source.mpd",
    "plan": "examples/8855-universal-joint-wings/scene.plan.json",
    "manual": "examples/8855-universal-joint-wings/index.html",
    "study_notes": "examples/8855-universal-joint-wings/study-notes.json",
    "study_guide": "examples/8855-universal-joint-wings/GUIDE.md",
    "generator": "examples/8855-universal-joint-wings/generate.py",
    "preview": "examples/8855-universal-joint-wings/renders/home.png",
    "board": "examples/8855-universal-joint-wings/board/mosaic.png",
    "visual_review": "examples/8855-universal-joint-wings/visual-review.json",
    "model_sha256": "94f0ceab4d69b1f2ecb6407ca0cabfa81bdcd069d5c5ea93bb8f391321e3680a"
  }
]
```
