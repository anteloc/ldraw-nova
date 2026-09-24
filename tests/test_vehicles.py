"""Vehicle regressions: real interfaces, wheel space and editable plans."""
import copy
import hashlib
import json

import numpy as np
import pytest
from ldraw import Piece, inspect_model

from ldraw_tools.builder import build_plan, rotation
from ldraw_tools.common import ROOT, jsonable
from ldraw_tools.connection_adapter import connection_contacts, query_frames
from ldraw_tools.examples import search_examples
from ldraw_tools.geometry import analyze_geometry
from ldraw_tools.vehicle_review import review_vehicle
from ldraw_tools.vehicles import DESIGNS, WHEEL_PACKS, axle, vehicle_plan, wheel_report
from ldraw_tools.vehicle_details import DETAILS, detail_plan


def errors(diagnostics):
    return [d for d in diagnostics if d['severity']=='error']


@pytest.mark.parametrize('name', DESIGNS)
def test_vehicle_plans_resolve_without_body_collisions_or_wheel_intrusions(official, name):
    plan = vehicle_plan(name)
    before = copy.deepcopy(plan)
    _, model, diagnostics = build_plan(plan, official)
    geometry = analyze_geometry(model, official, detail='full', output_limit=500)
    profile = DESIGNS[name].get('profile','road')
    report = review_vehicle(model, official, profile=profile)
    assert plan == before
    assert not errors(diagnostics+geometry['diagnostics']+report['diagnostics'])
    assert geometry['complete'] and geometry['contacts_checked']
    if profile in {'road','motorcycle'}:
        assert report['wheel_count'] == (4 if profile=='road' else 2) and report['axle_count'] == 2
        assert report['wheelbase_ldu'] == (DESIGNS[name]['wheelbase']*20 if profile=='road' else 107)
        assert not report['wheel_space_candidates']
        assert not report['unreviewed_wheels']
    else:
        assert report['coverage']['wheel_review']=='not_applicable'
        assert all(report['family_parts'].values())
    assert report['physical_validity'] == 'not_proven'
    assert all(np.linalg.det(np.array(o.matrix.rows)) == pytest.approx(1) for o in model.iter_occurrences())
    # Wheel-pin and round lamp metadata is incomplete; the actual studded
    # structure must nevertheless be one connected group, with bonded seams.
    occurrences=list(model.iter_occurrences())
    if profile!='motorcycle':  # Dedicated frame/fairing snap metadata is absent.
        structural={i for i,o in enumerate(occurrences) if o.part_code not in {'6014b','6015','6141'}}
        assert any(structural <= set(group) for group in geometry['optimistic_components'])


@pytest.mark.parametrize('name', WHEEL_PACKS)
def test_wheel_recipes_match_official_shortcut_offsets_and_measured_road(official, name):
    p = WHEEL_PACKS[name]
    shortcut = official.part(code=p['source'].removesuffix('.dat'))
    refs = {o.reference:o for o in shortcut.objects if isinstance(o, Piece)}
    assert jsonable(refs[p['tyre']+'.dat'].position) == [0,0,p['tyre_offset']]
    report = wheel_report(official, name)[name]
    _, model, ds = build_plan(axle(name).plan(), official)
    assert not errors(ds)
    tyres = [o for o in inspect_model(model,official).occurrences if o.occurrence.part_code==p['tyre']]
    assert len(tyres) == 2
    assert all(t.bounds.max.y == pytest.approx(0, abs=.001) for t in tyres)
    assert report['track_ldu'] == pytest.approx(abs(tyres[0].occurrence.position.x-tyres[1].occurrence.position.x))


def test_wide_rim_uses_its_hole_axis_without_mutating_geometry(official):
    _, model, _ = build_plan(axle().plan(), official)
    inspection = inspect_model(model, official)
    original = jsonable(inspection.occurrences[1].connections)
    adjusted = query_frames(inspection)
    rim = next(c for c in adjusted.occurrences[1].connections if str(c.kind)=='rim_seat')
    assert np.allclose(np.abs(jsonable(rim.axis)), [1,0,0])
    assert any({c.first_occurrence.index,c.second_occurrence.index} == {1,2}
               for c in connection_contacts(inspection))
    assert jsonable(inspection.occurrences[1].connections) == original


@pytest.mark.parametrize('mutation,code', [
    ('axis','vehicle.wheel_axis'), ('lift','vehicle.ground_contact'),
    ('axle','vehicle.axle_pair'), ('rim','vehicle.rim_fit'),
    ('asymmetry','vehicle.axle_symmetry'),
])
def test_vehicle_review_catches_actual_wheel_failures(official, mutation, code):
    plan = vehicle_plan('grand-tourer')
    wheel = next(s for s in plan['sections'] if s['name']=='axle-touring.ldr')['steps'][0]
    tyre = next(p for p in wheel if p['id']=='left-tyre')
    if mutation=='axis':
        tyre.pop('yaw');tyre['matrix']=jsonable(rotation('x',90))
    elif mutation=='lift':tyre['at'][1]-=8
    elif mutation=='axle':tyre['at'][2]+=20
    elif mutation=='rim':next(p for p in wheel if p['id']=='left-rim')['at'][0]-=8
    else:tyre['at'][0]-=8
    _, model, _ = build_plan(plan, official)
    report = review_vehicle(model, official)
    assert not report['checks_passed']
    assert code in {d['code'] for d in report['diagnostics']}


def test_wheel_space_is_a_review_candidate_and_reports_are_bounded(official):
    plan = vehicle_plan('grand-tourer')
    plan['sections'][0]['steps'][0].append(dict(id='obstruction', ref='3001.dat', colour=4, at=[46,-30,-100]))
    _, model, _ = build_plan(plan, official)
    report = review_vehicle(model, official, limit=1)
    assert report['wheel_space_candidates']
    assert report['truncated'] and len(report['wheels'])==1
    assert any(d['code']=='vehicle.wheel_space' and d['severity']=='warning' for d in report['diagnostics'])
    with pytest.raises(ValueError, match='budget'):
        review_vehicle(model, official, instance_limit=1)
    with pytest.raises(ValueError, match='finite'):
        review_vehicle(model, official, ground_y=float('nan'))


def test_no_wheels_is_not_a_successful_vehicle_review(official):
    from ldraw_tools.architecture import Module
    m=Module('box','Not a vehicle');m.add('3001',4,h=24)
    _,model,_=build_plan(m.plan(),official)
    assert not review_vehicle(model,official)['checks_passed']


def test_vehicle_palette_and_family_errors_are_explicit():
    with pytest.raises(ValueError, match='Unknown vehicle'):vehicle_plan('imaginary')
    with pytest.raises(ValueError, match='vehicle palette'):vehicle_plan('pickup','botanical-bookshop')
    with pytest.raises(ValueError, match='scale'):search_examples(family='vehicle',scale='microscale')
    with pytest.raises(ValueError, match='Unknown vehicle detail'):detail_plan('imaginary')
    with pytest.raises(ValueError, match='vehicle palette'):detail_plan('driver-cockpit','botanical-bookshop')


def test_unknown_wheels_and_technic_parts_are_reported(official):
    plan=vehicle_plan('pickup')
    plan['sections'][0]['steps'][0].extend([
        dict(id='unknown-tyre',ref='11209.dat',colour=0,at=[200,-100,0]),
        dict(id='technic',ref='3700.dat',colour=0,at=[200,-150,0]),
    ])
    _,model,_=build_plan(plan,official)
    report=review_vehicle(model,official)
    assert report['unreviewed_wheels'][0]['ref']=='11209.dat'
    assert {'vehicle.unreviewed_wheels','vehicle.technic_part'} <= {d['code'] for d in report['diagnostics']}
    assert not report['checks_passed']


def test_cli_exports_plan_and_brief_and_protects_both_paths(official, tmp_path, monkeypatch):
    from ldraw_tools import cli
    monkeypatch.setattr(cli,'get_parts',lambda *a,**kw:official)
    target=tmp_path/'pickup.plan.json'
    args=cli.parser().parse_args(['vehicle','plan','pickup','--output',str(target)])
    report,status=cli.run(args)
    assert status==0 and json.loads(target.read_text())==vehicle_plan('pickup')
    assert json.loads((tmp_path/'pickup.plan.brief.json').read_text())['wheel_pack']=='touring'
    target.unlink()
    with pytest.raises(ValueError,match='Plan/brief exists'):cli.run(args)
    args.force=True
    assert cli.run(args)[1]==0


def test_saved_examples_are_reproducible_and_reports_match_current_revision(official):
    atlas=ROOT/'examples/vehicle-atlas'
    catalog=json.loads((atlas/'catalog.json').read_text())
    assert {row['key'] for row in catalog['examples']}==set(DESIGNS)
    assert {row['key'] for row in catalog['details']}==set(DETAILS)
    for name in [*DESIGNS,*DETAILS]:
        is_detail=name in DETAILS
        folder=atlas/'details'/name if is_detail else atlas/name
        plan=detail_plan(name) if is_detail else vehicle_plan(name)
        assert json.loads((folder/'scene.plan.json').read_text())==plan
        text,_,ds=build_plan(plan,official)
        assert not errors(ds) and text.encode()==(folder/(name+'.mpd')).read_bytes()
        sha=hashlib.sha256(text.encode()).hexdigest()
        for report in ['validation','bom','bom-comparison','render-manifest','visual-review']+([] if is_detail else ['vehicle-check']):
            assert json.loads((folder/(report+'.json')).read_text())['source_sha256']==sha
    assert search_examples('pickup',family='vehicle')['total']==1
    assert search_examples(family='vehicle',limit=1)['truncated']
    assert search_examples('cockpit',family='vehicle',details=True)['total']==2


@pytest.mark.parametrize('name', DETAILS)
def test_vehicle_fitting_interfaces_resolve_and_are_connected(official, name):
    _,model,diagnostics=build_plan(detail_plan(name),official)
    geometry=analyze_geometry(model,official,detail='full')
    assert not errors(diagnostics+geometry['diagnostics'])
    assert geometry['complete'] and geometry['contacts_checked']
    assert geometry['optimistic_component_count']==(3 if name=='navigation-lights' else 1)
    if name=='driver-cockpit':
        refs={o.part_code for o in model.iter_occurrences()}
        assert {'4079','3829c01','3069bp25'} <= refs
    if name=='jet-engine-pod':
        bounds=inspect_model(model,official).bounds
        assert bounds.min.y==pytest.approx(-4)
        assert bounds.max.y==pytest.approx(46)


@pytest.mark.parametrize('name,part,delta,code', [
    ('touring-motorcycle','85983.dat',[0,8,0],'vehicle.assembly_fit'),
    ('touring-motorcycle','50861.dat',[20,0,0],'vehicle.motorcycle_wheel'),
    ('courier-jet','87612.dat',[0,0,20],'vehicle.assembly_fit'),
    ('courier-jet','30355.dat',[-20,0,0],'vehicle.family_symmetry'),
    ('harbour-launch','2551.dat',None,'vehicle.family_part'),
])
def test_family_review_detects_missing_and_misaligned_dedicated_parts(official,name,part,delta,code):
    plan=vehicle_plan(name)
    for section in plan['sections']:
        found=False
        for step in section['steps']:
            placement=next((p for p in step if p['ref']==part),None)
            if placement:
                if delta is None:step.remove(placement)
                else:placement['at']=[a+b for a,b in zip(placement['at'],delta)]
                found=True
                break
        if found:break
    _,model,_=build_plan(plan,official)
    report=review_vehicle(model,official,profile=DESIGNS[name]['profile'])
    assert not report['checks_passed']
    assert code in {d['code'] for d in report['diagnostics']}


def test_cli_vehicle_details_and_profile_selection(official,tmp_path,monkeypatch):
    from ldraw_tools import cli
    monkeypatch.setattr(cli,'get_parts',lambda *a,**kw:official)
    target=tmp_path/'cockpit.json'
    args=cli.parser().parse_args(['vehicle','details','driver-cockpit','--output',str(target)])
    result,status=cli.run(args)
    assert status==0 and json.loads(target.read_text())==detail_plan('driver-cockpit')
    assert result['recipe']['parts']==DETAILS['driver-cockpit']['parts']
    with pytest.raises(ValueError,match='exists'):cli.run(args)
    args.force=True
    assert cli.run(args)[1]==0
    text,_,_=build_plan(vehicle_plan('harbour-launch'),official)
    boat=tmp_path/'boat.mpd';boat.write_text(text)
    parsed=cli.parser().parse_args(['vehicle','check',str(boat),'--profile','watercraft'])
    report,status=cli.run(parsed)
    assert status==0 and report['profile']=='watercraft'
    parsed.profile='road'
    assert cli.run(parsed)[1]==1
