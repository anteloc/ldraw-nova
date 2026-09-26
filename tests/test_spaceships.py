from types import SimpleNamespace

import pytest

from ldraw_tools.geometry import geometry_complete
from ldraw_tools.spaceships import design_brief, export_spaceship


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
