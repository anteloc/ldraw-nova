from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
from pathlib import Path

from .common import ROOT, CACHE, atomic_write, database_path, models_path


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


def search_models(query, *, root=None, database=None, limit=10, submodels=False, offset=0):
    if limit < 1 or offset < 0:
        raise ValueError("Limit must be positive and offset nonnegative")
    root = models_path(root)
    db = database_path(database)
    if db.exists():
        with sqlite3.connect(db.as_uri() + "?mode=ro", uri=True) as con:
            con.row_factory = sqlite3.Row
            table = "SUBMODELS_DESCRIPTIONS_FTS" if submodels else "MODELS_DESCRIPTIONS_FTS"
            columns = "model, submodel, description" if submodels else "model, description"
            total = con.execute(f"SELECT count(*) FROM {table} WHERE {table} MATCH ?", (query,)).fetchone()[0]
            rows = con.execute(f"SELECT {columns}, rank FROM {table} WHERE {table} MATCH ? ORDER BY rank, model LIMIT ? OFFSET ?", (query, limit, offset)).fetchall()
        matches = [dict(r) | {"path": str(root / r["model"]), "source_exists": (root / r["model"]).is_file()} for r in rows]
        return dict(source=str(db), query_language="SQLite FTS5", index_mtime=db.stat().st_mtime, results=matches,
                    total=total, offset=offset, truncated=offset+len(matches)<total,
                    note="Existing index reused read-only. Check the source header before reuse; annotations and index may be stale.")
    matches = []
    for path in sorted(root.glob("*.mpd")):
        sections = model_sections(path)["sections"]
        for row in sections[1:] if submodels else sections[:1]:
            if all(term in row["description"].casefold() for term in query.casefold().split()):
                matches.append(dict(model=path.name, submodel=row["name"], description=row["description"], path=str(path), source_exists=True))
    return dict(source=str(root), query_language="plain AND terms (database absent)", total=len(matches),
                offset=offset, truncated=offset+limit<len(matches), results=matches[offset:offset+limit])


def model_sections(path, section=None):
    """Inventory raw headers and records, including sources without FILE blocks."""
    lines = list(enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1))
    rows, active = [], None
    for number, line in lines:
        fields = line.split(None, 2)
        if fields[:2] == ["0", "FILE"] and len(fields) == 3:
            active = dict(name=fields[2], start_line=number, lines=[], has_file=True)
            rows.append(active)
        if active is not None:
            active["lines"].append([number, line])
        if fields[:2] == ["0", "NOFILE"]:
            active = None
    if not rows:
        from .document import parse_source
        rows = [dict(name=parse_source(path).name, start_line=1, lines=lines, has_file=False)]
    if section is not None:
        matches = [r for r in rows if r["name"].casefold() == section.casefold()]
        if not matches:
            matches = [r for r in rows if r["name"].strip().casefold() == section.strip().casefold()]
        if len(matches) != 1:
            raise ValueError(f"{'Ambiguous' if matches else 'Unknown'} section {section!r}")
        return dict(source=str(path), sections=matches)
    result = []
    for row in rows:
        body = row["lines"][1:] if row["has_file"] else row["lines"]
        title = next((line[2:] for _, line in body if line.startswith("0 ")), "")
        counts = {str(k):sum(line.split()[:1] == [str(k)] for _,line in body) for k in range(1,6)}
        theme = next((line.split("!THEME",1)[1].strip() for _,line in body if line.startswith("0 !THEME ")), "")
        result.append(dict(name=row["name"], start_line=row["start_line"], has_file=row["has_file"], description=title,
                           placements=counts["1"], raw_geometry=sum(counts[str(k)] for k in range(2,6)), theme=theme))
    return dict(source=str(path), sections=result)
