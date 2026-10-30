import hashlib
import json
from pathlib import Path

import pytest
from PIL import Image

from ldraw_tools.mosaic import compose_mosaic
from ldraw_tools.cli import parser, run


def fixture(tmp_path, mode='views'):
    panels = []
    for i, colour in enumerate(['red', 'blue', 'green', 'yellow']):
        path = tmp_path / f'{i}.png'
        Image.new('RGB', (400, 300), colour).save(path)
        panels.append(dict(image=path.name, label=f'View {i}', subject='selected assembly in parent coordinates',
                           camera={'position': [0, -400, -400], 'target': [0, 0, 0], 'up': [0, -1, 0], 'fov': 30}))
    manifest = tmp_path/'panels.json'
    manifest.write_text(json.dumps(dict(mode=mode, panels=panels)))
    return manifest


def test_grid_order_provenance_and_no_source_changes(tmp_path):
    manifest = fixture(tmp_path)
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    report = compose_mosaic(manifest, tmp_path/'board.png', panel_width=400)
    with Image.open(report['output']) as board:
        for panel, colour in zip(report['panels'], [(255,0,0),(0,0,255),(0,128,0),(255,255,0)]):
            x,y,w,h = panel['image_box']
            assert board.getpixel((x+w//2,y+h//2)) == colour
            assert panel['sha256'] == hashlib.sha256((tmp_path/Path(panel['image']).name).read_bytes()).hexdigest()
    assert all((tmp_path/name).read_bytes() == data for name,data in before.items())
    assert report['visual_review'] == 'pending'
    assert json.loads((tmp_path/'board.json').read_text()) == report


def test_analysis_preserves_registration_and_rejects_mismatches(tmp_path):
    manifest = fixture(tmp_path, 'analysis')
    report = compose_mosaic(manifest, tmp_path/'board.png')
    assert len({tuple(p['image_box'][2:]) for p in report['panels']}) == 1
    data = json.loads(manifest.read_text())
    data['panels'][1]['camera']['fov'] = 45
    manifest.write_text(json.dumps(data))
    with pytest.raises(ValueError, match='same camera'):
        compose_mosaic(manifest, tmp_path/'other.png')
    data['panels'][1]['camera']['fov'] = 30
    manifest.write_text(json.dumps(data))
    Image.new('RGB',(300,400)).save(tmp_path/'1.png')
    with pytest.raises(ValueError, match='dimensions'):
        compose_mosaic(manifest, tmp_path/'other.png')
    assert not (tmp_path/'other.png').exists()


def test_overwrite_protection_and_cli_without_library(tmp_path, monkeypatch):
    manifest = fixture(tmp_path)
    for key in ['LDRAW_DIR', 'LDRAWDIR']:
        monkeypatch.delenv(key, raising=False)
    for command in ['manual','mechanism']:
        report, status = run(parser().parse_args([command,'mosaic',str(manifest),'--output',str(tmp_path/f'{command}.png')]))
        assert status == 0
    with pytest.raises(ValueError, match='exists'):
        compose_mosaic(manifest, tmp_path/'manual.png')
    with pytest.raises(ValueError, match='overwrite inputs'):
        compose_mosaic(manifest, tmp_path/'0.png', force=True)
    with pytest.raises(ValueError, match='overwrite inputs'):
        compose_mosaic(manifest, tmp_path/'panels.png', force=True)


def test_different_aspects_letterbox_without_cropping(tmp_path):
    manifest = fixture(tmp_path)
    Image.new('RGB',(200,400),'blue').save(tmp_path/'1.png')
    report = compose_mosaic(manifest,tmp_path/'board.png',panel_width=400)
    assert report['panels'][1]['image_box'][2:] == [150,300]
    assert report['panels'][0]['image_box'][2:] == [400,300]
