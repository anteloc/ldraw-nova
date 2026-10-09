"""Check official LEGO models of one family and measure how they are built.

    .venv/bin/python scripts/official_corpus.py --family spaceship         # check report and problem tally
    .venv/bin/python scripts/official_corpus.py --family spaceship --json docs/dev/reports/ship-corpus.json
    .venv/bin/python scripts/official_corpus.py --signatures               # writes ldraw_tools/data/family-signatures.json

Official models are well built, so a failure here is a gap in `check` (or a genuinely loose
accessory). Calibrate `check` on a family's corpus before writing that family's recipes.
Each model is judged on its main craft: the largest submodel of the first FILE block when it
holds most of the parts, otherwise the whole file (minifigures and stands stay outside).
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ldraw_tools.check import analyze, placed_rows  # noqa: E402
from ldraw_tools.common import get_parts, library_path  # noqa: E402
from ldraw_tools.signature import METRICS, RANGES, signature  # noqa: E402
from ldraw_tools.validation import validate_file  # noqa: E402

MODELS = ROOT / "data/models-annotated"
# Minifigure-scale and display ships across Classic Space, Blacktron, M:Tron, Space Police,
# Ice Planet, Spyrius, Futuron and Star Wars (sets with a craft as their main model).
SHIPS = ("918 924 6929 6891 6842 6810 6830 6850 1620 6894 6832 1479 6954 6981 1887 6877 6862 6923 6811 6781 "
         "6886 6897 6813 3015 6879 6973 1731 6835 6939 7140 7141 7111 8029 8031 8033 7667 20019 20021 30050 "
         "30051 3219 6825 75033").split()
SPACE = re.compile(r"space|star ?wars|starfighter|spaceship|x-wing|tie fighter|shuttle|rocket|lunar|galactic|blacktron|m:?tron", re.I)
KEYWORDS = {
    "building": r"\b(house|building|shop|store|cafe|café|bakery|station|townhouse|cottage|cabin|tower|lighthouse|library|hotel|restaurant|modular)\b",
    "car": r"\b(car|truck|van|pickup|lorry|tractor|roadster|racer|race car|jeep|bus|ambulance|fire engine)\b",
    "aircraft": r"\b(airplane|aeroplane|aircraft|plane|jet|helicopter|biplane|glider)\b",
    "boat": r"\b(boat|ship|sailboat|yacht|submarine|barge|ferry|galleon|tugboat)\b",
    "technic": r"\btechnic\b",
}
FAMILIES = ("spaceship", *KEYWORDS)


def corpus(family, limit=60):
    if family == "spaceship":
        return [MODELS / f"{s}-1.mpd" for s in SHIPS if (MODELS / f"{s}-1.mpd").exists()]
    db = sqlite3.connect(f"file:{ROOT / 'data/ldraw-info.db'}?mode=ro", uri=True)
    pattern = re.compile(KEYWORDS[family], re.I)
    picks = []
    for model, description in db.execute("SELECT model, description FROM MODELS_DESCRIPTIONS ORDER BY model"):
        if not pattern.search(description) or SPACE.search(description):
            continue
        if family != "technic" and re.search(r"\btechnic\b", description, re.I):
            continue
        if (MODELS / model).exists():
            picks.append(MODELS / model)
    return picks[:limit]


def craft_section(path):
    """The largest submodel of the first FILE block if it holds at least half the parts, else None."""
    blocks, order, name = {}, [], None
    for line in path.read_text(errors="replace").splitlines():
        text = line.strip()
        if text.lower().startswith("0 file "):
            name = text[7:].strip()
            blocks[name.lower()] = (name, [])
            order.append(name.lower())
            continue
        bits = text.split()
        if name and len(bits) >= 15 and bits[0] == "1":
            blocks[name.lower()][1].append(" ".join(bits[14:]).lower())
    if not order:
        return None

    def count(key, depth=0):
        return sum(count(ref, depth + 1) if ref in blocks and depth < 12 else 1 for ref in blocks[key][1])
    subs = {ref for ref in blocks[order[0]][1] if ref in blocks}
    if not subs:
        return None
    best = max(subs, key=count)
    return blocks[best][0] if count(best) >= 0.5 * count(order[0]) else None


def judge(path, parts, library):
    section = craft_section(path)
    model, diagnostics = validate_file(path, parts, assembly=True, section=section)
    if model is None:
        return dict(model=path.name, section=section, error="unparsable")
    rows, _, _ = placed_rows(model, path, parts, library)
    result = analyze(rows, limit=200)
    names = {row["code"]: row["local"].data.description for row in rows}
    problems = Counter()
    for group in result["floating_groups"]:
        for member in group["parts"]:
            problems[f"floating  {member['part']} {names.get(member['part'], '')[:40]}"] += 1
    for item in result["collisions"]:
        a, b = sorted([item["a"]["part"], item["b"]["part"]])
        problems[f"collision {a} {names.get(a, '')[:24]} × {b} {names.get(b, '')[:24]}"] += 1
    for item in result["seating"]:
        pair = [item.get(k, {}).get("part", "?") for k in ("stud", "on")]
        problems[f"seating   {pair[0]} {names.get(pair[0], '')[:24]} in {pair[1]} {names.get(pair[1], '')[:24]}"] += 1
    clean = not (result["floating_count"] or result["collision_count"] or result["seating_count"])
    errors = sum(d["severity"] == "error" for d in diagnostics)
    return dict(model=path.name, section=section, parts=len(rows), clean=clean, floating=result["floating_count"],
                collisions=result["collision_count"], seating=result["seating_count"], source_errors=errors,
                problems=dict(problems), signature=signature(rows))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--family", choices=FAMILIES)
    parser.add_argument("--json", type=Path, help="Write the full results here")
    parser.add_argument("--signatures", action="store_true", help=f"Measure every family and write {RANGES.name}")
    parser.add_argument("--limit", type=int, default=60)
    args = parser.parse_args()
    if not args.family and not args.signatures:
        parser.error("choose --family or --signatures")
    parts, library = get_parts(), library_path()
    families = FAMILIES if args.signatures else (args.family,)
    results, ranges = {}, {}
    for family in families:
        judged = [judge(path, parts, library) for path in corpus(family, args.limit)]
        judged = [j for j in judged if "error" not in j and j["parts"]]
        results[family] = judged
        measured = [j["signature"] for j in judged if j["signature"].get("parts")]
        metrics = {m: [round(float(np.percentile([s[m] for s in measured], q)), 3) for q in (25, 50, 75)]
                   for m in METRICS}
        wide = {m: [round(float(np.percentile([s[m] for s in measured], q)), 3) for q in (10, 50, 90)] for m in METRICS}
        ranges[family] = dict(models=len(measured), metrics=metrics, wide=wide)
        if args.family:
            for j in judged:
                state = "clean " if j["clean"] else "ISSUES"
                print(f"{state} {j['model']:22s} {j['parts']:5d} parts  floating {j['floating']:3d}  collisions {j['collisions']:2d}  "
                      f"seating {j['seating']:2d}  source errors {j['source_errors']:2d}  [{j['section'] or 'whole file'}]")
            tally = Counter()
            for j in judged:
                tally.update(j["problems"])
            print(f"\n{sum(j['clean'] for j in judged)} of {len(judged)} {family} models are geometry-clean\n")
            for problem, n in tally.most_common(30):
                print(f"{n:4d}  {problem}")
    if args.signatures:
        RANGES.write_text(json.dumps(ranges, indent=1) + "\n")
        print(f"wrote {RANGES.relative_to(ROOT)}: " + ", ".join(f"{f} ({r['models']})" for f, r in ranges.items()))
    if args.json:
        args.json.write_text(json.dumps(results, indent=1, default=str) + "\n")


if __name__ == "__main__":
    main()
