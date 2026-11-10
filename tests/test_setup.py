"""Exercise the local installer without network access or global tool writes."""
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

from ldraw_tools.common import ROOT


def executable(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('#!/bin/sh\nset -eu\n' + body)
    path.chmod(0o755)


def test_local_tool_install_and_library_rerun(tmp_path):
    project = tmp_path / 'project with spaces'
    (project / 'scripts').mkdir(parents=True)
    shutil.copy(ROOT / 'scripts/setup-tools.sh', project / 'scripts/setup-tools.sh')
    executable(project / 'bin/uv', '''
if [ "$1" = --version ]; then echo 'uv 0.9.3'; exit 0; fi
printf '%s|%s|%s|%s|%s\n' "$UV_TOOL_DIR" "$UV_TOOL_BIN_DIR" "$UV_CACHE_DIR" "$UV_PYTHON_INSTALL_DIR" "$*" >> "$INSTALL_LOG"
''')
    archive = tmp_path / 'complete.zip'
    with zipfile.ZipFile(archive, 'w') as z:
        z.writestr('ldraw/LDConfig.ldr', '0 fixture\n')
        z.writestr('ldraw/parts/3001.dat', '0 brick\n')
        z.writestr('ldraw/p/stud.dat', '0 stud\n')
    commands = tmp_path / 'commands'
    executable(commands / 'curl', '''
while [ "$1" != --output ]; do shift; done
cp "$TEST_ARCHIVE" "$2"
printf 'download\n' >> "$DOWNLOAD_LOG"
''')
    env = dict(os.environ, PATH=str(commands) + os.pathsep + os.environ['PATH'],
               TEST_ARCHIVE=str(archive), INSTALL_LOG=str(tmp_path / 'install.log'),
               DOWNLOAD_LOG=str(tmp_path / 'download.log'))
    command = ['sh', str(project / 'scripts/setup-tools.sh')]
    subprocess.run(command, cwd=tmp_path, env=env, check=True, capture_output=True)
    assert (project / 'data/ldraw/parts/3001.dat').exists()
    installs = (tmp_path / 'install.log').read_text().splitlines()
    assert len(installs) == 4
    for row in installs:
        assert row.startswith('|'.join(str(project / p) for p in
                              ['bin/uv-tools', 'bin', '.cache/uv', 'bin/python']) + '|')
        assert 'tool install --python 3.12 --reinstall https://' in row
    assert 'ldraw_xray-0.5.0' in installs[0]
    assert 'jev_rerank-0.5.0' in installs[1]
    assert 'ldraw_annotator_nova-0.5.0' in installs[2]
    assert 'lsynth_nova-0.5.0' in installs[3]
    subprocess.run(command, cwd=tmp_path, env=env, check=True, capture_output=True)
    assert (tmp_path / 'download.log').read_text().splitlines() == ['download']
    assert not list((project / '.cache').glob('setup.*'))
    (project / 'data/ldraw/LDConfig.ldr').unlink()
    result = subprocess.run(command, cwd=tmp_path, env=env, capture_output=True, text=True)
    assert result.returncode == 2
    assert 'incomplete' in result.stderr
    assert (project / 'data/ldraw/parts/3001.dat').exists()


def test_viewer_install_reuses_pin_and_preserves_install_on_failure(tmp_path):
    import tarfile
    project = tmp_path / 'project with spaces'
    (project / 'scripts').mkdir(parents=True)
    shutil.copy(ROOT / 'scripts/setup-viewer.sh', project / 'scripts/setup-viewer.sh')
    source = tmp_path / 'archive/library'
    for name in ['public/assets/ldbi/js/three.min.js', 'public/assets/ldbi/js/LDRLoader.js',
                 'public/assets/js/ldraworgscene.js', 'public/assets/js/WebGL.js', 'LICENSE']:
        path = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('fixture')
    archive = tmp_path / 'viewer.tar.gz'
    with tarfile.open(archive, 'w:gz') as tar:
        tar.add(source, arcname='library')
    commands = tmp_path / 'commands'
    executable(commands / 'curl', '''
while [ "$1" != --output ]; do shift; done
cp "$TEST_ARCHIVE" "$2"
printf 'download\n' >> "$DOWNLOAD_LOG"
''')
    env = dict(os.environ, PATH=str(commands) + os.pathsep + os.environ['PATH'],
               TEST_ARCHIVE=str(archive), DOWNLOAD_LOG=str(tmp_path / 'downloads'))
    cmd = ['sh', str(project / 'scripts/setup-viewer.sh')]
    for _ in range(2):
        subprocess.run(cmd, env=env, capture_output=True, check=True)
    vendor = project / 'bin/ldbi-viewer'
    assert (tmp_path / 'downloads').read_text().splitlines() == ['download']
    assert (vendor / 'LICENSE-ldraworg-library.txt').read_text() == 'fixture'
    (vendor / '.revision').write_text('old revision')
    archive.write_text('broken download')
    failed = subprocess.run(cmd, env=env, capture_output=True)
    assert failed.returncode != 0
    assert (vendor / 'js/ldraworgscene.js').read_text() == 'fixture'
    assert not list((project / '.cache').glob('viewer-setup.*'))
