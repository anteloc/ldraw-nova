"""Keep the cat's diagonal details and repeated joints seated when examples change."""
from collections import Counter
from dataclasses import replace
import hashlib
import json

import numpy as np
import pytest
from ldraw import Vector
from ldraw.connection_types import ConnectionKind as Kind, connection_residual

from ldraw_tools.builder import build_plan, load_plan
from ldraw_tools.common import ROOT, jsonable
from ldraw_tools.connection_adapter import query_frames
from ldraw_tools.connectivity import inspect_connections
from ldraw_tools.document import parse_source
from ldraw_tools.geometry import analyze_geometry, components

REFERENCE = ROOT / 'examples/snot/cat'


@pytest.mark.parametrize('name,count,groups', [('head',16,1), ('leg',3,1), ('cat',55,4)])
def test_cat_examples_reproduce_reviewed_models(official, name, count, groups):
    text, model, diagnostics = build_plan(load_plan(REFERENCE/f'{name}.plan.json'),official)
    assert not diagnostics
    assert text.encode() == (REFERENCE/f'{name}.mpd').read_bytes()
    report = analyze_geometry(model,official,contacts='all')
    assert report['complete']
    assert report['occurrence_count'] == count
    assert report['optimistic_component_count'] == groups
    assert not [d for d in report['diagnostics'] if d['severity']=='error']


def test_cat_source_preserved_and_every_prepared_pose_accounted_for(official):
    manifest = json.loads((REFERENCE/'preparation.json').read_text())
    assert hashlib.sha256((REFERENCE/'source.ldr').read_bytes()).hexdigest() == manifest['original_sha256']
    source = list(parse_source(REFERENCE/'source.ldr').iter_occurrences())
    prepared = list(parse_source(REFERENCE/'cat.mpd').iter_occurrences())
    def inventory(occurrences):
        return Counter(('3023b.dat' if o.reference=='3023.dat' else o.reference,o.colour.code)
                       for o in occurrences)
    assert inventory(source) == inventory(prepared)
    records = manifest['parts']
    assert {p['source_index'] for p in records} == set(range(55))
    assert {p['prepared_occurrence'] for p in records} == set(range(55))
    shift = np.array(manifest['root_translation_ldu'])
    for record in records:
        before, after = source[record['source_index']], prepared[record['prepared_occurrence']]
        delta = np.array(jsonable(after.position))-np.array(jsonable(before.position))-shift
        assert np.allclose(delta,record['correction_ldu'],atol=1e-7,rtol=0)
        assert np.linalg.norm(delta) < 0.191
        matrix = np.array(after.matrix.rows)
        assert np.allclose(matrix.T@matrix,np.eye(3),atol=1e-9)
        assert np.linalg.det(matrix) == pytest.approx(1)
        assert np.max(np.abs(matrix-np.array(before.matrix.rows))) < 1e-6


def test_cat_diagonal_stud_pivots_and_detached_ear(official):
    plan = load_plan(REFERENCE/'head.plan.json')
    _, head, _ = build_plan(plan,official)
    rows = [p for step in plan['sections'][0]['steps'] for p in step]
    inspection = query_frames(inspect_connections(head,official))
    items = {row['id']:item for row,item in zip(rows,inspection.occurrences,strict=True)}
    for support,detail in [('face-base','left-ear'),('face-base','right-ear'),
                           ('left-ear','left-ear-tip'),('right-ear','right-ear-tip'),
                           ('muzzle-jumper','nose')]:
        studs = [f for f in items[support].connections if f.kind is Kind.STUD]
        sockets = [f for f in items[detail].connections if f.kind is Kind.STUD_RECEPTACLE]
        matches = [(a,b) for a in studs for b in sockets
                   if abs(a.position-b.position)<1e-7 and a.axis.dot(b.axis)<-.999999]
        assert len(matches) == 1, (support,detail)
    # Keeping the ear's internal clutch does not connect it to the face.
    detached = {id(head.pieces[i]) for i,row in enumerate(rows)
                if row['id'] in {'left-ear','left-ear-tip'}}
    broken = replace(head,objects=[replace(o,position=o.position+Vector(-40,0,0))
                                  if id(o) in detached else o for o in head.objects])
    assert analyze_geometry(broken,official)['optimistic_component_count'] > 1


def test_cat_joints_and_supplemental_connection_evidence(official):
    model = parse_source(REFERENCE/'cat.mpd')
    inspection = query_frames(inspect_connections(model,official))
    records = json.loads((REFERENCE/'preparation.json').read_text())['parts']
    source = {r['source_index']:inspection.occurrences[r['prepared_occurrence']] for r in records}
    for a,b in [(7,28),(27,19),(33,37),(29,42),(36,46),(51,35)]:
        balls = [f for f in source[a].connections if f.kind is Kind.GENERIC]
        sockets = [f for f in source[b].connections if f.kind is Kind.GENERIC]
        assert any(abs(x.position-y.position)<1e-7 for x in balls for y in sockets)
    for a,b in [(21,24),(41,39),(45,44),(54,53)]:
        clip = next(f for f in source[a].connections if 'snap_clp' in f.feature_id)
        bar = next(f for f in source[b].connections if f.kind is Kind.BAR)
        assert abs(clip.position-bar.position) < 1e-7
        assert abs(clip.axis.dot(bar.axis)) > .999999
    report = analyze_geometry(model,official,contacts='all',output_limit=5000)
    edges = [c['instances'] for c in report['contacts']]
    evidence = json.loads((REFERENCE/'interface-evidence.json').read_text())
    for interface in evidence['interfaces']:
        a,b = [inspection.occurrences[i] for i in interface['prepared_occurrences']]
        assert [a.occurrence.reference,b.occurrence.reference] == interface['parts']
        fa,fb = [{f.feature_id:f for f in o.connections} for o in (a,b)]
        if interface['kind']=='stud':
            for match in interface['matches']:
                stud,socket = fa[match['stud']],fb[match['socket']]
                assert abs(stud.position-socket.position) < 1e-7
                assert stud.axis.dot(socket.axis) < -.999999
        else:
            axle,hole = fa[interface['axle']],fb[interface['hole']]
            assert abs(axle.position-hole.position) < 1e-7
            residual = connection_residual(axle,hole)
            assert residual.alignment > .999999
            assert residual.roll_alignment > .999999
            end = hole.axis.dot(axle.axis)*hole.profile.length
            assert sorted([0,end]) == interface['nominal_hole_interval_on_axle_ldu']
            assert abs(end) <= axle.profile.length/2
        edges.append(interface['prepared_occurrences'])
    assert len(components(list(range(55)),edges)) == 1
