"""Scene assembly for the Linden Row House (orchestrator). Run from repo root:
    .venv/bin/python output/urban-house/generate.py [--regen]
--regen first re-runs every module generator. Writes output/urban-house/scene.plan.json.
"""
import json, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
MODULES = ['street', 'ground', 'floor2', 'floor3', 'roof']

if '--regen' in sys.argv:
    for m in MODULES:
        g = HERE / 'modules' / m / 'generate.py'
        if g.exists():
            subprocess.run([sys.executable, str(g)], check=True)

present = [m for m in MODULES if (HERE / 'modules' / m / f'{m}.plan.json').exists()]
steps = []
if 'street' in present:
    steps.append([dict(id='street', ref='street.ldr', colour=71, at=[0, 0, 0],
                       purpose='Plot, sidewalk, alley, garden and street props')])
else:
    steps.append([dict(id='street', ref='3811.dat', colour=2, at=[0, 0, 0], purpose='placeholder baseplate')])
prev = None
for m, purpose in [('ground', 'Café storey on the baseplate, footprint X -12..12 Z -6..10'),
                   ('floor2', 'Apartment storey with bay window'),
                   ('floor3', 'Apartment storey with balcony'),
                   ('roof', 'Roof terrace')]:
    if m not in present:
        break
    p = dict(id=m, ref=f'{m}.ldr', colour=71, purpose=purpose)
    if prev is None:
        p['at'] = [0, 0, 40]
    else:
        p['attach'] = dict(to=prev, anchor='next', using='base')
    steps.append([p])
    prev = m
plan = dict(version=1, author='Linden Row SNOT orchestrator (Claude Opus 5.5) with Haiku 5.5 module workers',
            includes=[f'modules/{m}/{m}.plan.json' for m in present],
            sections=[dict(name='linden-row.ldr',
                           description='Linden Row House (SNOT edition): original 3-storey urban townhouse with café, apartments and roof terrace',
                           steps=steps)])
(HERE / 'scene.plan.json').write_text(json.dumps(plan, indent=1))
print(json.dumps(dict(present=present)))
