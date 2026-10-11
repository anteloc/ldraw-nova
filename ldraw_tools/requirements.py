"""Explicit, measurable feature envelopes; separate from material/connection checks."""
import math

import numpy as np

from .check import world_box


def check_requirements(spec, rows, construction):
    """Evaluate a small strict contract vocabulary on source-linked occurrences.

    Bounds are body AABBs. These requirements establish envelopes, not watertight
    surfaces, usable circulation, strength or complete architectural correctness.
    """
    if not isinstance(spec, dict) or set(spec) != {"version", "requirements"} or spec["version"] != 1:
        raise ValueError("Requirements need version=1 and a requirements list")
    if not isinstance(spec["requirements"], list) or not spec["requirements"]:
        raise ValueError("Provide at least one requirement")
    identifiers, findings = set(), []

    def number(value):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError("Requirement dimensions must be finite numbers")
        return value

    def selected(selectors):
        if not isinstance(selectors, list) or not selectors or not all(isinstance(s, str) and s for s in selectors):
            raise ValueError("Select parts by a nonempty list of exact IDs or assembly ID prefixes")
        selected_rows = {}
        for selector in selectors:
            matches = [(i, r) for i, r in enumerate(rows)
                       if r["label"] == selector or r["label"].startswith(selector + ">")]
            if not matches:
                raise LookupError(f"No occurrences match {selector!r}")
            selected_rows.update(matches)
        return list(selected_rows.values())

    def bounds(selectors):
        boxes = [world_box(r) for r in selected(selectors)]
        return np.min([b[0] for b in boxes], axis=0), np.max([b[1] for b in boxes], axis=0)

    for rule in spec["requirements"]:
        if not isinstance(rule, dict):
            raise ValueError("Each requirement must be an object")
        identifier, kind = rule.get("id"), rule.get("kind")
        if not isinstance(identifier, str) or not identifier.strip() or identifier in identifiers:
            raise ValueError("Requirement IDs must be nonempty and unique")
        identifiers.add(identifier)
        keys = {
            "extent": {"parts", "axis", "min", "max"},
            "envelope_covers": {"cover", "target", "axes"},
            "above": {"upper", "lower", "min_gap"},
            "clearance": {"parts", "min", "max"},
            "connection": {"modules"},
        }
        if not isinstance(kind, str) or kind not in keys or set(rule) != {"id", "kind", *keys.get(kind, ())}:
            raise ValueError(f"Invalid fields for requirement {identifier!r} ({kind!r})")
        try:
            if kind == "extent":
                if rule["axis"] not in ("x", "y", "z"):
                    raise ValueError("extent axis must be x, y or z")
                lo, hi = bounds(rule["parts"])
                size = float((hi-lo)["xyz".index(rule["axis"])])
                minimum, maximum = number(rule["min"]), number(rule["max"])
                if minimum < 0 or maximum < minimum:
                    raise ValueError("extent requires 0 <= min <= max")
                passed, measured = minimum <= size <= maximum, dict(extent_ldu=size)
            elif kind == "envelope_covers":
                axes = rule["axes"]
                if not isinstance(axes, list) or not axes or not all(isinstance(a, str) and a in ("x", "y", "z") for a in axes) or len(set(axes)) != len(axes):
                    raise ValueError("envelope_covers axes must select x, y and/or z")
                c0, c1 = bounds(rule["cover"])
                t0, t1 = bounds(rule["target"])
                indices = ["xyz".index(a) for a in axes]
                passed = bool(np.all(c0[indices] <= t0[indices]+1e-6) and np.all(c1[indices] >= t1[indices]-1e-6))
                measured = dict(cover_min=c0.tolist(), cover_max=c1.tolist(), target_min=t0.tolist(), target_max=t1.tolist())
            elif kind == "above":
                _, upper = bounds(rule["upper"])
                lower, _ = bounds(rule["lower"])
                minimum = number(rule["min_gap"])
                if minimum < 0:
                    raise ValueError("above min_gap must be nonnegative")
                gap = float(lower[1]-upper[1])  # LDraw Y grows downwards.
                passed, measured = gap >= minimum-1e-6, dict(gap_ldu=gap)
            elif kind == "clearance":
                if any(not isinstance(rule[k], list) or len(rule[k]) != 3 for k in ("min", "max")):
                    raise ValueError("Clearance bounds must be three-dimensional")
                lo, hi = (np.array([number(v) for v in rule[k]]) for k in ("min", "max"))
                if not np.all(lo < hi):
                    raise ValueError("Clearance min must precede max on every axis")
                occupants = [r["label"] for r in selected(rule["parts"])
                             if np.all(world_box(r)[0] < hi-1e-6) and np.all(world_box(r)[1] > lo+1e-6)]
                passed, measured = not occupants, dict(occupants=occupants)
            else:
                modules = rule["modules"]
                if not isinstance(modules, list) or len(modules) != 2 or not all(isinstance(m, str) for m in modules) or modules[0] == modules[1]:
                    raise ValueError("connection requires two distinct module IDs")
                existing = {r["module"] for r in construction.get("modules", [])}
                if not set(modules) <= existing:
                    raise LookupError("Unknown module in required connection")
                edges = [e for e in construction["module_edges"] if {e["a"], e["b"]} == set(modules)]
                passed, measured = bool(edges), dict(edges=edges)
        except LookupError as error:
            passed, measured = False, dict(error=str(error))
        findings.append(dict(id=identifier, kind=kind, passed=bool(passed), **measured))
    return dict(checks_passed=all(r["passed"] for r in findings), requirements=findings,
                coverage="Body envelopes and detected direct module connections; not solid-surface or functional proof")
