#!/usr/bin/env python3
"""LDraw annotated model selector: index data/models-annotated, then serve it.

    python3 model-selector/serve.py [--port 8770] [--no-open]

1. Writes output/model-selector/models-annotated.json (name, path, url, description, parts).
2. Serves model-selector.html (search), search.js and viewer.html (3D) on 127.0.0.1 only.

Standard library only. See model-selector/README.md.
"""

import argparse
import json
import os
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

HERE = Path(__file__).resolve().parent              # model-selector/
ROOT = HERE.parent                                  # the repository
MODELS = ROOT / "data" / "models-annotated"
LDRAW = Path(os.environ.get("LDRAW_DIR") or os.environ.get("LDRAWDIR") or ROOT / "data/ldraw").expanduser().resolve()
VENDOR = ROOT / "bin" / "ldbi-viewer"               # fetched by setup.sh
INDEX = ROOT / "output" / "model-selector" / "models-annotated.json"


def describe(mpd: Path) -> tuple[str, int]:
    """(description, parts) of one model, in a single read.

    The description is the line after "0 FILE"; without a "0 FILE" line it is the first line.
    Leading blank lines are skipped (e.g. 4906-1.mpd starts with one).
    parts is the number of parts in the built model, as the 3D viewer counts them: from the
    main model (see count_parts), each submodel counted once per use. A reference to a library
    part or to a part defined inside the file ("0 FILE x.dat") counts as one part."""
    head, sections, current = [], {}, ""            # section name -> its type-1 references ("" before any 0 FILE)
    with mpd.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if len(head) < 2:
                head.append(line)
            if line.startswith("0 FILE "):
                current = ref_name(line[len("0 FILE "):])
                sections.setdefault(current, [])
            elif line.startswith("1 "):
                tokens = line.split(maxsplit=14)
                if len(tokens) == 15:
                    sections.setdefault(current, []).append(ref_name(tokens[14]))
    first, second = (head + ["", ""])[:2]
    line = second if first.startswith("0 FILE") else first
    description = line[2:].strip() if line.startswith("0 ") else line
    return description, count_parts(sections)


def ref_name(name: str) -> str:
    """LDraw file names are case-insensitive and may use either slash."""
    return name.strip().lower().replace("\\", "/")


def count_parts(sections: dict) -> int:
    """Parts in the main model: the first section with references (like the viewer, which skips
    an empty first section, e.g. 6360-1.mpd), expanding submodels (not .dat parts) recursively."""
    counts, open_ = {}, set()

    def count(name):
        if name not in counts:
            if name in open_:                       # a submodel that includes itself: stop
                return 0
            open_.add(name)
            counts[name] = sum(count(ref) if ref in sections and not ref.endswith(".dat") else 1
                               for ref in sections[name])
            open_.discard(name)
        return counts[name]

    main = next((name for name, refs in sections.items() if refs), None)
    return count(main) if main is not None else 0


def build_index() -> list[dict]:
    if not MODELS.is_dir():
        raise ValueError(f"Model directory missing: {MODELS}")
    models = []
    for mpd in sorted(MODELS.glob("*.mpd")):
        description, parts = describe(mpd)
        models.append({
            "name": mpd.name,
            "path": mpd.relative_to(ROOT).as_posix(),     # what the user gives the agent
            "url": f"/models/{quote(mpd.name)}",                 # what the viewer loads
            "description": description,
            "parts": parts,
        })
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps(models, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return models


def inside(root: Path, rel: str) -> Path | None:
    """root/rel, or None when it would leave root (../ tricks)."""
    path = (root / rel).resolve()
    return path if path.is_relative_to(root.resolve()) else None


def ldraw_by_id(part_id: str) -> Path | None:
    """A type-1 reference as LDraw resolves it: parts/, then p/, then models/.
    Same as ldraw-nova's /ldraw-id/ endpoint: one request per part, no 404 probing."""
    for sub in ("parts", "p", "models"):
        for name in (part_id, part_id.lower()):   # the library's file names are lowercase
            path = inside(LDRAW / sub, name)
            if path and path.is_file():
                return path
    return None


class Handler(SimpleHTTPRequestHandler):
    # URL prefix -> folder. Everything else comes from model-selector/ itself.
    ROUTES = {"/models/": MODELS, "/ldraw/": LDRAW, "/vendor/": VENDOR}
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map,
                      ".mpd": "text/plain; charset=utf-8", ".ldr": "text/plain; charset=utf-8",
                      ".dat": "text/plain; charset=utf-8"}

    def translate_path(self, path: str) -> str:
        url = unquote(urlsplit(path).path)
        if url == "/":
            return str(HERE / "model-selector.html")
        if url == "/models-annotated.json":
            return str(INDEX)
        if url.startswith("/ldraw-id/"):
            found = ldraw_by_id(url[len("/ldraw-id/"):])
            return str(found or HERE / "missing")      # missing -> plain 404
        for prefix, root in self.ROUTES.items():
            if url.startswith(prefix):
                found = inside(root, url[len(prefix):])
                return str(found or HERE / "missing")
        found = inside(HERE, url.lstrip("/"))
        return str(found or HERE / "missing")

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")  # always the newest index and pages
        super().end_headers()

    def log_message(self, format, *args):           # quiet: only report errors
        if args and str(args[1])[:1] in "45":
            super().log_message(format, *args)


def main():
    global LDRAW
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=8770)
    parser.add_argument("--no-open", action="store_true", help="don't open the browser")
    parser.add_argument("--library", type=Path, help="LDraw library (LDRAW_DIR, LDRAWDIR, then data/ldraw)")
    parser.add_argument("--index-only", action="store_true", help="rebuild the model index without starting a server")
    args = parser.parse_args()
    if args.library:
        LDRAW = args.library.expanduser().resolve()
    Handler.ROUTES["/ldraw/"] = LDRAW

    missing = [p for p in (LDRAW / "LDConfig.ldr", VENDOR / "js" / "ldraworgscene.js") if not p.is_file()]
    if missing:
        raise SystemExit(f"Missing {', '.join(str(p) for p in missing)}: "
                         "run ./setup.sh or set --library (docs/setup.md).")

    models = build_index()
    print(f"Indexed {len(models)} models -> {INDEX.relative_to(ROOT)}")

    if args.index_only:
        return

    server = ThreadingHTTPServer(("127.0.0.1", args.port), partial(Handler, directory=str(HERE)))
    url = f"http://127.0.0.1:{server.server_port}/"
    print(f"Model selector at {url}  (Ctrl+C to stop)")
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
