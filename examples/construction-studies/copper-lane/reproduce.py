"""Inspect and repair copies of a composed building, without changing its source.

This is a construction-reuse experiment, not a new model-generation benchmark.
Run from the repository root with .venv/bin/python. Every check remains enabled;
reference-supported window findings remain REVIEW/FAIL in the raw reports.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

from ldraw_tools.builder import build_plan, load_plan
from ldraw_tools.check import check_model
from ldraw_tools.common import atomic_write, get_parts, library_path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "examples/modular-street"


def write_json(path, value):
    atomic_write(path, json.dumps(value, indent=2) + "\n")


def repair_plans(folder):
    scene_path = folder / "scene.plan.json"
    scene = json.loads(scene_path.read_text())
    steps = scene["sections"][0]["steps"]
    # Move the fixture and its exposed mounting studs together. Moving only the
    # lamp would put its foot through the paving tile at the new location.
    for entry in steps[0]:
        if entry["id"] in ("paving--220--180", "paving-220--180"):
            entry["at"][2] = -140
            entry["id"] = entry["id"].replace("--180", "--140")
    lamp = next(p for step in steps for p in step if p["id"] == "lamps")
    lamp["at"][2] = -180
    write_json(scene_path, scene)

    path = folder / "details.plan.json"
    details = json.loads(path.read_text())
    sign = next(s for s in details["sections"] if s["name"] == "detail-book-sign.ldr")
    tile = next(p for step in sign["steps"] for p in step if p["id"] == "books-sign")
    # The vertical tile has two socket rows, 10 LDU either side of its origin.
    # Align its lower row with the side studs at Y=-22; body-centre alignment
    # in the original places both socket rows 10 LDU away from those studs.
    tile["at"][1] = -32
    write_json(path, details)


def run(folder, floors, parts):
    folder.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    subprocess.run([sys.executable, str(SOURCE / "generate.py"), "--floors", str(floors),
                    "--outdir", str(folder)], check=True, capture_output=True, text=True)
    repair_plans(folder)
    generated = time.perf_counter()
    text, _, diagnostics = build_plan(load_plan(folder / "scene.plan.json"), parts)
    errors = [d for d in diagnostics if d["severity"] == "error"]
    if errors:
        raise ValueError(errors)
    path = folder / "copper-lane-study.mpd"
    atomic_write(path, text)
    built = time.perf_counter()
    report = check_model(path, parts, library_path(), limit=1000)
    checked = time.perf_counter()
    write_json(folder / "check.json", report)
    write_json(folder / "source-diagnostics.json", diagnostics)
    result = dict(floors=floors, parts=report["parts"], verdict=report["verdict"],
                  collisions=report["collision_count"], floating=report["floating_count"],
                  reviews=report["review_count"], seating=report["seating_count"],
                  generation_seconds=round(generated-start, 3),
                  source_build_seconds=round(built-generated, 3),
                  check_seconds=round(checked-built, 3),
                  total_seconds=round(checked-start, 3),
                  sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    write_json(folder / "timing.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=ROOT / "output/construction-approach-study/reuse")
    parser.add_argument("--floors", type=int, nargs="+", default=[3, 4, 5], choices=range(2, 6))
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    source_files = [SOURCE / "generate.py", ROOT / "ldraw_tools/details.py",
                    ROOT / "ldraw_tools/data/design-palettes.json"]
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}
    parts = get_parts()
    results = []
    for floors in args.floors:
        result = run(args.outdir / f"{floors}-floors", floors, parts)
        results.append(result)
        print(json.dumps(result), flush=True)
    assert hashes == {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}
    write_json(args.outdir / "experiment.json", dict(
        purpose="Construction reuse and local repair; not an original design or timed agent comparison",
        source_hashes=hashes, original_files_unchanged=True, checker_modified=False,
        changes=["Move lamps and their paving openings forward by 40 LDU",
                 "Raise BOOKS tile by 10 LDU to engage one socket row with the side studs"],
        results=results))


if __name__ == "__main__":
    main()
