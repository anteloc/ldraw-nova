"""Run from the repository: .venv/bin/python examples/python_api.py

The JSON builder is simpler for most agents. This example shows procedural reuse.
"""
from pathlib import Path

from ldraw_tools.common import atomic_write, dumps, get_parts
from ldraw_tools.workflow import build_checked

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
atomic_write(Path("output/tower.plan.json"), dumps(plan) + "\n")
text, _, report = build_checked(plan, get_parts(), detail="summary")
if not report['checks_passed']:
    raise SystemExit(dumps(report))
atomic_write(Path("output/tower.mpd"), text)
print("Wrote output/tower.plan.json and output/tower.mpd. Next: ./ldraw-agent review output/tower.mpd")
