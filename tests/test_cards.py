"""The cards are what agents copy: their examples must build exactly as written."""
import json

import numpy as np
import re
from pathlib import Path

from ldraw_tools.builder import build_plan

ROOT = Path(__file__).resolve().parents[1]


def blocks(name):
    text = (ROOT / 'docs/agent/cards' / name).read_text()
    return re.findall(r'```json\n(.*?)\n```', text, re.S)


def plan_from(snippet, extra_sections=()):
    entries = json.loads('[' + snippet + ']')
    return dict(version=1, author='Card test', sections=[
        dict(name='card.ldr', description='Card example', steps=[[entry] for entry in entries]), *extra_sections])


def errors(diagnostics):
    return [d for d in diagnostics if d['severity'] == 'error']


def test_plan_card_example_builds_with_its_seats(official):
    plan = json.loads(blocks('plan.md')[0])
    context = {}
    _, model, diagnostics = build_plan(plan, official, context=context)
    assert not errors(diagnostics) and len(model.pieces) == 4
    assert {s['placement']: s['mated'] for s in context['seats']} == {'lamp': 1, 'lens': 1}


def test_snot_card_examples_build(official):
    seat, module = blocks('snot.md')
    context = {}
    _, _, diagnostics = build_plan(plan_from(seat), official, context=context)
    assert not errors(diagnostics) and context['seats'][0]['mated'] == 4
    flank = dict(name='flank.ldr', description='Flat panel', steps=[[dict(id='plate', ref='3710.dat', colour=16, at=[0, 0, 0])]])
    core = '{"id": "core", "ref": "30414.dat", "colour": 71, "at": [0, -24, 0], "yaw": 90}, ' + module
    _, model, diagnostics = build_plan(plan_from(core, [flank]), official)
    assert not errors(diagnostics) and len(model.pieces) == 2
    # roll 90 lays the flat panel along the brick's row of side studs (world -Z after yaw 90).
    panel = model.pieces[1]
    assert np.allclose(np.array(panel.matrix.rows) @ [1, 0, 0], [0, 0, -1])
    assert np.allclose([panel.position.x, panel.position.y, panel.position.z], [-18, -14, 0])
