import copy
import pytest

from ldraw_tools.builder import build_plan
from ldraw_tools.catalog import resolve_colour, resolve_part, search_catalog
from ldraw_tools.details import RECIPES, detail_plan, palette_report
from ldraw_tools.geometry import analyze_geometry


def test_catalog_symbols_are_real_and_do_not_import_py4bricks(official):
    import sys
    assert resolve_part('@arches.Arch1X6X2WithThickTopAndReinforcedUnderside',official)=='3307.dat'
    assert resolve_colour('@colours.Dark_Green',official)==288
    assert 'py4bricks' not in sys.modules
    with pytest.raises(ValueError,match='Unknown category symbol'):
        resolve_part('@arches.MadeUp',official)


def test_numeric_dimensions_do_not_match_digits_inside_part_ids(official):
    report=search_catalog(official,'parts','arch 1 x 6',category='arches',limit=100)
    assert report['total']>0
    assert '3659.dat' not in {p['filename'] for p in report['results']}
    assert all('6' in p['description'] for p in report['results'])


def test_legacy_entries_are_explicit_and_results_bounded(official):
    report=search_catalog(official,'parts','',category='bricks',limit=3)
    assert len(report['results'])==3 and report['truncated']
    assert all(r['available'] and not r['legacy_or_internal'] for r in report['results'])
    with pytest.raises(ValueError,match='Unknown category'):
        search_catalog(official,'parts',category='imaginary')


def test_symbolic_plan_is_not_mutated_and_builds_numeric_mpd(official):
    plan=detail_plan('arched-window');before=copy.deepcopy(plan)
    text,model,d=build_plan(plan,official)
    assert plan==before and not any(x['severity']=='error' for x in d)
    assert any(p.reference=='3307.dat' for p in model.pieces)
    assert all(not p.reference.startswith('@') for p in model.pieces)
    assert model.pieces[0].colour.code==15


@pytest.mark.parametrize('name',list(RECIPES))
def test_details_resolve_geometry_and_avoid_body_collisions(official,name):
    _,model,d=build_plan(detail_plan(name),official)
    report=analyze_geometry(model,official)
    assert report['complete']
    assert not [x for x in d+report['diagnostics'] if x['severity']=='error']
    if name=='striped-awning':
        # A one-stud beam under the slope's rear closed area missed every socket.
        assert report['contact_count']>=8 and report['optimistic_component_count']==1


def test_palette_values_are_from_installed_ldconfig(official):
    p=palette_report(official,'botanical-bookshop')['botanical-bookshop']
    assert p['resolved']['shopfront']['code']==288
    assert p['roles']['shopfront']=='@colours.Dark_Green'
    assert p['resolved']['glass']['alpha']==128  # Supplied snapshot incorrectly says 255.


def test_catalog_reads_literals_without_executing_generated_modules(parts,monkeypatch,tmp_path):
    (tmp_path/'parts').mkdir()
    (tmp_path/'parts/bricks.py').write_text("raise RuntimeError('must not run')\nBrick2X4 = '3001'\n")
    (tmp_path/'colours.py').write_text("import unavailable_dependency\nRed = Colour(code=4, alpha=255)\n")
    (tmp_path/'dimensions.py').write_text("PartsDimensions = {'3001': {'ldu_x':80, 'ldu_y':28, 'ldu_z':40}}\n")
    monkeypatch.setenv('LDRAW_CATEGORIES',str(tmp_path))
    assert resolve_part('@bricks.Brick2X4',parts)=='3001.dat'
    assert resolve_colour('@colours.Red',parts)==4
    row=search_catalog(parts,'parts',measure=True)['results'][0]
    # Independent fixture has a 24-high body without studs; snapshot is taller.
    assert row['measured_size_ldu']==[80,24,40]
    assert row['geometry_complete'] and row['dimensions_disagree']
    assert search_catalog(parts,'parts',max_size=[80,24,40])['total']==0


def test_catalog_rejects_misleading_filters(parts):
    with pytest.raises(ValueError,match='finite positive'):
        search_catalog(parts,'parts',max_size=[20,float('nan'),20])
    with pytest.raises(ValueError,match='apply to catalog parts'):
        search_catalog(parts,'colours',measure=True)


def test_missing_categories_do_not_break_numeric_plans(official,monkeypatch,tmp_path):
    monkeypatch.setenv('LDRAW_CATEGORIES',str(tmp_path/'absent'))
    plan=dict(version=1,author='Test',sections=[dict(name='main.ldr',description='Numeric plan',steps=[[dict(id='brick',ref='3001.dat',colour=4,at=[0,0,0])]])])
    _,_,d=build_plan(plan,official)
    assert not d
    with pytest.raises(ValueError,match='Categories missing'):
        resolve_part('@bricks.Brick1X1',official)
