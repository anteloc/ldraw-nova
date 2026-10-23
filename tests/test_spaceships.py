from types import SimpleNamespace
from pathlib import Path

import pytest

from ldraw_tools.geometry import geometry_complete
from ldraw_tools.examples import search_examples
from ldraw_tools.spaceships import default_reference, design_brief, export_spaceship


def test_mesh_completeness_does_not_confuse_connector_warnings_with_missing_solids():
    def diagnostic(code,severity='warning'):
        return SimpleNamespace(to_dict=lambda:dict(code=code,severity=severity))
    def inspection(*diagnostics,skipped=()):
        return SimpleNamespace(skipped_geometry=skipped,diagnostics=diagnostics)
    assert geometry_complete(inspection())
    assert geometry_complete(inspection(diagnostic('connection.invalid_transform')))
    assert not geometry_complete(inspection(diagnostic('geometry.incomplete')))
    assert not geometry_complete(inspection(diagnostic('connection.invalid_transform','error')))
    assert not geometry_complete(inspection(skipped=['unresolved part']))


def test_spaceship_briefs_have_distinct_modules_and_independent_palettes():
    fighter=design_brief('starfighter');freighter=design_brief('freighter');capital=design_brief('capital-ship')
    assert fighter['modules'] != freighter['modules'] != capital['modules']
    assert any('display mount' in s for s in capital['modules'])
    assert any('cargo' in s for s in freighter['modules'])
    fighter['palette']['hull']=4
    assert design_brief('starfighter')['palette']['hull']==71
    with pytest.raises(ValueError):design_brief('road')


def test_inspiration_sources_cannot_be_exported_as_checked_assemblies(tmp_path, monkeypatch):
    import json
    monkeypatch.setattr('ldraw_tools.spaceships.ROOT',tmp_path)
    atlas=tmp_path/'examples/spaceship-atlas';atlas.mkdir(parents=True)
    (atlas/'catalog.json').write_text(json.dumps(dict(examples=[dict(key='star-destroyer-study',use='inspiration')],details=[])))
    with pytest.raises(ValueError,match='inspiration'):
        export_spaceship('star-destroyer-study',tmp_path/'ship')
    assert not (tmp_path/'ship').exists()
    with pytest.raises(ValueError,match='Unknown'):
        export_spaceship('../../unknown',tmp_path/'ship')


@pytest.mark.parametrize('archetype', ['starfighter', 'freighter', 'capital-ship'])
def test_all_spaceship_briefs_default_to_snot_and_halcyon(archetype):
    brief = design_brief(archetype)
    assert brief['construction'] == 'SNOT'
    assert brief['references'][0] == 'halcyon'
    assert brief['default_reference']['key'] == 'halcyon'
    for field in ['model', 'plan', 'guide', 'generator', 'preview', 'visual_review']:
        assert Path(brief['default_reference'][field]).is_file()
    brief['references'].clear()
    assert design_brief(archetype)['references'][0] == 'halcyon'


def test_spaceship_discovery_prioritizes_halcyon_and_preserves_detail_search():
    assert search_examples(family='spaceship', limit=1)['results'][0]['key'] == 'halcyon'
    result = search_examples('SNOT', family='spaceship')['results']
    assert result[0]['key'] == 'halcyon' and result[0]['default']
    assert all(r['key'] != 'halcyon' for r in search_examples(family='spaceship', details=True)['results'])
    assert search_examples('nacelle', family='spaceship', details=True)['results']


def test_halcyon_export_preserves_editable_design_and_protects_existing_work(tmp_path):
    import importlib.util
    import json
    reference = default_reference()
    destination = tmp_path/'ship'
    report = export_spaceship('halcyon', destination)
    assert report['scope'] == 'design-reference'
    for key in ['model', 'plan', 'generator', 'preview', 'visual_review']:
        original = Path(reference[key])
        assert (destination/original.name).read_bytes() == original.read_bytes()
    spec = importlib.util.spec_from_file_location('exported_halcyon', destination/'generate.py')
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    assert generator.build() == json.loads(Path(report['plan']).read_text())
    with pytest.raises(ValueError, match='exists'):
        export_spaceship('halcyon', destination)
    export_spaceship('halcyon', destination, force=True)
    with pytest.raises(ValueError, match='separate'):
        export_spaceship('halcyon', Path(reference['guide']).parent, force=True)
