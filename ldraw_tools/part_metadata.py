"""Read-only part information. No installed library or geometric expansion.

SQLite owns matching/indexing; generated category modules are parsed as data.
The source database is authoritative, and derived metadata is disposable.
"""
from __future__ import annotations

from contextlib import contextmanager
import csv
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import sqlite3
from tempfile import NamedTemporaryFile

from .common import CACHE, RESOURCE_DATA, database_path, normalized

CACHE_VERSION = 2


def filename(value):
    value = normalized(value.strip())
    if not value:
        raise ValueError('A part filename is required')
    return value if value.endswith('.dat') else value + '.dat'


@contextmanager
def database(path=None):
    path = database_path(path)
    if not path.is_file():
        raise ValueError(f'Part information database missing: {path}; restore it or choose another informational source')
    con = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    try:
        con.execute('SELECT part, description FROM PARTS_DESCRIPTIONS LIMIT 0')
        yield con
    except sqlite3.Error as exc:
        raise ValueError(f'Part information database {path}: {exc}; restore the required table/index; no library scan is performed') from exc
    finally:
        con.close()


def descriptions(path=None):
    with database(path) as con:
        return {r['part']: r['description'] for r in con.execute('SELECT part, description FROM PARTS_DESCRIPTIONS ORDER BY part')}


@lru_cache(maxsize=2)
def category_data(root, stamp, *, cache=None):
    """Persist the existing safe parser's output; never execute source modules."""
    from .catalog import _load
    key = hashlib.sha256(str(root).encode()).hexdigest()[:16]
    destination = (Path(cache or CACHE / 'part-metadata') / (key + '.sqlite')).resolve()
    signature = json.dumps([CACHE_VERSION, str(root), stamp])
    if destination.is_file():
        try:
            with sqlite3.connect(destination.as_uri() + '?mode=ro', uri=True) as con:
                if con.execute('SELECT signature FROM metadata').fetchone()[0] == signature:
                    values = dict(con.execute('SELECT name, payload FROM datasets'))
                    return tuple(json.loads(values[k]) for k in ('entries', 'colours', 'dimensions'))
        except (sqlite3.Error, ValueError, KeyError, TypeError, IndexError):
            pass  # A disposable cache can be rebuilt from its unchanged owners.
    values = _load(str(root), stamp)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=destination.parent, suffix='.sqlite', delete=False) as f:
        temporary = Path(f.name)
    try:
        with sqlite3.connect(temporary) as con:
            con.execute('CREATE TABLE metadata(signature TEXT NOT NULL)')
            con.execute('INSERT INTO metadata VALUES(?)', (signature,))
            con.execute('CREATE TABLE datasets(name TEXT PRIMARY KEY, payload TEXT NOT NULL)')
            con.executemany('INSERT INTO datasets VALUES(?,?)', [(k, json.dumps(v)) for k, v in zip(('entries', 'colours', 'dimensions'), values)])
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return values


def _category_dimensions():
    from .catalog import catalog_data, category_path
    try:
        return catalog_data()[2], str(category_path() / 'dimensions.py')
    except (OSError, ValueError, SyntaxError) as exc:
        return {}, str(exc)


def _usable(size):
    return size is not None and len(size) == 3 and all(isinstance(v, (float, int)) and math.isfinite(v) and v >= 0 for v in size)


def dimension_records(refs, *, path=None):
    refs = [filename(r) for r in refs]
    estimates, category_source = _category_dimensions()
    boxes = {}
    with database(path) as con:
        has_boxes = con.execute("SELECT 1 FROM sqlite_master WHERE name='PART_BBOXES'").fetchone() is not None
        if has_boxes:
            con.execute('SELECT alias, dim_x, dim_y, dim_z, complete FROM PART_BBOXES LIMIT 0')
            # Bounded batches avoid SQLite's parameter limit for filtered searches.
            unique = list(dict.fromkeys(refs))
            for start in range(0, len(unique), 500):
                batch = unique[start:start + 500]
                for row in con.execute('SELECT * FROM PART_BBOXES WHERE alias IN (' + ','.join('?' for _ in batch) + ')', batch):
                    boxes[row['alias']] = dict(row)
    results = []
    for ref in refs:
        box = boxes.get(ref)
        estimate = estimates.get(ref.removesuffix('.dat'))
        complete = bool(box and str(box.get('complete')).casefold() in {'true', '1'})
        size = [box.get('dim_' + a) for a in 'xyz'] if box else None
        cached = [estimate.get('ldu_' + a) for a in 'xyz'] if estimate else None
        selected = size if complete and _usable(size) else cached if _usable(cached) else None
        source = 'PART_BBOXES' if complete and _usable(size) else 'categories/dimensions.py' if selected is not None else None
        results.append(dict(part=ref, bbox=box, bbox_complete=complete if box else None,
                            category_estimate=estimate, selected_size_ldu=selected, selected_source=source,
                            missing=selected is None))
    return dict(source=str(database_path(path)), category_source=category_source, results=results,
                note='Cached local-axis extents, not stacking heights, connection planes or proof of fit. Sources may disagree; no geometry was loaded.')


def validate_sizes(min_size=None, max_size=None):
    for size in (min_size, max_size):
        if size is not None and (not _usable(size) or any(v <= 0 for v in size)):
            raise ValueError('Dimensions must be three finite positive LDU values')
    if min_size and max_size and any(a > b for a, b in zip(min_size, max_size)):
        raise ValueError('Minimum dimensions must not exceed maximum dimensions')


def search_parts(query, *, path=None, field='both', match='terms', limit=10, offset=0,
                 dimensions=False, min_size=None, max_size=None):
    if field not in {'part', 'description', 'both'} or match not in {'terms', 'exact', 'like'}:
        raise ValueError('Choose field part/description/both and match terms/exact/like')
    if limit < 1 or offset < 0 or not query.strip():
        raise ValueError('Query must be nonblank, limit positive and offset nonnegative')
    validate_sizes(min_size, max_size)
    columns = ['part', 'description'] if field == 'both' else [field]
    params, clauses = [], []
    terms = query.casefold().split() if match == 'terms' else [query]
    for term in terms:
        alternatives = []
        for column in columns:
            if match == 'exact':
                # Stored filenames are lowercase; equality uses the primary-key index.
                alternatives.append(f'{column} = ?' if column == 'part' else f'{column} = ? COLLATE NOCASE')
                params.append(filename(term) if column == 'part' else term)
            else:
                alternatives.append(f"{column} LIKE ? ESCAPE '\\'")
                literal = term.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
                params.append('%' + literal + '%' if match == 'terms' else term)
        clauses.append('(' + ' OR '.join(alternatives) + ')')
    where = ' AND '.join(clauses)
    order = ' ORDER BY CASE WHEN part = ? THEN 0 ELSE 1 END, length(description), part'
    filtered = min_size is not None or max_size is not None
    with database(path) as con:
        total = con.execute('SELECT count(*) FROM PARTS_DESCRIPTIONS WHERE ' + where, params).fetchone()[0]
        sql = 'SELECT part AS code, description FROM PARTS_DESCRIPTIONS WHERE ' + where + order
        args = [*params, filename(query)]
        if not filtered:
            sql += ' LIMIT ? OFFSET ?'
            args += [limit, offset]
        rows = [dict(r) for r in con.execute(sql, args)]
    if dimensions or filtered:
        details = dimension_records([r['code'] for r in rows], path=path)['results']
        for row, detail in zip(rows, details):
            row['dimensions'] = detail
        if filtered:
            rows = [r for r in rows if (s := r['dimensions']['selected_size_ldu']) is not None
                    and (min_size is None or all(v >= bound for v, bound in zip(s, min_size)))
                    and (max_size is None or all(v <= bound for v, bound in zip(s, max_size)))]
            total = len(rows)
            rows = rows[offset:offset + limit]
    return dict(source=str(database_path(path)), table='PARTS_DESCRIPTIONS', field=field, match=match,
                query=query, total=total, offset=offset, truncated=offset + len(rows) < total, results=rows,
                note='Descriptions are database metadata. Duplicate descriptions retain distinct filenames; installed availability and fit are unverified.')


def export_descriptions(*, path=None, output=None, force=False):
    target = Path(output or RESOURCE_DATA / 'parts-descriptions-full.tsv')
    if target.exists() and not force:
        return dict(path=str(target), created=False, reused=True, source=str(database_path(path)),
                    note='Existing snapshot preserved. Use --force to refresh after database changes.')
    target.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(mode='w', encoding='utf-8', newline='', dir=target.parent, delete=False) as f:
        temporary = Path(f.name)
        try:
            with database(path) as con:
                con.execute('BEGIN')
                writer = csv.writer(f, delimiter='\t', lineterminator='\r\n')
                writer.writerow(['part', 'description'])
                count = 0
                for row in con.execute('SELECT part, description FROM PARTS_DESCRIPTIONS ORDER BY part'):
                    writer.writerow(row)
                    count += 1
            f.flush()
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    return dict(path=str(target), created=True, reused=False, rows=count, source=str(database_path(path)),
                note='Full description snapshot. Refresh explicitly with --force after database changes.')
