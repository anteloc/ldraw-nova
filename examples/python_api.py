"""Run from the repository: .venv/bin/python examples/python_api.py

The JSON builder is simpler for most agents. This example shows procedural reuse.
"""
from pathlib import Path

from ldraw_tools.builder import build_plan
from ldraw_tools.common import atomic_write, get_parts
from ldraw_tools.geometry import analyze_geometry

plan = {
    "version": 1,
    "author": "LDraw Nova example",
    "sections": [{
        "name": "tower-main.ldr", "description": "Alternating colour brick tower",
        "steps": [[{"id": f"brick-{i}", "ref": "3003.dat", "colour": 4 if i % 2 else 1,
                    **({"on": f"brick-{i-1}"} if i else {"at": [0, 0, 0]})}]
                  for i in range(4)]
    }]
}
parts = get_parts()
text, model, issues = build_plan(plan, parts)
assert not any(i["severity"] == "error" for i in issues), issues
report = analyze_geometry(model, parts)
assert not any(i["severity"] == "error" for i in report["diagnostics"]), report["diagnostics"]
atomic_write(Path("output/tower.mpd"), text)
print("Wrote output/tower.mpd; render and review before delivery.")
