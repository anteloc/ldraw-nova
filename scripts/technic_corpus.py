"""Measure the Technic port table and the Technic checks against the official sets.

    .venv/bin/python scripts/technic_corpus.py ports      # seat rates, coverage, withheld ports
    .venv/bin/python scripts/technic_corpus.py ports --apply   # also record usage and withheld ports
    .venv/bin/python scripts/technic_corpus.py checks     # how often each Technic check fires on official sets

The official models in data/models-annotated are the evidence: a derived pin
or axle that almost never sits in a hole there is not a real port, and a rule
that fires often on them is not a rule. Results go to
docs/reports/benchmarks/technic-corpus.json.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ldraw_tools.common import DATA, atomic_write, get_parts, models_path, shadow_paths  # noqa: E402
from ldraw_tools.document import parse_source, physical_context  # noqa: E402
from ldraw_tools.technic import canonical  # noqa: E402

REPORT = ROOT / 'docs' / 'reports' / 'benchmarks' / 'technic-corpus.json'
TOL = 0.5
MALE = {'pin', 'axle'}


_FULL = {}


def full_registry():
    """Reviewed and derived parts, including derived ports withheld from the tools."""
    if not _FULL:
        reviewed = json.loads((DATA / 'technic-parts.json').read_text())
        derived = json.loads((DATA / 'technic-ports.json').read_text())
        parts = dict(derived['parts'])
        parts.update(reviewed['parts'])
        _FULL.update(parts=parts, aliases={**derived.get('aliases', {}), **reviewed['aliases']})
    return _FULL


def port_arrays():
    """Local port arrays per canonical part code."""
    table = {}
    for code, entry in full_registry()['parts'].items():
        ports = [p for p in entry['ports'] + entry.get('withheld', []) if p['kind'] in ('pin', 'axle', 'pin_hole', 'axle_hole')]
        if not ports:
            continue
        table[code] = dict(
            at=np.array([p['at'] for p in ports], float), axis=np.array([p['axis'] for p in ports], float),
            length=np.array([p['length'] for p in ports], float),
            male=np.array([p['kind'] in MALE for p in ports]), axle=np.array([p['kind'] in ('axle', 'axle_hole') for p in ports]),
            ids=[p['id'] for p in ports], role=entry['role'], description=entry['description'])
    return table


def occurrences(path, parts):
    model, overlay = physical_context(parse_source(path), parts)
    rows = []
    for occurrence in model.iter_occurrences(include_steps=False):
        rows.append((occurrence.part_code.casefold(), np.array(occurrence.matrix.rows, float),
                     np.array([occurrence.position.x, occurrence.position.y, occurrence.position.z], float)))
    return rows


def world_ports(rows, table):
    """Stack every port of a model in world coordinates."""
    at, axis, length, male, axle, owner, code, port = [], [], [], [], [], [], [], []
    for index, (name, matrix, position) in enumerate(rows):
        key = canonical(name)
        local = table.get(key)
        if local is None:
            continue
        if abs(np.linalg.det(matrix) - 1) > 1e-3:
            continue  # mirrored or scaled placements carry no port evidence
        at.append(local['at'] @ matrix.T + position)
        axis.append(local['axis'] @ matrix.T)
        length.append(local['length'])
        male.append(local['male'])
        axle.append(local['axle'])
        owner.append(np.full(len(local['ids']), index))
        code.extend([key] * len(local['ids']))
        port.extend(local['ids'])
    if not at:
        return None
    return dict(at=np.vstack(at), axis=np.vstack(axis), length=np.concatenate(length), male=np.concatenate(male),
                axle=np.concatenate(axle), owner=np.concatenate(owner), code=np.array(code), port=np.array(port))


def seat(world):
    """For each port: seated (bool) and, for unseated males, why an aligned hole failed."""
    count = len(world['at'])
    seated = np.zeros(count, bool)
    reason = np.full(count, '', dtype=object)
    males = np.flatnonzero(world['male'])
    holes = np.flatnonzero(~world['male'])
    if not len(males) or not len(holes):
        return seated, reason
    hole_at, hole_axis, hole_length = world['at'][holes], world['axis'][holes], world['length'][holes]
    hole_axle, hole_owner = world['axle'][holes], world['owner'][holes]
    reach_max = hole_length.max() / 2 + 2
    for begin in range(0, len(males), 256):
        chunk = males[begin:begin + 256]
        delta = hole_at[None, :, :] - world['at'][chunk][:, None, :]
        reach = world['length'][chunk][:, None] / 2 + reach_max
        close = np.einsum('mhk,mhk->mh', delta, delta) <= reach ** 2
        for row, column in zip(*np.nonzero(close)):
            m = chunk[row]
            if hole_owner[column] == world['owner'][m]:
                continue
            a = world['axis'][m]
            if abs(float(a @ hole_axis[column])) < 0.9995:
                continue
            d = delta[row, column]
            along = float(d @ a)
            if float(np.linalg.norm(d - along * a)) > TOL:
                continue
            half_male, half_hole = world['length'][m] / 2, hole_length[column] / 2
            low, high = along - half_hole, along + half_hole
            if min(high, half_male) - max(low, -half_male) <= 1:
                continue
            h = holes[column]
            inside = min(high, half_male) - max(low, -half_male)
            partial = world['axle'][m] and inside >= min(hole_length[column], 10) - 2.5 - TOL
            if not world['axle'][m] and hole_axle[column]:
                why = 'family'
            elif (low < -half_male - TOL or high > half_male + TOL) and not partial:
                why = 'engagement'
            elif not world['axle'][m] and not (
                    (abs(along) <= TOL and abs(hole_length[column] - world['length'][m]) <= TOL)
                    or (abs(hole_length[column] - 10) <= TOL and abs(abs(along) - 5) <= TOL)):
                why = 'grip'
            else:
                seated[m] = seated[h] = True
                continue
            if not reason[m]:
                reason[m] = why
    return seated, reason


def technic_heavy(rows, descriptions):
    names = [name for name, _, _ in rows]
    technic = sum(descriptions.get(name, '').lstrip('~=_ ').startswith('Technic') for name in names)
    return len(names) >= 50 and technic / len(names) > 0.5


def ports_report(limit=None, seconds=None):
    parts = get_parts(shadows=shadow_paths())
    descriptions = {}
    for line in Path(parts.path).read_text(errors='replace').splitlines():
        match = re.match(r'(\S+)\.dat\s+(.*)', line.strip(), re.I)
        if match:
            descriptions[match.group(1).casefold()] = match.group(2)
    table = port_arrays()
    reviewed = set(json.loads((DATA / 'technic-parts.json').read_text())['parts'])
    seen = collections.Counter()          # (code, port) -> occurrences
    ok = collections.Counter()
    why = collections.defaultdict(collections.Counter)
    uses = collections.Counter()          # code -> placements in Technic-heavy models
    connected = collections.Counter()     # code -> placements with a seated port
    technic_total = technic_ported = technic_reviewed = 0
    models = 0
    started = time.time()
    files = sorted(models_path().glob('*.mpd'), key=lambda p: p.stat().st_size)
    for path in files:
        if limit and models >= limit or seconds and time.time() - started > seconds:
            break
        try:
            rows = occurrences(path, parts)
        except Exception:
            continue
        if not technic_heavy(rows, descriptions):
            continue
        models += 1
        for name, _, _ in rows:
            title = descriptions.get(name, '')
            # '~' titles are hose, cable and chain segments of a flexible part, not parts.
            if title.lstrip('=_ ').startswith('Technic'):
                technic_total += 1
                technic_ported += canonical(name) in table
                technic_reviewed += canonical(name) in reviewed
        world = world_ports(rows, table)
        if world is None:
            continue
        seated, reason = seat(world)
        for code, port, good, text in zip(world['code'], world['port'], seated, reason):
            seen[code, port] += 1
            ok[code, port] += bool(good)
            if text:
                why[code, port][text] += 1
        owners = collections.defaultdict(bool)
        for owner, good in zip(world['owner'], seated):
            owners[owner] |= bool(good)
        for owner, good in owners.items():
            code = canonical(rows[owner][0])
            uses[code] += 1
            connected[code] += good
    every = lambda code: full_registry()['parts'][code]['ports'] + full_registry()['parts'][code].get('withheld', [])
    males = {key for key in seen if any(p['id'] == key[1] and p['kind'] in MALE for p in every(key[0]))}
    male_seen = sum(seen[k] for k in males)
    male_ok = sum(ok[k] for k in males)
    withheld = collections.defaultdict(list)
    weak = []
    for key in sorted(males):
        code, port = key
        if code in reviewed or seen[key] < 10:
            continue
        rate = ok[key] / seen[key]
        if rate < 0.5:
            withheld[code].append(port)
        elif rate < 0.9:
            weak.append(dict(part=code, port=port, seen=seen[key], seated=ok[key], reasons=dict(why[key])))
    reasons = collections.Counter()
    for key in males:
        reasons.update(why[key])
    return dict(
        models=models, seconds=round(time.time() - started, 1),
        technic_placements=technic_total,
        covered_by_reviewed=round(technic_reviewed / technic_total, 4), covered_by_table=round(technic_ported / technic_total, 4),
        male_ports=male_seen, male_ports_seated=male_ok, male_seat_rate=round(male_ok / male_seen, 4),
        unseated_reasons=dict(reasons),
        withheld={k: v for k, v in sorted(withheld.items())}, weak=sorted(weak, key=lambda r: -r['seen'])[:60],
        parts_seen=len(uses), parts_connected_90=sum(1 for c in uses if uses[c] >= 10 and connected[c] / uses[c] >= 0.9),
        parts_seen_10=sum(1 for c in uses if uses[c] >= 10),
        least_connected=[dict(part=c, description=table[c]['description'], uses=uses[c], connected=round(connected[c] / uses[c], 3))
                         for c in sorted(uses, key=lambda c: connected[c] / uses[c]) if uses[c] >= 30][:40],
        uses={c: n for c, n in uses.most_common()},
        port_rates={f'{c}:{p}': [ok[c, p], seen[c, p]] for c, p in sorted(males) if seen[c, p] >= 10})


def checks_report(seconds=300, largest=900):
    """How often each Technic check fires on official models (it should be rare)."""
    from ldraw_tools.connection_adapter import connection_contacts
    from ldraw_tools.connectivity import inspect_connections
    from ldraw_tools.technic_checks import review
    from ldraw_tools.technic_review import review_inspection
    from ldraw_tools.validation import validate_file
    parts = get_parts(shadows=shadow_paths())
    descriptions = {}
    for line in Path(parts.path).read_text(errors='replace').splitlines():
        match = re.match(r'(\S+)\.dat\s+(.*)', line.strip(), re.I)
        if match:
            descriptions[match.group(1).casefold()] = match.group(2)
    counts, affected, examples = collections.Counter(), collections.Counter(), collections.defaultdict(list)
    errors, rules = collections.Counter(), collections.Counter()
    totals = collections.Counter()
    started = time.time()
    for path in sorted(models_path().glob('*.mpd'), key=lambda p: p.stat().st_size):
        if time.time() - started > seconds:
            break
        try:
            rows = occurrences(path, parts)
        except Exception:
            continue
        if not technic_heavy(rows, descriptions) or len(rows) > largest:
            continue
        try:
            model, _ = validate_file(path, parts, assembly=True)
            if model is None:
                continue
            inspection = inspect_connections(model, parts)
            found = connection_contacts(inspection)
            problems, summary = review(inspection, found)
            # The seating errors that `build` adds from the joint review (invalid_seating, occupied_hole, ...).
            problems = problems + review_inspection(inspection, seating_only=True, found=found)
        except Exception as error:
            totals['failed'] += 1
            continue
        totals['models'] += 1
        totals['placements'] += len(rows)
        for key in ('gears', 'meshes', 'joints', 'pins_and_axles', 'seated'):
            totals[key] += (summary or {}).get(key, 0)
        names = {o.index: o.occurrence.reference for o in inspection.occurrences}
        for problem in problems:
            counts[problem['code']] += 1
            if problem.get('severity') == 'error':
                errors[problem['code']] += 1
            for rule in problem.get('rules') or ():
                rules[problem['code'], rule.split(':')[0], problem.get('severity')] += 1
            affected[problem['code']] += len(problem.get('instances', []))
            if len(examples[problem['code']]) < 12:
                examples[problem['code']].append(f"{path.name}: {[names.get(i) for i in problem.get('instances', [])][:4]} "
                                                  f"{problem['message'][:90]}")
    per = {code: round(1000 * n / totals['placements'], 3) for code, n in counts.most_common()}
    # The gate: an error may fire less than once per 1,000 official placements.
    error_per = {code: round(1000 * n / totals['placements'], 3) for code, n in errors.most_common()}
    return dict(seconds=round(time.time() - started, 1), **totals, findings=dict(counts.most_common()),
                per_1000_placements=per, errors=dict(errors.most_common()), errors_per_1000_placements=error_per,
                rules={f'{c} / {r} / {s}': n for (c, r, s), n in rules.most_common()}, examples=examples)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest='command', required=True)
    c = commands.add_parser('ports', help='Seat rates and coverage of the port table')
    c.add_argument('--limit', type=int, help='Only the first N Technic-heavy models (smallest first)')
    c.add_argument('--seconds', type=float, help='Stop reading models after this long')
    c.add_argument('--apply', action='store_true', help='Record usage and withheld ports for scripts/technic_ports.py')
    c = commands.add_parser('checks', help='How often each Technic check fires on official models')
    c.add_argument('--seconds', type=float, default=300)
    c.add_argument('--largest', type=int, default=900, help='Skip models with more placements than this')
    args = parser.parse_args(argv)
    if args.command == 'checks':
        report = checks_report(args.seconds, args.largest)
        saved = json.loads(REPORT.read_text()) if REPORT.exists() else {}
        saved['checks'] = report
        atomic_write(REPORT, json.dumps(saved, indent=1) + '\n')
        print(json.dumps({k: v for k, v in report.items() if k != 'examples'}, indent=1))
        for code, rows in report['examples'].items():
            print(code)
            for row in rows[:6]:
                print('   ', row)
        return 0
    if args.command == 'ports':
        report = ports_report(args.limit, args.seconds)
        saved = json.loads(REPORT.read_text()) if REPORT.exists() else {}
        saved['ports'] = report
        atomic_write(REPORT, json.dumps(saved, indent=1) + '\n')
        shown = {k: v for k, v in report.items() if k not in ('uses', 'port_rates', 'weak', 'least_connected')}
        print(json.dumps(shown, indent=1))
        print('weak ports (50-90% seated):', json.dumps(report['weak'][:25]))
        print('least connected parts:', json.dumps(report['least_connected'][:25]))
        if args.apply:
            path = DATA / 'technic-corpus.json'
            atomic_write(path, json.dumps(dict(
                note='Written by scripts/technic_corpus.py ports --apply; read by scripts/technic_ports.py.',
                models=report['models'], withheld=report['withheld'], uses=report['uses']), indent=1) + '\n')
            print(f'wrote {path.relative_to(ROOT)}; rerun scripts/technic_ports.py')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
