import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from conftest import mpd, ref
from ldraw_tools.document import parse_source
from ldraw_tools.manuals import (construction_steps, current_manual, export_manual,
    operation_notes, prepare_manual, preview_section, review_manual, sha)


NOTES = dict(function='Reference fixture', fixed='Base', moving='No motion tested',
    input='Unresolved', output='Unresolved', parent_context='No parent in fixture',
    reuse_notes='Review attachments after placement')


def test_steps_include_final_unterminated_group_and_keep_child_callouts(tmp_path, parts):
    source = tmp_path/'nested.mpd'
    source.write_text(mpd(ref(colour=16)+'\n0 STEP\n0 STEP\n'+ref('child.ldr',position='100 0 0'))
        +mpd(ref('3003.dat',colour=16),name='child.ldr'))
    model = parse_source(source)
    steps = construction_steps(model, model.name, parts)
    assert [s['number'] for s in steps] == [1,3]
    assert steps[1]['parts'][0]['kind'] == 'submodel'
    assert steps[1]['parts'][0]['quantity'] == 1
    assert construction_steps(model, 'child.ldr', parts)[0]['parts'][0]['ref'] == '3003.dat'
    preview = preview_section(model, model.name, 4)
    assert preview.pieces[0].colour.code == 4
    assert model.pieces[0].colour.code == 16
    assert preview.submodels['child.ldr'].pieces[0].colour.code == 16


def fake_step_render(path, library, outdir, *, steps, views, bounds=None):
    result = []
    for number in steps:
        for view in views:
            name = f'step-{number:03}-{view}.png'
            (Path(outdir)/name).write_bytes(f'fixture {number} {view}'.encode())
            result.append(dict(step=number, view=view, file=name))
    return result


def test_preview_preserves_embedded_part_dependencies(tmp_path, parts):
    from ldraw_tools.builder import serialize_mpd
    from ldraw_tools.external import cad_source
    source=tmp_path/'embedded.mpd'
    source.write_text(mpd(ref('custom.dat',colour=16))
        +mpd('0 !LDRAW_ORG Unofficial_Part\n'+ref('shape.dat',colour=16),name='custom.dat')
        +mpd('0 !LDRAW_ORG Unofficial_Subpart\n3 16 0 0 0 10 0 0 0 10 0',name='shape.dat'))
    model=parse_source(source)
    preview=preview_section(model,model.name,4)
    assert set(preview.submodels)=={'custom.dat','shape.dat'}
    path=tmp_path/'preview.mpd';path.write_text(serialize_mpd(preview))
    temp=tmp_path/'materialized';temp.mkdir()
    prepared,library,names=cad_source(path,parts.path.parent,temp)
    assert prepared != path and set(names.values())=={'custom.dat','shape.dat'}
    assert all((library/'parts'/name).is_file() for name in names)


def study_fixture(tmp_path, parts, monkeypatch, *, renders=True):
    source = tmp_path/'source file.mpd'
    source.write_text(mpd(ref()+'\n0 STEP\n'+ref('3003.dat',position='100 0 0')))
    monkeypatch.setattr('ldraw_tools.manuals.render_steps', fake_step_render)

    def final_render(path, library, outdir, **kwargs):
        outdir.mkdir(parents=True,exist_ok=True)
        (outdir/'home.png').write_bytes(b'final fixture')
        (outdir/'leocad-bom.csv').write_text('Part ID,Color Code,Quantity\n3001.dat,4,1\n3003.dat,4,1\n')
    monkeypatch.setattr('ldraw_tools.manuals.render', final_render)
    folder = tmp_path/'study'
    manual = prepare_manual(source, 'main.ldr', folder, parts, colour=4, renders=renders, notes=NOTES)
    return source, folder, manual


def test_study_review_export_preserve_evidence_without_motion_claims(tmp_path, parts, monkeypatch):
    source, folder, manual = study_fixture(tmp_path, parts, monkeypatch)
    assert manual['physical_placements'] == 2 and manual['bom_matches']
    assert manual['source_checks_passed'] and manual['analytical_verification'] == 'deferred'
    assert sha(source) == manual['source']['sha256']
    with pytest.raises(ValueError, match='review'):
        export_manual(folder,tmp_path/'copy')
    images = [p for s in manual['sections'] for step in s['steps'] for p in step['images'].values()]+['renders/home.png']
    with pytest.raises(ValueError, match='every rendered'):
        review_manual(folder,images=images[:-1],note='Incomplete')
    review_manual(folder,images=images,note='Fixture review, no physical claim')
    report = export_manual(folder,tmp_path/'copy')
    assert report['analytical_verification']=='deferred'
    assert (tmp_path/'copy/source.mpd').read_bytes()==(folder/'source.mpd').read_bytes()
    current_manual(tmp_path/'copy')
    (folder/images[0]).write_bytes(b'replaced render')
    with pytest.raises(ValueError, match='changed'):
        export_manual(folder,tmp_path/'other')


def test_unrendered_and_refreshed_studies_do_not_keep_current_review(tmp_path, parts, monkeypatch):
    source, folder, manual = study_fixture(tmp_path, parts, monkeypatch, renders=False)
    assert manual['bom_matches'] is None
    with pytest.raises(ValueError, match='review'):
        export_manual(folder,tmp_path/'copy')
    (folder/'visual-review.json').write_text('{}')
    prepare_manual(source,'main.ldr',folder,parts,colour=4,renders=False,force=True)
    assert not (folder/'visual-review.json').exists()
    with pytest.raises(ValueError, match='overwrite its source'):
        prepare_manual(folder/'source.mpd',manual['source_root'],folder,parts,colour=4,force=True)


def test_artifact_paths_and_source_edits_are_checked(tmp_path, parts, monkeypatch):
    _, folder, manual = study_fixture(tmp_path, parts, monkeypatch)
    manual['artifact_hashes']['../source file.mpd']=sha(tmp_path/'source file.mpd')
    (folder/'manual.json').write_text(json.dumps(manual))
    with pytest.raises(ValueError):
        current_manual(folder)


def test_renderer_uses_exact_step_numbers_and_cannot_reuse_stale_images(tmp_path, parts, monkeypatch):
    from ldraw_tools.external import render_steps
    source=tmp_path/'source with spaces.mpd'
    source.write_text(mpd(ref()))
    seen=[]

    def cad(command, **kwargs):
        seen.append(command)
        image=Path(command[command.index('-i')+1])
        for n in range(int(command[command.index('--from')+1]),int(command[command.index('--to')+1])+1):
            image.with_name(image.stem+f'{n:02}.png').write_bytes(b'render fixture')
        return SimpleNamespace(returncode=0,stdout='',stderr='')
    monkeypatch.setattr('ldraw_tools.external.subprocess.run',cad)
    rows=render_steps(source,parts.path.parent,tmp_path/'renders',steps=[1,3],views=['home'])
    assert [r['step'] for r in rows]==[1,3]
    assert seen[0][-1]==str(source) and '--highlight' in seen[0]
    monkeypatch.setattr('ldraw_tools.external.subprocess.run',lambda *a,**k:SimpleNamespace(returncode=0,stdout='',stderr=''))
    with pytest.raises(ValueError,match='every requested'):
        render_steps(source,parts.path.parent,tmp_path/'renders',steps=[1,3],views=['home'])


def test_single_step_renderer_and_mechanism_discovery(tmp_path, parts, monkeypatch):
    from ldraw_tools.external import render_steps
    from ldraw_tools.discovery import mechanism_candidate,structural_candidate
    source=tmp_path/'single.mpd'; source.write_text(mpd(ref()))
    def cad(command,**kwargs):
        Path(command[command.index('-i')+1]).write_bytes(b'single frame')
        return SimpleNamespace(returncode=0,stdout='',stderr='')
    monkeypatch.setattr('ldraw_tools.external.subprocess.run',cad)
    assert render_steps(source,parts.path.parent,tmp_path/'images',steps=[1],views=['top'])[0]['step']==1
    row=dict(kind='submodels',description='Worm gear drive',theme='Technic',parent_description='A tree')
    assert mechanism_candidate(row,{'bom':[{'description':'Technic Worm Gear'}]})
    assert not structural_candidate(row)
    assert not mechanism_candidate(row,{'bom':[{'description':'Brick 2 x 4'}]})
    assert not mechanism_candidate(dict(row,description='A static frame',parent_description='Gearbox'))
    with pytest.raises(ValueError):operation_notes({'function': {'not':'text'}})


def test_general_construction_manual_has_its_own_notes_and_export(tmp_path, parts, monkeypatch):
    source, _, _ = study_fixture(tmp_path, parts, monkeypatch)
    folder = tmp_path/'construction'
    notes = dict(lesson='Bond a plate across the support', construction='Two layers',
                 interfaces='Inspect bottom sockets', parent_context='Standalone fixture', reuse_notes='Adapt the support')
    manual = prepare_manual(source, 'main.ldr', folder, parts, colour=4, notes=notes, kind='construction')
    assert manual['scope'] == 'construction-construction-study'
    assert (folder/'study-notes.json').is_file() and not (folder/'operation.json').exists()
    assert 'analytical_verification' not in manual
    images=[p for s in manual['sections'] for step in s['steps'] for p in step['images'].values()]+manual['final_images']
    review_manual(folder,images=images,note='Inspected the fixture steps')
    export_manual(folder,tmp_path/'copied')
    current_manual(tmp_path/'copied')
    assert 'What this construction teaches' in (folder/'index.html').read_text()


def test_overview_is_not_a_step_manual_and_requires_all_views(tmp_path, parts, monkeypatch):
    source, _, _ = study_fixture(tmp_path, parts, monkeypatch)
    def final_render(path, library, outdir, **kwargs):
        outdir.mkdir(parents=True,exist_ok=True)
        for view in kwargs['views']:(outdir/(view+'.png')).write_bytes(view.encode())
        (outdir/'leocad-bom.csv').write_text('Part ID,Color Code,Quantity\n3001.dat,4,1\n3003.dat,4,1\n')
    def no_steps(*args,**kwargs):raise AssertionError('Overview must not render steps')
    monkeypatch.setattr('ldraw_tools.manuals.render',final_render)
    monkeypatch.setattr('ldraw_tools.manuals.render_steps',no_steps)
    folder=tmp_path/'overview'
    manual=prepare_manual(source,'main.ldr',folder,parts,colour=4,kind='construction',overview=True,views=['home','top'])
    assert manual['final_images']==['renders/home.png','renders/top.png']
    assert all(not s['images'] for sec in manual['sections'] for s in sec['steps'])
    assert 'not construction steps' in (folder/'index.html').read_text()
    with pytest.raises(ValueError):review_manual(folder,images=['renders/home.png'],note='Incomplete')
    review_manual(folder,images=manual['final_images'],note='Opened both completed-model views')
    (folder/'renders/top.png').write_bytes(b'changed')
    with pytest.raises(ValueError,match='changed'):current_manual(folder)
