"""Preserve source geometry and distinguish checked callouts from a flat car."""
from collections import Counter
from copy import deepcopy
import hashlib
import json
import runpy

import pytest

from ldraw_tools.builder import build_plan, load_plan
from ldraw_tools.common import ROOT, jsonable, normalized
from ldraw_tools.document import parse_source, section_table, source_blocks
from ldraw_tools.geometry import analyze_geometry
from ldraw_tools.manuals import current_manual

REFERENCE = ROOT / 'examples/snot/ferrari-f40'
ANNOTATE = runpy.run_path(str(REFERENCE / 'prepare.py'))['annotate']


def read_json(path):
    return json.loads(path.read_text())


def test_semantic_annotation_preserves_source_records_and_section_identity():
    source = REFERENCE / 'original.ldr'
    annotations = read_json(REFERENCE / 'annotations.json')
    manifest = read_json(REFERENCE / 'sections.json')
    annotated = REFERENCE / 'ferrari-f40.mpd'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == annotations['source_sha256']
    assert ANNOTATE(source, annotations).encode() == annotated.read_bytes()
    assert hashlib.sha256(annotated.read_bytes()).hexdigest() == manifest['annotated_sha256']
    before, after = source_blocks(source), source_blocks(annotated)
    assert list(before) == list(after)
    assert len(before) == 74

    def operational(block):
        return [line for _, line in block if line.split() and (
            line.split()[0] in {'1', '2', '3', '4', '5'}
            or line.startswith(('0 STEP', '0 ROTSTEP', '0 BFC', '0 ROTATION', '0 !TEXMAP')))]

    for section in before:
        assert operational(before[section]) == operational(after[section]), section
        original_credits = [line for _, line in before[section]
                            if line.startswith(('0 Author:', '0 !LICENSE'))]
        assert all(line in [text for _, text in after[section]] for line in original_credits)


@pytest.mark.parametrize('change', ['source_hash', 'missing_section', 'duplicate_section'])
def test_annotation_rejects_stale_or_ambiguous_metadata(change):
    annotations = deepcopy(read_json(REFERENCE / 'annotations.json'))
    if change == 'source_hash':
        annotations['source_sha256'] = '0' * 64
    elif change == 'missing_section':
        annotations['sections'].pop()
    else:
        annotations['sections'].append(annotations['sections'][0])
    with pytest.raises(ValueError):
        ANNOTATE(REFERENCE / 'original.ldr', annotations)


def test_context_annotations_do_not_invent_declared_parent_links():
    source = parse_source(REFERENCE / 'original.ldr')
    table = section_table(source)
    manifest = read_json(REFERENCE / 'sections.json')
    assert manifest['main_is_flat'] and not manifest['geometry_edited']
    assert len(source.pieces) == 1156
    assert not any(normalized(p.reference) in table for p in source.pieces)
    assert sum(row['reachable_from_main'] for row in manifest['sections']) == 1
    for row in manifest['sections']:
        key = normalized(row['section'])
        parents = [s.name for s in table.values() for p in s.pieces
                   if normalized(p.reference) == key]
        children = Counter(p.reference for p in table[key].pieces
                           if normalized(p.reference) in table)
        assert row['declared_parents'] == parents
        assert row['declared_children'] == children
        assert row['reachable_from_main'] == (table[key] is source)
        assert all(1 <= step <= 83 for step in row['context_steps'])


@pytest.mark.parametrize('name,section,count', [
    ('body-mount', 'subModel-6.ldr', 5),
    ('door-rail', 'subModel-35.ldr', 6),
    ('rear-lamp', 'subModel-53.ldr', 8),
    ('window-louver', 'subModel-57.ldr', 5),
    ('fascia-core', 'subModel-63.ldr', 6),
])
def test_exported_study_rebuilds_original_placements_and_connections(official, name, section, count):
    folder = REFERENCE / 'studies' / name
    _, manual = current_manual(folder)  # Also verifies all copied evidence hashes.
    assert manual['source_checks_passed'] and manual['bom_matches']
    assert manual['source']['sha256'] == read_json(REFERENCE / 'sections.json')['annotated_sha256']
    _, model, diagnostics = build_plan(load_plan(folder / 'scene.plan.json'), official)
    assert not [d for d in diagnostics if d['severity'] == 'error']
    original = section_table(parse_source(REFERENCE / 'original.ldr'))[normalized(section)]

    def placements(model):
        return Counter((normalized(o.reference), o.colour.code,
                        tuple(jsonable(o.position)), tuple(tuple(row) for row in o.matrix.rows))
                       for o in model.iter_occurrences())

    assert placements(model) == placements(original)
    report = analyze_geometry(model, official, contacts='all')
    assert report['complete']
    assert report['occurrence_count'] == count
    assert report['optimistic_component_count'] == 1
    assert not [d for d in report['diagnostics'] if d['severity'] == 'error']


def test_catalog_keeps_complete_car_errors_visible_and_repairs_traceable():
    entries = read_json(REFERENCE / 'catalog.json')['entries']
    assert len(entries) == 74
    repairs = set()
    for index, entry in enumerate(entries):
        folder = REFERENCE / 'catalog' / f'{index:02}'
        card = read_json(folder / 'card.json')
        checks = read_json(folder / 'source-checks.json')
        assert card['assembly_checks_passed'] == checks['source_checks_passed'] == (index != 0)
        assert entry['source_checks_passed'] == card['assembly_checks_passed']
        assert card['status'] == ('reference' if index else 'adaptation_needed')
        assert card['bom_comparison']['matches'] is True
        assert card['contacts_checked'] is False
        assert card['visual_review']['decision'] == 'technique'
        assert card['visual_review']['image_sha256'] == hashlib.sha256(
            (folder / 'renders/home.png').read_bytes()).hexdigest()
        if index == 0:
            errors = [d for d in checks['geometry']['diagnostics'] if d['severity'] == 'error']
            assert len(errors) == 25
            assert {d['code'] for d in errors} == {'assembly.body_overlap'}
        for change in card['source_repairs']:
            if change['kind'] == 'normalize_rounded_rotation':
                assert change['max_coefficient_change'] < 0.0001
                repairs.add((change['section'], change['source_line']))
    assert len(repairs) == 14
    assert {section for section, _ in repairs} == {
        'subModel-42.ldr', 'subModel-68.ldr', 'subModel-69.ldr'}
