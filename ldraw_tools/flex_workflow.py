"""Check constraints, synthesize and measure before publishing a flexible asset."""
from __future__ import annotations

from pathlib import Path
import hashlib
import shutil
from tempfile import TemporaryDirectory

from . import flex
from .common import CACHE, atomic_write, dumps
from .flex_constraints import check
from .flex_review import check_asset


def require_pass(report):
    if not report['checks_passed']:
        raise ValueError('Flexible asset checks failed: ' + dumps(report['diagnostics']))


def prepare_asset(asset, parts):
    """Materialize a declared source in the disposable project cache."""
    source = Path(asset['source']).resolve()
    namespace = asset['namespace']
    key = hashlib.sha256(str(source).encode() + b'\0' + source.read_bytes() + b'\0' + namespace.encode()).hexdigest()
    return build(source, CACHE / 'flex-assets' / key / (namespace + '.mpd'), parts,
                 namespace=namespace, force=True, checks=asset.get('checks'), timeout=asset.get('timeout', 90))


def publish(staged, output):
    """Roll back both files if publishing either one fails."""
    pairs = [(staged, output), (staged.with_suffix('.manifest.json'), output.with_suffix('.manifest.json'))]
    backups, replaced = {}, []
    for _, target in pairs:
        if target.exists():
            backup = staged.parent / ('previous-' + target.name)
            shutil.copyfile(target, backup)
            backups[target] = backup
    try:
        for source, target in pairs:
            source.replace(target)
            replaced.append(target)
    except OSError:
        for target in reversed(replaced):
            if target in backups:
                backups[target].replace(target)
            else:
                target.unlink()
        raise


def build(source, output, parts, *, namespace=None, force=False, timeout=90, cache=True, checks=None):
    """One checked operation; failures leave the previous asset and manifest intact.

    ``checks`` takes the same named geometric limits as ``check_asset``. Cache
    reuse skips only the LSynth subprocess, never current checks or packaging.
    The lower-level ``flex.build`` remains available for diagnostic experiments.
    """
    source, output = Path(source).resolve(), Path(output).resolve()
    manifest = output.with_suffix('.manifest.json')
    if output.suffix.lower() != '.mpd':
        raise ValueError('Flex output must be an .mpd asset')
    if source in (output, manifest):
        raise ValueError('Keep the original constraints separate from the generated asset')
    if any(p.exists() and not p.is_file() for p in (output, manifest)):
        raise ValueError('Flex output and manifest must be files, not directories')
    if not force and (output.exists() or manifest.exists()):
        raise ValueError('Flex output already exists; use --force to rebuild')
    constraints = check(source)
    require_pass(constraints)
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix='.flex-', dir=output.parent) as temp:
        staged = Path(temp) / output.name
        report = flex.build(source, staged, parts, namespace=namespace, timeout=timeout, cache=cache)
        measured = check_asset(source, staged, source_report=constraints, parts=parts, **(checks or {}))
        require_pass(measured)
        if hashlib.sha256(source.read_bytes()).hexdigest() != constraints['source_sha256']:
            raise ValueError('Constraints changed during review; rerun on the saved revision')
        measured['asset'] = str(output)
        report.update(output=str(output), manifest=str(manifest), checks_passed=True, validation=measured)
        atomic_write(staged.with_suffix('.manifest.json'), dumps({k: v for k, v in report.items() if k != 'manifest'}) + '\n')
        publish(staged, output)
    return report
