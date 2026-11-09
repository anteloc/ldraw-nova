"""Deterministic driver for run 3 (orchestrator-owned). Run from repo root:
    .venv/bin/python output/urban-house-run3/orchestrate.py [--concurrency 4] [--skip-tasks] [--no-repair]

Phases: tasks (fresh headless Haiku per task) -> integration r1 -> Opus review (one call, tickets) ->
repairs (fresh Haiku per affected task) -> integration r2 -> final ldraw-agent review -> costs/summary.
Every LLM call is a headless `claude -p` with stream-json output; per-request usage is logged and every
call's total_cost_usd goes to costs.jsonl.
"""
import argparse, concurrent.futures as cf, json, subprocess, sys, time
from pathlib import Path
RUN = Path(__file__).resolve().parent
REPO = RUN.parents[1]
WORK = Path('/private/tmp/claude-501/-Users-captain-workspaces-workspace-ai-ldraw-nova/'
            '8af0d69f-e18f-4241-8564-66546c71a0a2/scratchpad/run3work')
PY = str(REPO / '.venv/bin/python')
LOG = RUN / 'logs'
COSTS = RUN / 'costs.jsonl'
TIMELINE = RUN / 'timeline.jsonl'
MODULES = ['street', 'ground', 'floor2', 'floor3', 'roof']


def stamp(event, **kw):
    rec = dict(t=time.strftime('%H:%M:%S'), event=event, **kw)
    with open(TIMELINE, 'a') as f:
        f.write(json.dumps(rec) + '\n')
    print(json.dumps(rec), flush=True)


def claude(call_id, role, model, prompt, tools='Bash,Read,Write,Edit', effort='medium', timeout=2400, budget=None):
    wd = WORK / call_id
    wd.mkdir(parents=True, exist_ok=True)
    cmd = ['claude', '-p', prompt, '--model', model, '--output-format', 'stream-json', '--verbose',
           '--strict-mcp-config', '--disable-slash-commands', '--no-session-persistence',
           '--tools', tools, '--allowedTools', tools, '--permission-mode', 'dontAsk',
           '--setting-sources', 'project', '--add-dir', str(REPO), '--effort', effort]
    if budget:
        cmd += ['--max-budget-usd', str(budget)]
    t0 = time.time()
    raw = LOG / f'{call_id}.jsonl'
    try:
        p = subprocess.run(cmd, cwd=wd, capture_output=True, text=True, timeout=timeout)
        out, err = p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        out, err = (e.stdout or b'').decode() if isinstance(e.stdout, bytes) else (e.stdout or ''), 'TIMEOUT'
    raw.write_text(out)
    reqs, result = [], {}
    for line in out.splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get('type') == 'assistant':
            u = (ev.get('message') or {}).get('usage') or {}
            mid = (ev.get('message') or {}).get('id')
            if u and (not reqs or reqs[-1]['id'] != mid):
                reqs.append(dict(id=mid, input=u.get('input_tokens', 0), cache_write=u.get('cache_creation_input_tokens', 0),
                                 cache_read=u.get('cache_read_input_tokens', 0), output=u.get('output_tokens', 0)))
        elif ev.get('type') == 'result':
            result = ev
    prompts = [r['input'] + r['cache_write'] + r['cache_read'] for r in reqs]
    rec = dict(call=call_id, role=role, model=model, cost_usd=result.get('total_cost_usd'), turns=result.get('num_turns'),
               duration_s=round(time.time() - t0, 1), usage=result.get('usage'), requests=len(reqs),
               max_prompt=max(prompts) if prompts else None, is_error=result.get('is_error', True),
               result=(result.get('result') or err or '')[:600], per_request=reqs)
    with open(COSTS, 'a') as f:
        f.write(json.dumps(rec) + '\n')
    stamp('call_done', call=call_id, role=role, cost=rec['cost_usd'], turns=rec['turns'], dur=rec['duration_s'],
          max_prompt=rec['max_prompt'], error=rec['is_error'])
    return rec


def sh(args, out_file=None):
    r = subprocess.run(args, cwd=REPO, capture_output=True, text=True)
    if out_file:
        Path(out_file).write_text(r.stdout + r.stderr)
    return r


BUILD_SNIPPET = """
import sys, json
from ldraw_tools.builder import load_plan
from ldraw_tools.workflow import build_checked
from ldraw_tools.common import get_parts
text, model, rep = build_checked(load_plan(sys.argv[1]), get_parts(), contacts='none')
open(sys.argv[2], 'w', encoding='utf-8', newline='').write(text)
errs = [dict(code=d.get('code'), penetration=d.get('penetration'), sections=[x.get('section') for x in (d.get('sources') or [])],
             parts=[x.get('part') for x in (d.get('sources') or [])]) for d in rep['diagnostics'] if d.get('severity') == 'error']
json.dump(errs, open(sys.argv[3], 'w'))
print('build errors', len(errs), 'parts', rep['geometry']['occurrence_count'])
"""


def auto_tickets(d, tasks):
    """Deterministic tickets: overlaps (to the submodel with the larger envelope), contract FAILs, part problems."""
    C = json.loads((RUN / 'contracts.json').read_text())
    env = {s['name']: s['envelope'] for m in C['modules'].values() for s in m['submodels']}
    owner = {n: t['id'] for t in tasks for n in t['submodels']}
    def sub_of(sec):
        sec = (sec or '').replace('.ldr', '')
        best = max((n for n in env if sec == n or sec.startswith(n + '-')), key=len, default=None)
        return best
    vol = lambda n: (env[n]['x'][1] - env[n]['x'][0]) * (env[n]['z'][1] - env[n]['z'][0]) * (env[n]['h'][1] - env[n]['h'][0])
    tickets, pairs = [], {}
    for e in json.loads((d / 'errors.json').read_text()):
        subs = [sub_of(s) for s in e['sections']]
        if len(subs) == 2 and all(subs):
            pairs.setdefault(tuple(sorted(subs)), []).append(e)
    for (a, b), es in pairs.items():
        y = a if a == b else (a if vol(a) >= vol(b) else b)
        other = b if y == a else a
        if y in owner:
            tickets.append(dict(task=owner[y], submodel=y, issue=f"{len(es)} body overlap error(s) with {other} (parts {es[0]['parts']})",
                                fix=f"make room for {other}: move/trim/remove your colliding parts so nothing interpenetrates; check.py now shows these"))
    for line in (d / 'contract.txt').read_text().splitlines():
        if line.startswith('FAIL') and 'VISUAL' not in line:
            n = line.split()[1]
            if n in owner:
                tickets.append(dict(task=owner[n], submodel=n, issue='contract_check FAIL', fix='run check.py and make it PASS'))
    for f in d.glob('assemble-*.txt'):
        for prob in f.read_text().split("'"):
            n = prob.split(':')[0]
            if n in owner and ':' in prob:
                tickets.append(dict(task=owner[n], submodel=n, issue=prob.strip(), fix='fix the part file so it builds'))
    sys.path.insert(0, str(RUN))
    from lib.storey_core import mounts
    MOUNT_TASK = {('ground', 'pier'): 'ground-rustication', ('ground', 'lintel'): 'ground-awning', ('ground', 'fascia'): 'ground-sign',
                  ('ground', 'rear'): 'ground-rear', ('floor2', 'head'): 'floor2-facade', ('floor2', 'pier'): 'floor2-facade',
                  ('floor2', 'box'): 'floor2-window-box', ('floor2', 'rear'): 'floor2-rear', ('floor3', 'cornice'): 'floor3-cornice',
                  ('floor3', 'pilaster'): 'floor3-pilaster', ('floor3', 'rear'): 'floor3-rear'}
    try:
        rows = json.loads((d / 'contract.json').read_text())
    except Exception:
        rows = []
    for r in rows:
        name = r.get('submodel', '')
        if not name.startswith('VISUAL'):
            continue
        own = name[name.index('(') + 1:-1].replace('.ldr', '')
        if own in owner:
            tickets.append(dict(task=owner[own], submodel=own, issue=r['fails'][0][:300],
                                fix='cover/use every side stud of your own bricks, or remove unused side-stud bricks; glass must show room, not a wall'))
        elif own.endswith('-walls') and 'locs' in r:
            mod = own.split('-')[0]
            hit = {}
            for nm, mt in mounts(mod).items():
                for x, h, z in r['locs']:
                    if any(abs(sx / 20 - x) < 0.6 and abs(-sy - h) < 1 for sx, sy, sz in mt['studs']):
                        hit[nm] = hit.get(nm, 0) + 1
            for nm, n in hit.items():
                key = (mod, nm.split('-')[0])
                sub = MOUNT_TASK.get(key)
                if sub in owner:
                    tickets.append(dict(task=owner[sub], submodel=sub, issue=f"{n} stud(s) of wall mount '{nm}' are exposed (nothing seated on them)",
                                        fix=f"seat your SNOT panel on ALL studs of ctx.mounts['{nm}'] (see brief), so none stay bare"))
    (d / 'auto_tickets.json').write_text(json.dumps(tickets, indent=1))
    return tickets


def integrate(rnd):
    d = RUN / 'integration' / rnd
    d.mkdir(parents=True, exist_ok=True)
    for m in MODULES:
        sh([PY, str(RUN / 'modules' / m / 'generate.py')], d / f'assemble-{m}.txt')
    sh([PY, str(RUN / 'generate.py')])
    mpd = RUN / 'linden-row.mpd'
    r = sh([PY, '-c', BUILD_SNIPPET, str(RUN / 'scene.plan.json'), str(mpd), str(d / 'errors.json')])
    (d / 'build.txt').write_text(r.stdout + r.stderr)
    sh([PY, str(RUN / 'contract_check.py'), str(mpd), '--json', str(d / 'contract.json')], d / 'contract.txt')
    sh([PY, str(RUN / 'check_floating.py'), str(mpd)], d / 'floating.txt')
    imgs = []
    r = sh(['ldraw-xray', 'render', str(mpd), '--view', 'home', '--view', 'front', '--view', 'back', '--view', 'right',
            '-o', str(d / 'whole'), '--force'])
    imgs += sorted((d / 'whole' / 'panels').glob('*.png'))
    for m in ['street', 'ground', 'floor2', 'floor3', 'roof']:
        sh(['ldraw-xray', 'render', str(mpd), '--section', f'{m}.ldr', '--view', 'home', '-o', str(d / f'mod-{m}'), '--force'])
        imgs += sorted((d / f'mod-{m}' / 'panels').glob('*.png'))
    for p in imgs:
        subprocess.run(['sips', '-Z', '1024' if 'mod-' in str(p) else '768', str(p)], capture_output=True)
    txt = (d / 'contract.txt').read_text()
    summary = txt.strip().splitlines()[-1] if txt.strip() else ''
    stamp('integrated', round=rnd, contract=summary, images=len(imgs))
    return d, imgs, txt


def review(rnd, d, imgs, contract_txt, tasks):
    fails = '\n'.join(l for l in contract_txt.splitlines() if 'FAIL' in l)[:6000]
    owners = '\n'.join(f"{t['id']}: {', '.join(t['submodels'])}" for t in tasks)
    prompt = f"""You are the design reviewer for "Linden Row House", an original 3-storey LDraw townhouse (café ground floor,
two apartments, roof terrace, street plot) built by 16 worker tasks. Read each image (Read tool) and the automatic check
failures below, then write at most 8 repair tickets for the most important REAL defects: automatic FAILs first, then clearly
visible problems (floating/misplaced parts, gaps, exposed side studs, glass showing solid wall, elements that do not read as what
they are, ugly or incoherent details). Ignore glass/blind-spot notes and taste nitpicks. Do not read any other files.
Images:
{chr(10).join(str(p) for p in imgs)}
Automatic check failures:
{fails or 'none'}
Task ownership:
{owners}
Write the tickets as a JSON list to {d / 'tickets.json'} with objects {{"task": "T05", "submodel": "floor2-facade",
"issue": "...", "fix": "concrete instruction"}} (empty list if nothing important). Then reply with the number of tickets."""
    return claude(f'review-{rnd}', 'review', 'opus', prompt, tools='Read,Write', effort='medium', budget=0.6)


def run_tasks(tasks, conc, prefix, prompt_of, role=None, repair=False):
    with cf.ThreadPoolExecutor(conc) as ex:
        futs = {ex.submit(claude, f"{prefix}{t['id']}", role or ('worker' if prefix == '' else 'repair'), t.get('model', 'haiku'),
                          prompt_of(t), budget=t.get('repair_budget' if repair else 'budget')): t for t in tasks}
        for f in cf.as_completed(futs):
            f.result()


def repair_round(rnd, tasks, conc, d, imgs, txt, do_review=True):
    tickets = auto_tickets(d, tasks)
    if do_review:
        review(rnd, d, imgs, txt, tasks)
        try:
            tickets += json.loads((d / 'tickets.json').read_text())
        except Exception:
            pass
    stamp('tickets', round=rnd, n=len(tickets))
    by_task = {}
    for tk in tickets:
        by_task.setdefault(tk.get('task'), []).append(tk)
    rep = [dict(t, tickets=by_task[t['id']]) for t in tasks if t['id'] in by_task]
    if rep:
        run_tasks(rep, conc, f'fix{rnd}-', lambda t: (
            f"Your task brief is {t['brief']} — Read it. Your part files already exist. Integration of the whole house found "
            f"these defects; fix them in your part files only (check.py now also builds the other tasks' parts of your module, "
            f"so collisions with them are reported):\n" +
            '\n'.join(f"- {x['submodel']}: {x['issue']} -> {x['fix']}" for x in t['tickets']) +
            "\nRe-run the check until RESULT PASS with no errors, then one --snap to confirm visually. ≤ 15 tool calls. Reply one line per fix."))
    stamp('repairs_done', round=rnd, tasks=len(rep))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--concurrency', type=int, default=4)
    ap.add_argument('--skip-tasks', action='store_true')
    ap.add_argument('--no-repair', action='store_true')
    ap.add_argument('--rounds', type=int, default=1, help='repair rounds')
    ap.add_argument('--quality', action='store_true', help='quality pass: every task reworks its existing parts first')
    a = ap.parse_args()
    LOG.mkdir(exist_ok=True); WORK.mkdir(parents=True, exist_ok=True)
    tasks = json.loads((RUN / 'tasks.json').read_text())
    stamp('start', tasks=len(tasks), concurrency=a.concurrency)
    if a.quality:
        run_tasks(tasks, a.concurrency, 'q-', role='quality', prompt_of=lambda t: (
            f"Your task brief is {t['brief']} — Read it (it has new QUALITY RULES). Your part files already exist from a first "
            f"pass that a human judged low quality (blocked windows, bare studs on facades, parts inside each other, crude shapes). "
            f"Run the check first: it now reports VISUAL problems for your submodels. Rework or rewrite your part files until "
            f"RESULT PASS with no VISUAL lines, then --snap and Read every image; improve anything that does not look good and "
            f"real. Work only on your files."))
        stamp('quality_tasks_done')
    elif not a.skip_tasks:
        run_tasks(tasks, a.concurrency, '', lambda t: f"Your task brief is {t['brief']} — Read it and complete the task exactly as it says.")
        stamp('tasks_done')
    d, imgs, txt = integrate('r1')
    if not a.no_repair:
        for k in range(1, a.rounds + 1):
            repair_round(f'r{k}', tasks, a.concurrency, d, imgs, txt, do_review=(k == 1))
            d, imgs, txt = integrate(f'r{k + 1}')
    sh(['./ldraw-agent', 'review', str(RUN / 'scene.plan.json'), '--outdir', str(RUN / 'review'), '--views', 'home', 'front',
        'back', 'top', 'bottom', '--contacts', 'all', '--force'], RUN / 'integration' / 'review.stdout.json')
    stamp('final_review_done')
    sh([PY, str(RUN / 'cost_model.py')], RUN / 'integration' / 'cost_model.txt')
    stamp('end')


if __name__ == '__main__':
    main()
