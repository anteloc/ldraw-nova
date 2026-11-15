"""Agent-facing output: summaries, one-line verdicts, compact JSON and the CLI trace."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from ldraw_tools.report import one_line, summarize, text

ROOT = Path(__file__).resolve().parents[1]


def build_report():
    placement = lambda path: dict(index=0, path=path, part='3001.dat', file='plan.json', pointer='/sections/0/steps/0/0')
    return dict(checks_passed=False, physical_validity='not_proven', output='m.mpd', written=False, draft='m.draft.mpd',
                source_map=[dict(index=i, path=f'p{i}') for i in range(500)],
                geometry=dict(occurrence_count=500, optimistic_component_count=2, main_group_size=499, contacts_checked=True,
                              overlap_candidate_count=9, bounds=dict(min=[0, 0, 0], max=[1, 1, 1]), instances=[{}] * 500,
                              appearance=dict(deep_overlaps=0, exposed_side_studs=3, glass_obstructed=0)),
                diagnostics=[dict(code='assembly.body_overlap', severity='error', message='Bodies overlap', separation=[0, -8, 0],
                                  instances=[1, 2], placements=[placement('wall/brick-1'), placement('wall/brick-2')]),
                             *[dict(code='part.alias_or_internal', severity='warning', message='3023.dat has moved',
                                    replacement='3023b.dat', placements=[placement(f'deck-{i}')]) for i in range(19)]])


def test_summary_keeps_every_error_names_placements_and_groups_warnings():
    summary = summarize(build_report())
    assert summary['errors'] == [dict(code='assembly.body_overlap', message='Bodies overlap',
                                      at=['wall/brick-1', 'wall/brick-2'], separation=[0, -8, 0])]
    assert summary['warnings']['part.alias_or_internal']['count'] == 19
    assert summary['warnings']['part.alias_or_internal']['at'] == ['deck-0', 'deck-1', 'deck-2']
    assert summary['geometry']['main_group'] == 499 and 'source_map' not in summary
    assert summary['next'].startswith('Fix assembly.body_overlap at wall/brick-1')
    assert len(text(summary)) < 2000 < len(text(build_report()))


def test_one_line_reports_verdict_counts_and_first_error():
    row = one_line(build_report())
    assert row['checks_passed'] is False and row['errors'] == 1 and row['warnings'] == 19
    assert row['first_error']['at'] == ['wall/brick-1'] or row['first_error']['at'][0] == 'wall/brick-1'
    assert row['draft'] == 'm.draft.mpd'


def test_text_puts_vectors_and_matrices_on_one_line():
    rendered = text(dict(at=[1, 2, 3], matrix=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], nested=dict(a=dict(b=[1, 2]), c='x' * 120)))
    assert '"at": [1, 2, 3]' in rendered and '"matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]]' in rendered
    assert json.loads(rendered)['nested']['a'] == {'b': [1, 2]}


@pytest.mark.parametrize('arguments', [['colours', 'red'], ['matrix', 'y', '90'], ['profiles'],
                                       ['knowledge', 'search', 'side stud', '--limit', '2']])
def test_cli_commands_print_json_and_append_a_trace(arguments, tmp_path):
    trace = tmp_path / 'trace.jsonl'
    result = subprocess.run([sys.executable, '-m', 'ldraw_tools.cli', *arguments], cwd=ROOT, capture_output=True,
                            text=True, env=dict(os.environ, LDRAW_AGENT_TRACE=str(trace)))
    assert result.returncode == 0, result.stderr
    json.loads(result.stdout)
    row = json.loads(trace.read_text().splitlines()[-1])
    assert row['argv'] == arguments and row['exit'] == 0 and row['stdout_bytes'] == len(result.stdout.encode())


def test_part_prints_compact_faces(official):
    result = subprocess.run([sys.executable, '-m', 'ldraw_tools.cli', 'part', '87087'], cwd=ROOT, capture_output=True, text=True)
    facts = json.loads(result.stdout)
    assert result.returncode == 0 and facts['studs']['-Z'] == [[0.0, 10.0, -10.0]] and len(result.stdout) < 1200
    full = subprocess.run([sys.executable, '-m', 'ldraw_tools.cli', 'part', '87087', '--full'], cwd=ROOT,
                          capture_output=True, text=True)
    assert 'connectors' in json.loads(full.stdout)
