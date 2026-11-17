"""Compact views of reports for agents; complete reports stay in files.

``summarize`` keeps every scalar result, names placements by plan path,
groups warnings by code and adds one ``next`` step. It never drops an error:
errors beyond the listed ones are counted. ``text`` formats JSON with short
lists and small objects on one line, which roughly halves the tokens of the
indented form.
"""
from __future__ import annotations

import json
import os

import jsonschema

ERRORS = 12
EXAMPLES = 3
BULKY = {'source_map', 'geometry', 'diagnostics', 'flex', 'structure', 'mechanism', 'artifacts', 'source_dependencies',
         'flex_interactions', 'sources'}
DETAILS = ('pointer', 'file', 'action', 'separation', 'gap', 'depth', 'penetration', 'count', 'group_size',
           'replacement', 'facing', 'side', 'connector_data', 'component_count', 'main_group',
           'required_contacts', 'observed_contacts', 'section', 'line_number', 'example', 'stage')


def short(path):
    """A path relative to the working directory when it lies inside it."""
    if not isinstance(path, str) or not os.path.isabs(path):
        return path
    relative = os.path.relpath(path)
    return path if relative.startswith('..') else relative


def where(diagnostic):
    names = [p.get('path') or p.get('part') for p in diagnostic.get('placements', [])]
    return [n for n in names if n][:4]


def compact(diagnostic):
    row = dict(code=diagnostic['code'], message=diagnostic['message'])
    places = where(diagnostic)
    if places:
        row['at'] = places
    for key in DETAILS:
        if diagnostic.get(key) not in (None, [], {}):
            row[key] = diagnostic[key]
    if diagnostic.get('nearest_placement'):
        row['nearest'] = diagnostic['nearest_placement'].get('path')
    if diagnostic.get('examples'):
        row['examples'] = diagnostic['examples'][:EXAMPLES]
    if places and 'line_number' in row:
        row.pop('line_number')
        row.pop('section', None)
    return row


def grouped(diagnostics):
    groups = {}
    for d in diagnostics:
        group = groups.setdefault(d['code'], dict(count=0, message=d['message'], at=[]))
        group['count'] += d.get('count', 1) if d['code'] == 'appearance.exposed_side_studs' else 1
        for name in where(d):
            if len(group['at']) < EXAMPLES and name not in group['at']:
                group['at'].append(name)
    for group in groups.values():
        if not group['at']:
            group.pop('at')
    return groups


def geometry_summary(geometry):
    if not geometry:
        return None
    keys = dict(placements='occurrence_count', groups='optimistic_component_count', main_group='main_group_size',
                contacts_checked='contacts_checked', overlap_candidates='overlap_candidate_count', bounds='bounds',
                appearance='appearance', technic='technic')
    return {name: geometry.get(key) for name, key in keys.items() if geometry.get(key) is not None}


def next_step(report, errors, warnings):
    if report.get('error') and not errors:
        return 'Fix the input named in error, then rerun.'
    if errors:
        first = errors[0]
        place = (first.get('at') or [first.get('pointer') or first.get('section') or ''])[0]
        return f"Fix {first['code']} at {place} first, then rerun." if place else f"Fix {first['code']} first, then rerun."
    if 'stages' in report:
        if report['stages'].get('render') == 'passed':
            attention = [c for c in warnings if c.startswith(('appearance.', 'assembly.floating'))]
            look = ' Check these warnings in the images: ' + ', '.join(attention) + '.' if attention else ''
            return 'Open the previews and compare them with the brief.' + look
        return 'Checks passed without renders; run review without --no-render before delivery.'
    if report.get('written'):
        return 'Run review on the plan and open the previews.'
    return None


def summarize(report):
    """Small report for stdout: results, errors, grouped warnings, one next step."""
    out = {k: v for k, v in report.items() if k not in BULKY and (v is None or isinstance(v, (str, int, float, bool)))}
    for key in ('output', 'draft', 'file'):
        if key in out:
            out[key] = short(out[key])
    for key in ('stages', 'coverage'):
        if isinstance(report.get(key), dict):
            out[key] = report[key]
    if isinstance(report.get('source'), dict):
        out['source'] = {k: short(report['source'][k]) for k in ('path', 'section') if report['source'].get(k)}
    geometry = geometry_summary(report.get('geometry'))
    if geometry:
        out['geometry'] = geometry
    diagnostics = report.get('diagnostics') or []
    errors = [compact(d) for d in diagnostics if d.get('severity') == 'error']
    warnings = grouped([d for d in diagnostics if d.get('severity') != 'error'])
    out['errors'] = errors[:ERRORS]
    if len(errors) > ERRORS:
        out['errors_not_listed'] = len(errors) - ERRORS
    out['warnings'] = warnings
    if isinstance(report.get('structure'), dict):
        out['structure'] = {name: dict(checks_passed=s.get('checks_passed'),
                                       errors=sum(d.get('severity') == 'error' for d in s.get('diagnostics', [])))
                            for name, s in report['structure'].items()}
    if isinstance(report.get('mechanism'), dict):
        out['mechanism'] = {name: dict(checks_passed=m.get('checks_passed'), degrees_of_freedom=m.get('degrees_of_freedom'),
                                       input_moves=m.get('input_moves'), output_moves_with_input=m.get('output_moves_with_input'))
                            for name, m in report['mechanism'].items()}
    if isinstance(report.get('flex'), list):
        out['flex'] = [dict(output=a.get('output'), checks_passed=(a.get('validation') or {}).get('checks_passed'))
                       for a in report['flex']]
    if isinstance(report.get('artifacts'), dict):
        out['previews'] = [short(f"{report['output']}/{name}") for name in sorted(report['artifacts'])
                           if name.startswith('previews/') and name.endswith('.png')]
        out['files'] = sorted(name for name in report['artifacts'] if not name.startswith(('previews/', 'sources/')))
    step = next_step(report, errors, warnings)
    if step:
        out['next'] = step
    return out


def one_line(report):
    """--quiet: verdict, counts and the first error only."""
    diagnostics = report.get('diagnostics') or []
    errors = [d for d in diagnostics if d.get('severity') == 'error']
    row = dict(checks_passed=report.get('checks_passed'), errors=len(errors),
               warnings=sum(d.get('severity') != 'error' for d in diagnostics))
    for key in ('output', 'written', 'draft', 'error', 'failed_stage', 'physical_placements'):
        if report.get(key) is not None:
            row[key] = report[key]
    if errors:
        row['first_error'] = compact(errors[0])
    return row


def _inline(value):
    if isinstance(value, list):
        return all(not isinstance(v, (dict, list)) for v in value) or \
            all(isinstance(v, list) and all(not isinstance(x, (dict, list)) for x in v) for v in value)
    if isinstance(value, dict):
        return len(value) <= 4 and all(not isinstance(v, (dict, list)) or (isinstance(v, list) and _inline(v))
                                       for v in value.values()) and len(json.dumps(value)) <= 100
    return True


def text(value, indent=0):
    """JSON with one-line vectors, matrices and small objects; one-space indents."""
    if _inline(value) or not value:
        return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(', ', ': '))
    pad, inner = ' ' * indent, ' ' * (indent + 1)
    if isinstance(value, dict):
        items = [f'{inner}{json.dumps(str(k), ensure_ascii=False)}: {text(v, indent + 1)}' for k, v in value.items()]
        return '{\n' + ',\n'.join(items) + '\n' + pad + '}'
    return '[\n' + ',\n'.join(inner + text(v, indent + 1) for v in value) + '\n' + pad + ']'


MODES = ('at', 'on', 'under', 'attach', 'snap', 'flex', 'join')
EXAMPLE = {
    'at': '"at": [0, -24, 0]', 'on': '"on": "base" or "on": {"to": "core", "face": "-Z"}',
    'attach': '"attach": {"to": "lower", "anchor": "next", "using": "base"}',
    'snap': '"snap": {"to": "base", "near": [0, -8, 0]}', 'ref': '"ref": "3001.dat"',
    'colour': '"colour": 4 or "colour": "@colours.Red"', 'matrix': '"matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]]',
    'repeat': '"repeat": {"count": 4, "step": [40, 0, 0]}', 'orient': '"orient": {"up": "-Z"}',
    'under': '"under": {"to": "deck", "socket": 0}',
    'join': '"join": {"to": "rail", "holes": {"hole-0": "hole-0", "hole-1": "hole-1"}, "side": "+X"}',
    'id': '"id": "wall-left"', 'steps': '"steps": [[{"id": "base", "ref": "3001.dat", "colour": 4, "at": [0, 0, 0]}]]',
}


def explain_placement(entry):
    """Plain reason for a placement that matches none of the position modes."""
    if not isinstance(entry, dict):
        return None, None
    present = [m for m in MODES if m in entry]
    if not present:
        return 'A placement needs exactly one position: at, on, under, join, attach, snap or flex.', 'at'
    if len(present) > 1:
        return f"This placement mixes position modes {', '.join(present)}; keep exactly one.", present[0]
    mode = present[0]
    if mode != 'flex' and 'ref' not in entry:
        return 'Add ref: the part (for example 3001.dat) or section (name.ldr) to place.', 'ref'
    if mode == 'flex' and entry.keys() & {'ref', 'yaw', 'matrix', 'orient', 'repeat', 'offset_studs'}:
        return 'A flex placement takes only id, colour and flex.', None
    if mode == 'join' and entry.keys() & {'matrix', 'yaw', 'orient', 'repeat', 'offset_studs'}:
        return 'join sets the pose from the matched holes; remove matrix, yaw, orient, repeat or offset_studs.', 'join'
    if 'repeat' in entry and mode != 'at':
        return 'repeat works only with at; use a generator loop or an included section.', 'repeat'
    if 'offset_studs' in entry and mode != 'on':
        return 'offset_studs works only with on.', 'on'
    if mode == 'attach' and entry.keys() & {'matrix', 'yaw', 'orient'}:
        return 'attach sets the orientation itself; remove matrix, yaw or orient.', 'attach'
    if mode == 'snap' and 'orient' in entry:
        return 'snap takes yaw or matrix as its starting orientation, not orient.', 'snap'
    if sum(k in entry for k in ('yaw', 'matrix', 'orient')) > 1:
        return 'Use one of yaw, matrix or orient.', 'orient'
    return None, None


def schema_diagnostic(exc, file=None):
    """One actionable diagnostic for a plan schema failure."""
    pointer = '/' + '/'.join(map(str, exc.absolute_path))
    message, field = None, None
    if exc.validator == 'oneOf' and isinstance(exc.instance, dict) and 'id' in exc.instance:
        message, field = explain_placement(exc.instance)
    if message is None:
        best = jsonschema.exceptions.best_match(exc.context) if exc.context else exc
        pointer = '/' + '/'.join(map(str, best.absolute_path)) if exc.context else pointer
        detail = best.message if len(best.message) <= 200 else best.message[:200] + '…'
        message = f'Plan field {pointer or "/"} is invalid: {detail}'
        field = next((str(p) for p in reversed(best.absolute_path) if isinstance(p, str)), None)
        if best.validator == 'additionalProperties' and isinstance(best.instance, dict):
            known = set(best.schema.get('properties', {}))
            extra = sorted(set(best.instance) - known)
            if extra:
                message = f"Unknown field(s) {', '.join(extra)} at {pointer or '/'}; allowed: {', '.join(sorted(known))}."
                field = None
    row = dict(code='plan.schema', severity='error', message=message, pointer=pointer,
               action='Correct this plan field and rerun.')
    if file:
        row['file'] = file
    if field in EXAMPLE:
        row['example'] = EXAMPLE[field]
    return row
