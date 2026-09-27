"""Typed, read-only source discovery with a disposable local search index.

Jev judges descriptions. This module owns identities, source resolution, record
types, measured content filters, provenance and diversity. It never edits OMR.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import subprocess
from collections import Counter
from pathlib import Path, PureWindowsPath
from tempfile import NamedTemporaryFile

from .common import CACHE, atomic_write, database_path, dumps, jsonable, models_path, normalized
from .document import dependency_closure, is_part, parse_source, physical_context, resolve_section, section_table
from .resources import model_sections

VERSION = 1
FIELDS = {kind: f'{table}_DESCRIPTIONS_JEV.full_description' for kind, table in
          [('parts', 'PARTS'), ('models', 'MODELS'), ('submodels', 'SUBMODELS')]}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def confined(root, filename):
    root = Path(root).resolve()
    if PureWindowsPath(filename).drive or Path(filename).is_absolute():
        raise ValueError(f'Expected a source-relative filename: {filename}')
    path = (root / filename.replace('\\', '/')).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f'Source escapes its configured root: {filename}')
    return path


def decode_description(kind, text):
    """Identifiers occupy the first separators; description prose may contain |."""
    if kind not in FIELDS or not isinstance(text, str):
        raise ValueError('Expected a supported description field and text')
    chunks = text.split('|', 2 if kind == 'submodels' else 1)
    expected = 3 if kind == 'submodels' else 2
    if len(chunks) != expected or any(not s.strip() for s in chunks[:-1]):
        raise ValueError(f'Malformed {FIELDS[kind]} value')
    row = dict(kind=kind, description=chunks[-1])
    if kind == 'parts':
        row['part'] = chunks[0]
    else:
        row['model'] = chunks[0]
        if kind == 'submodels':
            row['section'] = chunks[1]
    return row


def source_id(kind, *, model=None, section=None, part=None):
    if kind not in FIELDS or (kind == 'parts' and not part) or (kind != 'parts' and not model) or (kind == 'submodels' and not section):
        raise ValueError('Incomplete source identity')
    key = [kind, *[normalized(v).strip() for v in [model, section, part] if v is not None]]
    return kind.removesuffix('s') + '-' + digest(key)[:24]


def record_id(row):
    return source_id(row.get('kind'), **{k: row[k] for k in ['model', 'section', 'part'] if k in row})


def physical_candidate(part, parts):
    code = normalized(part).removesuffix('.dat')
    title = parts.by_code.get(code)
    return title is not None and '/' not in code and not title.startswith(('~', '=', '_'))


class DiscoveryIndex:
    def __init__(self, parts, root=None, *, database=None, cache=None):
        self.parts = parts
        self.root = models_path(root)
        self.database = database_path(database)
        self.cache = Path(cache or CACHE/'discovery'/digest([str(self.root), str(self.database), str(parts.path.resolve())])[:16]).resolve()
        self.cache.mkdir(parents=True, exist_ok=True)
        self.path = self.cache/'catalog.sqlite'
        self.manifest_path = self.cache/'index.json'
        self._models = {}

    def signature(self):
        files = sorted(self.root.rglob('*.mpd')) + sorted(self.root.rglob('*.ldr'))
        stamps = [(str(p.relative_to(self.root)), p.stat().st_size, p.stat().st_mtime_ns) for p in files]
        db = self.database.stat()
        part_index = self.parts.path.stat()
        return digest([VERSION, str(self.database), db.st_size, db.st_mtime_ns, stamps,
                       str(self.parts.path.resolve()), part_index.st_size, part_index.st_mtime_ns])

    def ensure(self, *, force=False):
        signature = self.signature()
        if not force and self.path.is_file() and self.manifest_path.is_file():
            report = json.loads(self.manifest_path.read_text())
            if report.get('signature') == signature:
                return report
        inventories = {}
        rows, errors = [], []
        with sqlite3.connect(self.database.as_uri()+'?mode=ro', uri=True) as source:
            for kind, field in FIELDS.items():
                table, column = field.split('.')
                for (text,) in source.execute(f'SELECT {column} FROM {table}'):
                    row = decode_description(kind, text)
                    row.update(id=record_id(row), source_field=field, indexed_description=row['description'],
                               original_full_description=text, source_exists=False)
                    try:
                        if kind == 'parts':
                            library = self.parts.path.parent
                            locations = [confined(library/'parts', row['part']), confined(library/'p', row['part']), confined(library, row['part'])]
                            path = next((p for p in locations if p.is_file()), locations[0])
                            row.update(path=str(path), source_exists=path.is_file(),
                                       record_type='physical_part' if physical_candidate(row['part'], self.parts) else 'internal_or_legacy_part')
                        else:
                            path = confined(self.root, row['model'])
                            if row['model'] not in inventories:
                                inventories[row['model']] = (model_sections(path)['sections'], hashlib.sha256(path.read_bytes()).hexdigest())
                            sections, sha = inventories[row['model']]
                            selected = sections[:1] if kind == 'models' else [s for s in sections if normalized(s['name']).strip() == normalized(row['section']).strip()]
                            if len(selected) != 1:
                                raise ValueError('Missing or ambiguous source section')
                            entry = selected[0]
                            row.update(path=str(path), source_exists=True, source_sha256=sha,
                                       source_section=entry['name'], start_line=entry['start_line'],
                                       description=entry['description'], parent_description=sections[0]['description'],
                                       theme=sections[0]['theme'], direct_placements=entry['placements'], has_file=entry['has_file'])
                            row['record_type'] = ('part_definition' if entry['name'].strip().lower().endswith('.dat') else
                                                  'assembly' if entry['placements'] else 'raw_geometry' if entry['raw_geometry'] else 'empty')
                        row['description_corrected'] = row['description'] != row['indexed_description']
                    except (OSError, ValueError) as exc:
                        row.update(record_type='unresolved', error=str(exc))
                        errors.append(dict(id=row['id'], error=str(exc)))
                    prefix = [row['part']] if kind == 'parts' else [row['model']] + ([row['section']] if kind == 'submodels' else [])
                    row['full_description'] = '|'.join([*prefix, row['description']])
                    rows.append(row)
        with NamedTemporaryFile(dir=self.cache, suffix='.sqlite', delete=False) as f:
            temporary = Path(f.name)
        try:
            with sqlite3.connect(temporary) as con:
                con.execute('CREATE TABLE records(id TEXT PRIMARY KEY, kind TEXT NOT NULL, payload TEXT NOT NULL)')
                con.execute('CREATE VIRTUAL TABLE search USING fts5(id UNINDEXED, body)')
                con.executemany('INSERT INTO records VALUES(?,?,?)', [(r['id'], r['kind'], json.dumps(r)) for r in rows])
                con.executemany('INSERT INTO search VALUES(?,?)', [(r['id'], r['full_description']) for r in rows])
            temporary.replace(self.path)
        finally:
            temporary.unlink(missing_ok=True)
        report = dict(version=VERSION, signature=signature, source=str(self.database), models_root=str(self.root), index=str(self.path),
                      counts=dict(Counter(r['kind'] for r in rows)), types=dict(Counter(r['record_type'] for r in rows)),
                      corrected_descriptions=sum(r.get('description_corrected', False) for r in rows), errors=errors,
                      note='Derived local index. Original database and model sources remain unchanged.')
        atomic_write(self.manifest_path, dumps(report)+'\n')
        self._models.clear()
        return report

    def rows(self, kind=None):
        with sqlite3.connect(self.path.as_uri()+'?mode=ro', uri=True) as con:
            return [json.loads(r[0]) for r in con.execute('SELECT payload FROM records'+(' WHERE kind=?' if kind else ''), (kind,) if kind else ())]

    def get(self, identity):
        with sqlite3.connect(self.path.as_uri()+'?mode=ro', uri=True) as con:
            row = con.execute('SELECT payload FROM records WHERE id=?', (identity,)).fetchone()
        if row is None:
            raise ValueError(f'Unknown reference ID {identity}')
        return json.loads(row[0])

    def inventory(self, row, *, max_instances=100000):
        if row['kind'] == 'parts':
            return dict(physical_placements=1, expanded_leaf_count=1, physical_accounting_complete=row['record_type']=='physical_part')
        path = confined(self.root, row['model'])
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        if sha != row.get('source_sha256'):
            raise ValueError('Source changed since indexing; rebuild the discovery index')
        key = digest([VERSION, row['id'], sha, self.manifest_path.read_text(), max_instances])
        cached = self.cache/'inventories'/(key+'.json')
        if cached.is_file():
            return json.loads(cached.read_text())
        if row['model'] not in self._models:
            # Bound retained source models; large full-model searches otherwise grow indefinitely.
            if len(self._models) >= 12:
                self._models.clear()
            self._models[row['model']] = parse_source(path)
        model = self._models[row['model']]
        selected = resolve_section(model, row.get('section'))
        closure = dependency_closure(model, selected.name)
        physical, overlay = physical_context(model, self.parts, selected.name)
        occurrences = []
        for occurrence in physical.iter_occurrences():
            occurrences.append(occurrence)
            if len(occurrences) > max_instances:
                raise ValueError(f'Inventory exceeds {max_instances} placements')
        counts = Counter(normalized(o.reference) for o in occurrences)
        bom = [dict(part=p, count=n, description=overlay.by_code.get(p.removesuffix('.dat'), ''),
                    physical_index_entry=p.removesuffix('.dat') in overlay.by_code) for p,n in sorted(counts.items())]
        from ldraw.lines import Line, OptionalLine, Triangle, Quadrilateral
        raw = [s.name for s in closure if not is_part(s) and any(isinstance(o, (Line, OptionalLine, Triangle, Quadrilateral)) for o in s.objects)]
        unresolved = [b for b in bom if not b['physical_index_entry']]
        technic = sum(b['count'] for b in bom if b['description'].startswith('Technic'))
        low = [min((getattr(o.position, a) for o in occurrences), default=0) for a in 'xyz']
        shape = sorted((o.reference.casefold(), tuple(round(getattr(o.position,a)-low[i], 5) for i,a in enumerate('xyz')),
                        tuple(round(v,5) for line in o.matrix.rows for v in line)) for o in occurrences)
        parents = [dict(section=s.name, at=jsonable(p.position), matrix=jsonable(p.matrix), colour=p.colour.code)
                   for s in section_table(model).values() for p in s.pieces if normalized(p.reference)==normalized(selected.name)]
        report = dict(source_sha256=sha, parser_section=selected.name, physical_placements=None if raw or unresolved else len(occurrences),
                      expanded_leaf_count=len(occurrences), physical_accounting_complete=not raw and not unresolved,
                      nonphysical_or_unresolved_leaves=unresolved, raw_geometry_sections=raw, bom=bom,
                      technic_named_placements=technic, technic_share=technic/len(occurrences) if occurrences else 0,
                      legacy_parts=[b for b in bom if b['description'].startswith(('~', '=', '_'))],
                      shape_fingerprint=digest(shape), recipe_fingerprint=digest(sorted(counts.items())),
                      fingerprint_note='Shape comparison ignores colour and global translation; rotations and mirrored geometry remain distinct.',
                      parents=parents, dependencies=[dict(section=s.name, kind='part_definition' if is_part(s) else 'assembly', author=s.author, license=s.license) for s in closure],
                      reachable=normalized(selected.name) in {normalized(s.name) for s in dependency_closure(model)})
        atomic_write(cached, dumps(report)+'\n')
        return report


def eligible(row, *, system=True):
    if not row['source_exists'] or row['record_type'] not in {'assembly', 'physical_part'}:
        return False
    if system and (re.search(r'\b(duplo|fabuland|znap|bionicle|technic)\b', row.get('theme','').casefold()) or
                   re.match(r'(duplo|fabuland|znap|bionicle|technic)\b', row['description'].casefold())):
        return False
    return True


def structural_candidate(row, inventory=None):
    """Inspect the selected section, never exclude it just for its parent theme."""
    from .technic import canonical, registry
    from .technic_review import MECHANISMS
    if row['kind'] == 'parts':
        return canonical(row['part']) in registry()['parts']
    text = row['description']
    if MECHANISMS.search(text):
        return False
    if not re.search(r'\b(frame|chassis|structure|structural|support|mount|tower|truss|brace|bracing|skeleton)\b', text, re.I):
        return False
    if inventory is not None:
        return not any(MECHANISMS.search(item.get('description', '')) for item in inventory['bom'])
    return True


def mechanism_candidate(row, inventory=None):
    """Discovery vocabulary, not a verdict that an assembly works or is complete."""
    vocabulary = re.compile(r'\b(gear|gears|gearbox|gearing|differential|crankshaft|crank|piston|rack|pinion|'
                            r'turntable|winch|steering|linkage|actuator|suspension|mechanism|worm|cam|lever)\b', re.I)
    if not vocabulary.search(row['description']):
        return False
    if inventory is not None:
        return any(vocabulary.search(item.get('description', '')) for item in inventory['bom'])
    return True


def search(index, kind, query, *, engine='jev', limit=10, candidates=500, pool=60, system=True, construction=None,
           max_parts=None, min_parts=2, max_technic_share=0.5, parent_cap=2, yes=None, no=None,
           timeout=240):
    if kind not in FIELDS or not query.strip() or engine not in {'jev','fts'}:
        raise ValueError('Choose parts/models/submodels, a nonblank query and jev/fts')
    if limit < 1 or pool < limit or candidates < 0 or (candidates and pool > candidates) or parent_cap < 1 or min_parts < 0:
        raise ValueError('Invalid result/candidate/parent/part budgets')
    if not 0 <= max_technic_share <= 1 or (max_parts is not None and max_parts < min_parts):
        raise ValueError('Invalid part/Technic limits')
    if (yes is None) != (no is None):
        raise ValueError('Supply both --yes and --no criteria')
    if construction not in {None, 'system', 'all', 'technic-structure', 'mechanism'}:
        raise ValueError('Unknown construction mode')
    if construction is not None:
        system = construction == 'system'
    manifest = index.ensure()
    allowed = {r['id']:r for r in index.rows(kind) if eligible(r, system=system)
               and (construction != 'technic-structure' or structural_candidate(r))
               and (construction != 'mechanism' or mechanism_candidate(r))}
    ranked, stats = [], {}
    if engine == 'jev':
        snapshot = index.cache/'queries'/(digest([manifest['signature'], kind, system, construction, sorted(allowed)])+'.sqlite')
        if not snapshot.exists():
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            with NamedTemporaryFile(dir=snapshot.parent, suffix='.sqlite', delete=False) as f:
                temp = Path(f.name)
            try:
                with sqlite3.connect(temp) as con:
                    con.execute('CREATE TABLE candidates(id TEXT PRIMARY KEY, full_description TEXT NOT NULL)')
                    con.executemany('INSERT INTO candidates VALUES(?,?)', [(r['id'],r['full_description']) for r in allowed.values()])
                temp.replace(snapshot)
            finally:
                temp.unlink(missing_ok=True)
        command = ['jev-rerank','--db',str(snapshot),'--table-field','candidates.full_description',
                   '--query',json.dumps(dict(query=query,yes=yes,no=no)) if yes is not None else query,
                   '--top',str(pool),'--candidates',str(candidates),'--model','jev-1.13.0','--json','--show']
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        if result.returncode:
            raise ValueError('Jev search failed; use --engine fts for explicit offline search. '+result.stderr[-1500:])
        data = json.loads(result.stdout)
        stats = dict(data['stats'], exhaustive=data.get('exhaustive'), command=command, eligible_records=len(allowed))
        for r in data['results']:
            identity = r['source']['key']['id']
            if identity not in allowed:
                raise ValueError('Jev returned an identity outside the filtered snapshot')
            ranked.append(dict(allowed[identity], score=r['score'], retrieval_rank=r['rank']))
    else:
        terms = re.findall(r'\w+', query.casefold())
        stop = {'a','an','the','with','for','of','and','to','in','on','from'}
        expression = ' OR '.join('"'+t+'"' for t in terms if t not in stop)
        if not expression:
            raise ValueError('Query needs a searchable term')
        with sqlite3.connect(index.path.as_uri()+'?mode=ro', uri=True) as con:
            for identity, rank in con.execute('SELECT id, rank FROM search WHERE search MATCH ? ORDER BY rank, id', (expression,)):
                if identity in allowed:
                    ranked.append(dict(allowed[identity], fts_rank=rank, retrieval_rank=len(ranked)+1))
                    if len(ranked) >= pool:
                        break
        stats = dict(eligible_records=len(allowed), shortlisted=len(ranked), query_language='token OR with BM25 ordering')
    kept, rejected, shapes, parents = [], [], {}, Counter()
    for row in ranked:
        try:
            if kind != 'parts':
                row['inventory'] = index.inventory(row)
                inv = row['inventory']
                reason = ('mechanism_content' if construction == 'technic-structure' and not structural_candidate(row, inv) else
                          'no_mechanism_parts_identified' if construction == 'mechanism' and not mechanism_candidate(row, inv) else
                          'nonphysical_accounting' if not inv['physical_accounting_complete'] else
                          'too_few_parts' if inv['expanded_leaf_count'] < min_parts else
                          'too_many_parts' if max_parts is not None and inv['expanded_leaf_count'] > max_parts else
                          'technic_share' if system and inv['technic_share'] > max_technic_share else None)
                if reason:
                    rejected.append(dict(id=row['id'], reason=reason, retrieval_rank=row['retrieval_rank'])); continue
                fingerprint = inv['shape_fingerprint']
                if fingerprint in shapes:
                    shapes[fingerprint].setdefault('variants',[]).append(dict(id=row['id'], model=row['model'], section=row.get('section'), score=row.get('score')))
                    continue
                parent = row['model'].split('_',1)[0].split('.',1)[0]
                if parents[parent] >= parent_cap:
                    rejected.append(dict(id=row['id'], reason='parent_diversity_cap', retrieval_rank=row['retrieval_rank'])); continue
                shapes[fingerprint] = row
                parents[parent] += 1
            kept.append(row)
            if construction == 'technic-structure':
                row['structural_review'] = 'required: verify joint roles, parent support, restraint, seating and assembly order'
            if construction == 'mechanism':
                row['mechanism_study'] = 'inspect source steps, parts and parent context; analytical mechanism verification is deferred'
        except (OSError, ValueError, RecursionError) as exc:
            rejected.append(dict(id=row['id'], reason='inventory_failed', error=str(exc)))
    return dict(query=query, kind=kind, engine=engine, source_field=FIELDS[kind], index_signature=manifest['signature'],
                results=kept[:limit], eligible_after_measurement=len(kept), rejected=rejected, stats=stats,
                filters=dict(system=system,construction=construction or ('system' if system else 'all'),min_parts=min_parts,max_parts=max_parts,max_technic_share=max_technic_share,parent_cap=parent_cap),
                note='Scores describe textual relevance. Results still require geometry, scale and visual review; no hidden fallback or automatic import approval.')


def part_suggestions(results, *, limit=20):
    """Rank real fittings by distinct supporting constructions, retaining provenance."""
    found = {}
    seen_shapes = set()
    for row in results:
        inventory = row.get('inventory',{})
        shape = inventory.get('shape_fingerprint',row['id'])
        if shape in seen_shapes:
            continue
        seen_shapes.add(shape)
        for b in inventory.get('bom',[]):
            if not b['physical_index_entry'] or b['description'].startswith(('~','=','_')):
                continue
            entry = found.setdefault(b['part'],dict(part=b['part'],description=b['description'],sources=[],placements=0))
            entry['sources'].append(dict(id=row['id'],model=row.get('model'),section=row.get('section')))
            entry['placements'] += b['count']
    rows = sorted(found.values(),key=lambda r:(-len(r['sources']),-r['placements'],r['part']))
    return dict(results=rows[:limit], total=len(rows), note='Parts used by the matched constructions, not a generated BOM. Inspect status, dimensions and colour availability.')
