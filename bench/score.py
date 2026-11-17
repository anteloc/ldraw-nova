"""Score benchmark runs: the delivered model, the brief's checks and the run's cost.

    .venv/bin/python bench/score.py run output/bench/SUITE/RUN --brief radio
    .venv/bin/python bench/score.py table output/bench/baseline output/bench/candidate
    .venv/bin/python bench/score.py sheets output/bench/baseline output/bench/candidate --out output/bench/blind
    .venv/bin/python bench/score.py unblind output/bench/blind

Every number comes from files: the delivered MPD and plan, the agent's
stream-json transcript and the toolkit's own trace (LDRAW_AGENT_TRACE). The
same scorer must score every arm of a comparison. Visual quality needs the
human rubric in bench/RUBRIC.md; scores are recorded in RUN/rubric.json.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import statistics
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
BRIEFS = Path(__file__).with_name('briefs.json')
IMAGES = ('.png', '.jpg', '.jpeg', '.gif', '.webp')
# Counted as defects whatever their severity: seating findings on derived ports are warnings in `build`.
TECHNIC_ERRORS = {'technic.through_solid', 'technic.cell_overlap', 'technic.invalid_seating', 'technic.occupied_hole',
                  'technic.occupied_span', 'technic.incomplete_grip'}


def brief_by_id(identity):
    return next(b for b in json.loads(BRIEFS.read_text())['briefs'] if b['id'] == identity)


def delivered_files(folder):
    root = folder / 'delivered' if (folder / 'delivered').is_dir() else folder
    skip = {'review', 'checks', 'xray', 'previews'}
    model = root / 'model.mpd'
    if not model.exists():
        found = sorted((p for p in root.rglob('*.mpd') if not skip & set(p.relative_to(root).parts[:-1])),
                       key=lambda p: p.stat().st_mtime)
        model = found[-1] if found else None
    plans = [p for p in root.rglob('*.json') if not skip & set(p.relative_to(root).parts[:-1])
             and p.name not in {'trace.json'} and _is_plan(p)]
    return root, model, plans


def _is_plan(path):
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError, UnicodeDecodeError):
        return False
    return isinstance(data, dict) and data.get('version') == 1 and isinstance(data.get('sections'), list)


def model_metrics(path):
    """Build-equivalent checks plus appearance counts on the delivered MPD."""
    from ldraw_tools.common import get_parts
    from ldraw_tools.geometry import analyze_geometry
    from ldraw_tools.validation import validate_file
    parts = get_parts()
    model, diagnostics = validate_file(path, parts, assembly=True)
    errors = [d for d in diagnostics if d['severity'] == 'error']
    if model is None or errors:
        return dict(present=True, source_errors=Counter(d['code'] for d in errors), checks_passed=False), None
    count = sum(1 for _ in model.iter_occurrences(include_steps=True)) if hasattr(model, 'iter_occurrences') else 0
    contacts = 'all' if count <= 3000 else 'none'
    geometry = analyze_geometry(model, parts, detail='full', contacts=contacts, output_limit=10 ** 6)
    problems = diagnostics + geometry['diagnostics']
    codes = Counter(d['code'] for d in problems)
    instances = geometry['instances']
    components = geometry.get('optimistic_components') or []
    main = max((len(g) for g in components), default=0)
    metrics = dict(
        present=True, placements=geometry['occurrence_count'],
        checks_passed=not any(d['severity'] == 'error' for d in problems),
        errors=sum(d['severity'] == 'error' for d in problems),
        distinct_parts=len({i['part'].casefold() for i in instances}),
        distinct_colours=len({(i['colour'] or {}).get('code') for i in instances}),
        groups=geometry.get('optimistic_component_count'),
        main_group_ratio=round(main / geometry['occurrence_count'], 3) if contacts == 'all' and geometry['occurrence_count'] else None,
        deep_overlaps=geometry['appearance']['deep_overlaps'],
        exposed_side_studs=geometry['appearance']['exposed_side_studs'],
        glass_obstructed=geometry['appearance']['glass_obstructed'],
        body_overlaps=codes.get('assembly.body_overlap', 0),
        alias_warnings=codes.get('part.alias_or_internal', 0),
        bounds=geometry['bounds'], contacts=contacts,
        codes=dict(codes))
    technic = geometry.get('technic')
    if technic:
        metrics['technic'] = {k: technic.get(k) for k in ('rigid_groups', 'joints', 'gears', 'meshes', 'pins_and_axles', 'seated')}
        metrics['technic']['seated_share'] = round(technic['seated'] / technic['pins_and_axles'], 3) \
            if technic.get('pins_and_axles') else None
        metrics['technic']['findings'] = {c: n for c, n in codes.items() if c.startswith('technic.')}
    return metrics, geometry


def extent(bounds, axis):
    k = 'xyz'.index(axis)
    return bounds['max'][k] - bounds['min'][k]


def brief_checks(brief, metrics, geometry):
    results = []
    instances = geometry['instances'] if geometry else []
    for check in brief.get('checks', []):
        kind, value, passed = check['type'], None, False
        if geometry is None:
            results.append(dict(id=check['id'], passed=False, value=None, reason='model missing or invalid'))
            continue
        if kind == 'placements':
            value = metrics['placements']
            passed = check.get('min', 0) <= value <= check.get('max', float('inf'))
        elif kind == 'connected':
            value = metrics['main_group_ratio']
            passed = value is not None and value >= check['min']
        elif kind == 'bom':
            pattern = re.compile(check['pattern'], re.I)
            value = sum(bool(pattern.search(i.get('description') or '')) for i in instances)
            passed = value >= check.get('min', 1)
        elif kind == 'parts_any':
            codes = {c.casefold() for c in check['codes']}
            value = sum(i['part'].casefold().removesuffix('.dat') in codes for i in instances)
            passed = value >= check.get('min', 1)
        elif kind == 'extent':
            value = extent(metrics['bounds'], check['axis'])
            value = round(value / 20, 2) if check.get('unit') == 'studs' else round(value, 1)
            passed = check.get('min', 0) <= value <= check.get('max', float('inf'))
        elif kind == 'ratio':
            denominator = extent(metrics['bounds'], check['denominator'])
            value = round(extent(metrics['bounds'], check['numerator']) / denominator, 3) if denominator else None
            passed = value is not None and check['min'] <= value <= check['max']
        elif kind == 'technic':
            value = ((metrics.get('technic') or {}).get(check['key']))
            passed = value is not None and check.get('min', 0) <= value <= check.get('max', float('inf'))
        elif kind == 'no_codes':
            found = metrics.get('codes') or {}
            value = {c: found[c] for c in check['codes'] if found.get(c)}
            passed = not value
        elif kind == 'ground':
            pattern = re.compile(check['pattern'], re.I)
            lows = [i['bounds']['max'][1] for i in instances if pattern.search(i.get('description') or '')]
            value = round(max(lows) - min(lows), 2) if lows else None
            passed = value is not None and value <= check['spread_max']
        else:
            raise ValueError(f'Unknown check type {kind}')
        results.append(dict(id=check['id'], passed=bool(passed), value=value))
    return results


def plan_metrics(plans):
    modes, matrices, entries = Counter(), Counter(), 0
    for path in plans:
        data = json.loads(path.read_text())
        for section in data['sections']:
            for step in section.get('steps', []):
                for entry in step:
                    entries += 1
                    mode = next((m for m in ('at', 'on', 'under', 'join', 'attach', 'snap', 'flex') if m in entry), 'other')
                    if mode == 'on' and isinstance(entry['on'], dict):
                        mode = 'on-technic' if entry['on'].keys() & {'hole', 'pin'} else 'on-connector'
                    modes[mode] += 1
                    if 'matrix' in entry:
                        matrices[json.dumps(entry['matrix'])] += 1
                    if 'orient' in entry:
                        modes['orient'] += 1
    port_based = modes.get('on-technic', 0) + modes.get('join', 0)
    return dict(plans=len(plans), entries=entries, modes=dict(modes),
                at_share=round(modes.get('at', 0) / entries, 3) if entries else None,
                technic_seat_share=round(port_based / entries, 3) if entries else None,
                raw_matrices=sum(matrices.values()), distinct_matrices=len(matrices))


def transcript_metrics(path):
    """Turns, tokens, images and tool calls from a claude -p stream-json log."""
    requests, tools, images, result = [], Counter(), 0, {}
    if not path.exists():
        return dict(available=False)
    for line in path.read_text(errors='replace').splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get('type') == 'assistant':
            message = event.get('message') or {}
            usage = message.get('usage') or {}
            if usage and (not requests or requests[-1]['id'] != message.get('id')):
                requests.append(dict(id=message.get('id'), prompt=usage.get('input_tokens', 0)
                                     + usage.get('cache_creation_input_tokens', 0) + usage.get('cache_read_input_tokens', 0),
                                     output=usage.get('output_tokens', 0)))
            for block in message.get('content') or []:
                if block.get('type') == 'tool_use':
                    tools[block.get('name')] += 1
                    target = str((block.get('input') or {}).get('file_path', ''))
                    if block.get('name') == 'Read' and target.lower().endswith(IMAGES):
                        images += 1
        elif event.get('type') == 'result':
            result = event
    prompts = [r['prompt'] for r in requests]
    final = (result.get('result') or '').strip().splitlines()
    return dict(available=True, requests=len(requests), turns=result.get('num_turns'),
                prompt_tokens=sum(prompts), max_context=max(prompts, default=0),
                output_tokens=sum(r['output'] for r in requests), tool_calls=dict(tools),
                images_opened=images, usd=result.get('total_cost_usd'),
                minutes=round(result.get('duration_ms', 0) / 60000, 1) if result.get('duration_ms') else None,
                is_error=result.get('is_error'), verdict=final[-1][:200] if final else None)


def trace_metrics(path):
    if not path.exists():
        return dict(available=False)
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    commands = Counter(r['argv'][0] if r['argv'] else '?' for r in rows)
    return dict(available=True, commands=len(rows), by_command=dict(commands),
                tool_seconds=round(sum(r['seconds'] for r in rows), 1),
                stdout_bytes=sum(r['stdout_bytes'] for r in rows),
                failures=sum(r['exit'] not in (0, None) for r in rows))


def score_run(folder, brief):
    folder = Path(folder)
    root, model, plans = delivered_files(folder)
    metrics, geometry = model_metrics(model) if model else (dict(present=False, checks_passed=False), None)
    review = root / 'review' / 'review.json'
    reviewed = json.loads(review.read_text()) if review.exists() else None
    transcript = transcript_metrics(folder / 'transcript.jsonl')
    trace = trace_metrics(root / 'trace.jsonl')
    checks = brief_checks(brief, metrics, geometry)
    rubric = folder / 'rubric.json'
    run = json.loads((folder / 'run.json').read_text()) if (folder / 'run.json').exists() else {}
    return dict(run=run.get('run', folder.name), brief=brief['id'], model_name=run.get('model'),
                repeat=run.get('repeat'), model={k: v for k, v in metrics.items() if k != 'bounds'},
                delivered=dict(model=str(model.relative_to(root)) if model else None,
                               review=bool(reviewed), review_passed=bool(reviewed and reviewed.get('checks_passed')),
                               readme=(root / 'README.md').exists()),
                checks=checks, checks_passed=sum(c['passed'] for c in checks), checks_total=len(checks),
                plan=plan_metrics(plans), cost=transcript, tools=trace,
                rubric=json.loads(rubric.read_text()) if rubric.exists() else None)


def row(score):
    m, c, t, p = score['model'], score['cost'], score['tools'], score['plan']
    rubric = score.get('rubric') or {}
    return dict(run=score['run'], brief=score['brief'], model=score.get('model_name'),
                built=m.get('checks_passed'), placements=m.get('placements'),
                main=m.get('main_group_ratio'), checks=f"{score['checks_passed']}/{score['checks_total']}",
                deep=m.get('deep_overlaps'), bare=m.get('exposed_side_studs'), glass=m.get('glass_obstructed'),
                at=p.get('at_share'), ports=p.get('technic_seat_share'), matrices=p.get('raw_matrices'),
                meshes=(m.get('technic') or {}).get('meshes'), seated=(m.get('technic') or {}).get('seated_share'),
                technic_errors=sum(n for c, n in ((m.get('technic') or {}).get('findings') or {}).items()
                                   if c in TECHNIC_ERRORS) if m.get('technic') else None,
                turns=c.get('turns'),
                context_k=round(c['max_context'] / 1000) if c.get('max_context') else None,
                images=c.get('images_opened'), tool_kb=round(t['stdout_bytes'] / 1024) if t.get('available') else None,
                usd=c.get('usd'), minutes=c.get('minutes'), rubric=rubric.get('mean'))


def table(folders):
    rows = []
    for folder in folders:
        for path in sorted(Path(folder).glob('*/score.json')):
            rows.append(dict(suite=Path(folder).name, **row(json.loads(path.read_text()))))
    if not rows:
        return 'No scored runs.'
    keys = list(rows[0])
    lines = ['| ' + ' | '.join(keys) + ' |', '|' + '---|' * len(keys)]
    lines += ['| ' + ' | '.join('' if r[k] is None else str(r[k]) for k in keys) + ' |' for r in rows]
    groups = {}
    for r in rows:
        groups.setdefault((r['suite'], r['brief'], r['model']), []).append(r)
    lines += ['', '| suite | brief | model | runs | built | checks | deep | bare | turns | context_k | usd |', '|' + '---|' * 11]
    for (suite, brief, model), items in sorted(groups.items()):
        def mean(key):
            values = [r[key] for r in items if isinstance(r[key], (int, float)) and not isinstance(r[key], bool)]
            return round(statistics.mean(values), 2) if values else ''
        built = sum(bool(r['built']) for r in items)
        checks = statistics.mean(int(r['checks'].split('/')[0]) / max(1, int(r['checks'].split('/')[1])) for r in items)
        lines.append(f"| {suite} | {brief} | {model} | {len(items)} | {built}/{len(items)} | {checks:.0%} | "
                     f"{mean('deep')} | {mean('bare')} | {mean('turns')} | {mean('context_k')} | {mean('usd')} |")
    return '\n'.join(lines)


def sheets(folders, out, seed=7):
    """Four views per delivered model from every suite, shuffled under anonymous IDs."""
    runs = sorted(p.parent for folder in folders for p in Path(folder).glob('*/score.json'))
    random.Random(seed).shuffle(runs)
    out = Path(out)
    key = {}
    for number, run in enumerate(runs, 1):
        _, model, _ = delivered_files(run)
        if model is None:
            continue
        anonymous = f'model-{number:02d}'
        key[anonymous] = str(run)
        subprocess.run([str(REPO / 'ldraw-agent'), 'render', str(model), '--outdir', str(out / anonymous),
                        '--views', 'home', 'front', 'right', 'top'], check=False, capture_output=True)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'key.json').write_text(json.dumps(key, indent=2) + '\n')
    template = {k: dict(identity=None, features=None, construction=None, finish=None, character=None, notes='')
                for k in key}
    if not (out / 'rubric.json').exists():
        (out / 'rubric.json').write_text(json.dumps(template, indent=1) + '\n')
    return dict(sheets=str(out), models=len(key), scores=str(out / 'rubric.json'),
                note='Fill rubric.json without opening key.json, then run unblind.')


def unblind(out):
    """Copy each anonymous rubric score into its run folder as rubric.json."""
    out = Path(out)
    key = json.loads((out / 'key.json').read_text())
    scores = json.loads((out / 'rubric.json').read_text())
    written = 0
    for anonymous, row in scores.items():
        values = [row.get(k) for k in ('identity', 'features', 'construction', 'finish', 'character')]
        if any(v is None for v in values):
            continue
        row = dict(row, mean=round(sum(values) / len(values), 2), sheet=anonymous)
        (Path(key[anonymous]) / 'rubric.json').write_text(json.dumps(row, indent=1) + '\n')
        written += 1
    return dict(unblinded=written, pending=len(scores) - written)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = p.add_subparsers(dest='command', required=True)
    c = commands.add_parser('run', help='Score one run folder')
    c.add_argument('folder')
    c.add_argument('--brief', required=True)
    c = commands.add_parser('table', help='Markdown table across suites')
    c.add_argument('folders', nargs='+')
    c = commands.add_parser('sheets', help='Blind four-view renders across suites for rubric scoring')
    c.add_argument('folders', nargs='+')
    c.add_argument('--out', required=True, help='Folder for the shuffled sheets, key.json and rubric.json')
    c = commands.add_parser('unblind', help='Copy completed rubric scores back into their run folders')
    c.add_argument('out')
    args = p.parse_args(argv)
    if args.command == 'run':
        scored = score_run(args.folder, brief_by_id(args.brief))
        (Path(args.folder) / 'score.json').write_text(json.dumps(scored, indent=2) + '\n')
        print(json.dumps(row(scored)))
    elif args.command == 'table':
        print(table(args.folders))
    elif args.command == 'sheets':
        print(json.dumps(sheets(args.folders, args.out)))
    else:
        print(json.dumps(unblind(args.out)))


if __name__ == '__main__':
    main()
