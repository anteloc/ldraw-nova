**A small construction in its actual parent**

This runnable entrance study composes a supported canopy with an offset bonded terrace, using the existing optional constructions. It teaches valid plan shape, named palette roles, parent attachment and the review route. Choose your own whole-building design; this is not a complete façade, interior or stair system.

Run from the repository root, in sequence:

```sh
.venv/bin/python examples/construction-studies/starter/generate.py --outdir output/entrance-starter
./ldraw-agent check output/entrance-starter/study.mpd --report output/entrance-starter/check.json
./ldraw-agent stage prepare output/entrance-starter/scene.plan.json --requirements output/entrance-starter/requirements.json --outdir output/entrance-starter/review --views home front right top
```

The generator first checks the two local constructions. The next commands check the actual parent assembly and prepare the exact revision for viewing. Open **all four** images in `output/entrance-starter/review/views/`. Inspect the terrace margin, entrance coverage, supports, palette and approach against `brief.md`. Record what you actually see:

```sh
./ldraw-agent stage review output/entrance-starter/review --images views/home.png views/front.png views/right.png views/top.png --decision accept --note 'Replace this with actual observations after opening every image'
./ldraw-agent stage export output/entrance-starter/review --output output/entrance-starter/accepted.mpd
```

Use `--decision revise` for an unsatisfactory result, repair its source and prepare again. The example note above is an instruction placeholder, not a completed review. Static PASS does not establish appearance, door motion, strength or a clear path through a future building.

To learn an edit, regenerate in a **new** directory with `--palette botanical-bookshop`, or change the parent's `[40, 0, 20]` offset in the generator while keeping its footprint on the deck and its stud grid aligned. Recheck and view the complete parent. Internal sill/storey-height edits are not supported by this starter: changing a child's position alone does not regenerate a surrounding wall or stair.

For quick engineering iterations, `stage prepare ... --no-render` retains reports but returns exit 1 with `technical_checks_passed: true` and `review_state: pending_images` when construction passes. That is pending visual work, not a construction failure. Use `check` for a static verdict with exit 0 on PASS; prepare with images for final acceptance. Never run dependent generation and checking concurrently.

Each included plan is ordinary editable JSON. Exact supported parameters, local supports, reserved spaces and hashes are in `sources/*/construction.json`. The [atlas learning pack](../../building-atlas/README.md) supplies additional visual and construction vocabulary with explicit limitations.
