"""Construction controls and deliberate defects for the Copper Lane reuse study.

The window-free model is a diagnostic copy only. All delivered study variants
retain their glazing. Negative controls must continue to fail without changing
the checker or marking parts free.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from ldraw_tools.builder import build_plan, load_plan
from ldraw_tools.catalog import resolve_part
from ldraw_tools.check import check_model
from ldraw_tools.common import atomic_write, get_parts, library_path

from evidence import assess, reference_evidence


def entries(plan):
    for section in plan["sections"]:
        for step in section["steps"]:
            yield from step


def run(plan, path, parts):
    text, _, diagnostics = build_plan(plan, parts)
    assert not [d for d in diagnostics if d["severity"] == "error"]
    atomic_write(path, text)
    report = check_model(path, parts, library_path(), limit=1000)
    path.with_suffix(".check.json").write_text(json.dumps(report, indent=2)+"\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    args = parser.parse_args()
    out = args.folder / "controls"
    out.mkdir(parents=True, exist_ok=True)
    parts = get_parts()
    plan = load_plan(args.folder / "scene.plan.json")
    summary = []

    structural = copy.deepcopy(plan)
    for section in structural["sections"]:
        for step in section["steps"]:
            kept = []
            for entry in step:
                ref = entry["ref"]
                ref = resolve_part(ref, parts) if ref.startswith("@") else ref
                if ref.removesuffix(".dat") not in {"60601", "60608", "57895"}:
                    kept.append(entry)
            step[:] = kept
        section["steps"] = [s for s in section["steps"] if s]
    r = run(structural, out / "diagnostic-without-window-inserts.mpd", parts)
    assert r["checks_passed"], r["verdict"]
    summary.append(dict(case="diagnostic without window inserts", verdict=r["verdict"], parts=r["parts"],
                        qualification="Diagnostic only; glazing remains in the actual study model"))

    bad_sign = copy.deepcopy(plan)
    next(p for p in entries(bad_sign) if p["id"] == "books-sign")["at"][1] += 10
    r = run(bad_sign, out / "negative-sign-half-stud-error.mpd", parts)
    assert r["verdict"] == "FAIL"
    assert any(p["part"] == "87079pt1" for g in r["floating_groups"] for p in g["parts"])
    summary.append(dict(case="restore half-stud sign error", verdict=r["verdict"], floating=r["floating_count"]))

    bad_roof = copy.deepcopy(plan)
    next(s for s in bad_roof["sections"] if s["name"] == "lane-roof.ldr")["anchors"]["base"]["at"][1] += 8
    r = run(bad_roof, out / "negative-roof-gap.mpd", parts)
    assert r["verdict"] == "FAIL" and any(g["size"] > 100 for g in r["floating_groups"])
    summary.append(dict(case="raise roof one plate", verdict=r["verdict"], floating=r["floating_count"]))

    bad_pane = copy.deepcopy(plan)
    next(p for p in entries(bad_pane) if p["id"] == "left-pane")["at"][0] += 10
    path = out / "negative-pane-offset.mpd"
    r = run(bad_pane, path, parts)
    evidence = assess(path, r, parts, reference_evidence(parts))
    path.with_suffix(".evidence.json").write_text(json.dumps(evidence, indent=2)+"\n")
    assert r["verdict"] == "FAIL" and evidence["unresolved"]
    summary.append(dict(case="offset pane half a stud", verdict=r["verdict"],
                        unsupported_findings=len(evidence["unresolved"])))

    (out / "summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
