"""Quiet per-task check (orchestrator-owned). Prints at most ~12 lines.

Usage (repo root):
  .venv/bin/python output/urban-house-run3/check.py <module> <submodel>[,<submodel>...] [--snap]

Builds core + every existing part of the module (other tasks' parts too, so collisions show; --isolated = only yours) into modules/<m>/check/<first-submodel>/,
runs the builder's checks and contract_check for those submodels, and with --snap renders one image of
each submodel (isolated, home view) and one in-parent front view, downscaled to 768 px.
"""
import json, subprocess, sys
from pathlib import Path
RUN = Path(__file__).resolve().parent
REPO = RUN.parents[1]
sys.path.insert(0, str(RUN)); sys.path.insert(0, str(REPO))
from lib.assemble import assemble  # noqa: E402


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    snap = '--snap' in sys.argv
    module, subs = args[0], args[1].split(',')
    isolated = '--isolated' in sys.argv
    out, problems = assemble(module, only=subs if isolated else None, outdir=RUN / 'modules' / module / 'check' / subs[0], quiet=True)
    problems = [p for p in problems if p.split(':')[0] in subs]
    for p in problems:
        print('PART PROBLEM ' + p)
    if any(p.split(':')[0] in subs for p in problems):
        print('RESULT FAIL (fix the part file first)'); return 1
    from ldraw_tools.builder import load_plan
    from ldraw_tools.workflow import build_checked
    from ldraw_tools.common import get_parts
    plan = load_plan(out / 'test.plan.json')
    text, model, report = build_checked(plan, get_parts(), contacts='none')
    mpd = out / f'{module}.mpd'
    mpd.write_text(text, encoding='utf-8', newline='')
    mine = lambda d: any(any((src.get('section') or '').startswith(x) for x in subs) for src in (d.get('sources') or [])) or not d.get('sources')
    errs = [d for d in report['diagnostics'] if d.get('severity') == 'error' and mine(d)]
    print(f"BUILD {'OK' if not errs else 'ERROR'}: {report['geometry']['occurrence_count']} parts")
    for d in errs[:4]:
        secs = ' vs '.join(f"{x.get('section')}:{x.get('part')}" for x in (d.get('sources') or []))
        print(f"  error {d.get('code')} {secs} (penetration {d.get('penetration')})")
    if len(errs) > 4:
        print(f"  ... {len(errs) - 4} more errors")
    ok = not errs
    r = subprocess.run([sys.executable, str(RUN / 'contract_check.py'), str(mpd), '--module', module],
                       capture_output=True, text=True, cwd=REPO)
    rows, cur = [], None
    for l in r.stdout.splitlines():
        if l.startswith(('PASS', 'FAIL')):
            cur = [l]; rows.append(cur)
        elif cur is not None and l.startswith('   '):
            cur.append(l)
    for row in rows:
        head = row[0]
        mine_row = any(head.split()[1] == x for x in subs) or ('VISUAL' in head and any(f'({x}' in head for x in subs))
        if not mine_row:
            continue
        for l in row[:3]:
            print(l[:320])
        if head.startswith('FAIL'):
            ok = False
    if snap:
        imgs = []
        for s in subs:
            d = out / 'snap' / s
            subprocess.run(['ldraw-xray', 'render', str(mpd), '--section', f'{s}.ldr', '--view', 'home', '-o', str(d), '--force'],
                           capture_output=True, cwd=REPO)
            imgs += sorted(d.glob('panels/*.png'))
        d = out / 'snap' / 'parent'
        subprocess.run(['ldraw-xray', 'render', str(mpd), '--view', 'front', '-o', str(d), '--force'], capture_output=True, cwd=REPO)
        imgs += sorted(d.glob('panels/*.png'))
        for p in imgs:
            subprocess.run(['sips', '-Z', '1024' if 'parent' in str(p) else '768', str(p)], capture_output=True)
            print('IMAGE ' + str(p))
    print('RESULT ' + ('PASS' if ok else 'FAIL'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
