import io
import zipfile

import pytest

from ldraw_tools.parts_catalog import MAX_CATALOG_BYTES, PartsCatalog, PartsUnavailable

PLACEMENT = '1 4 0 0 0 1 0 0 0 1 0 0 0 1 3001.dat\n'
XML = '<INVENTORY><ITEM><ITEMTYPE>P</ITEMTYPE><ITEMID>3001</ITEMID><COLOR>5</COLOR><MINQTY>2</MINQTY></ITEM></INVENTORY>'


def studio(content, extra=None):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('model.ldr', content)
        for name, data in (extra or {}).items():
            archive.writestr(name, data)
    return output.getvalue()


@pytest.mark.parametrize('filename,data', [
    ('palette.csv', b'part_id,color_id,max_quantity\n3001,4,2\n'),
    ('bom.CSV', b'\xef\xbb\xbfLdrawId,LDrawColorId,Qty\n3001.dat,4,1\n3001.dat,4,1\n'),
    ('model.ldr', (PLACEMENT * 2).encode()),
    ('wanted.xml', XML.encode()),
    ('studio.io', studio(PLACEMENT * 2)),
])
def test_all_formats_preserve_exact_parts_colors_and_counts(filename, data, tmp_path):
    path = tmp_path / filename
    path.write_bytes(data)
    palette = PartsCatalog.load(path)
    palette.validate({('3001', 4): 2})
    assert palette.parts[('3001', 4)].max_quantity == 2
    for inventory in ({('3001', 4): 3}, {('3001', 0): 1}, {('3005', 4): 1}):
        with pytest.raises(PartsUnavailable):
            palette.validate(inventory)
    assert PartsCatalog.from_csv(palette.to_csv()).parts == palette.parts


def test_nested_models_count_occurrences_inherit_colors_and_ignore_unused_sections():
    root = '0 FILE root.ldr\n' + PLACEMENT.replace('3001.dat', 'child.ldr') * 2
    child = '0 FILE child.ldr\n' + PLACEMENT.replace('1 4 ', '1 16 ')
    content = root + child + '0 FILE unused.ldr\n' + PLACEMENT.replace('3001', '3005')
    palette = PartsCatalog.from_upload('model.ldr', content.encode())
    assert set(palette.parts) == {('3001', 4)}
    assert palette.parts[('3001', 4)].max_quantity == 2
    archive = studio(root, {'child.ldr': PLACEMENT.replace('1 4 ', '1 16 ')})
    assert PartsCatalog.from_upload('model.io', archive).parts == palette.parts


@pytest.mark.parametrize('content', [
    PLACEMENT.replace('3001.dat', '../3001.dat'),
    PLACEMENT.replace('3001.dat', 'missing.ldr'),
    PLACEMENT.replace('1 4 ', '1 16 '),
    PLACEMENT.replace('1 4 ', '1 24 '),
    PLACEMENT.replace('0 0 0', 'nan 0 0', 1),
    '0 FILE root.ldr\n' + PLACEMENT.replace('3001.dat', 'root.ldr'),
    '0 FILE root.ldr\n' + PLACEMENT + '0 FILE root.ldr\n' + PLACEMENT,
    '0 FILE root.ldr\n' + PLACEMENT + '0 FILE 3001.dat\n',
    '0 !COLOUR Fake CODE 4 VALUE #000000 EDGE #000000\n' + PLACEMENT,
    '3 4 0 0 0 1 1 1 2 2 2',
    'not an LDraw model',
])
def test_invalid_models_are_rejected(content):
    with pytest.raises(ValueError):
        PartsCatalog.from_upload('bad.ldr', content.encode())


def test_recursive_and_explosive_graphs_are_bounded():
    content = ''.join('0 FILE s%d.ldr\n' % i +
        (PLACEMENT.replace('3001.dat', 's%d.ldr' % (i + 1)) * 2 if i < 17 else PLACEMENT)
        for i in range(18))
    with pytest.raises(ValueError, match='100,000'):
        PartsCatalog.from_upload('huge.ldr', content.encode())


@pytest.mark.parametrize('content', [
    XML.replace('<COLOR>5', '<COLOR>99999'),
    XML.replace('<ITEMTYPE>P', '<ITEMTYPE>S'),
    XML.replace('<MINQTY>2', '<MINQTY>-1'),
    '<!DOCTYPE INVENTORY [<!ENTITY a "3001">]>' + XML,
    '<INVENTORY>', '<INVENTORY/>', '<other/>',
])
def test_invalid_xml_is_rejected(content):
    with pytest.raises(ValueError):
        PartsCatalog.from_upload('bad.xml', content.encode())


def test_xml_aggregates_duplicates_and_uses_bricklink_color_namespace():
    item = XML.removeprefix('<INVENTORY>').removesuffix('</INVENTORY>')
    palette = PartsCatalog.from_upload('wanted.xml', ('<INVENTORY>' + item * 2 + '</INVENTORY>').encode())
    assert palette.parts[('3001', 4)].max_quantity == 4
    assert ('3001', 5) not in palette.parts
    assert PartsCatalog.from_upload('wanted.xml', XML.replace('<MINQTY>2</MINQTY>', '').encode()).parts[('3001', 4)].max_quantity == 1


@pytest.mark.parametrize('data', [
    b'not a zip', studio(PLACEMENT, {'../escape.ldr': PLACEMENT}),
    studio(PLACEMENT, {'MODEL.LDR': PLACEMENT}),
    studio('x' * (MAX_CATALOG_BYTES + 1)),
])
def test_unsafe_or_oversized_studio_archives_are_rejected(data):
    with pytest.raises(ValueError):
        PartsCatalog.from_upload('bad.io', data)


@pytest.mark.parametrize('filename,data', [
    ('empty.ldr', b''), ('bad.zip', b'PK'), ('bad.xml', b'\xff'),
    ('big.csv', b'x' * (MAX_CATALOG_BYTES + 1)),
    ('bom.csv', b'LdrawId,LDrawColorId,Qty\n3001.dat,4,0\n'),
    ('bom.csv', b'LdrawId,LDrawColorId,Qty\n3001.dat,4,\n'),
])
def test_invalid_uploads_are_rejected(filename, data):
    with pytest.raises(ValueError):
        PartsCatalog.from_upload(filename, data)


def test_encrypted_studio_container_and_alternate_models():
    import base64
    data = base64.b64decode(
        'UEsDBBQACQAIAOCOUF3pXzFBIAAAACUAAAAJABwAbW9kZWwubGRyVVQJAANDq9JqQ6vSanV4CwABBPUBAAAEFAAAACbSkwU2bMhu75WTGchxgXgCPqdeMuj/pCCAvGskbju5UEsHCOlfMUEgAAAAJQAAAFBLAQIeAxQACQAIAOCOUF3pXzFBIAAAACUAAAAJABgAAAAAAAEAAACkgQAAAABtb2RlbC5sZHJVVAUAA0Or0mp1eAsAAQT1AQAABBQAAABQSwUGAAAAAAEAAQBPAAAAcwAAAAAA')
    assert PartsCatalog.from_upload("encrypted.io", data).parts[("3001", 4)].max_quantity == 1
    primary = "0 FILE main.ldr\n" + PLACEMENT
    archive = studio(primary, {"model2.ldr": primary.replace("1 4 ", "1 5 "), "modelv1.ldr": "Studio metadata"})
    assert set(PartsCatalog.from_upload("model.io", archive).parts) == {("3001", 4)}
