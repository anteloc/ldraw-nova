"""Assemble a module from orchestrator core + task parts (orchestrator-owned).

assemble(module, only=None, outdir=None): builds the core, then every parts/<submodel>.py whose build(ctx)
returns a Module (optional attribute `place` = list of ([X,Y,Z] LDU, R or None); default one placement at
the origin). Children whose contract parent is another submodel are placed inside that parent.
`only` restricts the task submodels (dependencies on parents are added automatically).
"""
from __future__ import annotations
import importlib.util, json, sys, traceback
from pathlib import Path
RUN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN))
from common import export, add_ldu  # noqa: E402
from lib.storey_core import build_core, Ctx, CORE  # noqa: E402

CONTRACTS = json.loads((RUN / 'contracts.json').read_text())
AUTHOR = 'Linden Row run 3: orchestrator core + Claude Haiku 5.5 task workers'


def task_subs(module):
    subs = [s for s in CONTRACTS['modules'][module]['submodels'] if s['name'] not in CORE[module]]
    return subs


def _load(path):
    spec = importlib.util.spec_from_file_location(path.stem.replace('-', '_'), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def assemble(module, only=None, outdir=None, quiet=False):
    mdir = RUN / 'modules' / module
    subs = task_subs(module)
    parent_of = {s['name']: s['parent'] for s in subs}
    want = None
    if only:
        want = set(only)
        for n in list(want):
            p = parent_of.get(n)
            while p and p != module:
                want.add(p); p = parent_of.get(p)
    root = build_core(module)
    ctx = Ctx(module)
    built, problems = {}, []
    for s in subs:
        n = s['name']
        if want is not None and n not in want:
            continue
        f = mdir / 'parts' / f'{n}.py'
        if not f.exists():
            problems.append(f'{n}: no part file'); continue
        try:
            m = _load(f).build(ctx)
            if m is None or not hasattr(m, 'steps') or not any(m.steps):
                problems.append(f'{n}: build() returned no parts'); continue
            if m.name != n:
                problems.append(f'{n}: Module name is {m.name!r}, must be {n!r}'); continue
            built[n] = m
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)[-1]
            problems.append(f'{n}: {type(e).__name__}: {e} (line {tb.lineno})')
    for n, m in built.items():
        p = parent_of[n]
        host = root if p == module or p not in built else built[p]
        for at, R in getattr(m, 'place', [((0, 0, 0), None)]):
            add_ldu(host, m, 71, at, R)
    out = Path(outdir) if outdir else mdir
    out.mkdir(parents=True, exist_ok=True)
    if not any(root.steps):
        problems.append(f'{module}: nothing to export yet')
        stale = out / f'{module}.plan.json'
        if stale.exists():
            stale.unlink()
        return out, problems
    import contextlib, io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        export(root, module, out, AUTHOR)
    if not quiet:
        for p in problems:
            print('PART PROBLEM ' + p)
    return out, problems


if __name__ == '__main__':
    mod = sys.argv[1]
    out, problems = assemble(mod)
    print(json.dumps(dict(module=mod, out=str(out), problems=problems)))
