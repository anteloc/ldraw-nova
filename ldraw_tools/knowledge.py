"""Offline retrieval of authored guidance and explicitly registered examples.

Example metadata lives in a README fenced ``ldraw-knowledge`` JSON list. Catalogs
are projections, never admission authorities. Indexes are rebuilt in memory so a
changed source cannot leave a stale on-disk search result.
"""
from __future__ import annotations

import hashlib
from itertools import zip_longest
import html
import json
import os
import re
import sqlite3
from pathlib import Path

from .common import ROOT

SCOPES = ('default', 'construction', 'tutorial', 'inspiration', 'diagnostic', 'research', 'archive', 'hold', 'all')
DEFAULT_SCOPES = {'guidance', 'construction', 'tutorial'}
_METADATA = re.compile(r'^```ldraw-knowledge\s*\n(.*?)\n```\s*$', re.M | re.S)
PATH_FIELDS = ('model', 'plan', 'generator', 'preview', 'manual', 'operation', 'study_notes', 'board', 'visual_review')


def confined(root, value):
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'Knowledge path escapes repository: {value}')
    return path


def examples(root=None):
    root = Path(root or ROOT)
    records = []
    identities = set()
    aliases = set()
    paths = [path for base in ('examples', 'tests/fixtures', 'lsynth-examples')
             for path in (root/base).rglob('README.md')]
    for path in sorted(paths):
        text = path.read_text(encoding='utf-8')
        matches = list(_METADATA.finditer(text))
        if not matches:
            continue
        if len(matches) != 1:
            raise ValueError(f'Expected one knowledge metadata block: {path}')
        entries = json.loads(matches[0].group(1))
        if not isinstance(entries, list):
            raise ValueError(f'Knowledge metadata must be a list: {path}')
        for entry in entries:
            required = ('id', 'title', 'scope', 'lesson', 'aliases', 'families')
            if not isinstance(entry, dict) or any(k not in entry for k in required):
                raise ValueError(f'Incomplete knowledge entry: {path}')
            if any(not isinstance(entry[k], str) or not entry[k].strip() for k in ('id', 'title', 'scope', 'lesson')):
                raise ValueError(f'Invalid knowledge entry text: {path}')
            if entry['scope'] not in SCOPES[1:-1]:
                raise ValueError(f'Invalid knowledge scope: {path}')
            if path.is_relative_to(root/'tests/fixtures') and entry['scope'] != 'diagnostic':
                raise ValueError(f'Test fixtures must retain diagnostic scope: {path}')
            if path.is_relative_to(root/'lsynth-examples') and entry['scope'] != 'research':
                raise ValueError(f'Raw LSynth sources must retain research scope: {path}')
            for key in ('aliases', 'families', 'subjects', 'techniques', 'legacy_groups'):
                if key in entry and (not isinstance(entry[key], list) or any(not isinstance(v, str) or not v for v in entry[key])):
                    raise ValueError(f'Invalid {key}: {path}')
            if 'source_group' in entry and (not isinstance(entry['source_group'], str) or not entry['source_group'].strip()):
                raise ValueError(f'Invalid source_group: {path}')
            if entry['id'] in identities:
                raise ValueError(f'Duplicate knowledge ID: {entry["id"]}')
            identities.add(entry['id'])
            for alias in entry['aliases']:
                if ':' not in alias or alias in aliases:
                    raise ValueError(f'Duplicate or unqualified knowledge alias: {alias}')
                aliases.add(alias)
            row = dict(entry, guide=str(path.resolve()), source_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            for key in PATH_FIELDS:
                if key in row:
                    target = confined(root, row[key])
                    if not target.exists():
                        raise ValueError(f'Missing {key} for {entry["id"]}: {target}')
                    row[key] = str(target)
            if 'model' in row:
                actual = hashlib.sha256(Path(row['model']).read_bytes()).hexdigest()
                if not row.get('model_sha256') or actual != row['model_sha256']:
                    row['declared_scope'] = row['scope']
                    row['scope'] = 'hold'
                    row['export_blocker'] = 'Registered model identity is missing or stale; review the changed source before admission.'
            records.append(row)
    # A canonical ID may not secretly resolve to another entry's alias.
    for row in records:
        for alias in row['aliases']:
            if alias in identities and alias != row['id']:
                raise ValueError(f'Alias conflicts with knowledge ID: {alias}')
    return records


def resolve(identity, *, family=None, root=None):
    """Resolve explicitly, including held entries; admission/export is separate."""
    rows = examples(root)
    canonical = next((r for r in rows if r['id'] == identity), None)
    if canonical and (family is None or family in canonical['families']):
        return canonical
    qualified = f'{family}:{identity}' if family and ':' not in identity else identity
    matches = [r for r in rows if qualified == r['id'] or qualified in r['aliases']]
    if not matches and not family and ':' not in identity:
        matches = [r for r in rows if any(a.rsplit(':', 1)[-1] == identity for a in r['aliases'])]
    if not matches:
        raise ValueError(f'Unknown knowledge example: {qualified}')
    if len(matches) != 1:
        raise ValueError('Ambiguous example; use one of: ' + ', '.join(sorted(r['id'] for r in matches)))
    return matches[0]


def require_exportable(record):
    """Admission is necessary, never sufficient for the existing export checks."""
    if record['scope'] not in ('construction', 'tutorial') or record.get('export_blocker'):
        raise ValueError(f"Example {record['id']} is {record['scope']}; reusable export is blocked. "
                         + record.get('export_blocker', record.get('limits', 'Read its source and scope.')))
    return record


def export_directory(identity, *, family=None, root=None):
    record = require_exportable(resolve(identity, family=family, root=root))
    return Path(record.get('model', record['guide'])).parent


def check_directory_scope(folder, *, root=None):
    """Explicit directory exports must not bypass a registered hold."""
    folder = Path(folder).resolve()
    rows = [r for r in examples(root) if Path(r.get('model', r['guide'])).parent == folder]
    for row in rows:
        require_exportable(row)
    return rows


def source_group(row):
    """Explicit source identity, with a conservative shared-section fallback."""
    return row.get('source_group', row['id'].split('#', 1)[0])


def interleave_sources(rows, *, key=source_group):
    """Stable round-robin across source groups, without removing any result."""
    groups = {}
    for row in rows:
        groups.setdefault(key(row), []).append(row)
    return [row for layer in zip_longest(*groups.values()) for row in layer if row is not None]


def write_compat_catalog(family, directory, *, root=None):
    """Regenerate legacy browsing views from README owners and frozen evidence.

    The JSON retains explicit non-default scopes for old callers. The gallery
    shows only default-eligible lessons; neither output grants export approval.
    """
    from .common import atomic_write
    from .manuals import current_manual, current_review
    directory = Path(directory).resolve()
    rows = []
    for entry in examples(root):
        aliases = [a for a in entry['aliases'] if a.startswith(family + ':')]
        if not aliases:
            continue
        row = dict(entry, key=aliases[0].split(':', 1)[1],
                   group='examples' if 'examples' in entry.get('legacy_groups', []) else 'details',
                   use='adapt' if entry['scope'] in DEFAULT_SCOPES else 'inspiration')
        folder = Path(entry.get('model', entry['guide'])).parent
        row['readme_sha256'] = row['source_sha256']
        if 'model_sha256' in row:
            row['source_sha256'] = row['model_sha256']
        row['category'] = ', '.join(entry.get('subjects', [])) or entry.get('kind', 'study')
        if (folder/'card.json').is_file():
            card = json.loads((folder/'card.json').read_text())
            row['reference_id'] = card['id']
            row['source_sha256'] = card['source']['sha256']
            row['source_checks_passed'] = card['assembly_checks_passed']
            row['bom_matches'] = card['bom_comparison']['matches']
        elif (folder/'validation.json').is_file():
            validation = json.loads((folder/'validation.json').read_text())
            row['checks_passed'] = validation.get('checks_passed', False)
            if (folder/'bom-comparison.json').is_file():
                row['bom_matches'] = json.loads((folder/'bom-comparison.json').read_text()).get('matches', False)
        if (folder/'manual.json').is_file():
            _, manual = current_manual(folder)
            row.update(source_checks_passed=manual['source_checks_passed'], bom_matches=manual['bom_matches'],
                       visual_review_status='visually_reviewed' if current_review(folder) else 'pending')
        for field in (*PATH_FIELDS, 'guide'):
            if field in row:
                row[field] = os.path.relpath(row[field], directory)
        rows.append(row)
    if family == 'spaceship':
        rows = interleave_sources(rows)
    catalog = dict(version=2, generated_from='package README registrations', family=family,
                   examples=[r for r in rows if r['group']=='examples'],
                   details=[r for r in rows if r['group']=='details'])
    atomic_write(directory/'catalog.json', json.dumps(catalog, indent=2, ensure_ascii=False)+'\n')
    cards = []
    for row in rows:
        if row['scope'] not in DEFAULT_SCOPES:
            continue
        preview = row.get('board', row.get('preview'))
        picture = f'<img src="{html.escape(preview, quote=True)}" alt="">' if preview else ''
        cards.append(f'<article><h2><a href="{html.escape(row["guide"], quote=True)}">{html.escape(row["title"])}</a></h2>'
                     +picture+'<p>'+html.escape(row['lesson'])+'</p><p>'+html.escape(row.get('limits',''))+'</p></article>')
    atomic_write(directory/'index.html', '<!doctype html><html lang="en"><meta charset="utf-8">'
                 '<meta name="viewport" content="width=device-width,initial-scale=1"><title>Construction lessons</title>'
                 '<style>body{font:16px/1.5 system-ui;max-width:900px;margin:2rem auto;padding:0 1rem}img{max-width:100%}article{margin:2rem 0}</style>'
                 '<h1>'+html.escape(family)+' construction lessons</h1><p>Generated from package READMEs. '
                 'Inspiration, held, diagnostic and retired sources require explicit knowledge search scopes.</p>'
                 +''.join(cards)+'</html>\n')
    return rows


def _sections(text):
    """Source heading, GitHub-style anchor, starting line and section body."""
    heading = 'Overview'; anchor = ''; start = 1; body = []; fenced = None; seen = {}
    for number, line in enumerate(text.splitlines(), 1):
        fence = re.match(r'^\s*(`{3,}|~{3,})', line)
        if fence:
            mark = fence[1][0]
            if fenced is None: fenced = mark
            elif fenced == mark: fenced = None
        match = re.match(r'^#{1,6}\s+(.+?)\s*#*$', line) if fenced is None and not fence else None
        if match:
            if body and any(s.strip() for s in body):
                yield heading, anchor, start, '\n'.join(body)
            heading = match[1]
            slug = re.sub(r'[^\w\- ]', '', heading.casefold()).replace(' ', '-')
            count = seen.get(slug, 0); seen[slug] = count + 1
            anchor = slug + (f'-{count}' if count else '')
            start = number; body = []
        else:
            body.append(line)
    if body and any(s.strip() for s in body):
        yield heading, anchor, start, '\n'.join(body)


def documents(root=None, *, include_research=False):
    root = Path(root or ROOT)
    paths = list((root/'docs/agent').rglob('*.md'))
    if include_research:
        paths += list((root/'docs/reports').glob('*.md'))
    for path in sorted(paths):
        # Historical verification is not current guidance; relocated reports are
        # outside this allowlisted root. Redirect stubs do not duplicate results.
        if path.name == 'verification.md': continue
        text = path.read_text(encoding='utf-8')
        if '<!-- knowledge-redirect -->' in text: continue
        relative = path.relative_to(root).as_posix()
        title = next((s[2:].strip() for s in text.splitlines() if s.startswith('# ')), path.stem)
        contexts = {}; stack = []; fence = None
        for number, line_text in enumerate(text.splitlines(), 1):
            marker = re.match(r'^\s*(`{3,}|~{3,})', line_text)
            if marker:
                char = marker[1][0]
                fence = None if fence == char else char if fence is None else fence
                continue
            heading = re.match(r'^(#{1,6})\s+(.+?)\s*#*$', line_text) if fence is None else None
            if heading:
                depth = len(heading[1])
                stack = [(d, h) for d, h in stack if d < depth] + [(depth, heading[2])]
                contexts[number] = [h for _, h in stack]
        for heading, anchor, line, body in _sections(text):
            context = contexts.get(line, [title, heading])
            yield dict(id=relative + ('#' + anchor if anchor else ''), title=' > '.join(context), headings=context,
                       scope='research' if path.is_relative_to(root/'docs/reports') else 'guidance',
                       kind='report' if path.is_relative_to(root/'docs/reports') else 'guide', guide=str(path.resolve()), anchor=anchor,
                       line=line, lesson=body, source_sha256=hashlib.sha256(text.encode()).hexdigest())


def search(query='', *, limit=5, scope='default', family=None, kind=None,
           subject=None, technique=None, only_examples=False, details=None, scale=None, root=None, diversify=None):
    if scope not in SCOPES: raise ValueError('Unknown knowledge scope: ' + scope)
    if limit <= 0: raise ValueError('limit must be positive')
    diversify = diversify or ('source' if family == 'spaceship' else 'none')
    if diversify not in {'source', 'none'}: raise ValueError('Choose source or none diversification')
    records = examples(root)
    if not only_examples: records.extend(documents(root, include_research=scope in ('research','all')))
    eligible = []
    for row in records:
        if scope == 'default' and row['scope'] not in DEFAULT_SCOPES: continue
        if scope not in ('default', 'all') and row['scope'] != scope: continue
        if family and family not in row.get('families', []): continue
        if kind and kind != row.get('kind'): continue
        if subject and subject.casefold() not in [v.casefold() for v in row.get('subjects', [])]: continue
        if technique and technique.casefold() not in [v.casefold() for v in row.get('techniques', [])]: continue
        if scale and scale != row.get('scale'): continue
        if details is not None and ('details' if details else 'examples') not in row.get('legacy_groups', []): continue
        eligible.append(row)
    terms = re.findall(r'\w+', query, re.UNICODE)
    if query.strip() and not terms:
        return dict(total=0, results=[], truncated=False, engine='sqlite-fts5-bm25', scope=scope, diversification=diversify)
    with sqlite3.connect(':memory:') as db:
        db.execute('CREATE VIRTUAL TABLE knowledge USING fts5(title, metadata, lesson)')
        for row in eligible:
            metadata = ' '.join([row['id'], *row.get('aliases', []), *row.get('families', []),
                                 *row.get('subjects', []), *row.get('techniques', [])])
            db.execute('INSERT INTO knowledge(title,metadata,lesson) VALUES(?,?,?)', (row['title'], metadata, row['lesson']))
        if terms:
            expression = ' OR '.join('"'+t.replace('"', '""')+'"' for t in terms)
            hits = db.execute("SELECT rowid, bm25(knowledge,5,2,1), snippet(knowledge,2,'[',']',' … ',48) FROM knowledge WHERE knowledge MATCH ? ORDER BY 2,rowid", (expression,)).fetchall()
        else:
            hits = [(i + 1, 0.0, row['lesson'][:400]) for i, row in enumerate(eligible)]
    retrieval_ranks = {hit[0]: rank for rank, hit in enumerate(hits, 1)}
    if diversify == 'source':
        # Scopes are already filtered. Keep the original BM25 rank for transparency.
        hits = interleave_sources(hits, key=lambda hit: source_group(eligible[hit[0] - 1]))
    results = []
    for number, score, excerpt in hits[:limit]:
        row = dict(eligible[number - 1])
        # Full guide sections are available at the returned path/line; bounded
        # excerpts keep routine retrieval small and preserve exact provenance.
        row.pop('lesson', None)
        row.update(excerpt=excerpt, score=-score, retrieval_rank=retrieval_ranks[number],
                   source_group=source_group(row))
        results.append(row)
    return dict(total=len(hits), results=results, truncated=len(hits)>limit,
                engine='sqlite-fts5-bm25', scope=scope, diversification=diversify,
                note='Local curated knowledge only; no automatic research fallback. Read the source and its limits. Search is not export approval.')
