"""Selector index, library routing and containment without browser dependencies."""
import importlib.util
import json
from pathlib import Path
from threading import Thread
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

from ldraw_tools.common import ROOT


@pytest.fixture
def selector(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location('model_selector', ROOT / 'model-selector/serve.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name, path in [('ROOT', tmp_path), ('MODELS', tmp_path / 'data/models-annotated'),
                       ('LDRAW', tmp_path / 'data/ldraw'), ('INDEX', tmp_path / 'output/index.json')]:
        monkeypatch.setattr(module, name, path)
    module.MODELS.mkdir(parents=True)
    return module


def test_index_counts_reused_modules_embedded_parts_and_encoded_names(selector):
    source = selector.MODELS / 'boat #1.mpd'
    source.write_text('''0 FILE root.ldr
0 Blue boat
1 4 0 0 0 1 0 0 0 1 0 0 0 1 child.ldr
1 4 0 0 0 1 0 0 0 1 0 0 0 1 child.ldr
0 FILE child.ldr
0 Child
1 4 0 0 0 1 0 0 0 1 0 0 0 1 3001.dat
1 4 0 0 0 1 0 0 0 1 0 0 0 1 embedded.dat
0 FILE embedded.dat
0 Geometry
1 16 0 0 0 1 0 0 0 1 0 0 0 1 primitive.dat
''')
    models = selector.build_index()
    assert models == [dict(name='boat #1.mpd', path='data/models-annotated/boat #1.mpd',
                           url='/models/boat%20%231.mpd', description='Blue boat', parts=4)]
    assert json.loads(selector.INDEX.read_text()) == models
    assert selector.count_parts({'cycle.ldr': ['cycle.ldr', '3001.dat']}) == 1


def test_http_routes_and_traversal_are_confined(selector, monkeypatch, tmp_path):
    parts = selector.LDRAW / 'parts'
    parts.mkdir(parents=True)
    (parts / '3001.dat').write_text('0 Test brick\n')
    (selector.MODELS / 'boat #1.mpd').write_text('0 Boat\n')
    monkeypatch.setattr(selector.Handler, 'ROUTES', {'/models/': selector.MODELS, '/ldraw/': selector.LDRAW})
    secret = tmp_path / 'secret.txt'
    secret.write_text('not served')
    server = selector.ThreadingHTTPServer(('127.0.0.1', 0), selector.Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f'http://127.0.0.1:{server.server_port}'
    try:
        for path, expected in [('/ldraw-id/3001.DAT', '0 Test brick\n'),
                               ('/models/boat%20%231.mpd', '0 Boat\n')]:
            with urlopen(base + path) as response:
                assert response.read().decode() == expected
        for path in ['/models/%2e%2e/%2e%2e/secret.txt', '/ldraw-id/../../secret.txt', '/../../secret.txt']:
            with pytest.raises(HTTPError) as error:
                urlopen(base + path)
            assert error.value.code == 404
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_library_environment_precedence(monkeypatch, tmp_path):
    script = ROOT / 'model-selector/serve.py'
    def load():
        spec = importlib.util.spec_from_file_location('selector_env', script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.LDRAW
    monkeypatch.setenv('LDRAW_DIR', str(tmp_path / 'primary'))
    monkeypatch.setenv('LDRAWDIR', str(tmp_path / 'fallback'))
    assert load() == tmp_path / 'primary'
    monkeypatch.setenv('LDRAW_DIR', '')
    assert load() == tmp_path / 'fallback'
    monkeypatch.delenv('LDRAWDIR')
    assert load() == ROOT / 'data/ldraw'
