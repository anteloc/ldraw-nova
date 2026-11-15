"""Benchmark tooling: scoring inputs, harness commands and the reading budget."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bench'))

import reading_cost  # noqa: E402
import run as bench_run  # noqa: E402
import score  # noqa: E402


def test_entry_document_required_reading_stays_under_budget():
    report = reading_cost.report(ROOT / 'AGENTS.md')
    assert report['required_tokens'] < 6000, report['required']
    assert {r['file'] for r in report['required']} >= {'AGENTS.md', 'docs/agent/cards/plan.md', 'docs/agent/cards/snot.md'}


def test_transcript_metrics_count_turns_tokens_images_and_cost(tmp_path):
    events = [
        dict(type='assistant', message=dict(id='m1', usage=dict(input_tokens=10, cache_read_input_tokens=1000, output_tokens=5),
                                            content=[dict(type='tool_use', name='Read', input=dict(file_path='review/previews/home.png'))])),
        dict(type='assistant', message=dict(id='m1', usage=dict(input_tokens=10, cache_read_input_tokens=1000, output_tokens=5),
                                            content=[dict(type='tool_use', name='Bash', input=dict(command='./ldraw-agent build x'))])),
        dict(type='assistant', message=dict(id='m2', usage=dict(input_tokens=20, cache_creation_input_tokens=3000, output_tokens=7),
                                            content=[])),
        dict(type='result', num_turns=2, total_cost_usd=0.12, duration_ms=90000, is_error=False, result='Built it.\nDONE'),
    ]
    path = tmp_path / 'transcript.jsonl'
    path.write_text('\n'.join(json.dumps(e) for e in events) + '\nnot json\n')
    metrics = score.transcript_metrics(path)
    assert metrics['requests'] == 2 and metrics['prompt_tokens'] == 1010 + 3020 and metrics['max_context'] == 3020
    assert metrics['images_opened'] == 1 and metrics['tool_calls'] == {'Read': 1, 'Bash': 1}
    assert metrics['usd'] == 0.12 and metrics['minutes'] == 1.5 and metrics['verdict'] == 'DONE'


def test_plan_metrics_measure_absolute_placements_and_matrices(tmp_path):
    plan = dict(version=1, author='x', sections=[dict(name='a.ldr', description='A', steps=[[
        dict(id='a', ref='3001.dat', colour=4, at=[0, 0, 0], matrix=[[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
        dict(id='b', ref='3001.dat', colour=4, on='a'),
        dict(id='c', ref='3070b.dat', colour=4, on=dict(to='b', face='-Z'))]])])
    path = tmp_path / 'model.plan.json'
    path.write_text(json.dumps(plan))
    metrics = score.plan_metrics([path])
    assert metrics['modes'] == {'at': 1, 'on': 1, 'on-connector': 1} and metrics['at_share'] == 0.333
    assert metrics['raw_matrices'] == 1


def test_brief_checks_use_bom_extent_and_ground_rules():
    brief = dict(checks=[dict(id='tyres', type='bom', pattern='Tyre', min=2),
                         dict(id='width', type='extent', axis='x', unit='studs', min=4, max=8),
                         dict(id='stance', type='ground', pattern='Tyre', spread_max=2)])
    instances = [dict(part='3641.dat', description='Tyre 6/50 x 8', bounds=dict(min=[0, 0, 0], max=[0, 20, 0])),
                 dict(part='3641.dat', description='Tyre 6/50 x 8', bounds=dict(min=[0, 0, 0], max=[0, 23, 0]))]
    metrics = dict(bounds=dict(min=[-60, 0, 0], max=[60, 20, 0]))
    results = {r['id']: r for r in score.brief_checks(brief, metrics, dict(instances=instances))}
    assert results['tyres']['passed'] and results['width']['value'] == 6.0
    assert not results['stance']['passed'] and results['stance']['value'] == 3


def test_dry_run_prints_isolated_headless_commands_without_writing(tmp_path, capsys):
    bench_run.main(['--suite', 'unit-test-dry', '--model', 'haiku', '--brief', 'radio', '--repeats', '1',
                    '--dry-run', '--workspace', str(tmp_path)])
    out = capsys.readouterr().out
    assert "'--model' haiku" not in out and '--model haiku' in out and 'output/bench/radio-haiku-r1' in out
    assert '--permission-mode dontAsk' in out and not (ROOT / 'output/bench/unit-test-dry').exists()
    assert not (tmp_path / 'unit-test-dry').exists()


def test_every_brief_has_checks_of_known_types():
    data = json.loads((ROOT / 'bench/briefs.json').read_text())
    known = {'placements', 'connected', 'bom', 'parts_any', 'extent', 'ratio', 'ground'}
    assert {b['round'] for b in data['briefs']} == {1, 2} and len([b for b in data['briefs'] if b['round'] == 1]) == 4
    for brief in data['briefs']:
        assert brief['checks'] and {c['type'] for c in brief['checks']} <= known, brief['id']
        assert '{outdir}' in data['harness']


def test_unblind_writes_completed_scores_back_to_runs(tmp_path):
    run_a, run_b = tmp_path / 'suite/a', tmp_path / 'suite/b'
    run_a.mkdir(parents=True), run_b.mkdir(parents=True)
    blind = tmp_path / 'blind'
    blind.mkdir()
    (blind / 'key.json').write_text(json.dumps({'model-01': str(run_a), 'model-02': str(run_b)}))
    (blind / 'rubric.json').write_text(json.dumps({
        'model-01': dict(identity=4, features=3, construction=4, finish=3, character=4, notes='ok'),
        'model-02': dict(identity=None, features=None, construction=None, finish=None, character=None, notes='')}))
    assert score.unblind(blind) == dict(unblinded=1, pending=1)
    assert json.loads((run_a / 'rubric.json').read_text())['mean'] == 3.6 and not (run_b / 'rubric.json').exists()
