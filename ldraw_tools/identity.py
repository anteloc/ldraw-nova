"""Placement identity and source attribution, independent of LDraw comments."""
from __future__ import annotations

import copy
import hashlib

import numpy as np

from .common import jsonable, normalized


def repeat_offsets(entry):
    """(id, translation) for each copy of a repeated placement.

    ``count: n`` with one ``step`` vector gives id-0 … id-(n-1). ``count: [n, m]``
    with two step vectors gives a grid id-i-j, offset i * step[0] + j * step[1].
    """
    spec = entry['repeat']
    count, step = spec['count'], spec['step']
    grid = isinstance(count, list)
    if grid != (len(step) == 2 and all(isinstance(s, list) for s in step)):
        raise ValueError(f"{entry['id']}: repeat.count [n, m] needs two step vectors; a single count needs one")
    if not grid:
        return [(f"{entry['id']}-{i}", np.array(step, float) * i) for i in range(count)]
    first, second = (np.array(s, float) for s in step)
    return [(f"{entry['id']}-{i}-{j}", first * i + second * j) for i in range(count[0]) for j in range(count[1])]


class Plan(dict):
    """An ordinary JSON dictionary with out-of-band source provenance."""

    def __init__(self, *args, sources=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.sources = sources or {}


class BuildError(ValueError):
    """Keep machine-readable failures while retaining the ValueError API."""

    def __init__(self, message, *, stage='authoring', diagnostics=None, **where):
        super().__init__(message)
        self.stage = stage
        self.diagnostics = [dict(d, **where) for d in diagnostics] if diagnostics else [dict(
            code='plan.' + stage, severity='error', message=message,
            action='Correct the identified source and rerun review.', **where)]


class Identity:
    def __init__(self, plan):
        self.sources = getattr(plan, 'sources', {})
        self.entries = {}
        self.origins = {}
        for si, section in enumerate(plan['sections']):
            key = normalized(section['name'])
            self.entries[key] = {}
            origin = self.sources.get(key, dict(file=None, pointer=f'/sections/{si}'))
            for ti, step in enumerate(section['steps']):
                for pi, entry in enumerate(step):
                    where = dict(origin, pointer=f"{origin['pointer']}/steps/{ti}/{pi}")
                    ids = [name for name, _ in repeat_offsets(entry)] if 'repeat' in entry else [entry['id']]
                    if 'join' in entry and entry['join'].get('pins', True) is not False:
                        # A join inserts one pin per matched hole pair: ID-pin-0, ID-pin-1, ...
                        ids += [f"{entry['id']}-pin-{n}" for n in range(len(entry['join'].get('holes', {})))]
                    for name in ids:
                        if (key, name) in self.origins:
                            raise BuildError(f'Duplicate placement id {name} in {section["name"]}',
                                             section=section['name'], placement=name, **where)
                        self.origins[key, name] = where

    def mirror(self, name, made):
        """Register a mirrored section's parts under the original section's IDs."""
        key = normalized(name)
        if key in self.entries and self.entries[key]:
            return
        model = made[name]
        stem = name.rsplit('-mirror-', 1)[0] + '.ldr'
        source = self.entries.get(normalized(stem))
        if source is None:
            # A mirror of a mirror's child: its original is named before the first suffix.
            return
        pieces = iter(model.pieces)
        self.entries[key] = {}
        for ident, record in source.items():
            if record['piece'] is None:
                continue
            self.entries[key][ident] = dict(piece=next(pieces), flex=False)
            if (normalized(stem), ident) in self.origins:
                self.origins[key, ident] = self.origins[normalized(stem), ident]

    def where(self, section, name):
        return dict(section=section, placement=name, **self.origins.get((normalized(section), name), {}))

    def add(self, section, entry, piece):
        self.entries[normalized(section)][entry['id']] = dict(piece=piece, flex='flex' in entry)

    def resolve(self, section, path):
        """Resolve one authored rigid leaf, composing every parent transform."""
        matrix, position = np.eye(3), np.zeros(3)
        current = normalized(section)
        for i, name in enumerate(path.split('/')):
            record = self.entries.get(current, {}).get(name)
            if record is None:
                raise ValueError(f'Unknown placement {path!r} in {section}; use placement IDs, including every parent')
            if record['flex']:
                raise ValueError(f'{path}: rigid interfaces cannot depend on generated flex geometry')
            piece = record['piece']
            position = position + matrix @ np.asarray(jsonable(piece.position))
            matrix = matrix @ np.asarray(piece.matrix.rows)
            current = normalized(piece.reference)
            if i == len(path.split('/')) - 1:
                if not current.endswith('.dat'):
                    raise ValueError(f'{path}: select a physical part inside the module')
                return dict(ref=piece.reference, at=position, matrix=matrix)
        raise ValueError('A placement path must not be empty')

    def map(self, model, parts, *, instance_limit=100000):
        from .document import physical_context
        physical, _ = physical_context(model, parts)
        ordinals = {key: [name for name, record in entries.items() if record['piece'] is not None]
                    for key, entries in self.entries.items()}
        indices, result = {}, []
        for index, occurrence in enumerate(physical.iter_occurrences(include_steps=True)):
            if index >= instance_limit:
                raise ValueError(f'Identity expansion exceeds {instance_limit} occurrences')
            path, origins, authored = [], [], True
            matrix, position, route = np.eye(3), np.zeros(3), None
            for hop in occurrence.path:
                key = normalized(hop.model.name)
                if id(hop.model) not in indices:
                    indices[id(hop.model)] = {id(p): n for n, p in enumerate(hop.model.pieces)}
                ordinal = indices[id(hop.model)][id(hop.piece)]
                names = ordinals.get(key, [])
                name = names[ordinal] if ordinal < len(names) else f'@{ordinal}'
                path.append(name)
                position = position + matrix @ np.asarray(jsonable(hop.piece.position))
                matrix = matrix @ np.asarray(hop.piece.matrix.rows)
                if self.entries.get(key, {}).get(name, {}).get('flex'):
                    route = dict(section=key, placement=name, path='/'.join(path),
                                 at=position.tolist(), matrix=matrix.tolist())
                authored &= ordinal < len(names)
                if (key, name) in self.origins:
                    origins.append(dict(section=hop.model.name, placement=name, **self.origins[key, name]))
            result.append(dict(index=index, path='/'.join(path), authored=authored,
                               section=occurrence.source_model.name, line_number=occurrence.source_line,
                               part=occurrence.reference, position=jsonable(occurrence.position),
                               matrix=jsonable(occurrence.matrix), sources=origins,
                               **({'inline_route': route} if route else {})))
        return result


def named_contract(contract, source_map, model):
    """Compile explicit intent, never infer required joints from observed contacts."""
    result = copy.deepcopy(contract)
    table = {row['path']: row['index'] for row in source_map if row['authored']}

    def resolve(path):
        if path not in table:
            raise ValueError(f'Structure references absent or non-physical placement {path!r}')
        return table[path]

    if 'retained_axles' in result:
        result['retained_axles'] = [resolve(p) for p in result['retained_axles']]
    for joint in result.get('required_joints', []):
        joint['between'] = [resolve(p) for p in joint['between']]
    for step in result.get('assembly', []):
        step['connector'] = resolve(step['connector'])
        step['before'] = [resolve(p) for p in step['before']]
    result.update(version=1, model_sha256=hashlib.sha256(model.to_ldraw().encode()).hexdigest())
    return result


def placement_location(row):
    """Keep diagnostics readable; complete transforms remain in the source map."""
    result = {key: row[key] for key in ('index', 'path', 'part')}
    if row['sources']:
        result.update({key: row['sources'][-1][key] for key in ('file', 'pointer')})
    return result


def annotate(diagnostics, source_map):
    rows = {row['index']: row for row in source_map}
    result = []
    for d in diagnostics:
        selected = [rows[i] for i in d.get('instances', []) if i in rows]
        if not selected and d.get('line_number') is not None:
            selected = [r for r in source_map if r['line_number'] == d['line_number']
                        and normalized(r['section']) == normalized(d.get('section') or '')]
        extra = {}
        if d.get('nearest_instance') in rows:
            extra['nearest_placement'] = placement_location(rows[d['nearest_instance']])
        if selected:
            extra['placements'] = [placement_location(r) for r in selected]
        result.append(dict(d, **extra) if extra else d)
    return result
