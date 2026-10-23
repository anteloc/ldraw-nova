import pytest
from ldraw_tools.parts_catalog import PartsCatalog, PartsUnavailable, flat_model_inventory, normalize_part_id

PLACEMENT = '1 4 0 0 0 1 0 0 0 1 0 0 0 1 3001.dat'

CATALOG = ('part_id,color_id,name,max_quantity\n'
           '3001,4,Brick 2 x 4,4\n'
           '3001,36,Brick 2 x 4 transparent,\n'
           '3005,4,Brick 1 x 1,\n')


def test_exact_color_quantity_and_normalization():
    catalog = PartsCatalog.from_csv(CATALOG)
    catalog.validate({('PARTS/3001.DAT', 4): 4, ('3001', 36): 1})
    for inventory in ({('3001', 0): 1}, {('3001', 4): 5}, {('unknown', 4): 1}):
        with pytest.raises(PartsUnavailable):
            catalog.validate(inventory)
    for quantity in (0, -1, 1.5, True):
        with pytest.raises(ValueError):
            catalog.validate({('3001', 4): quantity})


def test_search_returns_bounded_relevant_pairs_without_pricing():
    catalog = PartsCatalog.from_csv(CATALOG)
    assert catalog.search('transparent')['parts'][0]['color_id'] == 36
    assert catalog.search('3001', 4)['total'] == 1
    assert len(catalog.search(limit=1)['parts']) == 1
    assert catalog.search(offset=100)['parts'] == []
    assert 'unit_price' not in catalog.search()['parts'][0]


def test_normalized_pairs_share_quantity_limits():
    catalog = PartsCatalog.from_csv("part_id,color_id,max_quantity\n3001,4,2\n")
    with pytest.raises(PartsUnavailable):
        catalog.validate({("3001", 4): 2, ("3001.dat", 4): 1})


@pytest.mark.parametrize('bad', ['../3001', '/3001', 's/3001', '3001.ldr', '3001;rm'])
def test_unsafe_identifiers_are_rejected(bad):
    with pytest.raises(ValueError):
        normalize_part_id(bad)


def test_ambiguous_pairs_and_empty_palette_fail_closed():
    with pytest.raises(ValueError, match='Ambiguous'):
        PartsCatalog.from_csv(CATALOG + '3001,4,Duplicate,\n')
    with pytest.raises(ValueError, match='no mapped'):
        PartsCatalog.from_csv(CATALOG.splitlines()[0] + '\n')


def test_round_trip_discards_external_metadata_and_preserves_quantities():
    external = 'part_id,color_id,name,max_quantity,unit_price,weight_kg,external_field\n3001,4,Brick,5,0.25,0.01,other\n'
    palette = PartsCatalog.from_csv(external)
    exported = palette.to_csv()
    assert 'unit_price' not in exported and 'weight_kg' not in exported and 'external_field' not in exported
    assert PartsCatalog.from_csv(exported).parts == palette.parts


def test_utf8_bom_does_not_hide_headers():
    catalog = PartsCatalog.from_csv('\ufeffpart_id,color_id,name\n3001,4,Brick\n')
    assert catalog.search()['parts'][0]['name'] == 'Brick'


def test_plain_palette_and_alias_quantity_limits():
    catalog = PartsCatalog.from_csv('part_id,color_id,sku,max_quantity\n3001,4,A,2\n3001a,4,A,2\n')
    catalog.validate({('3001', 4): 1, ('3001a', 4): 1})
    with pytest.raises(PartsUnavailable):
        catalog.validate({('3001', 4): 2, ('3001a', 4): 1})
    with pytest.raises(ValueError, match='Inconsistent'):
        PartsCatalog.from_csv('part_id,color_id,sku,max_quantity\n3001,4,A,2\n3001a,4,A,3\n')


def test_physical_inventory_rejects_impersonation_and_bad_transforms():
    assert flat_model_inventory('0 FILE root.ldr\n' + PLACEMENT + '\n0 STEP\n' + PLACEMENT) == {('3001', 4): 2}
    for content in [PLACEMENT + '\n0 FILE 3001.dat\n0 Fake geometry',
                    '0 !COLOUR Fake CODE 4 VALUE #000000 EDGE #333333\n' + PLACEMENT,
                    PLACEMENT + '\n3 4 0 0 0 1 1 1 2 2 2',
                    PLACEMENT.replace('0 0 0', 'NaN 0 0', 1),
                    PLACEMENT.replace('3001.dat', 'assembly.ldr')]:
        with pytest.raises(ValueError):
            flat_model_inventory(content)


def test_catalog_name_and_shared_groups_survive_round_trip():
    palette = PartsCatalog.from_csv("part_id,color_id,sku,max_quantity\n3001,4,A,2\n3001a,4,A,2\n", name="My inventory")
    assert palette.name == "My inventory"
    restored = PartsCatalog.from_csv(palette.to_csv())
    assert restored.search("A")["total"] == 2
    with pytest.raises(PartsUnavailable):
        restored.validate({("3001", 4): 2, ("3001a", 4): 1})


def test_oversized_csv_field_is_a_validation_error():
    with pytest.raises(ValueError):
        PartsCatalog.from_csv('part_id,color_id,name\n3001,4,' + 'x' * 200_000)
