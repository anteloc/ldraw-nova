"""Check every curated example model and record the verdict agents see.

    .venv/bin/python scripts/example_status.py

Writes examples/status.json (read by ``ldraw-agent examples``) and examples/STATUS.md.
An example that fails check teaches broken construction: repair it, or say so when citing it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ldraw_tools.check import check_model  # noqa: E402
from ldraw_tools.common import get_parts, library_path  # noqa: E402

SKIP = ("part-board", "shortlist", "/proto/", "review-manual", "rose-fit", "window-fit", "/manual/", "/work/",
        "/studies/", "/research/", "/assets/", "mechanism-sources", "/archive/")


def models():
    for path in sorted((ROOT / "examples").rglob("*.mpd")):
        relative = path.relative_to(ROOT).as_posix()
        if path.name not in {"source.mpd", "preview.mpd"} and not any(s in "/" + relative for s in SKIP):
            yield relative


def summary(report):
    if "parts" not in report:
        return "source errors"
    problems = [f"{report['floating_count']} floating" if report["floating_count"] else "",
                f"{report['collision_count']} collisions" if report["collision_count"] else "",
                f"{report['seating_count']} badly seated" if report["seating_count"] else "",
                f"{report['duplicate_count']} duplicates" if report["duplicate_count"] else ""]
    return ", ".join(p for p in problems if p) or "clean"


def main():
    parts, library = get_parts(), library_path()
    status = {}
    for relative in models():
        report = check_model(ROOT / relative, parts, library)
        status[relative] = dict(verdict="PASS" if report.get("checks_passed") else "FAIL", parts=report.get("parts"),
                                problems=summary(report))
        print(f"{status[relative]['verdict']} {relative}: {status[relative]['problems']}")
    (ROOT / "examples/status.json").write_text(json.dumps(status, indent=1) + "\n")
    passed = sum(s["verdict"] == "PASS" for s in status.values())
    lines = ["# Example status", "",
             f"`check` verdicts for the curated examples ({passed} of {len(status)} pass). "
             "Regenerate with `.venv/bin/python scripts/example_status.py`.", "",
             "A failing example still shows ideas (shapes, palettes, layouts), but its construction has the listed "
             "defects. Do not copy its coordinates. Prefer the [recipes](../docs/reference/README.md), which always pass.", "",
             "| Example | Parts | Check | Problems |", "|---|---:|---|---|"]
    for relative, s in status.items():
        lines.append(f"| [{relative.removeprefix('examples/')}]({relative.removeprefix('examples/')}) | {s['parts']} | {s['verdict']} | {s['problems']} |")
    (ROOT / "examples/STATUS.md").write_text("\n".join(lines) + "\n")
    print(f"{passed} of {len(status)} pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
