"""Run every recipe page's generator, require a PASS, and refresh its preview image.

    .venv/bin/python scripts/build_recipes.py              # all docs/reference/*.md recipes
    .venv/bin/python scripts/build_recipes.py small-car    # one recipe

A recipe page holds exactly one ```python block that saves output/<name>/<name>.mpd.
Previews are written to docs/reference/img/<name>.png with the views named in the
page's image alt text (e.g. "home, front and top views").
"""
from __future__ import annotations

import contextlib
import io
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ldraw_tools.common import get_parts, library_path  # noqa: E402
from ldraw_tools.look import look  # noqa: E402

VIEWS = ("home", "front", "back", "left", "right", "top", "bottom")


def recipes(names=()):
    for page in sorted((ROOT / "docs/reference").glob("*.md")):
        code = re.findall(r"```python\n(.*?)```", page.read_text(), re.S)
        if len(code) == 1 and (not names or page.stem in names):
            yield page, code[0]


def run(page, code, workdir):
    """Execute a recipe in ``workdir``; return (passed, mpd path, printed check)."""
    previous = Path.cwd()
    output = io.StringIO()
    try:
        os.chdir(workdir)
        with contextlib.redirect_stdout(output):
            exec(compile(code, str(page), "exec"), {"__name__": "__recipe__"})
    finally:
        os.chdir(previous)
    saved = re.search(r'save\("([^"]+)"', code).group(1)
    text = output.getvalue()
    return text.startswith("PASS"), Path(workdir) / saved, text


def main():
    parts, library = get_parts(), library_path()
    failures = 0
    for page, code in recipes(sys.argv[1:]):
        with tempfile.TemporaryDirectory(prefix="recipe-") as temp:
            passed, mpd, text = run(page, code, temp)
            print(f"{'PASS' if passed else 'FAIL'} {page.name}: {text.splitlines()[0] if text else 'no check output'}")
            if not passed:
                failures += 1
                continue
            alt = re.search(r"!\[[^\]]*:\s*([^\]]*)\]\(img/", page.read_text())
            views = [v for v in VIEWS if alt and v in alt.group(1)] or ["home", "top"]
            sheet = look(mpd, parts, library, Path(temp) / "look", views=views, cell=420)["sheet"]
            target = ROOT / "docs/reference/img" / f"{page.stem}.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(sheet, target)
            print(f"     preview {target.relative_to(ROOT)} ({', '.join(views)})")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
