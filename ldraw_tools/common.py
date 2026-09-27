from __future__ import annotations

import dataclasses
import hashlib
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

import numpy as np
from ldraw import Parts, Vector, Matrix

ROOT = Path(__file__).resolve().parents[1]
RESOURCE_DATA = ROOT / "data"
CACHE = ROOT / ".cache"
DATA = Path(__file__).parent / "data"


def library_path(value=None):
    path = value or os.environ.get("LDRAW_DIR") or os.environ.get("LDRAWDIR")
    if not path:
        raise ValueError("Set LDRAW_DIR (or LDRAWDIR) to the parts library, or pass --library")
    return Path(path).expanduser().resolve()


def models_path(value=None):
    """Project-owned sources; an explicit path is reserved for library callers/tests."""
    return Path(value or RESOURCE_DATA / "models-annotated").expanduser().resolve()


def database_path(value=None):
    return Path(value or RESOURCE_DATA / "ldraw-info.db").expanduser().resolve()


def atomic_write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    try:
        with NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
            tmp = Path(f.name)
            f.write(text)
        tmp.replace(path)
    finally:
        if tmp:
            tmp.unlink(missing_ok=True)


def normalized(name):
    return name.replace("\\", "/").casefold()


def jsonable(value):
    if isinstance(value, Vector):
        return [float(value.x), float(value.y), float(value.z)]
    if isinstance(value, Matrix):
        return value.rows
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if hasattr(value, "to_dict"):
        return jsonable(value.to_dict())
    if dataclasses.is_dataclass(value):
        return {f.name: jsonable(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [jsonable(v) for v in value]
    return value


def dumps(value):
    return json.dumps(jsonable(value), indent=2, ensure_ascii=False, allow_nan=False)


def shadow_paths(sources=None):
    """Explicit sources replace defaults; [] disables all external shadows."""
    if sources is None:
        configured = os.environ.get("LDRAW_SHADOW")
        sources = configured.split(os.pathsep) if configured else ([RESOURCE_DATA / "offLibShadow"] if (RESOURCE_DATA / "offLibShadow").is_dir() else [])
    result = []
    for source in sources:
        path = Path(source).expanduser().resolve()
        if not path.exists():
            raise ValueError(f"LDCad shadow library missing at {path}")
        if path.is_dir() and not any((path / name).is_dir() for name in ("parts", "p")):
            raise ValueError(f"Shadow directory must contain parts/ or p/: {path}")
        if path.is_file():
            import zipfile
            if not zipfile.is_zipfile(path):
                raise ValueError(f"Shadow archive must be a ZIP or CSL: {path}")
        if path not in result:
            result.append(path)
    return result


def get_parts(root=None, *, refresh=False, shadows=None):
    """Supply pyldraw3's required index without writing into the source library."""
    root = library_path(root)
    if not (root / "parts").is_dir() or not (root / "p").is_dir():
        raise ValueError(f"LDraw library missing at {root}; set LDRAW_DIR (or LDRAWDIR) or --library")
    target = CACHE / ("library-" + hashlib.sha256(str(root).encode()).hexdigest()[:12])
    target.mkdir(parents=True, exist_ok=True)
    # Only a read-through view: library geometry and colour files remain authoritative.
    for entry in root.iterdir():
        if entry.name.lower() in {"parts", "p", "ldconfig.ldr"}:
            link = target / entry.name
            if not link.is_symlink():
                link.symlink_to(entry, target_is_directory=entry.is_dir())
    if not any(p.name.lower() == "ldconfig.ldr" for p in target.iterdir()):
        raise ValueError(f"LDConfig.ldr missing from {root}")
    files = sorted((root / "parts").glob("*.dat"))
    signature = hashlib.sha256("\n".join(
        f"{p.name}:{p.stat().st_size}:{p.stat().st_mtime_ns}" for p in files
    ).encode()).hexdigest()
    stamp = target / "signature"
    index = target / "parts.lst"
    if refresh or not index.exists() or not stamp.exists() or stamp.read_text() != signature:
        rows = []
        for p in files:
            with p.open(encoding="utf-8-sig", errors="replace") as f:
                title = next(f, "0").strip().removeprefix("0").strip()
            rows.append(f"{p.name} {title}")
        atomic_write(index, "\n".join(rows) + "\n")
        atomic_write(stamp, signature)
    parts = Parts(index)
    for source in shadow_paths(shadows):
        parts.add_connection_shadow(source)
    return parts


def issue(code, message, *, line=None, section=None, severity="error", **extra):
    return dict(code=code, severity=severity, message=message, line_number=line, section=section, **extra)
