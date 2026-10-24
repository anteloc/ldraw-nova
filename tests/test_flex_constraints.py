"""Constraint authoring and repairs must be independent of a particular model."""
import importlib.util
from functools import lru_cache

import numpy as np
import pytest

pytest.importorskip('lsynth_nova', reason='Install the optional engine with ./setup.sh --with-lsynth')

from ldraw_tools import flex
from ldraw_tools.cli import parser, run
from ldraw_tools.common import ROOT
from ldraw_tools.flex_authoring import Endpoint, Waypoint, band, document, hose, marker_matrix, placement
from ldraw_tools.flex_constraints import check_text
from ldraw_tools.flex_knowledge import family, guide
from ldraw_tools.flex_review import check_asset, closest_segments, shape


@lru_cache
def lab():
    spec=importlib.util.spec_from_file_location('flex_constraint_lab',ROOT/'examples/flex/constraint-lab/generate.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def codes(report):
    return {d['code'] for d in report['diagnostics']}


def straight(y=0, name='line'):
    return hose(Endpoint((0,y,0),(1,0,0),22), Endpoint((120,y,0),(-1,0,0),22), name=name)


def built(tmp_path, official, source):
    src, dst = tmp_path/'constraints.ldr', tmp_path/'asset.mpd'
    src.write_bytes(document(source).encode())
    flex.build(src,dst,official)
    return src,dst


def test_every_installed_method_and_product_has_specific_guidance():
    cfg, _, _ = flex.engine()
    for t in cfg.hose_types+cfg.band_types:
        g = guide(t.type)
        assert g['family'] == family(t.type)
        assert g['design'] and g['inspect'] and g['constraints']
        assert (ROOT/g['example']).exists()
    for p in cfg.products:
        assert guide(p.nickname)['method'] == p.method
    with pytest.raises(ValueError, match='Unknown exact'):
        guide('PLI_TECHNIC_AXLE_FLEXIBLE_7_typo')


@pytest.mark.parametrize('direction', [(1,0,0),(0,1,0),(0,0,-1),(1,2,3),(-4,1,2)])
def test_marker_frames_are_proper_and_follow_negative_y(direction):
    r = marker_matrix(direction)
    assert np.allclose(r.T@r,np.eye(3))
    assert np.linalg.det(r)==pytest.approx(1)
    assert np.allclose(-r[:,1], np.array(direction)/np.linalg.norm(direction))


def test_roll_and_local_port_transform():
    r = marker_matrix((1,0,0),up=(0,0,1))
    assert np.allclose(r[:,2],(0,0,1))
    e = Endpoint.on_part((10,20,30),r,(0,-10,0),(0,-1,0),lead=22)
    assert np.allclose(e.at,(20,20,30)) and np.allclose(e.outward,(1,0,0))
    with pytest.raises(ValueError,match='parallel'):
        marker_matrix((1,0,0),up=(1,0,0))
    with pytest.raises(ValueError,match='proper'):
        Endpoint.on_part((0,0,0),np.diag([-1,1,1]),(0,0,0),(1,0,0))


def test_endpoint_outward_direction_is_reversed_exactly_once():
    report = check_text(straight())
    assert report['checks_passed'] and not report['diagnostics']
    frames = report['routes'][0]['frames']
    assert [f['at'][0] for f in frames] == [0,22,98,120]
    assert all(f['direction']==[1,0,0] for f in frames)


def test_author_rejects_duplicate_zero_and_cusp_constraints():
    with pytest.raises(ValueError,match='coincide'):
        hose(Endpoint((0,0,0),(1,0,0)),Endpoint((0,0,0),(-1,0,0)))
    with pytest.raises(ValueError,match='nonzero'):
        Endpoint((0,0,0),(0,0,0))
    with pytest.raises(ValueError,match='nonzero'):
        hose(Endpoint((0,0,0),(1,0,0)),Endpoint((0,0,0),(1,0,0)),via=[(20,0,0)])


def test_errors_identify_source_line_and_repair():
    s = '0 SYNTH BEGIN TECHNIC_PNEUMATIC_HOSE_BEVELED 4\n' + placement('LS01.dat',(0,0,0))+'\n'
    s += placement('LS01.dat',(0,0,0))+'\n0 SYNTH END\n'
    r = check_text(s)
    assert 'flex.coincident_markers' in codes(r) and not r['checks_passed']
    assert all(d.get('line') and d['action'] for d in r['diagnostics'])
    s = s.replace('1 0 0 0 1 0 0 0 1 LS01','2 0 0 0 1 0 0 0 1 LS01',1)
    assert 'flex.constraint_transform' in codes(check_text(s))


def test_hidden_and_unrecognized_constraints_cannot_silently_lose_a_route():
    s = '0 SYNTH BEGIN TECHNIC_PNEUMATIC_HOSE_BEVELED 4\n0 '+placement('LS01.dat',(0,0,0))+'\n'
    s += placement('3001.dat',(100,0,0))+'\n0 SYNTH END\n'
    r = check_text(s)
    assert {'flex.hidden_constraint','flex.not_a_constraint','flex.marker_count'} <= codes(r)
    assert not r['checks_passed']


def test_band_plane_tangent_and_ownership():
    a=placement('4185.dat',(0,0,0))
    good=band([a,placement('4185.dat',(120,0,0))])
    assert check_text(good)['checks_passed']
    assert 'flex.wheel_plane' in codes(check_text(band([a,placement('4185.dat',(120,0,1))])))
    assert 'flex.no_tangent' in codes(check_text(band([a,'0 SYNTH OUTSIDE',placement('4185.dat',(40,0,0))])))
    assert 'flex.duplicate_wheel' in codes(check_text(band([a,placement('4185.dat',(120,0,0)),a])))
    assert check_text(band([a,placement('4185.dat',(120,0,0))],hide=True))['routes'][0]['hidden_wheels']


def test_wheel_plane_respects_nonstandard_library_axes():
    a=placement('2983.dat',(0,0,0))
    assert check_text(band([a,placement('2983.dat',(120,0,0))]))['checks_passed']
    assert 'flex.wheel_plane' in codes(check_text(band([a,placement('2983.dat',(120,1,0))])))


@pytest.mark.parametrize('middle,tail,second,passes', [
    (['0 SYNTH CROSS'],[],True,False),
    ([],['0 SYNTH CROSS'],True,False),
    ([],['0 SYNTH OUTSIDE'],True,False),
    (['0 SYNTH CROSS','0 SYNTH CROSS'],[],True,True),
    ([],[],False,False),
])
def test_band_control_checks_match_actual_engine(tmp_path,official,middle,tail,second,passes):
    rows=[placement('4185.dat',(0,0,0)),*middle]
    if second: rows.append(placement('4185.dat',(40,0,0)))
    source=band([*rows,*tail])
    report=check_text(source)
    assert ('flex.no_tangent' not in codes(report)) == passes
    if passes:
        built(tmp_path,official,source)
    else:
        with pytest.raises(ValueError,match='no tangent'):
            built(tmp_path,official,source)


@pytest.mark.parametrize('a,b,d', [
    ([(0,0,0),(10,0,0)],[(5,-5,0),(5,5,0)],0),
    ([(0,0,0),(10,0,0)],[(5,-5,3),(5,5,3)],3),
    ([(0,0,0),(10,0,0)],[(2,4,0),(8,4,0)],4),
    ([(0,0,0),(10,0,0)],[(20,0,0),(30,0,0)],10),
])
def test_segment_distance_catches_crossings_between_samples(a,b,d):
    assert closest_segments(a,b)[0]==pytest.approx(d)
    assert closest_segments(b,a)[0]==pytest.approx(d)


def test_self_crossing_and_curvature_measurements():
    p=[(-20,-20,0),(20,20,0),(-20,20,0),(20,-20,0)]
    assert closest_segments(p,p,self_gap=10)[0]==pytest.approx(0)
    theta=np.linspace(0,np.pi,100)
    row,_,_=shape(np.column_stack((30*np.cos(theta),30*np.sin(theta),np.zeros(100))))
    assert row['minimum_sampled_radius_ldu']==pytest.approx(30,abs=0.3)


def test_actual_synthesis_and_stale_evidence(tmp_path,official):
    src,dst=built(tmp_path,official,straight())
    r=check_asset(src,dst,min_radius=15,tube_radius=5)
    assert r['checks_passed'],r['diagnostics']
    assert r['measurements'][0]['endpoint_check'].startswith('generated sleeves')
    src.write_text(src.read_text()+'0 changed\n')
    with pytest.raises(ValueError,match='Stale'):
        check_asset(src,dst)


@pytest.mark.parametrize('method',['ELECTRIC_CABLE','ELECTRIC_NXT_CABLE','TECHNIC_FLEX-SYSTEM_HOSE','TECHNIC_PNEUMATIC_HOSE'])
def test_single_stretched_segment_is_a_valid_measurable_route(tmp_path,official,method):
    source=hose(Endpoint((0,0,0),(1,0,0),up=(0,0,1)),Endpoint((400,0,0),(-1,0,0),up=(0,0,1)),method=method)
    src,dst=built(tmp_path,official,source)
    r=check_asset(src,dst,min_radius=15)
    assert r['checks_passed']
    assert r['measurements'][0]['polyline_length_ldu']==pytest.approx(400,abs=0.01)


def test_asset_geometry_is_not_accepted_by_only_its_filename(tmp_path,official):
    src,dst=built(tmp_path,official,straight())
    dst.write_text(dst.read_text()+'0 edited\n')
    with pytest.raises(ValueError,match='model_sha256'):
        check_asset(src,dst)


def test_intersections_at_ends_are_not_exempted(tmp_path,official):
    src,dst=built(tmp_path,official,straight()+straight(y=5,name='nearby'))
    r=check_asset(src,dst,min_separation=10)
    assert not r['checks_passed'] and 'flex.separation' in codes(r)
    scoped=check_asset(src,dst,min_separation=10,block=1)
    assert len(scoped['measurements'])==1 and 'flex.separation' in codes(scoped)


def test_connector_selection_uses_real_part_frames(official):
    e=Endpoint.from_feature(official,'4694c01-f1','4694c04@R0/4694@R0/snap_cyl@L10:I0',
                           at=(100,0,0),lead=22)
    assert np.allclose(e.at,(110,26,6)) and np.allclose(e.outward,(1,0,0))
    with pytest.raises(ValueError,match='connector'):
        Endpoint.from_feature(official,'4694c01-f1','invented')


def test_obstacle_candidates_include_fitting_end_regions(tmp_path,official):
    src,dst=built(tmp_path,official,straight())
    obstacle=tmp_path/'obstacle.ldr'
    obstacle.write_text('0 Obstacle\n'+placement('3001.dat',(10,-10,0))+'\n')
    r=check_asset(src,dst,obstacles=obstacle,parts=official,tube_radius=5)
    assert 'flex.obstacle_bounds' in codes(r)
    assert r['obstacle_candidates'][0]['part']=='3001.dat'
    assert r['settings']['obstacles_sha256']


def test_length_and_short_curve_limits_are_explicit(tmp_path,official):
    src,dst=built(tmp_path,official,straight())
    r=check_asset(src,dst,length=10,length_tolerance=1)
    assert 'flex.length' in codes(r)
    with pytest.raises(ValueError,match='finite'):
        check_asset(src,dst,min_radius=float('nan'))
    with pytest.raises(ValueError,match='block'):
        check_asset(src,dst,block=2)


def test_links_are_addressed_by_section_and_piece_range(tmp_path,official):
    route=band([placement('4019.dat',(-60,0,0)),placement('4019.dat',(60,0,0))],method='TECHNIC_CHAIN_LINK')
    src,dst=built(tmp_path,official,route)
    r=check_asset(src,dst)
    assert r['checks_passed'] and r['measurements'][0]['generated_segments']==24
    assert r['measurements'][0]['representation']=='links'
    row=r['measurements'][0]
    assert row['closure_check'].startswith('not_measured')
    assert row['placement_origin_bounds_ldu']['min'][0]<row['placement_origin_bounds_ldu']['max'][0]
    assert not {'closure_origin_gap_ldu','polyline_length_ldu','minimum_sampled_radius_ldu'} & row.keys()
    with pytest.raises(ValueError,match='Hose geometry limits'):
        check_asset(src,dst,min_radius=15)


def test_repeated_geometry_checks_do_not_pollute_source_diagnostics(tmp_path,official):
    from ldraw_tools.flex_constraints import check
    src,dst=built(tmp_path,official,straight())
    source_report=check(src)
    bad=check_asset(src,dst,source_report=source_report,length=1)
    assert not bad['checks_passed']
    assert source_report['checks_passed'] and not source_report['diagnostics']
    assert check_asset(src,dst,source_report=source_report)['checks_passed']
    src.write_text(src.read_text()+'0 edited source\n')
    with pytest.raises(ValueError,match='Stale source report'):
        check_asset(src,dst,source_report=source_report)


def test_existing_press_is_a_geometry_regression(tmp_path,official):
    s=ROOT/'examples/flex/pneumatic-press/hoses.ldr'
    dst=tmp_path/'press.mpd'
    flex.build(s,dst,official)
    r=check_asset(s,dst,min_radius=15,min_separation=10)
    assert r['checks_passed'],r['diagnostics']
    assert len(r['measurements'])==3


def test_cli_authors_then_checks_without_requiring_a_parts_library(tmp_path,monkeypatch):
    monkeypatch.delenv('LDRAW_DIR',raising=False)
    monkeypatch.delenv('LDRAWDIR',raising=False)
    out=tmp_path/'hose.ldr'
    args=parser().parse_args(['flex','hose','--start','0','0','0','--start-direction','1','0','0',
        '--end','120','0','0','--end-direction','-1','0','0','--lead','22','--output',str(out)])
    report,status=run(args)
    assert status==0 and out.exists()
    assert run(parser().parse_args(['flex','check',str(out)]))[1]==0
    with pytest.raises(ValueError,match='exists'):
        run(args)


@pytest.mark.parametrize('method',[t['name'].lower() for t in guide()['methods']])
def test_every_installed_method_synthesis_fixture(tmp_path,official,method):
    source=dict(lab().family_cases())[method]
    assert check_text(source)['checks_passed']
    if method=='brick_arc':
        # Preserve the strict rigid rule even when the upstream renderer emits a reflection.
        with pytest.raises(ValueError,match='assembly.nonrigid'):
            built(tmp_path,official,source)
        return
    src,dst=built(tmp_path,official,source)
    report=check_asset(src,dst)
    assert report['checks_passed'],report['diagnostics']
    assert len(report['measurements'])==1


@pytest.mark.parametrize('name',[n for n,_ in lab().cases()])
def test_actual_constraint_patterns_and_a_known_failure(tmp_path,official,name):
    src,dst=built(tmp_path,official,dict(lab().cases())[name])
    r=check_asset(src,dst,min_radius=15,tube_radius=5)
    assert r['checks_passed'] == (name!='corner-6'),r['diagnostics']
    if name=='corner-6': assert 'flex.bend' in codes(r)


def test_bend_evidence_survives_rigid_rotation_and_translation(tmp_path,official):
    from ldraw_tools.builder import rotation
    from lsynth_nova.config import parse_type1
    source=lab().corner(32)
    src,dst=built(tmp_path,official,source)
    baseline=check_asset(src,dst,min_radius=15)['measurements'][0]
    r=np.array(rotation('y',37).rows) @ np.array(rotation('z',23).rows)
    shift=np.array([123,-87,234])
    lines=[]
    for line in source.splitlines():
        p=parse_type1(line)
        lines.append(placement(p.type,r@p.offset+shift,r@p.orient,4) if p else line)
    moved=tmp_path/'moved';moved.mkdir()
    src,dst=built(moved,official,'\n'.join(lines)+'\n')
    report=check_asset(src,dst,min_radius=15)
    assert report['checks_passed'],report['diagnostics']
    assert report['measurements'][0]['minimum_sampled_radius_ldu']==pytest.approx(baseline['minimum_sampled_radius_ldu'],abs=.1)
