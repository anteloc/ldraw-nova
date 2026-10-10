"""Cached per-part data for fast checks: solid triangles and clean connection ports.

Ports. LDCad shadow metadata is authored for snapping, so a part whose metadata
coverage is complete keeps only its authored interfaces. pyldraw3 also infers
features from primitives; on such parts those guesses are noise (for example pin
holes on the npeghole cut-outs between Technic holes, or hole faces instead of
centred bores, male axles read into axle holes, and stud receptacles that reach
10 LDU below a brick and fake a mate across a one-plate gap). One exception: a
complete part with no authored socket at all takes its inferred stud receptacles,
clipped to its body, and a plate-height part also a socket under each top stud. Newer
library revisions remodel parts with primitives the
shadow library predates; the 2026-05 wings 41769a/41770a keep authored studs while
their receptacles are inferred only. Parts without complete metadata fall back to
the inferred features and primitive studs. Exact duplicate descriptions merge into
one port.

Triangles. Expanded directly from the library files, omitting male stud
primitives: studs are mating geometry, judged through ports, not solids.

Everything is cached under .cache/partdata-<key>/, keyed by the library index
signature and shadow sources, so a changed library starts a fresh cache.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from ldraw.connection_types import (AnnularProfile, ConnectionSource, CylindricalProfile,
                                    FingerProfile, GenericProfile)

from .common import CACHE, normalized

VERSION = 14
AUTHORED = {ConnectionSource.LDCAD_SHADOW, ConnectionSource.LDCAD_INLINE, ConnectionSource.OVERRIDE,
            ConnectionSource.SHORTCUT, ConnectionSource.STUDIO}
EMPTY = np.zeros((0, 3, 3))
# Plain rectangular parts whose oriented body box is a faithful solid: aligned
# overlaps between them leave no crossing edges, so they get a box test too.
BOXY = re.compile(r"^~?(Brick|Plate|Tile|Technic Beam)\s+\d+(\.\d+)?(\s*x\s*\d+(\.\d+)?){0,2}"
                  r"(\s+with Groove)?$", re.I)


def _stud_title(title):
    """Male stud primitives: 'Stud', 'Stud Open', 'Stud Group 2 x 2', not tubes."""
    title = title.lstrip("~").strip()
    return bool(re.match(r"Stud\b", title)) and not re.match(r"Stud (Tube|Underside|Duplo Tube)", title)


class LibraryFiles:
    """Case-insensitive index of the library's parts/ and p/ trees (LDraw names use \\ and any case)."""

    def __init__(self, root):
        self.root = Path(root)
        self.index = {}
        for base in ("parts", "p"):
            top = self.root / base
            for dirpath, _, filenames in os.walk(top):
                relative = Path(dirpath).relative_to(top).as_posix()
                prefix = "" if relative == "." else relative.lower() + "/"
                for name in filenames:
                    self.index.setdefault((base, prefix + name.lower()), Path(dirpath) / name)

    def find(self, name):
        key = name.replace("\\", "/").strip().lower()
        return self.index.get(("parts", key)) or self.index.get(("p", key))


class TriangleExpander:
    """Expand LDraw type 3/4 geometry through type 1 references, memoized per file."""

    def __init__(self, files, embedded=None):
        self.files, self.embedded = files, {normalized(k): Path(v) for k, v in (embedded or {}).items()}
        self.memo, self.titles, self.missing = {}, {}, set()

    def path(self, name):
        key = normalized(name).strip()
        return self.embedded.get(key) or self.files.find(key)

    def title(self, name):
        key = normalized(name).strip()
        if key not in self.titles:
            path = self.path(key)
            self.titles[key] = ""
            if path is not None:
                with open(path, encoding="utf-8-sig", errors="replace") as handle:
                    self.titles[key] = next(handle, "0").strip().removeprefix("0").strip()
        return self.titles[key]

    def is_stud(self, name, depth=0):
        title = self.title(name)
        moved = re.match(r"~Moved to (\S+)", title)
        if moved and depth < 4:
            return self.is_stud(moved.group(1) + ("" if moved.group(1).lower().endswith(".dat") else ".dat"), depth + 1)
        return _stud_title(title)

    def placements(self, name, wanted, depth=0):
        """(file, R, t) for every reference to a file in ``wanted``, through nested subfiles."""
        path = self.path(name)
        if path is None or depth > 12:
            return []
        found = []
        with open(path, encoding="utf-8-sig", errors="replace") as handle:
            for line in handle:
                t = line.split()
                if len(t) < 15 or t[0] != "1":
                    continue
                child = normalized(" ".join(t[14:])).strip()
                values = np.array(t[2:14], dtype=float)
                R, offset = values[3:].reshape(3, 3), values[:3]
                if child in wanted:
                    found.append((child, R, offset))
                elif not self.is_stud(child):
                    found.extend((c, R @ r, R @ o + offset) for c, r, o in self.placements(child, wanted, depth + 1))
        return found

    def triangles(self, name, depth=0):
        key = normalized(name).strip()
        if key in self.memo:
            return self.memo[key]
        path = self.path(key)
        if path is None or depth > 40:
            self.missing.add(key)
            self.memo[key] = EMPTY
            return EMPTY
        chunks = []
        with open(path, encoding="utf-8-sig", errors="replace") as handle:
            for line in handle:
                t = line.split()
                if not t:
                    continue
                if t[0] == "3" and len(t) >= 11:
                    chunks.append(np.array(t[2:11], dtype=float).reshape(1, 3, 3))
                elif t[0] == "4" and len(t) >= 14:
                    q = np.array(t[2:14], dtype=float).reshape(4, 3)
                    chunks.append(np.stack([q[[0, 1, 2]], q[[0, 2, 3]]]))
                elif t[0] == "1" and len(t) >= 15:
                    child = " ".join(t[14:])
                    if self.is_stud(child):
                        continue
                    sub = self.triangles(child, depth + 1)
                    if len(sub):
                        values = np.array(t[2:14], dtype=float)
                        chunks.append(sub @ values[3:].reshape(3, 3).T + values[:3])
        result = np.concatenate(chunks) if chunks else EMPTY
        self.memo[key] = result
        return result


def unique_edges(tris):
    """Distinct triangle edges; shared edges are tested once."""
    if not len(tris):
        return np.zeros((0, 2, 3))
    edges = tris[:, [0, 1, 1, 2, 2, 0]].reshape(-1, 2, 3)
    # Order each edge's endpoints lexicographically so A-B and B-A compare equal.
    a, b = np.round(edges[:, 0], 3), np.round(edges[:, 1], 3)
    flip = (a[:, 0] > b[:, 0]) | ((a[:, 0] == b[:, 0]) & ((a[:, 1] > b[:, 1]) | ((a[:, 1] == b[:, 1]) & (a[:, 2] > b[:, 2]))))
    canonical = np.where(flip[:, None, None], edges[:, ::-1], edges)
    keys = np.round(canonical.reshape(-1, 6), 3)
    _, keep = np.unique(keys, axis=0, return_index=True)
    edges = canonical[np.sort(keep)]
    return edges[np.linalg.norm(edges[:, 1] - edges[:, 0], axis=1) > 1e-6]


def _vector(value):
    return [round(float(value.x), 4), round(float(value.y), 4), round(float(value.z), 4)]


def _unit(values):
    array = np.array(values, dtype=float)
    length = np.linalg.norm(array)
    return (array / length).round(6).tolist() if length > 1e-9 else [0.0, 0.0, 0.0]


def port_record(feature):
    """One interface as plain data: axial midpoint, unit axis, half length and fitting sections."""
    profile = feature.profile
    record = dict(kind=str(feature.kind), gender={"male": "M", "female": "F"}.get(str(feature.role), "N"),
                  p=_vector(feature.axial_midpoint), axis=_unit(_vector(feature.axis)),
                  half=round(float(feature.length) / 2, 4), group=feature.group, centered=bool(feature.centered),
                  source="authored" if feature.source in AUTHORED else "inferred")
    if isinstance(profile, CylindricalProfile):
        rigid = [s for s in profile.sections if not s.flexible] or list(profile.sections)
        record["secs"] = sorted({(str(s.shape)[0].upper(), round(float(s.radius), 2)) for s in rigid})
        if record["secs"] and any(shape in "AS" for shape, _ in record["secs"]):
            record["roll"] = _unit(_vector(feature.radial))
    elif isinstance(profile, FingerProfile):
        record["secs"] = [("F", round(float(profile.radius), 2))]
        record["fingers"] = [round(float(v), 2) for v in profile.sequence]
    elif isinstance(profile, AnnularProfile):
        record["secs"] = [("N", round(float(profile.radius), 2))]
    elif isinstance(profile, GenericProfile):
        # Generic interfaces (ball joints, special clips) carry their size in bounds.
        extent = max((float(v) for v in (profile.bounds.dimensions if profile.bounds else ())), default=0.0)
        record["secs"] = [("G", round(extent, 2))]
        record["generic"] = profile.name
    else:
        record["secs"] = []
    if feature.compatible_parts:
        record["compatible"] = [normalized(c).removesuffix(".dat") for c in feature.compatible_parts]
    return record


def _clipped(record, lo, hi):
    """The record with its span cut to the body box along its axis, or None if almost nothing is left."""
    axis, p = np.array(record["axis"]), np.array(record["p"])
    reach = _box_support(lo, hi, axis)
    centre = float(p @ axis)
    start, end = max(centre - record["half"], reach[0]), min(centre + record["half"], reach[1])
    if end - start < 0.5:
        return None
    middle = (start + end) / 2
    return dict(record, p=(p + axis * (middle - centre)).round(4).tolist(), half=round((end - start) / 2, 4))


def _box_support(lo, hi, axis):
    corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    reach = corners @ axis
    return float(reach.min()), float(reach.max())


def _curated(kind, gender, p, axis, half, secs):
    return dict(kind=kind, gender=gender, p=list(p), axis=list(axis), half=half, group=None, centered=True,
                source="curated", secs=[list(s) for s in secs])


# Interfaces the LDCad shadow library clears or never authored, measured from the part's own
# geometry. Calibrated on official Technic sets (docs/dev/reports/technic-corpus.md).
CURATED_PORTS = {
    # Engine crankshaft: the shadow keeps only the centre axle hole; the throw is an axle stub
    # (x=-10, z -9.8..20, capped by axleend.dat) that enters the next crank or a beam.
    "2853": [_curated("axle", "M", (-10.0, 0.0, 5.1), (0.0, 0.0, 1.0), 14.9, [("A", 6.0)])],
}


def clean_ports(geometry, body=None, hinges=(), curated=()):
    """Authored interfaces when metadata coverage is complete, else every inferred feature.

    ``body`` (lo, hi) clips the inferred receptacles a complete part without authored sockets takes.
    ``hinges`` are authored finger hinges from referenced primitives; they replace the part's
    inferred hinges unless the part's own metadata already authors one. ``curated`` ports
    (CURATED_PORTS) add interfaces the shadow library lacks.
    """
    metadata = geometry.connection_metadata
    complete = metadata is not None and str(metadata.coverage) == "complete"
    features = [f for f in geometry.connections if not complete or f.source in AUTHORED]
    records = [port_record(f) for f in features if f.confidence > 0] + [dict(c) for c in curated]
    if complete and not any(r["gender"] == "F" for r in records):
        inferred = [port_record(f) for f in geometry.connections if f.source not in AUTHORED and f.confidence > 0]
        inferred = [r for r in inferred if r["kind"] == "stud_receptacle"]
        if body is not None:
            inferred = [c for c in (_clipped(r, *body) for r in inferred) if c is not None]
            if body[1][1] - body[0][1] <= 8.5:   # plate height: every top stud has a socket under it
                taken = [(r["p"][0], r["p"][2]) for r in inferred]
                for stud in [r for r in records if r["kind"] == "stud" and r["axis"][1] < -0.99]:
                    if all(abs(stud["p"][0] - x) > 1 or abs(stud["p"][2] - z) > 1 for x, z in taken):
                        inferred.append(dict(kind="stud_receptacle", gender="F", p=[stud["p"][0], round(float(body[1][1]) - 2, 4), stud["p"][2]],
                                             axis=[0.0, -1.0, 0.0], half=2.0, group=None, centered=False, source="inferred",
                                             secs=[("R", 6.0)]))
        records += inferred
    if not complete:
        # Partial metadata: a guess of a kind the part already authors is noise (the inverted
        # slope 4287 gets studs inside its body); other guessed sockets are cut to the body.
        authored_kinds = {r["kind"] for r in records if r["source"] == "authored"}
        kept = []
        for r in records:
            if r["source"] not in ("authored", "curated") and authored_kinds:
                if r["kind"] in authored_kinds:
                    continue
                if r["gender"] == "F" and body is not None:
                    r = _clipped(r, *body)
                    if r is None:
                        continue
            kept.append(r)
        records = kept
    if hinges or any(r["kind"] == "hinge" and r["source"] == "authored" for r in records):
        # Inferred hinges run along the fingers' extent, not the pivot: keep only real data.
        authored = [r for r in records if r["kind"] == "hinge" and r["source"] == "authored"]
        extra = [h for h in hinges if all(np.linalg.norm(np.subtract(h["p"], a["p"])) > 2 for a in authored)]
        records = [r for r in records if r["kind"] != "hinge"] + authored + extra
    if not any(r["kind"] == "stud" for r in records) and not complete:
        for stud in geometry.top_studs:
            up = _unit(_vector(stud.up))
            records.append(dict(kind="stud", gender="M", p=(np.array(_vector(stud.position)) + 2 * np.array(up)).round(4).tolist(),
                                axis=up, half=2.0, group=None, centered=False, source="primitive-stud", secs=[("R", 6.0)]))
    unique, seen = [], set()
    for r in records:
        axis = np.array(r["axis"])
        if axis[np.argmax(np.abs(axis))] < 0:
            axis = -axis
        key = (r["kind"], r["gender"], tuple(np.round(r["p"], 2)), tuple(np.round(axis, 3)), round(r["half"], 2), tuple(map(tuple, r["secs"])))
        if key not in seen:
            seen.add(key)
            unique.append(r)
    order = {k: i for i, k in enumerate(["stud", "stud_receptacle", "pin_hole", "axle_hole", "pin", "axle", "bar", "clip", "hinge", "rim_seat", "tyre_bead", "generic"])}
    unique.sort(key=lambda r: (order.get(r["kind"], 99), r["p"][2], r["p"][0], r["p"][1]))
    counts = {}
    for r in unique:
        counts[r["kind"]] = counts.get(r["kind"], -1) + 1
        r["name"] = f"{r['kind']}[{counts[r['kind']]}]"
    return unique, "complete" if complete else (str(metadata.coverage) if metadata is not None else "none")


@dataclass
class PartData:
    code: str
    description: str
    tris: np.ndarray
    edges: np.ndarray
    lo: np.ndarray
    hi: np.ndarray
    ports: list = field(default_factory=list)
    coverage: str = "none"
    boxy: bool = False
    missing: list = field(default_factory=list)

    @property
    def tri_lo(self):
        return self.tris.min(axis=1) if len(self.tris) else np.zeros((0, 3))

    @property
    def tri_hi(self):
        return self.tris.max(axis=1) if len(self.tris) else np.zeros((0, 3))


class PartCache:
    """Load or build PartData for library and embedded parts."""

    def __init__(self, parts, library, embedded_paths=None):
        self.parts, self.library = parts, Path(library)
        signature_file = Path(parts.path).parent / "signature"
        signature = signature_file.read_text() if signature_file.exists() else ""
        shadows = ";".join(str(getattr(s, "source", "")) for s in getattr(parts, "_connection_shadow_libraries", []))
        key = hashlib.sha256(f"{VERSION}|{self.library}|{signature}|{shadows}".encode()).hexdigest()[:12]
        self.directory = CACHE / f"partdata-{key}"
        self.embedded_paths = {normalized(k): Path(v) for k, v in (embedded_paths or {}).items()}
        self._files = None
        self._expander = None
        self._fingers = None
        self.memory = {}

    @property
    def finger_primitives(self):
        """Authored finger hinges of shadow primitives (h1, h2, clh*), in primitive coordinates.

        When a part references one of these primitives, pyldraw3 replaces its authored
        SNAP_FGR with a primitive guess along the wrong axis (the fingers' extent instead of
        the pivot), so hinged parts never mate once turned. The authored data is carried
        into the part by `_primitive_hinges` instead.
        """
        if self._fingers is None:
            self._fingers = {}
            for shadow in getattr(self.parts, "_connection_shadow_libraries", []):
                folder = Path(str(getattr(shadow, "source", ""))) / "p"
                for path in sorted(folder.glob("*.dat")) if folder.is_dir() else []:
                    if "SNAP_FGR" not in path.read_text(errors="replace"):
                        continue
                    try:
                        geometry = self.parts.geometry(path.stem)
                    except Exception:  # a primitive the parts library lacks
                        continue
                    records = [port_record(f) for f in geometry.connections
                               if f.source in AUTHORED and f.confidence > 0 and isinstance(f.profile, FingerProfile)]
                    if records:
                        self._fingers[path.name.lower()] = records
        return self._fingers

    def _primitive_hinges(self, code):
        """Authored finger hinges of the hinge primitives a part references, in part coordinates."""
        wanted = self.finger_primitives
        records = []
        for child, R, offset in self.expander.placements(code + ".dat", wanted) if wanted else []:
            for record in wanted[child]:
                axis = R @ np.array(record["axis"])
                scale = float(np.linalg.norm(axis))
                if scale < 1e-9:
                    continue
                records.append(dict(record, p=(R @ np.array(record["p"]) + offset).round(4).tolist(),
                                    axis=(axis / scale).round(6).tolist(), half=round(record["half"] * scale, 4),
                                    fingers=[round(v * scale, 3) for v in record.get("fingers", [])]))
        return records

    @property
    def expander(self):
        if self._expander is None:
            if self._files is None:
                self._files = LibraryFiles(self.library)
            self._expander = TriangleExpander(self._files, {k + ".dat": v for k, v in self.embedded_paths.items()})
        return self._expander

    def _file(self, code):
        if code in self.embedded_paths:
            digest = hashlib.sha256(self.embedded_paths[code].read_bytes()).hexdigest()[:16]
            return self.directory / f"embedded-{digest}.npz"
        safe = re.sub(r"[^a-z0-9._-]", "_", code)
        return self.directory / f"{safe}.npz"

    def get(self, code):
        code = normalized(code).removesuffix(".dat")
        if code in self.memory:
            return self.memory[code]
        path = self._file(code)
        data = None
        if path.exists():
            try:
                with np.load(path, allow_pickle=False) as stored:
                    meta = json.loads(bytes(stored["meta"]).decode())
                    data = PartData(code=code, tris=stored["tris"].astype(float), edges=stored["edges"].astype(float),
                                    lo=np.array(meta["lo"]), hi=np.array(meta["hi"]), **{k: meta[k] for k in
                                    ("description", "ports", "coverage", "boxy", "missing")})
            except (OSError, ValueError, KeyError):
                data = None
        if data is None:
            data = self._build(code)
            self.directory.mkdir(parents=True, exist_ok=True)
            meta = dict(description=data.description, ports=data.ports, coverage=data.coverage, boxy=data.boxy,
                        missing=data.missing, lo=data.lo.tolist(), hi=data.hi.tolist())
            temporary = path.with_suffix(f".{os.getpid()}.tmp.npz")
            np.savez_compressed(temporary, tris=data.tris.astype(np.float32), edges=data.edges.astype(np.float32),
                                meta=np.frombuffer(json.dumps(meta).encode(), dtype=np.uint8))
            temporary.replace(path)
        self.memory[code] = data
        return data

    def _library_twin(self, code, geometry):
        """An embedded copy of a library part ('42110 - 49294') may borrow its authored ports."""
        match = re.search(r"(\d{3,}[a-z0-9]*)$", code)
        if code not in self.embedded_paths or not match or geometry.bounds is None:
            return None
        twin = match.group(1)
        if twin in self.embedded_paths or self.parts.find_part(code=twin) is None:
            return None
        library = self.parts.geometry(twin)
        if library.bounds is None:
            return None
        same = np.allclose(_vector(library.bounds.min), _vector(geometry.bounds.min), atol=1.0) and \
            np.allclose(_vector(library.bounds.max), _vector(geometry.bounds.max), atol=1.0)
        return library if same else None

    def _library_description(self, code, description):
        """An embedded copy titled only by its number ('35188') takes the library part's description.

        Reports and family rules (gears, hubs, flexible parts) read descriptions, and a bare
        number hides that the copy is, say, a clutch gear.
        """
        match = re.search(r"(\d{3,}[a-z0-9]*)$", code)
        if code not in self.embedded_paths or not match or description.lower() != match.group(1):
            return description
        if self.parts.find_part(code=match.group(1)) is None:
            return description
        return (self.parts.geometry(match.group(1)).description or description).strip()

    def _moved_target(self, code, description):
        """'~Moved to 32532a': the target code when the stub places it unrotated at the origin."""
        match = re.match(r"~Moved to (\S+)", description)
        if not match or code in self.embedded_paths:
            return None
        target = normalized(match.group(1)).removesuffix(".dat")
        path = self.expander.path(code + ".dat")
        if self.parts.find_part(code=target) is None or path is None:
            return None
        lines = [line.split() for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines()]
        references = [t for t in lines if len(t) >= 15 and t[0] == "1"]
        if len(references) != 1 or [float(v) for v in references[0][2:14]] != [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1]:
            return None
        return target

    def _build(self, code):
        geometry = self.parts.geometry(code)
        target = self._moved_target(code, (geometry.description or "").strip())
        if target is not None:
            # A renamed part: its stub has no shadow data of its own, so its ports were guesses.
            moved = self.get(target)
            return PartData(code=code, description=moved.description, tris=moved.tris, edges=moved.edges, lo=moved.lo,
                            hi=moved.hi, ports=moved.ports, coverage=moved.coverage + f" (moved to {target})",
                            boxy=moved.boxy, missing=moved.missing)
        twin = self._library_twin(code, geometry)
        expander = self.expander
        before = set(expander.missing)
        tris = expander.triangles(code + ".dat")
        tris = tris[np.linalg.norm(np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0]), axis=1) > 1e-9] if len(tris) else tris
        if len(tris):
            lo, hi = tris.reshape(-1, 3).min(axis=0), tris.reshape(-1, 3).max(axis=0)
        elif geometry.bounds is not None:
            lo, hi = np.array(_vector(geometry.bounds.min)), np.array(_vector(geometry.bounds.max))
        else:
            lo = hi = np.zeros(3)
        ports, coverage = clean_ports(twin or geometry, body=(lo, hi), hinges=self._primitive_hinges(code),
                                      curated=CURATED_PORTS.get(code, ()))
        description = self._library_description(code, (geometry.description or "").strip())
        return PartData(code=code, description=description, tris=tris, edges=unique_edges(tris), lo=lo, hi=hi,
                        ports=ports, coverage=coverage + (f" (ports from library {twin.code})" if twin else ""),
                        boxy=bool(BOXY.match(description)), missing=sorted(expander.missing - before))
