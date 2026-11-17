# Checks card

`build`, `review` and `validate` print a summary:

- `checks_passed`;
- `errors`, each with the placement paths it concerns in `at`;
- `warnings`, grouped by code with example placements;
- `next`, the step to take.

Fix the first error, rebuild and repeat. `--quiet` prints one line and `--report FILE` saves the complete report. A failed `build` writes `NAME.draft.mpd` beside the plan, and `review --draft` renders the failing model.

| Code | What to do |
|---|---|
| `plan.schema` | Fix the field at `pointer`; `example` shows a valid value. |
| `plan.authoring` | A placement could not be built. The message names it and lists the faces, studs, sockets or Technic ports that exist; a failed Technic seat names the fit rule. |
| `assembly.body_overlap` | Two bricks or plates share space. Move the second placement by `separation` (the first by the opposite), or rebuild the joint. |
| `assembly.duplicate` | The same part twice in one place: delete one. |
| `assembly.floating_group` | These placements touch nothing in the main model. `gap` is how far their box is from the nearest main part, named in `nearest`; seat them on studs. When it says the parts have no connector data, check the render instead. |
| `assembly.became_floating` | Your last edit disconnected these placements. Restore their support rather than deleting them. |
| `appearance.deep_overlap` | Two parts are probably inside each other. Look at a close-up, then move one. |
| `appearance.exposed_side_studs` | Bare sideways studs show. Cover them with tiles unless they are intended. |
| `appearance.glass_obstructed` | A part sits right behind or in front of a window pane, so the window looks blocked. |
| `part.alias_or_internal` | The part number has moved: use `replacement`. |
| `technic.*` | A Technic rule failed: the [Technic card](technic.md#what-the-build-checks) gives the fix for each code. |
| `coverage.*` | Something a check could not cover. It is not an error, but look at those parts in the images. |

Warnings do not fail a build. Every `appearance.*` and `assembly.*` warning still names parts a person will notice, so check them in the render before delivering.

If two repairs of the same interface fail, rebuild that interface alone in a small plan, check it, then put it back.
