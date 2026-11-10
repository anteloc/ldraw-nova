"""Portable executable and resource resolution, independent of the working directory."""
import os
from pathlib import Path
import subprocess

import pytest

from ldraw_tools import common
from ldraw_tools.catalog import category_path
from ldraw_tools.discovery import DiscoveryIndex
from ldraw_tools.external import prepare_glb
from ldraw_tools.resources import search_models


def test_parts_library_precedence_and_missing_configuration(monkeypatch, tmp_path):
    monkeypatch.setattr(common, 'RESOURCE_DATA', tmp_path / 'data')
    primary = tmp_path / 'primary library'
    fallback = tmp_path / 'fallback library'
    explicit = tmp_path / 'explicit library'
    monkeypatch.setenv('LDRAW_DIR', str(primary))
    monkeypatch.setenv('LDRAWDIR', str(fallback))
    assert common.library_path(explicit) == explicit
    assert common.library_path() == primary
    monkeypatch.delenv('LDRAW_DIR')
    assert common.library_path() == fallback
    monkeypatch.setenv('LDRAW_DIR', '')
    assert common.library_path() == fallback
    monkeypatch.delenv('LDRAWDIR')
    with pytest.raises(ValueError, match='LDRAWDIR'):
        common.library_path()


def test_resources_are_project_local_from_other_working_directories(monkeypatch, tmp_path, parts):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('LDRAW_LIB_DIR', str(tmp_path / 'old library'))
    monkeypatch.setenv('MODELS_DIR', str(tmp_path / 'old models'))
    monkeypatch.delenv('LDRAW_CATEGORIES', raising=False)
    monkeypatch.delenv('LDRAW_SHADOW', raising=False)
    resources = common.ROOT / 'data'
    assert common.models_path() == resources / 'models-annotated'
    assert common.database_path() == resources / 'ldraw-info.db'
    assert category_path() == resources / 'categories'
    assert common.shadow_paths() == [resources / 'offLibShadow']
    index = DiscoveryIndex(parts, cache=tmp_path / 'cache')
    assert index.root == common.models_path()
    assert index.database == common.database_path()


def test_model_search_without_database_scans_project_sources(monkeypatch, tmp_path):
    monkeypatch.setattr(common, 'RESOURCE_DATA', tmp_path)
    models = tmp_path / 'models-annotated'
    models.mkdir()
    (models / 'boat.mpd').write_text('0 A small tugboat\n0 Name: boat.ldr\n')
    result = search_models('tugboat')
    assert result['source'] == str(models)
    assert result['results'][0]['path'] == str(models / 'boat.mpd')
    assert result['results'][0]['source_exists']


@pytest.mark.parametrize('mode,name', [('model', 'a model.mpd'), ('part', '3001.dat'), ('file', 'local model.mpd')])
@pytest.mark.parametrize('primary', [None, '', 'primary parts'])
def test_glb_wrapper_resolves_paths_with_spaces(tmp_path, mode, name, primary):
    project = tmp_path / 'project with spaces'
    project.mkdir()
    wrapper = project / 'prepare-glb.sh'
    wrapper.write_text((common.ROOT / 'prepare-glb.sh').read_text())
    launcher = project / 'ldraw-agent'
    launcher.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n')
    launcher.chmod(0o755)
    env = dict(os.environ, LDRAWDIR=str(tmp_path / 'fallback parts'), MODELS_DIR=str(tmp_path / 'old models'))
    env.pop('LDRAW_DIR', None)
    if primary is not None:
        env['LDRAW_DIR'] = str(tmp_path / primary) if primary else ''
    library = env.get('LDRAW_DIR') or env['LDRAWDIR']
    output = str(tmp_path / 'export with spaces.glb')
    result = subprocess.run(['sh', str(wrapper), '--' + mode, name, output],
                            cwd=tmp_path, env=env, text=True, capture_output=True, check=True)
    source = {'model': str(project / 'data/models-annotated' / name),
              'part': str(Path(library) / 'parts' / name), 'file': name}[mode]
    assert result.stdout.splitlines() == ['--library', library, 'glb', source, '--output', output]


def test_glb_export_uses_global_converter(parts, tmp_path, monkeypatch):
    source = tmp_path / 'source model.mpd'
    source.write_text('0 Test source\n')
    target = tmp_path / 'output model.glb'
    calls = []

    def convert(command, **kwargs):
        calls.append(command)
        assert command[0] == 'mpd2glb.sh'
        descriptions = Path(command[command.index('--descriptions') + 1])
        assert '3001.dat\t' in descriptions.read_text()
        Path(command[command.index('-o') + 1]).write_bytes(b'test conversion')
        return subprocess.CompletedProcess(command, 0, '', '')

    monkeypatch.setattr('ldraw_tools.external.subprocess.run', convert)
    prepare_glb(source, tmp_path / 'parts library', target, parts)
    assert calls[0][-1] == str(source)
    assert target.read_bytes() == b'test conversion'


def test_library_uses_project_install_without_environment(monkeypatch, tmp_path):
    monkeypatch.setattr(common, 'RESOURCE_DATA', tmp_path / 'data')
    monkeypatch.delenv('LDRAW_DIR', raising=False)
    monkeypatch.delenv('LDRAWDIR', raising=False)
    library = tmp_path / 'data/ldraw'
    (library / 'parts').mkdir(parents=True)
    monkeypatch.chdir(tmp_path.parent)
    assert common.library_path() == library
    monkeypatch.setenv('LDRAW_DIR', str(tmp_path / 'explicit'))
    assert common.library_path() == tmp_path / 'explicit'


def test_tool_resolution_local_then_path_and_renderer_override(monkeypatch, tmp_path):
    project = tmp_path / 'project with spaces'
    monkeypatch.setattr(common, 'ROOT', project)
    monkeypatch.delenv('LEOCAD', raising=False)
    monkeypatch.setattr(common.shutil, 'which', lambda name: '/system/bin/' + name)
    assert common.tool_path('jev-rerank') == '/system/bin/jev-rerank'
    local = project / 'bin/jev-rerank'
    local.parent.mkdir(parents=True)
    local.write_text('#!/bin/sh\nexit 0\n')
    local.chmod(0o644)
    assert common.tool_path('jev-rerank') == '/system/bin/jev-rerank'
    local.chmod(0o755)
    assert common.tool_path('jev-rerank') == str(local)
    renderer = project / 'bin/LeoCAD.app/Contents/MacOS/LeoCAD'
    renderer.parent.mkdir(parents=True)
    renderer.write_text('#!/bin/sh\nexit 0\n')
    renderer.chmod(0o755)
    assert common.tool_path('leocad') == str(renderer)
    monkeypatch.setenv('LEOCAD', '/custom path/LeoCAD')
    assert common.tool_path('leocad') == '/custom path/LeoCAD'


def test_glb_wrapper_uses_local_library_without_exports(tmp_path):
    project = tmp_path / 'project with spaces'
    (project / 'data/ldraw/parts').mkdir(parents=True)
    wrapper = project / 'prepare-glb.sh'
    wrapper.write_text((common.ROOT / 'prepare-glb.sh').read_text())
    launcher = project / 'ldraw-agent'
    launcher.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n')
    launcher.chmod(0o755)
    env = dict(os.environ)
    env.pop('LDRAW_DIR', None)
    env.pop('LDRAWDIR', None)
    result = subprocess.run(['sh', str(wrapper), '--part', '3001.dat'],
                            cwd=tmp_path, env=env, capture_output=True, text=True, check=True)
    assert result.stdout.splitlines()[:4] == [
        '--library', str(project / 'data/ldraw'), 'glb',
        str(project / 'data/ldraw/parts/3001.dat')]
