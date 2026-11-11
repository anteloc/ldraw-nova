"""Information retrieval must work with no parts library and never execute metadata."""
import csv
import json
from pathlib import Path
import sqlite3
from types import SimpleNamespace

import pytest

from ldraw_tools import common, part_metadata as metadata
from ldraw_tools.cli import parser, run
from ldraw_tools.discovery import PartDiscoveryIndex, search, source_id


@pytest.fixture
def sources(tmp_path, monkeypatch):
    monkeypatch.setattr(common, 'RESOURCE_DATA', tmp_path)
    monkeypatch.setattr(metadata, 'RESOURCE_DATA', tmp_path)
    monkeypatch.setattr(metadata, 'CACHE', tmp_path / 'cache')
    categories = tmp_path / 'categories'
    (categories / 'parts/minifig').mkdir(parents=True)
    (categories / 'parts/minifig/accessories.py').write_text('raise RuntimeError("never execute")\nShield="a"\nOtherShield="b"\n')
    (categories / 'parts/technic.py').write_text('Gear="gear"\n')
    (categories / 'colours.py').write_text('Red = Colour(code=4)\n')
    (categories / 'dimensions.py').write_text('PartsDimensions={"a":{"ldu_x":90,"ldu_y":90,"ldu_z":90},"b":{"ldu_x":10,"ldu_y":20,"ldu_z":30}}\n')
    monkeypatch.setenv('LDRAW_CATEGORIES', str(categories))
    path = tmp_path / 'ldraw-info.db'
    with sqlite3.connect(path) as con:
        con.executescript('''
            CREATE TABLE PARTS_DESCRIPTIONS(part TEXT PRIMARY KEY, description TEXT NOT NULL);
            CREATE VIRTUAL TABLE PARTS_DESCRIPTIONS_FTS USING fts5(part,description,content='PARTS_DESCRIPTIONS',content_rowid='rowid');
            CREATE VIEW PARTS_DESCRIPTIONS_JEV AS SELECT part || '|' || description AS full_description FROM PARTS_DESCRIPTIONS;
            CREATE TABLE PART_BBOXES(alias TEXT PRIMARY KEY, dim_x REAL, dim_y REAL, dim_z REAL, complete TEXT);
        ''')
        con.executemany('INSERT INTO PARTS_DESCRIPTIONS VALUES(?,?)', [
            ('a.dat', 'Minifig shield'), ('b.dat', 'Minifig shield'), ('gear.dat', 'Technic Gear 8 Tooth'),
            ('s/internal.dat', '~Shield subpart'), ('q.dat', 'Tile 100%_test "quoted"'),
            ('newline.dat', 'A tab\tand newline\ncarriage\rremain intact'), ('punct.dat', "O'Brien special"),
        ])
        con.executemany('INSERT INTO PART_BBOXES VALUES(?,?,?,?,?)', [('a.dat', 5, 6, 7, 'true'), ('b.dat', 99, 99, 99, 'false')])
        con.execute("INSERT INTO PARTS_DESCRIPTIONS_FTS(PARTS_DESCRIPTIONS_FTS) VALUES('rebuild')")
    return tmp_path


def test_literal_modes_and_pagination(sources):
    report = metadata.search_parts('A', field='part', match='exact')
    assert [r['code'] for r in report['results']] == ['a.dat']
    assert metadata.search_parts('MINIFIG SHIELD', field='description', match='exact')['total'] == 2
    assert metadata.search_parts('shield minifig')['total'] == 2
    assert metadata.search_parts('100%_test')['total'] == 1
    assert metadata.search_parts('%', field='description')['total'] == 1
    assert metadata.search_parts('minifig%', field='description', match='like')['total'] == 2
    assert metadata.search_parts("O'Brien")['total'] == 1
    assert metadata.search_parts("' OR 1=1 --", match='exact')['total'] == 0
    first = metadata.search_parts('shield', limit=1)
    second = metadata.search_parts('shield', limit=1, offset=1)
    assert first['truncated'] and first['total'] == 3
    assert first['results'][0]['code'] != second['results'][0]['code']
    assert metadata.search_parts('a', limit=1)['results'][0]['code'] == 'a.dat'
    with pytest.raises(ValueError):
        metadata.search_parts('shield', offset=-1)
    with pytest.raises(ValueError):
        metadata.search_parts(' ')


def test_dimensions_sources_and_filters(sources):
    rows = metadata.dimension_records(['A.DAT', 'b', 'unknown'])['results']
    assert rows[0]['selected_size_ldu'] == [5, 6, 7]
    assert rows[0]['category_estimate']['ldu_x'] == 90
    assert rows[1]['selected_source'] == 'categories/dimensions.py'
    assert rows[1]['bbox_complete'] is False
    assert rows[2]['missing'] and rows[2]['selected_source'] is None
    report = metadata.search_parts('shield', min_size=[8, 8, 8], max_size=[20, 20, 30])
    assert report['total'] == 1 and report['results'][0]['code'] == 'b.dat'
    assert metadata.search_parts('shield', max_size=[100, 100, 100], limit=1, offset=1)['total'] == 2
    for bounds in ([float('nan'), 1, 1], [-1, 2, 3]):
        with pytest.raises(ValueError):
            metadata.search_parts('shield', min_size=bounds)
    with pytest.raises(ValueError):
        metadata.search_parts('shield', min_size=[3, 3, 3], max_size=[1, 1, 1])


def test_export_complete_quoted_immutable_and_refreshable(sources):
    before = (sources / 'ldraw-info.db').read_bytes()
    report = metadata.export_descriptions()
    target = Path(report['path'])
    with target.open(newline='') as f:
        rows = list(csv.reader(f, delimiter='\t'))
    assert rows[0] == ['part', 'description'] and len(rows) == report['rows'] + 1
    assert [r[0] for r in rows[1:]] == sorted(r[0] for r in rows[1:])
    assert dict(rows[1:])['newline.dat'] == 'A tab\tand newline\ncarriage\rremain intact'
    assert sum(r[1] == 'Minifig shield' for r in rows[1:]) == 2
    assert (sources / 'ldraw-info.db').read_bytes() == before
    target.write_text('existing snapshot\n')
    assert metadata.export_descriptions()['reused']
    assert target.read_text() == 'existing snapshot\n'
    assert metadata.export_descriptions(force=True)['created']


def test_failed_export_preserves_existing_file(sources, monkeypatch):
    target = sources / 'snapshot.tsv'
    target.write_text('keep me')
    original = metadata.csv.writer
    def writer(*args, **kwargs):
        real = original(*args, **kwargs)
        def fail(row):
            raise OSError('disk error')
        return SimpleNamespace(writerow=fail)
    monkeypatch.setattr(metadata.csv, 'writer', writer)
    with pytest.raises(OSError, match='disk error'):
        metadata.export_descriptions(output=target, force=True)
    assert target.read_text() == 'keep me'
    assert not list(sources.glob('tmp*'))


def test_persistent_cache_reused_and_invalidated(sources, monkeypatch):
    from ldraw_tools import catalog
    first = catalog.catalog_data()
    metadata.category_data.cache_clear()  # Exercise reuse across processes, not just the memory cache.
    old = catalog._load
    def fail(*args):
        raise AssertionError('Parser should not run for a fresh cache')
    monkeypatch.setattr(catalog, '_load', fail)
    assert catalog.catalog_data() == first
    monkeypatch.setattr(catalog, '_load', old)
    p = sources / 'categories/parts/minifig/accessories.py'
    p.write_text(p.read_text() + 'Helmet="helmet"\n')
    assert 'minifig.accessories.Helmet' in catalog.catalog_data()[0]


def test_metadata_routes_never_initialize_library(sources, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('metadata route touched installed library')
    monkeypatch.setattr('ldraw_tools.cli.get_parts', forbidden)
    monkeypatch.setattr('ldraw_tools.cli.library_path', forbidden)
    monkeypatch.setattr('ldraw_tools.mechanism_catalog._header', forbidden)
    monkeypatch.setattr('ldraw_tools.discovery.model_sections', forbidden)
    original_open = Path.open
    def guarded_open(path, *args, **kwargs):
        if path.suffix.lower() == '.dat':
            forbidden()
        return original_open(path, *args, **kwargs)
    monkeypatch.setattr(Path, 'open', guarded_open)
    commands = [
        ['search', 'parts', 'shield'], ['dimensions', 'a', 'b'], ['export-parts-descriptions'],
        ['catalog', 'parts', 'shield', '--category', 'minifig'], ['catalog', 'categories'],
        ['discover', 'search', 'parts', 'shield', '--engine', 'fts'],
        ['discover', 'show', source_id('parts', part='a.dat')],
        ['technic', 'catalog', 'gear'],
    ]
    for command in commands:
        result, code = run(parser().parse_args(['--library', '/missing-library', *command]))
        assert code == 0
    result, _ = run(parser().parse_args(['catalog', 'parts', '--category', 'minifig']))
    assert result['total'] == 2 and all(r['available'] is None for r in result['results'])
    result, _ = run(parser().parse_args(['technic', 'catalog', 'gear']))
    assert result['parts'] and all(r['canonical_ref'] is None and r['installed'] is None for r in result['parts'])


def test_parts_fts_uses_existing_index_and_stable_ids(sources):
    index = PartDiscoveryIndex(cache=sources / 'discovery')
    report = search(index, 'parts', 'shield', engine='fts')
    assert {r['part'] for r in report['results']} == {'a.dat', 'b.dat'}
    assert report['results'][0]['id'] == source_id('parts', part=report['results'][0]['part'])
    assert not (sources / 'discovery/catalog.sqlite').exists()
    with sqlite3.connect(sources / 'ldraw-info.db') as con:
        con.execute('DROP TABLE PARTS_DESCRIPTIONS_FTS')
    with pytest.raises(ValueError, match='PARTS_DESCRIPTIONS_FTS'):
        search(PartDiscoveryIndex(), 'parts', 'shield', engine='fts')


def test_missing_and_invalid_database_do_not_scan(sources):
    with pytest.raises(ValueError, match='database missing'):
        metadata.search_parts('shield', path=sources / 'absent.db')
    invalid = sources / 'invalid.db'
    sqlite3.connect(invalid).close()
    with pytest.raises(ValueError, match='PARTS_DESCRIPTIONS'):
        metadata.search_parts('shield', path=invalid)


def test_selected_technic_inspection_does_not_read_other_parts(sources, parts, monkeypatch):
    from ldraw_tools import mechanism_catalog
    touched = []
    def header(library, code):
        touched.append(code)
        assert code == 'gear'
        return None
    monkeypatch.setattr(mechanism_catalog, '_header', header)
    report = mechanism_catalog.catalog(parts, 'gear.dat', connectors=True)
    assert touched == ['gear']
    assert report['parts'][0]['interfaces']['status'] == 'unavailable'


def test_jev_metadata_route_uses_filtered_snapshot_and_keeps_scores(sources, monkeypatch):
    identity = source_id('parts', part='a.dat')
    calls = []
    def rerank(command, **kwargs):
        calls.append(command)
        snapshot = Path(command[command.index('--db') + 1])
        with sqlite3.connect(snapshot) as con:
            rows = con.execute('SELECT id, full_description FROM candidates').fetchall()
        assert identity in {r[0] for r in rows}
        assert not any('s/internal.dat' in r[1] for r in rows)
        return SimpleNamespace(returncode=0, stderr='', stdout=json.dumps(dict(
            stats={'api_calls': 1}, exhaustive=False,
            results=[dict(source={'key': {'id': identity}}, score=0.91, rank=1)])))
    monkeypatch.setattr('ldraw_tools.discovery.subprocess.run', rerank)
    monkeypatch.setattr('ldraw_tools.discovery.tool_path', lambda _: '/tools/jev-rerank')
    monkeypatch.setattr('ldraw_tools.cli.get_parts', lambda *a, **kw: pytest.fail('loaded library'))
    report, code = run(parser().parse_args(['discover', 'search', 'parts', 'a heraldic shield', '--engine', 'jev']))
    assert code == 0 and report['results'][0]['score'] == 0.91
    assert report['results'][0]['id'] == identity and len(calls) == 1


def test_invalid_query_schema_and_dimension_gaps(sources):
    with sqlite3.connect(sources / 'ldraw-info.db') as con:
        con.execute('DROP TABLE PART_BBOXES')
    assert metadata.dimension_records(['a'])['results'][0]['selected_source'] == 'categories/dimensions.py'
    with sqlite3.connect(sources / 'ldraw-info.db') as con:
        con.execute('ALTER TABLE PARTS_DESCRIPTIONS RENAME TO OLD_DESCRIPTIONS')
    with pytest.raises(ValueError, match='PARTS_DESCRIPTIONS'):
        metadata.search_parts('a')


def test_regex_export_and_ignore_rule(sources):
    import subprocess
    target = Path(metadata.export_descriptions()['path'])
    result = subprocess.run(['rg', '-m', '1', '^a\\.dat', str(target)], capture_output=True, text=True)
    assert result.returncode == 0 and 'Minifig shield' in result.stdout
    ignored = subprocess.run(['git', 'check-ignore', 'data/parts-descriptions-full.tsv'],
                             cwd=common.ROOT, capture_output=True, text=True)
    assert ignored.returncode == 0


def test_malformed_bbox_schema_is_actionable(sources):
    with sqlite3.connect(sources / 'ldraw-info.db') as con:
        con.execute('DROP TABLE PART_BBOXES')
        con.execute('CREATE TABLE PART_BBOXES(wrong TEXT)')
    with pytest.raises(ValueError, match='alias'):
        metadata.dimension_records(['a'])


def test_part_index_refreshes_on_database_and_wal_changes(sources):
    index = PartDiscoveryIndex()
    identity = source_id('parts', part='a.dat')
    before = index.ensure()['signature']
    with sqlite3.connect(sources / 'ldraw-info.db') as con:
        con.execute('PRAGMA journal_mode=WAL')
        con.execute("UPDATE PARTS_DESCRIPTIONS SET description='Updated shield' WHERE part='a.dat'")
        con.commit()
        assert index.get(identity)['description'] == 'Updated shield'
        assert index.ensure()['signature'] != before
        con.execute("UPDATE PARTS_DESCRIPTIONS SET description='Another shield' WHERE part='a.dat'")
        con.commit()
        assert index.get(identity)['description'] == 'Another shield'
