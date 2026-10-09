"""Construction signature: how a model is built, as shares of part classes and orientations.

Official LEGO models of one family share a typical signature. Spaceships mount almost
half their parts sideways or hinged and use few plain bricks; a "spaceship" of upright
bricks reads as a building with wings. `compare()` states that in numbers, using the
official ranges in data/family-signatures.json (scripts/official_corpus.py writes them).
"""
from __future__ import annotations

import json
import re

import numpy as np

from .common import ROOT

RANGES = ROOT / "ldraw_tools/data/family-signatures.json"
# Figures, their accessories and display bases are not construction.
SKIP = re.compile(r"^(Minifig|Figure|Torso|Legs|Hips|Arm|Hand|Head|Hair|Helmet|Baseplate|Sticker|Animal|String|Electric|Duplo)", re.I)
CLASSES = [("snot", r"Bracket|Studs? on .*Side|with Headlight|Brick\s+1\s*x\s*1\s+with\s+Clip"),
           ("hinge", r"Hinge|Clip|\bBar\b|Click"),
           ("round", r"^(Cone|Cylinder|Dish|Radar|Dome)|\bRound\b"),
           ("wedge", r"^(Wedge|Wing)"), ("slope", r"^Slope"), ("tile", r"^Tile"), ("technic", r"^Technic"),
           ("glass", r"Windscreen|Canopy|Glass|Window|Cockpit"), ("plate", r"^Plate"),
           ("brick", r"^Brick\s+\d+\s*x\s*\d+(\s*x\s*\d+)?\s*$")]
# Reported shares, in the order they are printed.
METRICS = ("brick", "plate", "wedge", "slope", "tile", "snot", "hinge", "round", "sideways", "angled")
LABELS = dict(brick="plain bricks", plate="plates", wedge="wedge plates", slope="slopes", tile="tiles",
              snot="brackets and side-stud bricks", hinge="hinges, clips and bars", round="round parts",
              sideways="sideways or upside down", angled="at non-right angles")


def classify(description):
    text = (description or "").lstrip("~=_ ")
    if SKIP.match(text):
        return None
    return next((name for name, pattern in CLASSES if re.search(pattern, text, re.I)), "other")


def signature(rows):
    """Shares of each class and orientation over the construction parts of placed rows.

    A row needs R (world rotation) and local.data.description, as from check.placed_rows.
    """
    kept = [(classify(row["local"].data.description), np.asarray(row["R"])) for row in rows]
    kept = [(cls, R) for cls, R in kept if cls is not None]
    if not kept:
        return dict(parts=0)
    count = len(kept)
    result = {name: sum(cls == name for cls, _ in kept) / count for name, _ in CLASSES}
    result["sideways"] = float(sum(bool(abs(R[1, 1]) < 0.99) for _, R in kept)) / count
    result["angled"] = float(sum(bool(np.any((np.abs(R) > 0.03) & (np.abs(R) < 0.97))) for _, R in kept)) / count
    result["parts"] = count
    return result


def ranges():
    return json.loads(RANGES.read_text()) if RANGES.is_file() else {}


def compare(sig, family):
    """Advice lines where the model sits outside the band most official models of its family share."""
    table = ranges().get(family)
    if not table or not sig.get("parts"):
        return []
    lines = []
    band = table.get("wide", table["metrics"])        # 10th-90th percentile: most official models sit inside
    for metric in ("brick", "sideways", "angled", "hinge", "wedge"):
        low, _, high = band[metric]
        value = sig[metric]
        if value > high + 0.02 or value < low - 0.02:
            lines.append(f"{value:.0%} {LABELS[metric]} (official {family}s {low:.0%}–{high:.0%})")
    if sig["brick"] > table["metrics"]["brick"][2] + 0.05 and sig["sideways"] < table["metrics"]["sideways"][0]:
        lines.insert(0, "reads as a building: mostly upright plain bricks, little sideways or angled construction")
    return lines


def format_signature(sig, family=None):
    if not sig.get("parts"):
        return "construction signature: no construction parts"
    text = "construction: " + ", ".join(f"{sig[m]:.0%} {LABELS[m]}" for m in ("brick", "plate", "sideways", "angled", "hinge", "wedge"))
    advice = compare(sig, family) if family else []
    if advice:
        text += "\n  style vs official " + family + "s: " + "; ".join(advice)
    return text
