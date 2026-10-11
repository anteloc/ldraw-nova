"""Minimal draft-to-engineering example: preserve a canopy's envelope.

Run from the repository: .venv/bin/python examples/python_kit.py
Then open each contact sheet produced by:
    ./ldraw-agent look output/porch-study/draft.mpd --outdir output/porch-study/draft-views
    ./ldraw-agent look output/porch-study/porch-study.mpd --outdir output/porch-study/final-views
"""
import json
from pathlib import Path

from ldraw_tools.common import atomic_write
from ldraw_tools.kit import Model


def main():
    output = Path("output/porch-study")
    atomic_write(output / "brief.md", """A canopy support study.

Preserve the 6-by-4-stud canopy footprint and its underside at 10 plate heights
above the ground. Engineer supports beneath it without shrinking or lowering it.
Review the front and side views; the static checker does not establish strength.
""")
    model = Model("porch-study", "Canopy support study")
    model.place("3032", "Tan", id="floor")
    model.place("3032", "Dark_Red", level=10, id="canopy")
    model.save(output / "draft.mpd", draft=True)

    # Resolve the missing support without changing the canopy's composition.
    for column, cell in enumerate(((0, 0), (5, 0), (0, 3), (5, 3))):
        for course in range(3):
            model.place("3005", "Tan", cell=cell, level=1 + 3 * course,
                        id=f"column-{column}-{course}")
    atomic_write(output / "porch-study.plan.json", json.dumps(model.plan(), indent=2) + "\n")
    report = model.save(output / "porch-study.mpd")
    atomic_write(output / "check.json", json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
