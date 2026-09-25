# Arcade Bay

A four-stud architectural bay with a real arch, adjustable brick piers and an articulated cornice.

Run from the repository root:

```sh
.venv/bin/python examples/reference-atlas/recipes/arcade-bay/generate.py --height 5 --render --outdir output/arcade-bay
```

`--height` accepts 2–10 brick courses. `--colour` changes the structure; `--accent` changes the cornice rounds or lantern collar. Parts keep their real geometry and proper rotations. The editable [plan](scene.plan.json) exposes a positioning frame at the base underside, Y=0. It is not an inferred mechanical connector.

Both the default and changed-height forms were checked for geometry errors and a single optimistic connection group. This is computational evidence; stability, clutch strength and fit in a larger scene remain unproven. Inspect [validation.json](validation.json) and [render.json](render.json), and preserve the source credit in the plan. Compare the [home view](renders/home.png) and other saved views before placing it.
