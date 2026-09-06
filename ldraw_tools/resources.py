from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
from pathlib import Path

from .common import ROOT, CACHE, atomic_write, models_path


def spec_pages(pdf=None):
    path = Path(pdf or ROOT / "docs/ldraw-specs.pdf")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    cache = CACHE / f"spec-{digest}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    # Poppler raw mode preserves words in this PDF better than layout/pypdf extraction.
    text = subprocess.run(["pdftotext", "-raw", str(path), "-"], check=True,
                          capture_output=True, text=True, timeout=60).stdout
    pages = text.split("\f")
    if not pages[-1].strip():
        pages.pop()
    result = dict(source=str(path), sha256=digest, extractor="pdftotext -raw", pages=pages)
    atomic_write(cache, json.dumps(result, ensure_ascii=False))
    return result


def search_spec(query=None, page=None, limit=8):
    source = spec_pages()
    if page is not None:
        if page < 1 or page > len(source["pages"]):
            raise ValueError(f"Page must be 1–{len(source['pages'])}")
        results = [dict(page=page, text=source["pages"][page-1])]
    else:
        terms = (query or "").casefold().split()
        results = []
        for i, text in enumerate(source["pages"], 1):
            if all(t in text.casefold() for t in terms):
                first = text.casefold().find(terms[0]) if terms else 0
                results.append(dict(page=i, excerpt=text[max(0, first-160):first+900]))
        results = results[:limit]
    return dict(source=source["source"], sha256=source["sha256"], page_count=len(source["pages"]), results=results)


def search_models(query, *, root=None, limit=10, submodels=False):
    root = models_path(root)
    db = root.parent / "scripts/ldraw-info.db"
    if db.exists():
        with sqlite3.connect(db.as_uri() + "?mode=ro", uri=True) as con:
            con.row_factory = sqlite3.Row
            table = "SUBMODELS_DESCRIPTIONS_FTS" if submodels else "MODELS_DESCRIPTIONS_FTS"
            columns = "model, submodel, description" if submodels else "model, description"
            rows = con.execute(f"SELECT {columns} FROM {table} WHERE {table} MATCH ? LIMIT ?", (query, limit)).fetchall()
        matches = [dict(r) | {"path": str(root / r["model"]), "source_exists": (root / r["model"]).is_file()} for r in rows]
        return dict(source=str(db), query_language="SQLite FTS5", index_mtime=db.stat().st_mtime, results=matches,
                    note="Existing index reused read-only. Check the source header before reuse; annotations and index may be stale.")
    # No database is required: deterministic bounded header scan, no model copying.
    matches = []
    for path in sorted(root.glob("*.mpd")):
        section, title = None, None
        for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            if line.startswith("0 FILE "):
                if section and not submodels:
                    break
                section, title = line[7:], None
            elif section and title is None and line.startswith("0 "):
                title = line[2:]
                if all(term in title.casefold() for term in query.casefold().split()):
                    matches.append(dict(model=path.name, submodel=section, description=title, path=str(path), source_exists=True))
                    if len(matches) >= limit:
                        return dict(source=str(root), query_language="plain AND terms (database absent)", results=matches)
    return dict(source=str(root), query_language="plain AND terms (database absent)", results=matches)


def model_sections(path, section=None):
    """Read original annotated blocks with absolute file line numbers, without rewriting."""
    rows = []
    active = None
    for number, line in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1):
        if line.startswith("0 FILE "):
            active = dict(name=line[7:], start_line=number, lines=[])
            rows.append(active)
        if active is not None:
            active["lines"].append([number, line])
    if section:
        matches = [r for r in rows if r["name"].casefold() == section.casefold()]
        if not matches:
            raise ValueError(f"No section named {section}")
        return dict(source=str(path), sections=matches)
    return dict(source=str(path), sections=[dict(name=r["name"], start_line=r["start_line"],
                 description=next((line[2:] for _, line in r["lines"][1:] if line.startswith("0 ")), ""),
                 placements=sum(line.startswith("1 ") for _, line in r["lines"])) for r in rows])
