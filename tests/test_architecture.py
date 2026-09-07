"""Atlas construction, attachment and delivery regressions against real geometry."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from ldraw_tools.architecture import Module, room, porch, gable, attach_roof, slab
from ldraw_tools.builder import build_plan, load_plan
from ldraw_tools.common import ROOT
from ldraw_tools.geometry import analyze_geometry, profiles
from ldraw_tools.examples import search_examples

ATLAS=ROOT/'examples/building-atlas'
spec=importlib.util.spec_from_file_location('atlas_generator',ATLAS/'generate.py')
atlas=importlib.util.module_from_spec(spec);spec.loader.exec_module(atlas)


def errors(ds):return [d for d in ds if d['severity']=='error']


def test_overlapping_paths_are_a_union_with_reserved_attachment_cells(official):
    m=Module('paths','Intersecting paths around a reserved lamp footprint')
    atlas.path(m,-4,-4,8,8,reserved=[(-1,-1,2,2)])
    atlas.path(m,-2,-6,4,12,reserved=[(-1,-1,2,2)])
    _,model,ds=build_plan(m.plan(),official)
    assert not errors(ds)
    g=analyze_geometry(model,official,contacts='none',detail='summary')
    assert not errors(g['diagnostics'])
    assert g['occurrence_count']==76
    assert not any(abs(o.position.x)<20 and abs(o.position.z)<20 for o in model.iter_occurrences())


def test_tiles_are_checked_for_overlap_but_not_offered_as_stud_support(official):
    m=Module('tile-overlap','Regression: paving used to escape rectangular body checks')
    a=m.add('3068b',71,0,8,0)
    m.add('3070b',71,.5,8,.5)
    _,model,_=build_plan(m.plan(),official)
    assert any(d['code']=='assembly.body_overlap' for d in analyze_geometry(model,official)['diagnostics'])
    m=Module('tile-support','Tiles do not expose studs')
    m.add('3068b',71,id='tile')
    p=m.plan();p['sections'][0]['steps'][0].append(dict(id='brick',ref='3003.dat',colour=4,on='tile'))
    with pytest.raises(ValueError,match='studded'):build_plan(p,official)


def test_module_name_conflicts_include_transitive_children():
    root=Module('root','Root');a=Module('same-parent','Same parent');b=Module('same-parent','Same parent')
    x=Module('child','Original');x.add('3003',4)
    y=Module('child','Changed');y.add('3003',1)
    a.add(x,4);b.add(y,4)
    root.add(a,4);root.add(b,4)
    with pytest.raises(ValueError,match='Conflicting'):root.plan()


def test_named_roof_anchor_uses_body_plane(official):
    scene=Module('scene','Named roof contract')
    shell=room('shell',14,12);roof=gable('roof',16,12,dormer=True)
    attach_roof(scene,shell,roof,x=3,h=24,z=2)
    _,model,ds=build_plan(scene.plan(),official)
    assert not errors(ds)
    assert model.pieces[1].position.y==-184
    assert model.pieces[1].position.x==60 and model.pieces[1].position.z==40
    g=analyze_geometry(model,official,contacts='none',detail='summary')
    assert g['complete'] and not errors(g['diagnostics'])


@pytest.mark.parametrize('key',list(atlas.DESIGNS))
def test_each_building_is_reproducible_resolved_and_on_its_site_grid(official,key):
    folder=ATLAS/key
    generated=atlas.DESIGNS[key]['factory']().plan()
    saved=json.loads((folder/'scene.plan.json').read_text())
    assert generated==saved
    text,model,ds=build_plan(load_plan(folder/'scene.plan.json'),official)
    assert not errors(ds) and text.encode()==(folder/(key+'.mpd')).read_bytes()
    g=analyze_geometry(model,official,detail='summary',contacts='none')
    assert g['complete'] and not errors(g['diagnostics'])
    assert g['occurrence_count']>=200
    # These particular examples intentionally use one standard site lattice.
    # Do not impose this restriction on arbitrary SNOT/hinged LDraw models.
    regular=profiles()
    for o in model.iter_occurrences():
        p=regular.get(o.part_code)
        if not p or abs(o.matrix.rows[1][1]-1)>1e-6:continue
        a=o.matrix.rows
        wx=abs(a[0][0])*p['x_studs']+abs(a[0][2])*p['z_studs']
        wz=abs(a[2][0])*p['x_studs']+abs(a[2][2])*p['z_studs']
        for position,width in [(o.position.x,wx),(o.position.z,wz)]:
            phase=position/20-width/2
            assert abs(phase-round(phase))<1e-6,(key,o.reference,o.position)


def test_catalog_covers_each_family_and_only_current_artifacts():
    manifest=json.loads((ATLAS/'catalog.json').read_text())
    assert {r['key'] for r in manifest['examples']}==set(atlas.DESIGNS)
    assert len({r['category'] for r in manifest['examples']})==21
    assert len(manifest['details'])>=18
    for row in manifest['examples']+manifest['details']:
        source=ATLAS/row['model'];sha=hashlib.sha256(source.read_bytes()).hexdigest()
        assert row['source_sha256']==sha
        for name in ['validation.json','bom-comparison.json','render-manifest.json']:
            r=json.loads((source.parent/name).read_text());assert r['source_sha256']==sha
        assert row['checks_passed'] and row['bom_matches']


def test_bounded_example_selection_and_scale():
    r=search_examples('farm',limit=2)
    assert r['total'] and r['results'][0]['key']=='farmstead'
    r=search_examples(scale='microscale');assert [v['key'] for v in r['results']]==['skyline']
    assert search_examples('porch',details=True)['total']
    assert len(search_examples(limit=2)['results'])==2
    assert search_examples(limit=2)['truncated']
