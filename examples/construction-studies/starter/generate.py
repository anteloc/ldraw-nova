"""Compose inspected modules on a real parent; emit editable source for review.

Run from the repository root. This is an entrance study, not a whole-house recipe.
"""
import argparse
import json
from pathlib import Path

from ldraw_tools.builder import build_plan, load_plan
from ldraw_tools.common import atomic_write, dumps, get_parts, library_path
from ldraw_tools.constructions import export_construction


def generate(outdir, *, palette="rose-townhouse"):
    outdir = Path(outdir)
    if outdir.exists() and any(outdir.iterdir()):
        raise ValueError("Choose a new output directory so earlier review evidence is preserved")
    parts, library = get_parts(), library_path()
    sources = {}
    for name, recipe, parameters in [
        ("deck", "bonded-floor", dict(width=12, depth=8)),
        ("canopy", "entrance-canopy", dict(depth=4, courses=7)),
    ]:
        folder = outdir/"sources"/name
        result = export_construction(recipe, folder, parts, library, parameters=parameters, palette=palette)
        if not result["checks_passed"]:
            raise ValueError(f"{name} needs review: {folder / 'check.json'}")
        sources[name] = json.loads((folder/"model.plan.json").read_text())["sections"][0]["name"]
    # The floor's upper stud plane is Y=-16. The child's underside/base frame is
    # Y=0. Offset in the parent's axes preserves the 20-LDU stud grid.
    plan = dict(version=1, author="LDraw NOVA", includes=[
        "sources/deck/model.plan.json", "sources/canopy/model.plan.json"], sections=[dict(
        name="entrance-study.ldr", description="Offset entrance on a bonded terrace", steps=[
            [dict(id="deck", ref=sources["deck"], colour="@colours.Tan", at=[0, 0, 0])],
            [dict(id="canopy", ref=sources["canopy"], colour="@colours.White",
                  attach=dict(to="deck", anchor="top", using="base", offset=[40, 0, 20]))],
        ])])
    source = outdir/"scene.plan.json"
    atomic_write(source, dumps(plan)+"\n")
    text, _, diagnostics = build_plan(load_plan(source), parts)
    if any(d["severity"] == "error" for d in diagnostics):
        raise ValueError(f"Source errors: {diagnostics}")
    atomic_write(outdir/"study.mpd", text)
    requirements = dict(version=1, requirements=[
        dict(id="parent-attachment", kind="connection", modules=["deck", "canopy"]),
        dict(id="covers-entrance", kind="envelope_covers", cover=["canopy>roof"],
             target=["canopy>entrance"], axes=["x", "z"]),
        dict(id="entrance-headroom", kind="above", upper=["canopy>roof"],
             lower=["canopy>entrance"], min_gap=8),
    ])
    atomic_write(outdir/"requirements.json", dumps(requirements)+"\n")
    atomic_write(outdir/"brief.md", """An offset covered entrance on a bonded terrace.

Choose the surrounding building's composition independently. This small study
demonstrates real parent support and a reproducible palette/layout edit.

| Feature | Intent | Evidence needed |
|---|---|---|
| Terrace | A visible margin around the offset entrance | Top/home views; actual parent attachment check |
| Canopy | Covers the entrance without lowering it | Coverage/headroom checks; front/side views |
| Palette | Coherent frame, roof and paving roles | Inspect the rendered colours |
| Access | Keep the entrance approach useful | Inspect all nearby parts; the three checks do not prove a route or door motion |

Review remains pending. No image has been viewed by this generator.
""")
    return dict(source=str(source), model=str(outdir/"study.mpd"),
                next_action="Run check, then stage prepare with requirements.json; open images before review")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=Path("output/entrance-starter"))
    parser.add_argument("--palette", default="rose-townhouse")
    args = parser.parse_args()
    print(dumps(generate(args.outdir, palette=args.palette)))
