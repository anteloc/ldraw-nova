import hashlib
import json
from pathlib import Path

import pytest

from ldraw_tools.knowledge import examples, resolve, search


def register(root, name, *, scope='construction', lesson='Supported wheel axle', aliases=None, **fields):
    folder=root/'examples'/name
    folder.mkdir(parents=True, exist_ok=True)
    entry=dict(id=name,title=name,scope=scope,lesson=lesson,aliases=aliases or ['test:'+name],families=['test'],**fields)
    (folder/'README.md').write_text('# '+name+'\n\n```ldraw-knowledge\n'+json.dumps([entry])+'\n```\n')
    return folder/'README.md'


def test_default_is_allowlisted_and_never_falls_back_to_research(tmp_path):
    register(tmp_path,'frame',lesson='Supported wheel axle')
    register(tmp_path,'inspiration',scope='inspiration',lesson='Quantum zeppelin')
    register(tmp_path,'held',scope='hold',lesson='Quantum zeppelin')
    register(tmp_path,'archive',scope='archive',lesson='Quantum zeppelin')
    raw=tmp_path/'examples/raw';raw.mkdir();(raw/'README.md').write_text('Quantum zeppelin')
    assert search('Quantum',root=tmp_path)['results']==[]
    assert [r['id'] for r in search('Quantum',scope='inspiration',root=tmp_path)['results']]==['inspiration']
    assert len(search('Quantum',scope='all',root=tmp_path)['results'])==3
    assert resolve('test:held',root=tmp_path)['scope']=='hold'


def test_guidance_returns_exact_heading_and_fresh_source(tmp_path):
    docs=tmp_path/'docs/agent';docs.mkdir(parents=True)
    page=docs/'routing.md';page.write_text('# Routing\nIntro\n## Tube departure\nPneumatic sleeve tangent.\n```text\n# not a heading\n```\n')
    (docs/'verification.md').write_text('# Historic\nPneumatic sleeve tangent.\n')
    result=search('sleeve',root=tmp_path)['results']
    assert len(result)==1
    assert result[0]['anchor']=='tube-departure' and result[0]['line']==3
    old=result[0]['source_sha256']
    page.write_text('# Routing\n## New direction\nPneumatic sleeve curvature.\n')
    new=search('curvature',root=tmp_path)['results'][0]
    assert new['source_sha256']!=old and new['anchor']=='new-direction'


def test_aliases_are_exact_and_ambiguous_short_names_fail(tmp_path):
    register(tmp_path,'truck',aliases=['vehicle:small'])
    register(tmp_path,'house',aliases=['building:small'])
    assert resolve('small',family='vehicle',root=tmp_path)['id']=='truck'
    with pytest.raises(ValueError,match='Ambiguous'):resolve('small',root=tmp_path)
    with pytest.raises(ValueError,match='Unknown'):resolve('../../truck',root=tmp_path)
    register(tmp_path,'collision',aliases=['vehicle:small'])
    with pytest.raises(ValueError,match='Duplicate'):examples(tmp_path)


def test_model_changes_hold_the_entry_without_rewriting_its_identity(tmp_path):
    model=tmp_path/'model.mpd';model.write_text('original source')
    identity=hashlib.sha256(model.read_bytes()).hexdigest()
    page=register(tmp_path,'stable',model='model.mpd',model_sha256=identity)
    original=page.read_bytes()
    assert search('axle',root=tmp_path)['results']
    model.write_text('changed source')
    assert not search('axle',root=tmp_path)['results']
    held=resolve('stable',root=tmp_path)
    assert held['scope']=='hold' and held['model_sha256']==identity
    assert page.read_bytes()==original


def test_paths_are_confined_and_queries_are_literals(tmp_path):
    register(tmp_path,'safe')
    assert search('" OR *',root=tmp_path)['results']==[]
    assert search('***',root=tmp_path)['results']==[]
    register(tmp_path,'escape',model='../outside.mpd')
    with pytest.raises(ValueError,match='escapes'):examples(tmp_path)


def test_all_legacy_aliases_resolve_with_the_planned_retirements():
    root=Path(__file__).resolve().parents[1]
    ledger=json.loads((root/'docs/plans/knowledge-base-overhaul/snapshot/example-migration-ledger.json').read_text())
    records=examples(root)
    by_alias={a:r for r in records for a in r['aliases']}
    assert all(row['alias'] in by_alias for row in ledger['legacy_catalog_aliases'])
    for row in ledger['retired_catalog_entries']:
        assert by_alias[row['alias']]['scope']=='archive'
    assert by_alias['technic:service-platform']['id']==by_alias['technic:mounted-frame-named']['id']
    assert by_alias['reference:rounded-cockpit-shell']['scope']=='hold'
    assert 'body' in by_alias['reference:rounded-cockpit-shell']['lesson']
    assert all(r['scope'] not in {'hold','archive','inspiration','research','diagnostic'}
               for r in search('',limit=1000,only_examples=True,root=root)['results'])


def test_cli_knowledge_does_not_initialize_parts(monkeypatch):
    from ldraw_tools.cli import parser, run
    monkeypatch.setattr('ldraw_tools.cli.get_parts',lambda *a,**k:pytest.fail('parts initialized'))
    args=parser().parse_args(['knowledge','search','pneumatic sleeve','--limit','2'])
    result,code=run(args)
    assert code==0 and result['engine']=='sqlite-fts5-bm25' and result['results']
    assert parser().parse_args(['examples']).family is None


def test_subject_heading_is_kept_for_sections_with_empty_parents(tmp_path):
    docs = tmp_path/'docs/agent/guides'; docs.mkdir(parents=True)
    (docs/'design.md').write_text('# Design\n## Vehicles\n### Shape\nBonnet cabin wheelbase.\n')
    result = search('wheelbase', root=tmp_path)['results'][0]
    assert result['headings'] == ['Design', 'Vehicles', 'Shape']
    assert result['line'] == 3


def test_export_aliases_and_directory_cannot_bypass_scope(tmp_path):
    from ldraw_tools.knowledge import check_directory_scope, export_directory
    register(tmp_path, 'held', scope='hold', aliases=['mechanism:old-name'])
    with pytest.raises(ValueError, match='blocked'):
        export_directory('old-name', family='mechanism', root=tmp_path)
    with pytest.raises(ValueError, match='blocked'):
        check_directory_scope(tmp_path/'examples/held', root=tmp_path)
    register(tmp_path, 'current')
    assert export_directory('test:current', root=tmp_path) == tmp_path/'examples/current'


def test_grouped_lessons_export_their_actual_source_directory(tmp_path):
    from ldraw_tools.knowledge import export_directory
    source = tmp_path/'examples/group/detail/source.mpd'
    source.parent.mkdir(parents=True); source.write_text('stable source')
    register(tmp_path, 'group', model='examples/group/detail/source.mpd',
             model_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    assert export_directory('group', root=tmp_path) == source.parent


def test_generated_gallery_does_not_readmit_archived_examples(tmp_path):
    from ldraw_tools.knowledge import write_compat_catalog
    register(tmp_path, 'current', lesson='Sideways panel attachment')
    register(tmp_path, 'retired', scope='archive', lesson='Old template')
    out = tmp_path/'catalog'; out.mkdir()
    write_compat_catalog('test', out, root=tmp_path)
    catalog = json.loads((out/'catalog.json').read_text())
    rows = catalog['examples'] + catalog['details']
    assert {r['id']: r['scope'] for r in rows} == {'current':'construction', 'retired':'archive'}
    html = (out/'index.html').read_text()
    assert 'Sideways panel attachment' in html and 'Old template' not in html


def test_promoted_sources_and_relocated_geometry_match_preserved_hashes():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root/'docs/plans/knowledge-base-overhaul/package-relocations.json').read_text())
    for row in manifest['files']:
        if Path(row['path']).suffix.lower() in {'.mpd', '.ldr', '.dat', '.png', '.jpg'}:
            assert hashlib.sha256((root/row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    for name in ['boombox','an225']:
        row = resolve(name,root=root)
        assert row['scope'] == 'construction'
        evidence = json.loads(Path(row['visual_review']).read_text())
        assert row['model_sha256'] == evidence['source_sha256']
        assert len(evidence['sections']) == (6 if name=='boombox' else 18)
