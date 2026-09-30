"""Regression coverage for MPD physical boundaries and modular construction."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
from ldraw import inspect_model

from conftest import mpd, ref
from ldraw_tools.builder import build_plan, load_plan
from ldraw_tools.common import ROOT, atomic_write, models_path
from ldraw_tools.document import (assembly_view, dependency_closure, extract_section,
                                  parse_source, physical_context, selected_source, study_model)
from ldraw_tools.geometry import analyze_geometry
from ldraw_tools.validation import validate_file, validate_text


def embedded(body=None, org='Unofficial_Part'):
    body = body or ref(matrix='2 0 0 0 1 0 0 0 1')
    return (mpd(ref('custom.dat')) + mpd(body,'custom.dat').replace('!LDRAW_ORG Model','!LDRAW_ORG '+org))


def errors(diags):
    return {d['code'] for d in diags if d['severity']=='error'}


def test_embedded_dat_counts_once_but_expands_geometry(parts):
    model,diags=validate_text(embedded(),parts)
    assert not errors(diags)
    physical,overlay=physical_context(model,parts)
    assert len(list(physical.iter_occurrences()))==1
    bom=physical.bill_of_materials(parts=overlay)
    assert sum(row.quantity for row in bom)==1
    inspected=inspect_model(physical,overlay)
    assert inspected.complete
    assert inspected.bounds.min.x==-80 and inspected.bounds.max.x==80
    assert 'custom' not in parts.by_code


def test_document_namespaces_do_not_leak(parts):
    a,_=validate_text(embedded(),parts)
    b,_=validate_text(embedded(ref(position='500 0 0')),parts)
    av,ap=physical_context(a,parts);bv,bp=physical_context(b,parts)
    assert inspect_model(av,ap).bounds.min.x==-80
    assert inspect_model(bv,bp).bounds.min.x==460
    assert inspect_model(av,ap).bounds.min.x==-80


def test_primitive_is_not_a_physical_placement(parts):
    _,d=validate_text(embedded(org='Unofficial_Primitive'),parts)
    assert 'assembly.library_internal' in errors(d)


def test_embedded_missing_dependency_is_error(parts):
    _,d=validate_text(embedded(ref('not-found.dat')),parts)
    assert errors(d)


@pytest.mark.parametrize('warp,valid',[(0.005,True),(0.2,False)])
def test_part_quad_uses_spec_angular_tolerance(parts,warp,valid):
    text=embedded(f'4 16 0 0 0 1 0 0 1 {warp} 1 0 0 1')
    _,d=validate_text(text,parts)
    assert ('geometry.nonplanar' not in errors(d)) is valid


def test_physical_matrix_rules_still_apply(parts):
    text=embedded().replace(ref('custom.dat'),ref('custom.dat',matrix='2 0 0 0 1 0 0 0 1'))
    _,d=validate_text(text,parts)
    assert 'assembly.nonrigid' in errors(d)


def test_extract_closure_and_explicit_bfc_repair(parts,tmp_path):
    source=tmp_path/'source.mpd'
    text=embedded('0 BFC CERTIFY CCW\n0 BFC INVERTNEXT\n0 // Original annotation\n'+ref())+mpd(ref(),'unused.ldr')
    atomic_write(source,text)
    before=source.read_bytes()
    copied,manifest=extract_section(source,'main.ldr',namespace='fixture',repair_bfc=True)
    assert source.read_bytes()==before
    assert manifest['source_sha256']==hashlib.sha256(before).hexdigest()
    assert len(manifest['renames'])==2 and 'unused.ldr' not in copied
    assert '0 // Original annotation\r\n0 BFC INVERTNEXT\r\n1 ' in copied
    assert len(manifest['changes'])==1
    assert all(a['author']=='Tests' for a in manifest['attribution'])
    _,d=validate_text(copied,parts)
    assert not errors(d)
    uncorrected,_=extract_section(source,'main.ldr',namespace='fixture')
    _,d=validate_text(uncorrected,parts)
    assert 'bfc.invertnext' in errors(d)


def test_rotation_repair_is_bounded_and_opt_in(parts,tmp_path):
    source=tmp_path/'source.mpd'
    atomic_write(source,mpd(ref(matrix='0.707 0 0.707 0 1 0 -0.707 0 0.707')))
    raw,_=extract_section(source,'main.ldr',namespace='raw')
    _,d=validate_text(raw,parts);assert 'assembly.nonrigid' in errors(d)
    fixed,manifest=extract_section(source,'main.ldr',namespace='fixed',normalize_rotations=True)
    _,d=validate_text(fixed,parts);assert not errors(d)
    assert manifest['changes'][0]['kind']=='normalize_rounded_rotation'
    atomic_write(source,mpd(ref(matrix='2 0 0 0 1 0 0 0 1')))
    still_bad,manifest=extract_section(source,'main.ldr',namespace='bad',normalize_rotations=True)
    _,d=validate_text(still_bad,parts);assert 'assembly.nonrigid' in errors(d)
    assert not manifest['changes']


def test_selected_section_retains_original_lines(parts,tmp_path):
    source=tmp_path/'source.mpd'
    atomic_write(source,mpd(ref('child.ldr'))+mpd(ref(),'child.ldr')+mpd(ref('absent.dat'),'unused.ldr'))
    selected,line_map=selected_source(source,'child.ldr',4)
    assert 'absent.dat' not in selected
    model,d=validate_file(source,parts,section='child.ldr',colour=4)
    assert not errors(d)
    occ=list(assembly_view(model).iter_occurrences())[0]
    assert source.read_text().splitlines()[occ.source_line-1]==ref()


def plan_section(name,steps,**extra):
    return dict(name=name,description=name,steps=steps,**extra)


def placement(id,ref='3001.dat',**kw):
    return dict(id=id,ref=ref,colour=4,**kw)


def test_anchor_composition_in_rotated_parent(parts):
    plan=dict(version=1,author='Tests',sections=[
        plan_section('main.ldr',[[placement('fixed','support.ldr',at=[100,0,0],yaw=90),
                                 placement('moving','moving.ldr',attach=dict(to='fixed',anchor='seat',using='base'))]]),
        plan_section('support.ldr',[[placement('brick',at=[0,0,0])]],anchors={'seat':dict(at=[20,-24,0],matrix=[[0,0,1],[0,1,0],[-1,0,0]])}),
        plan_section('moving.ldr',[[placement('brick',at=[0,0,0])]],anchors={'base':dict(at=[0,8,0])})])
    _,model,d=build_plan(plan,parts)
    assert not errors(d)
    piece=model.pieces[1]
    assert np.allclose([piece.position.x,piece.position.y,piece.position.z],[100,-32,-20])
    assert np.allclose(piece.matrix.rows,[[-1,0,0],[0,1,0],[0,0,-1]])
    plan['sections'][0]['steps'][0][1]['attach']['anchor']='unknown'
    with pytest.raises(ValueError,match='Unknown module anchor'):build_plan(plan,parts)


def test_includes_repeats_and_authorship(parts,tmp_path):
    child=dict(version=1,author='Module author',sections=[plan_section('unit.ldr',[[placement('brick',at=[0,0,0])]])])
    root=dict(version=1,author='Scene author',includes=['unit.json'],sections=[plan_section('main.ldr',[[placement('unit','unit.ldr',at=[0,0,0],repeat=dict(count=12,step=[100,0,0]))]])])
    (tmp_path/'unit.json').write_text(json.dumps(child));(tmp_path/'scene.json').write_text(json.dumps(root))
    loaded=load_plan(tmp_path/'scene.json')
    text,model,d=build_plan(loaded,parts)
    assert not errors(d)
    assert len(list(model.iter_occurrences()))==12
    assert model.submodels['unit.ldr'].author=='Module author'
    assert '// unit-11:' in text
    report=analyze_geometry(model,parts,contacts='none',output_limit=3,offset=5)
    assert [r['index'] for r in report['instances']]==[5,6,7]
    assert report['instances_truncated'] and report['occurrence_count']==12
    assert not report['contacts_checked'] and report['optimistic_components'] is None
    child['includes']=['scene.json'];(tmp_path/'unit.json').write_text(json.dumps(child))
    with pytest.raises(ValueError,match='cycle'):load_plan(tmp_path/'scene.json')


def test_asset_merge_retains_definitions_and_rejects_collisions(parts,tmp_path):
    asset=tmp_path/'asset.mpd';atomic_write(asset,embedded())
    p=dict(version=1,author='Scene author',assets=[str(asset)],sections=[plan_section('scene.ldr',[[placement('asset','main.ldr',at=[100,0,0])]])])
    text,model,d=build_plan(p,parts)
    assert not errors(d)
    assert '0 Author: Tests' in text and 'Unofficial_Part' in text
    physical,overlay=physical_context(model,parts)
    assert inspect_model(physical,overlay).bounds.min.x==20
    p['sections'][0]['name']='main.ldr'
    with pytest.raises(ValueError,match='Duplicate section'):build_plan(p,parts)


def test_auto_contacts_does_not_invent_connectivity(parts):
    plan=dict(version=1,author='Tests',sections=[plan_section('main.ldr',[[placement('brick',at=[0,0,0],repeat=dict(count=501,step=[100,0,0]))]])])
    _,model,d=build_plan(plan,parts)
    report=analyze_geometry(model,parts,detail='summary')
    assert report['occurrence_count']==501 and not report['contacts_checked']
    assert not report['instances'] and report['optimistic_component_count'] is None
    assert 'coverage.contacts_skipped' in {d['code'] for d in report['diagnostics']}


def test_original_complex_example(official):
    plan=load_plan(ROOT/'examples/modular-street/scene.plan.json')
    text,model,d=build_plan(plan,official)
    assert not errors(d)
    assert text.encode()==(ROOT/'examples/modular-street/copper-lane.mpd').read_bytes()
    report=analyze_geometry(model,official,detail='summary',contacts='none')
    assert report['complete'] and not errors(report['diagnostics'])
    assert report['occurrence_count']>1500
    assert len(model.submodels)>=9


def test_bookshop_physical_boundary_integration(official):
    source=models_path()/'10270-1.mpd'
    if not source.exists():pytest.skip('Annotated Bookshop reference unavailable')
    model=parse_source(source)
    assert len(model.submodels)+1==42
    assert len(dependency_closure(model))==39
    assert len(list(assembly_view(model).iter_occurrences()))==2456


def test_renderer_materializes_embedded_parts(parts,tmp_path):
    from ldraw_tools.external import cad_source
    source=tmp_path/'source.mpd';atomic_write(source,embedded())
    original=source.read_bytes()
    temporary=tmp_path/'render';temporary.mkdir()
    ready,library,names=cad_source(source,parts.path.parent,temporary)
    assert source.read_bytes()==original
    assert len(names)==1 and list(names.values())==['custom.dat']
    code=next(iter(names))
    assert '0 FILE custom.dat' not in ready.read_text()
    assert code in ready.read_text()
    assert (library/'parts'/code).exists()
    assert (library/'parts'/'3001.dat').is_symlink()
    assert not (parts.path.parent/'parts'/code).exists()
    assert 'Author: Tests' in (library/'parts'/code).read_text()


def test_bom_comparison_does_not_hide_missing_embedded_parts(parts,tmp_path):
    from ldraw_tools.external import compare_bom
    model,d=validate_text(embedded(),parts)
    csv=tmp_path/'bom.csv'
    csv.write_text('Part ID,Color Code,Quantity\n')
    report=compare_bom(model,parts,csv)
    assert not report['matches'] and report['physical_placements']==1
    assert report['differences']==[dict(part='custom.dat',colour=4,python=1,leocad=0)]
    csv.write_text('Part ID,Color Code,Quantity\nCUSTOM.DAT,4,1\n')
    assert compare_bom(model,parts,csv)['matches']


def test_case_insensitive_library_shadow_is_rejected(parts):
    _,d=validate_text(mpd(ref('3001.DAT'))+mpd(ref('3003.dat'),'3001.DAT'),parts)
    assert 'mpd.library_shadow' in errors(d)


def test_embedded_part_can_be_selected_as_cad_root(parts,tmp_path):
    from ldraw_tools.external import cad_source
    source=tmp_path/'part.mpd'
    atomic_write(source,mpd(ref(),'custom.dat').replace('!LDRAW_ORG Model','!LDRAW_ORG Unofficial_Part'))
    temporary=tmp_path/'render';temporary.mkdir()
    ready,library,names=cad_source(source,parts.path.parent,temporary)
    assert ready.read_text().startswith('0 FILE nova-cad-root.ldr')
    assert next(iter(names)) in ready.read_text()


def test_root_license_does_not_relicense_included_modules(parts,tmp_path):
    child=dict(version=1,author='Independent author',sections=[plan_section('child.ldr',[[placement('brick',at=[0,0,0])]])])
    root=dict(version=1,author='Scene author',license='CC0',includes=['child.json'],sections=[plan_section('main.ldr',[[placement('child','child.ldr',at=[0,0,0])]])])
    (tmp_path/'child.json').write_text(json.dumps(child));(tmp_path/'root.json').write_text(json.dumps(root))
    _,model,d=build_plan(load_plan(tmp_path/'root.json'),parts)
    assert not errors(d)
    assert model.license=='CC0'
    assert model.submodels['child.ldr'].author=='Independent author'
    assert model.submodels['child.ldr'].license is None
