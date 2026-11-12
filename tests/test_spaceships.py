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
    row = dict(id='star-destroyer-study', title='Inspiration ship', scope='inspiration',
               lesson='Shape only', aliases=['spaceship:star-destroyer-study'], families=['spaceship'])
    (atlas/'README.md').write_text('```ldraw-knowledge\n'+json.dumps([row])+'\n```\n')
    with pytest.raises(ValueError,match='inspiration'):
        export_spaceship('star-destroyer-study',tmp_path/'ship')
    assert not (tmp_path/'ship').exists()
    with pytest.raises(ValueError,match='Unknown'):
        export_spaceship('../../unknown',tmp_path/'ship')


@pytest.mark.parametrize('archetype', ['starfighter', 'freighter', 'capital-ship'])
def test_spaceship_briefs_choose_technique_from_brief(archetype):
    brief = design_brief(archetype)
    assert brief['construction'] is None
    assert brief['default_reference'] is None
    assert 'halcyon' not in brief['references']
    assert all(not key.endswith('-study') for key in brief['references'])
    brief['references'].clear()
    assert design_brief(archetype)['references']


def test_spaceship_discovery_keeps_halcyon_explicit_and_inspiration_opt_in():
    result = search_examples('halcyon', family='spaceship')['results']
    assert any(r['key'] == 'halcyon' for r in result)
    assert not default_reference()['default']
    assert all(r['scope'] != 'inspiration' for r in search_examples(family='spaceship', limit=100)['results'])
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


def test_spaceship_snot_shortlist_exposes_multiple_source_constructions():
    from ldraw_tools.knowledge import search
    report = search('hull shell', family='spaceship', technique='snot', limit=6)
    assert report['diversification'] == 'source'
    assert len({r['source_group'] for r in report['results'][:4]}) >= 3
    assert any(r['id'].startswith('b-wing-6208#') for r in report['results'])
    assert any(r['id'] == '10283-oms-pod' for r in report['results'])
    assert all('retain_' not in r['excerpt'] for r in report['results'])


def test_spaceship_browsing_includes_modules_and_preserves_all_matches():
    from ldraw_tools.knowledge import search
    varied = search_examples(family='spaceship', limit=100)
    plain = search_examples(family='spaceship', limit=100, diversify='none')
    assert {r['id'] for r in varied['results']} == {r['id'] for r in plain['results']}
    assert len({r['source_group'] for r in varied['results'][:5]}) == 5
    assert {'x-wing-nacelle', 'canopy-cockpit', '10283-oms-pod', 'halcyon'} <= {r['id'] for r in varied['results']}
    for row in search('', family='spaceship', only_examples=True, limit=100)['results']:
        assert row['source_group']
        assert not row['excerpt'].startswith('retain_')


def test_spaceship_metadata_cli_does_not_initialize_parts_and_has_no_default_help(monkeypatch):
    import argparse
    from ldraw_tools.cli import parser, run
    monkeypatch.setattr('ldraw_tools.cli.get_parts', lambda *a, **k: pytest.fail('parts initialized'))
    root = parser()
    subcommands = next(a for a in root._actions if isinstance(a, argparse._SubParsersAction))
    help_text = subcommands.choices['spaceship'].format_help().lower()
    assert 'halcyon' not in help_text
    for command in [['spaceship', 'list', '--limit', '5'], ['spaceship', 'details', '--limit', '5'],
                    ['spaceship', 'brief', 'starfighter']]:
        result, status = run(root.parse_args(command))
        assert status == 0
        if 'results' in result:
            assert len({r['source_group'] for r in result['results']}) == 5
        else:
            assert result['default_reference'] is None and result['reference_selection']['workflow']
            assert 'Halcyon' not in result['construction_strategy']


def test_cross_listed_lessons_keep_identity_and_scope():
    from ldraw_tools.knowledge import resolve
    for old, new in [('submodel:06-10283-shuttle-framework', 'spaceship:oms-pod'),
                     ('submodel:s22-10030-isd-tower', 'spaceship:micro-tantive'),
                     ('submodel:s16-30050-shuttle-fuselage', 'spaceship:micro-shuttle')]:
        a, b = resolve(old), resolve(new)
        assert a['id'] == b['id'] and a['model_sha256'] == b['model_sha256']
        assert a['scope'] == b['scope'] == 'construction'
    assert resolve('spaceship:b-wing-6208-front')['id'] == 'b-wing-6208#front'
