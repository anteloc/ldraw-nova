# Copper Lane

Leaf and Letter is a botanical bookshop beside the quieter Rose House. This original parameterized streetscape demonstrates how composition, part selection and reusable details work together: green-and-white awnings, a gold BOOKS sign, arched flower windows, embossed masonry, a dormer, a stepped clock pediment, layered leaf trees and fluted lamps. Its five furnished storeys lift off for access. The default has 1,655 physical placements across nineteen FILE blocks.

[Generated MPD](copper-lane.mpd) · [Reviewed preview](preview.png) · [Validation](validation.json) · [BOM comparison](bom-comparison.json)

[Design brief](design-brief.json) · [Before/after review](visual-review.md) · [Front elevation](front.png) · [Window detail](window.png)

```sh
.venv/bin/python examples/modular-street/generate.py
./ldraw-agent build examples/modular-street/scene.plan.json --output output/copper-lane.mpd --detail summary
./ldraw-agent render output/copper-lane.mpd --outdir output/copper-lane-review
./ldraw-agent compare-bom output/copper-lane.mpd --csv output/copper-lane-review/leocad-bom.csv
```

Use `--force` on intentional rebuilds. `generate.py --floors 4 --outdir output/four-storeys` generates a four-storey shop and three-storey house without altering the supplied plans. Paths in `includes` are relative to their declaring plan. Edit the generator for persistent parameter/pattern changes; direct JSON edits are overwritten when regenerating.

`scene.plan.json` places the street and buildings; `buildings.plan.json` defines storeys/roofs; `details.plan.json` defines reusable windows, doors, furniture and landscaping. The generator uses the shared [detail recipes](../../ldraw_tools/details.py), [palette roles](../../ldraw_tools/data/design-palettes.json), and descriptive `@category.Symbol` / `@colours.Name` values resolved from the supplied categories. Edit the generator to change composition; edit the shared recipes to improve details across models. Export an individual starting recipe with `./ldraw-agent design details arched-window --output output/window.plan.json`.

A storey's `base` is its floor-plate underside at Y=8; `next` is the cornice top at Y=-160. Attachment therefore advances 168 LDU upwards. Each arch replaces reserved wall cells; the dormer replaces conflicting roof slopes. The awning's two-row support beam meets actual slope sockets. Interiors are visible when each storey is rendered separately. Floors lift off; no internal stairwell is represented.

Follow the [visual-design](../../docs/agent/guides/design-models.md) and [complex-model workflows](../../docs/agent/guides/compose-modules.md), and read [verification](../../docs/reports/tooling-verification-history.md). Full-scene contacts are explicitly skipped in auto mode; general shape collisions and connection/stability limits still require review. The generated model demonstrates tooling, not physical certification or inventory availability. It contains no copied OMR geometry.

## Knowledge registration

```ldraw-knowledge
[
  {
    "id": "copper-lane",
    "title": "Copper lane",
    "scope": "construction",
    "kind": "assembly",
    "aliases": [
      "standalone:copper-lane"
    ],
    "families": [
      "building"
    ],
    "legacy_groups": [
      "examples"
    ],
    "lesson": "Three-storey bookshop beside two-storey house; distinct blue dormer roof and red clock-pediment roof, planted pavement and lamps. Retain parameterized facade/composition lesson; no complete circulation plan. Open-topped shop storey has green striped awnings, BOOKS sign, glazing and simple bookcase/table interior. Parent places it at bookshop ground level.",
    "limits": "Static visual evidence only unless the linked package records specific further checks. Search eligibility does not certify fit, motion or strength.",
    "audit": "docs/plans/knowledge-base-overhaul/snapshot/standalone-audit.json",
    "model": "examples/modular-street/copper-lane.mpd",
    "generator": "examples/modular-street/generate.py",
    "model_sha256": "a3ac48138bb5e3b382b076c289c3bc14741380600ac96f36dbcc994424b97c21",
    "audit_pointer": "/items/0",
    "findings": "docs/plans/knowledge-base-overhaul/snapshot/standalone-findings.md",
    "techniques": [],
    "subjects": [
      "architecture"
    ]
  }
]
```

## Audited section observations

These observations refer to the source hashes in the registrations. They correct earlier source descriptions and preserve static visual scope; existing numeric and export checks remain separate.

### Copper lane

| Source section | Opened-image observation |
|---|---|
| `copper-lane.ldr` | Three-storey bookshop beside two-storey house; distinct blue dormer roof and red clock-pediment roof, planted pavement and lamps. Retain parameterized facade/composition lesson; no complete circulation plan. |
| `lane-ground.ldr` | Open-topped shop storey has green striped awnings, BOOKS sign, glazing and simple bookcase/table interior. Parent places it at bookshop ground level. |
| `lane-upper.ldr` | Tan upper reading-room storey repeats twice above shop; arched flower windows and rear/side glazing frame sparse bookcase/table interior. |
| `lane-house-ground.ldr` | Sand-green house ground floor has traditional entrance, flower windows and same simplified bookcase/table furniture; not a fully furnished dwelling. |
| `lane-house-upper.ldr` | House upper floor repeats the reading-room furniture, front flower windows and rear/side paired glazing. No staircase is represented. |
| `lane-roof.ldr` | Bookshop roof has cut-in dormer, slope courses and chimney. Isolated inherited-colour surfaces render yellow; actual parent roof is blue. |
| `lane-house-roof.ldr` | House roof has stepped clock pediment and chimney; actual parent colour is red, independent of isolated colour fallback. |
| `lane-window.ldr` | Two stacked frame/pane windows form a tall opening. All four distinct storey parents inspected, including repeated instances and parent colours. |
| `lane-door.ldr` | Traditional green door in frame at bookshop entrance; frame inherits colour from parent. |
| `lane-bookcase.ldr` | Flat bookcase uses green, blue and red brick rows as books; repeated identically across all four floor types. Keep as simple interior prop, not a varied furnishing pattern. |
| `lane-table.ldr` | Minimal studded tabletop on two block legs; inspected in all four floor types. Keep as a beginner interior prop with repetition explicitly visible. |
| `lane-house-door.ldr` | Traditional brown door in inherited-colour frame at house entrance; same construction family as green shop door. |
| `detail-arched-window.ldr` | White arch surrounds green rectangular frame and flower sill. Above frame is an open arch void, not glazed fanlight. |
| `detail-striped-awning.ldr` | Alternating green/white slopes on rear support beam, repeated over shop glazing. Preserve measured socket offsets from its existing local check. |
| `detail-flower-planter.ldr` | Despite section name, this is a small layered foliage tree on a flowered base, placed at pavement edge. Correct searchable identity to planted tree. |
| `detail-book-sign.ldr` | Printed gold BOOKS tile on green side-stud supports with top cap; actual parent locates it over entrance. |
| `lane-house-window.ldr` | Tan/brown colour variant of arch, frame and flower sill; both house-floor parents inspected. Arch opening above frame is unglazed. |
| `lane-tall-tree.ldr` | Taller round-trunk foliage tree on planted base; same construction family as shorter misnamed flower-planter, with extra trunk height. |
| `lane-lamp.ldr` | Fluted moulded post with round lantern stack and conical finial, repeated at pavement. Retain as contextual prop with existing connector limits. |
