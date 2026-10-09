"""Deliver the exact final revision in one call: check, views, BOMs, GLB and a summary.

    ./ldraw-agent deliver output/my-model/my-model.mpd     # writes output/my-model/delivery/

The summary (delivery/summary.md) states the check verdict, part counts, the
module-connection graph and links to every artifact, so the final answer can
point to one file. Re-run it after the last source change.
"""
from __future__ import annotations

import time
from collections import Counter
from pathlib import Path

from . import check as checker
from .common import atomic_write, jsonable
from .document import physical_context
from .external import compare_bom, prepare_glb, render
from .look import look
from .validation import validate_file

VIEWS = ("home", "front", "back", "left", "right", "top", "bottom")
FRICTION = """# Friction report

Fill this in before you finish. It is how the toolkit and the recipes improve for the next agent.

- Slowest or most repeated step:
- Helper code I wrote, and why the kit or a recipe did not cover it:
- What a recipe, port name or error message should have told me:
- Checks I could not satisfy, and why:
"""


def deliver(path, parts, library, outdir=None, *, glb=True, family=None):
    started = time.perf_counter()
    path = Path(path).resolve()
    outdir = Path(outdir) if outdir else path.parent / "delivery"
    outdir.mkdir(parents=True, exist_ok=True)
    report = checker.check_model(path, parts, library, family=family)
    atomic_write(outdir / "check.json", __import__("json").dumps(report, indent=1, default=str) + "\n")
    sheet = look(path, parts, library, outdir, views=VIEWS)["sheet"]
    rendered = render(path, library, outdir / "views", views=VIEWS)
    model, _ = validate_file(path, parts, assembly=True)
    bom_rows = Counter()
    if model is not None:
        view, overlay = physical_context(model, parts)
        for row in jsonable(view.bill_of_materials(parts=overlay)):
            bom_rows[(f"{row['part']} {row.get('description') or ''}".strip(), row.get("colour_name") or str(row.get("colour_code")))] += row["quantity"]
    comparison = compare_bom(model, parts, rendered["bom"]) if model is not None else dict(matches=False)
    glb_result = None
    if glb:
        try:
            glb_result = prepare_glb(path, library, outdir / (path.stem + ".glb"), parts)
        except (OSError, ValueError) as error:
            glb_result = dict(error=str(error)[:300])
    verdict = "PASS" if report.get("checks_passed") else "FAIL"
    lines = [f"# {path.stem}", "",
             f"**Check: {verdict}**: {report.get('parts', 0)} parts of {report.get('part_types', 0)} types; "
             f"floating {report.get('floating_count', '?')}, collisions {report.get('collision_count', '?')}, "
             f"badly seated {report.get('seating_count', '?')}, duplicates {report.get('duplicate_count', '?')}.",
             f"LeoCAD BOM {'matches' if comparison.get('matches') else 'DIFFERS from'} the Python BOM.", "",
             *([checker.format_signature(report["signature"], family), ""] if family and "signature" in report else []),
             f"![Views]({Path(sheet).name})", "", "## Modules", "", "```mermaid", checker.mermaid_graph(report) if "modules" in report else "flowchart LR", "```", "",
             "## Parts", "", "| Part | Colour | Qty |", "|---|---|---:|"]
    for (part, colour), quantity in bom_rows.most_common(25):
        lines.append(f"| {part} | {colour} | {quantity} |")
    if len(bom_rows) > 25:
        lines.append(f"| … {len(bom_rows) - 25} more | | |")
    lines += ["", "## Files", "", f"- Model: `{path}`", f"- Plan: `{path.with_suffix('.plan.json')}`" if path.with_suffix(".plan.json").exists() else "",
              f"- Check report: `check.json`", f"- Views: `{Path(sheet).name}` and `views/*.png`", "- LeoCAD BOM: `views/leocad-bom.csv`"]
    if glb_result and "output" in glb_result:
        lines.append(f"- GLB: `{Path(glb_result['output']).name}`")
    elif glb_result:
        lines.append(f"- GLB: not produced ({glb_result.get('error', 'unknown error')})")
    if not report.get("checks_passed"):
        lines += ["", "## Open problems", "", "```", checker.format_report(report), "```"]
    friction = path.parent / "friction.md"
    if not friction.exists():
        atomic_write(friction, FRICTION)
    lines.append(f"- Friction report: `{friction}`")
    summary = outdir / "summary.md"
    atomic_write(summary, "\n".join(line for line in lines if line is not None) + "\n")
    return dict(verdict=verdict, summary=str(summary), sheet=sheet, outdir=str(outdir),
                bom_matches=bool(comparison.get("matches")), glb=(glb_result or {}).get("output"),
                seconds=round(time.perf_counter() - started, 1))
