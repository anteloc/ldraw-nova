"""Render every Mermaid block in agent-facing Markdown to catch syntax errors.

    .venv/bin/python scripts/check_mermaid.py [FILES...]   # default: instructions.md, docs/**/*.md, examples/**/*.md

Uses mermaid-cli through npx (@mermaid-js/mermaid-cli). When puppeteer's own
headless Chrome is missing, set CHROME to a local browser executable; on macOS
Google Chrome is found automatically. Exit 1 if any block fails to render.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAC_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def blocks(paths):
    for path in paths:
        for number, block in enumerate(re.findall(r"```mermaid\s*\n(.*?)```", path.read_text(), re.S)):
            yield path, number, block


def main():
    paths = [Path(p) for p in sys.argv[1:]] or [ROOT / "instructions.md", *sorted((ROOT / "docs").rglob("*.md")),
                                                *sorted((ROOT / "examples").rglob("*.md"))]
    chrome = os.environ.get("CHROME") or (MAC_CHROME if Path(MAC_CHROME).exists() else None)
    failures = 0
    with tempfile.TemporaryDirectory(prefix="mermaid-") as temp:
        config = Path(temp) / "puppeteer.json"
        config.write_text(json.dumps({"executablePath": chrome, "args": ["--no-sandbox"]} if chrome else {}))
        for path, number, block in blocks(paths):
            source = Path(temp) / f"block-{number}.mmd"
            source.write_text(block)
            result = subprocess.run(["npx", "--yes", "@mermaid-js/mermaid-cli", "-p", str(config), "-q",
                                     "-i", str(source), "-o", str(source.with_suffix(".svg"))],
                                    capture_output=True, text=True)
            label = f"{path.relative_to(ROOT) if path.is_relative_to(ROOT) else path} #{number}"
            if result.returncode:
                failures += 1
                print(f"FAIL {label}: {(result.stderr.strip().splitlines() or ['?'])[0]}")
            else:
                print(f"ok   {label}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
