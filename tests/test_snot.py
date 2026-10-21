"""Real SNOT seating, preserved reference inventory, and bounded socket adaptation."""
from collections import Counter
from dataclasses import replace
import hashlib
import json

import numpy as np
import pytest
from ldraw import Model, Piece, Vector
from ldraw.connection_types import ConnectionKind, CylindricalCaps, SectionShape

from ldraw_tools.builder import build_plan, load_plan, rotation
from ldraw_tools.common import ROOT, jsonable
from ldraw_tools.connection_adapter import query_frames
from ldraw_tools.connectivity import inspect_connections, snap_report, apply_snap
from ldraw_tools.document import parse_source
from ldraw_tools.geometry import analyze_geometry, components

REFERENCE = ROOT / 'examples/snot/parrot'


@pytest.mark.parametrize('code,height', [('22885',40), ('67329',40), ('47457',16)])
@pytest.mark.parametrize('axis,degrees', [('y',0), ('z',90), ('x',90), ('z',37)])
def test_deep_socket_snap_in_rigid_orientations(official, code, height, axis, degrees):
    orient = rotation(axis, degrees)
    origin = Vector(130,50,80)
    original = official.connections(code)
    hole = next(f for f in original if f.kind is ConnectionKind.PIN_HOLE
                and f.position.x == -10 and f.position.z == 0)
    stud = next(f for f in official.connections('3023b') if f.kind is ConnectionKind.STUD
                and f.position.x == -10 and f.position.z == 0)
    model = Model.from_pieces([
        Piece.place('3023b', colour=4, position=origin, matrix=orient),
        Piece.place(code, colour=15, position=origin+orient*Vector(0,-height-20,0), matrix=orient),
    ], name='socket.ldr')
    report = snap_report(model, official, 1, 0,
                         moving_feature=hole.feature_id, fixed_feature=stud.feature_id)
    candidate = report['candidates'][0]
    assert candidate['position'] == pytest.approx(jsonable(origin+orient*Vector(0,-height,0)))
    assert np.allclose(candidate['matrix'], orient.rows)
    assert candidate['contact_status'] == 'potential'
    assert candidate['collision']['status'] != 'blocked'
    assert analyze_geometry(apply_snap(model,report),official)['optimistic_component_count'] == 1
    assert official.connections(code) == original  # Native metadata is not rewritten.


@pytest.mark.parametrize('change', ['unknown_part','open','centered','radius','length','flexible','axle'])
def test_deep_socket_projection_does_not_generalize_to_other_holes(official, change):
    model = Model.from_pieces([Piece.place('67329',colour=15)], name='socket.ldr')
    inspection = inspect_connections(model,official)
    item = inspection.occurrences[0]
    feature = next(f for f in item.connections if f.kind is ConnectionKind.PIN_HOLE)
    profile = feature.profile
    section = profile.sections[0]
    if change == 'unknown_part':
        occurrence = replace(item.occurrence,reference='3001.dat',part_code='3001')
        item = replace(item,attribution=replace(item.attribution,occurrence=occurrence))
    elif change == 'open':
        profile = replace(profile,caps=CylindricalCaps.NONE)
    elif change == 'centered':
        profile = replace(profile,centered=True)
    elif change == 'radius':
        section = replace(section,radius=4)
    elif change == 'length':
        section = replace(section,length=20)
    elif change == 'flexible':
        section = replace(section,flexible=True)
    elif change == 'axle':
        section = replace(section,shape=SectionShape.AXLE)
    feature = replace(feature,profile=replace(profile,sections=(section,)))
    inspection = replace(inspection,occurrences=(replace(item,connections=(feature,)),))
    assert query_frames(inspection).occurrences[0].connections == (feature,)


def test_parrot_head_is_connected_and_removed_eye_is_detected(official):
    _, head, diagnostics = build_plan(load_plan(REFERENCE/'head.plan.json'),official)
    assert not diagnostics
    report = analyze_geometry(head,official,contacts='all')
    assert report['occurrence_count'] == 14
    assert report['optimistic_component_count'] == 1
    assert not [d for d in report['diagnostics'] if d['severity']=='error']
    eye = next(p for p in head.pieces if p.reference=='14769p0k.dat')
    moved = replace(eye,position=eye.position+Vector(0,0,20))
    broken = replace(head,objects=[moved if obj is eye else obj for obj in head.objects])
    assert analyze_geometry(broken,official)['optimistic_component_count'] > 1


def test_parrot_preparation_preserves_inventory_and_fixes_overlap(official):
    manifest = json.loads((REFERENCE/'preparation.json').read_text())
    assert hashlib.sha256((REFERENCE/'source.ldr').read_bytes()).hexdigest() == manifest['original_sha256']
    source = parse_source(REFERENCE/'source.ldr')
    _, prepared, diagnostics = build_plan(load_plan(REFERENCE/'parrot.plan.json'),official)
    assert not diagnostics
    def inventory(model):
        return Counter((('3023b.dat' if o.reference=='3023.dat' else o.reference),o.colour.code)
                       for o in model.iter_occurrences())
    assert inventory(prepared) == inventory(source)
    report = analyze_geometry(prepared,official,contacts='all',output_limit=1000)
    assert report['occurrence_count'] == 66
    assert report['complete']
    assert not [d for d in report['diagnostics'] if d['severity']=='error']
    original = analyze_geometry(source,official,contacts='none')
    assert any(d['code']=='assembly.body_overlap' for d in original['diagnostics'])
    assert max(p['correction_distance_ldu'] for p in manifest['parts']) < 0.012

    # These authored sockets are recessed relative to the part's overall box.
    # Check their actual entry frames without overriding the generic checker.
    evidence = json.loads((REFERENCE/'interface-evidence.json').read_text())
    inspection = query_frames(inspect_connections(prepared,official))
    edges = [contact['instances'] for contact in report['contacts']]
    for interface in evidence['interfaces']:
        a,b = interface['prepared_occurrences']
        owners = [inspection.occurrences[i] for i in (a,b)]
        assert [o.occurrence.reference for o in owners] == interface['parts']
        features = [{f.feature_id:f for f in o.connections} for o in owners]
        for match in interface['matches']:
            stud,socket = features[0][match['stud']],features[1][match['socket']]
            assert stud.kind is ConnectionKind.STUD
            assert socket.kind is ConnectionKind.STUD_RECEPTACLE
            assert abs(stud.position-socket.position) < 1e-7
            assert stud.axis.dot(socket.axis) < -0.999999
        edges.append((a,b))
    assert len(components(list(range(66)),edges)) == 1
