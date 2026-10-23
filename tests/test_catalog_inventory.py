import pytest
from ldraw_tools.catalog_inventory import model_inventory, check_rigid_transform
from ldraw_tools.parts_catalog import PartsCatalog, PartsUnavailable

MODEL = '0 FILE root.ldr\n1 4 0 0 0 1 0 0 0 1 0 0 0 1 child.ldr\n0 FILE child.ldr\n1 16 0 0 0 1 0 0 0 1 0 0 0 1 3001.dat\n'


@pytest.fixture
def library(parts):
    return parts.library_root


def test_hierarchy_colors_and_unknown_dependencies(tmp_path, library):
    source = tmp_path / 'model.mpd'; source.write_text(MODEL)
    inventory = model_inventory(source, library)
    assert inventory == {('3001', 4): 1}
    catalog = PartsCatalog.from_csv('part_id,color_id\n3001,4\n')
    catalog.validate(inventory)
    source.write_text(MODEL.replace('1 4 ', '1 0 '))
    with pytest.raises(PartsUnavailable):
        catalog.validate(model_inventory(source, library))
    source.write_text(MODEL.replace('3001.dat', 'missing.ldr'))
    with pytest.raises((ValueError, FileNotFoundError, KeyError)):
        model_inventory(source, library)


def test_parser_rejects_embedded_part_override(tmp_path, library):
    source = tmp_path / 'model.mpd'; source.write_text(MODEL + '0 FILE 3001.dat\n0 Fake\n')
    with pytest.raises(PartsUnavailable):
        model_inventory(source, library)


def test_palette_parts_allow_rotations_but_not_changed_geometry():
    check_rigid_transform([[0.707107, 0, 0.707107], [0, 1, 0], [-0.707107, 0, 0.707107]])
    for rows in ([[2, 0, 0], [0, 1, 0], [0, 0, 1]],
                 [[1, .1, 0], [0, 1, 0], [0, 0, 1]],
                 [[-1, 0, 0], [0, 1, 0], [0, 0, 1]],
                 [[float('nan'), 0, 0], [0, 1, 0], [0, 0, 1]]):
        with pytest.raises(ValueError):
            check_rigid_transform(rows)


def test_unknown_dat_and_scaled_parts_fail_closed(tmp_path, library):
    source = tmp_path / 'model.mpd'
    for content in (MODEL.replace('3001.dat', 'missing.dat'),
                    MODEL.replace('1 16 0 0 0 1 ', '1 16 0 0 0 2 ')):
        source.write_text(content)
        with pytest.raises((ValueError, FileNotFoundError, KeyError)):
            model_inventory(source, library)


@pytest.mark.parametrize('option', ['--palette', '--catalog'])
def test_inventory_cli_accepts_palette_and_legacy_catalog(option, tmp_path, library, monkeypatch, capsys):
    import json
    from ldraw_tools.catalog_inventory import main
    source = tmp_path / 'model.mpd'
    source.write_text(MODEL)
    palette = tmp_path / 'parts.csv'
    palette.write_text('part_id,color_id,max_quantity\n3001,4,1\n')
    monkeypatch.setattr('sys.argv', ['catalog_inventory', str(source), str(library), option, str(palette)])
    main()
    assert json.loads(capsys.readouterr().out) == [['3001', 4, 1]]
