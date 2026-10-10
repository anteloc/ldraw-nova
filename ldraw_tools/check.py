"""Fast, decisive model check: floating parts and collisions, named by plan id.

1. Occurrences come from pyldraw3; embedded .dat definitions stay single leaves.
   Near-rigid rounded rotations are snapped to the nearest rotation for analysis
   (as ldraw-mecha does); real scale or shear is reported, never corrected.
2. Connectivity uses clean ports (see partcache). Two ports mate when their
   genders differ, axes are parallel, centre lines coincide, axial spans overlap
   and their sections fit, following LDCad's snapping semantics. Parts outside
   the largest connected group are floating unless declared free.
3. Collisions test body triangles (studs omitted) of every AABB-overlapping pair:
   an edge of one part properly crossing a triangle of the other deeper than the
   tolerance is a collision. Plain bricks, plates, tiles and straight beams also
   get an oriented body-box test, because aligned overlaps leave no crossing edge.

The report names parts by plan ids ("0 // id: purpose" comments written by the
builder), joined along the submodel path, e.g. ``boom>B0-beam-3``.
Declarations go before a placement line (the builder writes them from a
placement's ``free`` / ``overlap`` fields): ``0 !NOVA FREE reason`` for an
intentionally separate object, ``0 !NOVA OVERLAP reason`` for a deliberate overlap,
which is then listed for review instead of failing.
"""
from __future__ import annotations

import math
import re
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from .collision import penetration
from .common import normalized
from .document import physical_context
from .partcache import PartCache
from .validation import validate_file
from .signature import compare, format_signature, signature

EPS = 0.02            # LDU: crossings shallower than this are touching surfaces
# Analysis-only snap of near-rigid rotations (ldraw-mecha uses 0.002). Reference
# models round coefficients to two or three decimals (0.056/0.995 is 0.34% off);
# intentional scaling is far larger, and the source is never rewritten.
ROUNDING_LIMIT = 0.01
COS_PARALLEL = math.cos(math.radians(3))
LINE_TOLERANCE = 0.6     # LDU between mated axes; reference models accumulate ~0.4 from rounding
GENERIC_TOLERANCE = 2.0  # generic interfaces (shooters, special fittings) describe volumes, not axes
TIGHT_FIT = 2.0          # LDU: official models fit grilles, fences and clips this closely; studs are judged by seating
RADIUS_TOLERANCE = 0.35
MALE_INTO = {"R": "RS", "A": "AR", "S": "S"}  # male section shape -> female shapes it fits
# Parts that interlock by design (teeth, clutch faces, cranks, ball joints, hubs in
# rims) often overlap in LDraw geometry without a port describing it. A collision
# between two parts of one family, or with a flexible part, is listed for review.
FAMILIES = {
    "gear": re.compile(r"\b(Gear|Worm|Rack|Turntable)\b", re.I),
    "drive": re.compile(r"Driving Ring|Clutch|Changeover|Transmission|Axle Joiner|Differential|Universal Joint|Cardan", re.I),
    "engine": re.compile(r"Technic Engine|Crankshaft|Piston|Connecting Rod|Pneumatic Cylinder", re.I),
    "joint": re.compile(r"Ball Joint|Ball Socket|Tow ?ball|with Ball\b|Socket|Steering Link|Suspension Arm", re.I),
    "wheel": re.compile(r"\b(Wheel|Tyre|Tire|Rim|Hub)\b(?! Arch)", re.I),
    "window": re.compile(r"Window|Glass|Pane\b|Door|Shutter|Frame", re.I),
    "clip": re.compile(r"Clip|\bBar\b|Handle|Holder", re.I),
    # Hinge halves whose finger data is missing or inferred along the wrong axis.
    "hinge": re.compile(r"\bHinge\b", re.I),
    # Roller-door segments slide in grooved bricks and panels without port data.
    "groove": re.compile(r"Roller Door|Brick\s+\d+\s*x\s*\d+\s+with\s+Groove|Panel 3 x 2 x 6", re.I),
    # Spring shooters and launchers: spring, housing and projectile interlock inside one body.
    "shooter": re.compile(r"Shooter|Launcher", re.I),
}
FIGURE = re.compile(r"Minifig|Figure", re.I)   # posed figures overlap furniture loosely: review only
FLEXIBLE = re.compile(r"String|Hose|Rubber Band|Chain|Tread|\bBand\b|Cable|Rope|Flex|Spring"
                      r"|Shock Absorber|Sticker|Plant|Flower|Lea(f|ves)|Stem|Vine|(?<!Technic )Bush\b|Grass", re.I)
# Chains, treads, strings and hoses hang on whatever they wrap or touch; official models also
# draw strings and hoses with bare primitives ("4-4cyli"). Contact connects them.
PRIMITIVE = re.compile(r"^\d+-\d+[a-z]")


def _flexible(row):
    return bool(FLEXIBLE.search(row["local"].data.description) or PRIMITIVE.match(row["code"]))


def _boxy_pair(first, second):
    """Two boxy parts are judged by their boxes, unless they meet at an angle: then the
    rounded ends of crossing beams are not their boxes, and the mesh test decides."""
    if not (first["local"].data.boxy and second["local"].data.boxy):
        return False
    turn = np.abs(first["R"].T @ second["R"])
    return bool(np.all((turn < 1e-3) | (turn > 1 - 1e-3)))


def _families(description):
    if re.search(r"Arch|Mudguard", description, re.I):
        return set()
    return {name for name, pattern in FAMILIES.items() if pattern.search(description)}


def _interlocking(first, second):
    if any(pattern.search(text) for pattern in (FLEXIBLE, FIGURE) for text in (first, second)):
        return True
    return bool(_families(first) & _families(second))


# --------------------------------------------------------------------- source ids

def placement_tags(path):
    """Map (section, line) of each type 1 line to (plan id, FREE reason, OVERLAP reason)."""
    tags, section, pending = {}, None, [None, None, None]
    for number, line in enumerate(Path(path).read_text(encoding="utf-8-sig", errors="replace").splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("0 FILE "):
            section, pending = normalized(stripped[7:].strip()), [None, None, None]
            continue
        match = re.match(r"0\s+//\s*([A-Za-z0-9_-]+):", stripped)
        if match:
            pending[0] = match.group(1)
            continue
        match = re.match(r"0\s+!NOVA\s+(FREE|OVERLAP)\b\s*(.*)", stripped)
        if match:
            pending[1 if match.group(1) == "FREE" else 2] = match.group(2).strip() or "declared"
            continue
        if stripped.startswith("1 "):
            tags[(section, number)] = tuple(pending)
            pending = [None, None, None]
    return tags


def _labels(occurrence, tags, root_name):
    hops, free, overlap = [], None, None
    for hop in occurrence.path:
        section = normalized(hop.model.name)
        plan_id, declared_free, declared_overlap = tags.get((section, hop.source_line), (None, None, None))
        free, overlap = free or declared_free, overlap or declared_overlap
        hops.append(plan_id or f"{Path(hop.model.name).stem}:{hop.source_line}")
    return ">".join(hops), free, overlap


# --------------------------------------------------------------------- transforms

def _world(occurrence):
    rotation = np.array(occurrence.matrix.rows, dtype=float)
    translation = np.array([occurrence.position.x, occurrence.position.y, occurrence.position.z], dtype=float)
    u, values, vt = np.linalg.svd(rotation)
    error = float(np.max(np.abs(values - 1)))
    if error <= 1e-8:
        return rotation, translation, "exact"
    if error <= ROUNDING_LIMIT:
        return u @ vt, translation, "normalized"
    return rotation, translation, "unsupported"


def _box_corners(lo, hi):
    return np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])


# --------------------------------------------------------------------- collisions

def _in_zones(points, zones):
    """Points inside any mated-bore cylinder (P, A, radius, axial lo, axial hi)."""
    inside = np.zeros(len(points), dtype=bool)
    for p, a, radius, low, high in zones:
        d = points - p
        s = d @ a
        radial = np.linalg.norm(d - s[:, None] * a, axis=1)
        inside |= (radial <= radius) & (s >= low) & (s <= high)
    return inside


def _crossings(edges, tris, stop):
    """Proper crossings of edges through triangles (one frame): points and shallower-end depths.

    Edges are processed in spatially sorted chunks so each chunk is only compared
    with the triangles near it; testing stops once ``stop`` crossings are found.
    """
    if not len(edges) or not len(tris):
        return np.zeros((0, 3)), np.zeros(0)
    tri_lo, tri_hi = tris.min(axis=1), tris.max(axis=1)
    origin = tris[:, 0]
    normal = np.cross(tris[:, 1] - origin, tris[:, 2] - origin)
    normal /= np.linalg.norm(normal, axis=1)[:, None]
    edges = edges[np.argsort(edges[:, :, 0].mean(axis=1))]
    edge_lo, edge_hi = edges.min(axis=1), edges.max(axis=1)
    points, depths, found = [], [], 0
    for start in range(0, len(edges), 128):
        chunk = slice(start, start + 128)
        near = np.nonzero(np.all((tri_lo <= edge_hi[chunk].max(axis=0) + EPS) & (tri_hi >= edge_lo[chunk].min(axis=0) - EPS), axis=1))[0]
        if not len(near):
            continue
        overlap = np.all((edge_lo[chunk, None, :] <= tri_hi[near][None] + EPS) & (edge_hi[chunk, None, :] >= tri_lo[near][None] - EPS), axis=2)
        ei, ti = np.nonzero(overlap)
        if not len(ei):
            continue
        ti = near[ti]
        p0, p1 = edges[chunk][ei, 0], edges[chunk][ei, 1]
        d0 = np.einsum("ij,ij->i", p0 - origin[ti], normal[ti])
        d1 = np.einsum("ij,ij->i", p1 - origin[ti], normal[ti])
        cross = (d0 * d1 < 0) & (np.minimum(np.abs(d0), np.abs(d1)) > EPS)
        if not cross.any():
            continue
        ti, p0, p1, d0, d1 = ti[cross], p0[cross], p1[cross], d0[cross], d1[cross]
        point = p0 + (p1 - p0) * (d0 / (d0 - d1))[:, None]
        a = tris[ti, 0]
        v0, v1, v2 = tris[ti, 1] - a, tris[ti, 2] - a, point - a
        d00, d01, d11 = np.einsum("ij,ij->i", v0, v0), np.einsum("ij,ij->i", v0, v1), np.einsum("ij,ij->i", v1, v1)
        d20, d21 = np.einsum("ij,ij->i", v2, v0), np.einsum("ij,ij->i", v2, v1)
        denominator = d00 * d11 - d01 * d01
        v = (d11 * d20 - d01 * d21) / denominator
        w = (d00 * d21 - d01 * d20) / denominator
        inside = (v > 1e-4) & (w > 1e-4) & (v + w < 1 - 1e-4)
        if inside.any():
            points.append(point[inside])
            depths.append(np.minimum(np.abs(d0), np.abs(d1))[inside])
            found += int(inside.sum())
            if found >= stop:
                break
    if not points:
        return np.zeros((0, 3)), np.zeros(0)
    return np.concatenate(points), np.concatenate(depths)


class _Local:
    """Per-part local AABBs of triangles and edges, computed once per check."""

    def __init__(self, data):
        self.data = data
        self.tri_lo, self.tri_hi = (data.tris.min(axis=1), data.tris.max(axis=1)) if len(data.tris) else (np.zeros((0, 3)),) * 2
        self.edge_lo, self.edge_hi = (data.edges.min(axis=1), data.edges.max(axis=1)) if len(data.edges) else (np.zeros((0, 3)),) * 2

    def select(self, lo, hi):
        tris = np.all(self.tri_lo <= hi, axis=1) & np.all(self.tri_hi >= lo, axis=1)
        edges = np.all(self.edge_lo <= hi, axis=1) & np.all(self.edge_hi >= lo, axis=1)
        return self.data.tris[tris], self.data.edges[edges]


def _outside(edges, tris, zones):
    """Drop geometry wholly inside mated bores: seated pins, axles and hinge fingers are not collisions."""
    if not zones:
        return edges, tris
    if len(edges):
        ends = _in_zones(edges.reshape(-1, 3), zones).reshape(-1, 2)
        edges = edges[~ends.all(axis=1)]
    if len(tris):
        corners = _in_zones(tris.reshape(-1, 3), zones).reshape(-1, 3)
        tris = tris[~corners.all(axis=1)]
    return edges, tris


SHIFTS = (2.0, 8.0, 32.0)  # LDU steps used to size a collision once it exceeds the tolerance


def _pair_depth(first, second, zones=(), tolerance=0.5):
    """Collision severity between two placed parts: (LDU, world point).

    Severity is the smallest shift of the second part, along either part's axes,
    that removes every crossing (tolerance, then 2, 8, 32 LDU; 64 means deeper).
    Crossing-edge lengths say nothing about depth: rounded source coordinates can
    leave a tile 0.02 LDU inside the plate below, with long edges crossing walls.
    """
    (li, ri, ti), (lj, rj, tj) = first, second
    rij, tij = ri.T @ rj, ri.T @ (tj - ti)
    corners = _box_corners(lj.data.lo, lj.data.hi) @ rij.T + tij
    lo = np.maximum(li.data.lo, corners.min(axis=0)) - EPS
    hi = np.minimum(li.data.hi, corners.max(axis=0)) + EPS
    if np.any(lo > hi):
        return 0.0, None
    local_zones = [(ri.T @ (p - ti), ri.T @ a, radius, low, high) for p, a, radius, low, high in zones]
    margin = SHIFTS[-1]   # geometry a shifted part could still reach
    tris_i, edges_i = li.select(lo - margin, hi + margin)
    back = (_box_corners(lo, hi) - tij) @ rij          # overlap box in j's frame
    tris_j, edges_j = lj.select(back.min(axis=0) - EPS, back.max(axis=0) + EPS)
    tris_j, edges_j = tris_j @ rij.T + tij, edges_j @ rij.T + tij
    edges_i, tris_i = _outside(edges_i, tris_i, local_zones)
    edges_j, tris_j = _outside(edges_j, tris_j, local_zones)

    def crossing_points(shift, stop):
        points = np.concatenate([_crossings(edges_i, tris_j + shift, stop)[0], _crossings(edges_j + shift, tris_i, stop)[0]])
        return points[~_in_zones(points, local_zones)] if local_zones and len(points) else points

    points = crossing_points(np.zeros(3), 64)
    if len(points) < 2:
        return 0.0, None
    at = ri @ points.mean(axis=0) + ti
    directions = np.unique(np.round(np.concatenate([np.eye(3), -np.eye(3), rij.T, -rij.T]), 6), axis=0)
    for magnitude in (tolerance, *SHIFTS):
        if any(len(crossing_points(d * magnitude, 2)) < 2 for d in directions):
            return magnitude, at
    return 2 * SHIFTS[-1], at


def _box_depth(first, second):
    (li, ri, ti), (lj, rj, tj) = first, second
    def box(local, rotation, translation):
        lo, hi = local.data.lo, local.data.hi
        return rotation @ ((lo + hi) / 2) + translation, rotation, (hi - lo) / 2
    a, b = box(li, ri, ti), box(lj, rj, tj)
    depth = penetration(a, b)
    return (depth or 0.0), (a[0] + b[0]) / 2


# --------------------------------------------------------------------- connectivity

def _fits(male, female):
    """Male sections fit female sections: same radius, compatible shapes (axle in round hole is a bearing)."""
    return any(shape_f in MALE_INTO.get(shape_m, shape_m) and abs(r_m - r_f) <= RADIUS_TOLERANCE
               for shape_m, r_m in male["secs"] for shape_f, r_f in female["secs"])


def _compatible(a, b):
    kinds = {a["secs"][0][0] if a["secs"] else "", b["secs"][0][0] if b["secs"] else ""}
    if kinds & {"F", "N", "G"}:
        if len(kinds) != 1:
            return False
        if "G" in kinds:
            return bool(a.get("group") and a.get("group") == b.get("group")) or (a.get("generic") == b.get("generic") and a["gender"] != b["gender"])
        if "N" in kinds:
            return a["gender"] != b["gender"] or a["gender"] == "N"
        return not (a.get("group") and b.get("group") and a["group"] != b["group"])
    if a["gender"] == b["gender"] or "N" in (a["gender"], b["gender"]):
        return False
    male, female = (a, b) if a["gender"] == "M" else (b, a)
    if male.get("compatible") and female["owner"] not in male["compatible"]:
        return False
    if female.get("compatible") and male["owner"] not in female["compatible"]:
        return False
    return _fits(male, female)


def _mates(ports):
    """Pairs of world ports (from different parts) that are mated."""
    cells = defaultdict(list)
    size = 10.0
    for index, port in enumerate(ports):
        ends = np.array([port["P"] - port["A"] * port["half"], port["P"] + port["A"] * port["half"]])
        lo = np.floor((ends.min(axis=0) - 0.5) / size).astype(int)
        hi = np.floor((ends.max(axis=0) + 0.5) / size).astype(int)
        for x in range(lo[0], hi[0] + 1):
            for y in range(lo[1], hi[1] + 1):
                for z in range(lo[2], hi[2] + 1):
                    cells[(x, y, z)].append(index)
    pairs = set()
    for members in cells.values():
        if len(members) < 2:
            continue
        for i, a in enumerate(members):
            for b in members[i + 1:]:
                if ports[a]["part"] != ports[b]["part"]:
                    pairs.add((a, b) if a < b else (b, a))
    found = []
    for a, b in pairs:
        pa, pb = ports[a], ports[b]
        delta = pb["P"] - pa["P"]
        generic = bool(pa["secs"] and pb["secs"] and pa["secs"][0][0] == pb["secs"][0][0] == "G")
        if abs(float(pa["A"] @ pb["A"])) < COS_PARALLEL:
            # A towball turns freely in its socket: same centre, any axis.
            if generic and pa["gender"] != pb["gender"] and float(np.linalg.norm(delta)) <= GENERIC_TOLERANCE \
                    and _compatible(pa, pb):
                found.append((a, b, False))
            continue
        along = float(delta @ pa["A"])
        if np.linalg.norm(delta - along * pa["A"]) > (GENERIC_TOLERANCE if generic else LINE_TOLERANCE):
            continue
        overlap = min(pa["half"], along + pb["half"]) - max(-pa["half"], along - pb["half"])
        needed = min(1.0, pa["half"] + pb["half"]) if pa["half"] + pb["half"] > 0.5 else -LINE_TOLERANCE
        if overlap < needed:
            continue
        if not _compatible(pa, pb):
            continue
        rolled = False
        if "R" in pa and "R" in pb:
            # An axle turned inside its cross hole is still connected; report it, do not disconnect it.
            ra, rb = pa["R"], pb["R"]
            angle = math.degrees(math.atan2(abs(float(ra @ np.cross(pa["A"], rb))), abs(float(ra @ rb))))
            rolled = 5 < angle < 85
        found.append((a, b, rolled))
    return found


def _components(count, edges):
    parent = list(range(count))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for a, b in edges:
        ra, rb = root(a), root(b)
        if ra != rb:
            parent[ra] = rb
    groups = defaultdict(list)
    for i in range(count):
        groups[root(i)].append(i)
    return sorted(groups.values(), key=len, reverse=True)


# --------------------------------------------------------------------- main entry

def check_model(path, parts, library, *, section=None, colour=None, tolerance=0.5, limit=12, family=None):
    started = time.perf_counter()
    model, diagnostics = validate_file(path, parts, assembly=True, section=section, colour=colour)
    errors = [d for d in diagnostics if d["severity"] == "error"]
    report = dict(file=str(path), section=section, checks_passed=False, tolerance=tolerance,
                  source_errors=[dict(code=d["code"], message=d["message"], line=d.get("line_number"), section=d.get("section")) for d in errors],
                  warnings=Counter(d["code"] for d in diagnostics if d["severity"] == "warning"))
    if model is None:
        report["seconds"] = round(time.perf_counter() - started, 2)
        return report
    rows, locals_, transforms = placed_rows(model, path, parts, library)
    result = analyze(rows, tolerance=tolerance, limit=limit)
    report.update(parts=len(rows), part_types=len(locals_), transforms=dict(transforms), **result)
    report["signature"] = signature(rows)
    if family:
        report["family"], report["style"] = family, compare(report["signature"], family)
    report["checks_passed"] = not errors and result["clean"]
    report["seconds"] = round(time.perf_counter() - started, 2)
    return report


def placed_rows(model, path, parts, library):
    """Every physical leaf of a parsed model with its plan id, module, world transform and part data."""
    view, overlay = physical_context(model, parts, section=None)
    embedded = {k: getattr(v, "path", None) for k, v in getattr(overlay, "embedded", {}).items()}
    cache = PartCache(overlay, library, {k: v for k, v in embedded.items() if v is not None})
    tags = placement_tags(path)
    rows, locals_, transforms = [], {}, Counter()
    for index, occurrence in enumerate(view.iter_occurrences(include_steps=True)):
        code = normalized(occurrence.part_code).removesuffix(".dat")
        if code not in locals_:
            locals_[code] = _Local(cache.get(code))
        rotation, translation, status = _world(occurrence)
        transforms[status] += 1
        label, free, overlap = _labels(occurrence, tags, view.name)
        top = occurrence.path[0]
        top_id = tags.get((normalized(top.model.name), top.source_line), (None, None, None))[0]
        module = (top_id or Path(top.piece.reference).stem) if len(occurrence.path) > 1 else Path(view.name).stem
        rows.append(dict(index=index, code=code, label=label, free=free, overlap=overlap, status=status, module=module,
                         section=occurrence.source_model.name, line=occurrence.source_line,
                         local=locals_[code], R=rotation, t=translation))
    return rows, locals_, transforms


def world_ports(row, part):
    """Ports of one placed part (a row with local data, R and t) in world coordinates."""
    ports = []
    for record in row["local"].data.ports:
        world = dict(record, part=part, owner=row["code"], P=row["R"] @ np.array(record["p"]) + row["t"],
                     A=row["R"] @ np.array(record["axis"]), half=float(record["half"]))
        if record.get("roll"):
            world["R"] = row["R"] @ np.array(record["roll"])
        ports.append(world)
    return ports


def world_box(row):
    corners = _box_corners(row["local"].data.lo, row["local"].data.hi) @ row["R"].T + row["t"]
    return corners.min(axis=0), corners.max(axis=0)


def analyze(rows, *, tolerance=0.5, limit=12):
    """Connectivity, collisions, seating and the module graph for placed parts.

    Each row needs: code, label, free, overlap, status, module, section, line,
    local (_Local), R (3x3 rotation) and t (translation).
    """
    # Broad phase on body boxes.
    lo = np.zeros((len(rows), 3))
    hi = np.zeros((len(rows), 3))
    for k, row in enumerate(rows):
        lo[k], hi[k] = world_box(row)
    candidates = []
    for start in range(0, len(rows), 256):
        block = slice(start, start + 256)
        overlap = np.all((lo[block, None, :] < hi[None] - 0.05) & (hi[block, None, :] > lo[None] + 0.05), axis=2)
        for i, j in zip(*np.nonzero(overlap)):
            i += start
            if i < j:
                candidates.append((i, j))
    # Connectivity first: mated bores are excluded from collision testing.
    ports, unknown = [], []
    for k, row in enumerate(rows):
        if not row["local"].data.ports or row["status"] == "unsupported":
            unknown.append(k)
            continue
        ports.extend(world_ports(row, k))
    mates = _mates(ports)
    rolled = [(a, b) for a, b, turned in mates if turned]
    mates = [(a, b) for a, b, _ in mates]
    part_edges = [(ports[a]["part"], ports[b]["part"]) for a, b in mates]
    mated_pairs = {(min(i, j), max(i, j)) for i, j in part_edges}
    # Interlocking parts without port data (glass in a frame, tyre on a spoked wheel,
    # spider gear in a differential) count as connected when their bodies overlap.
    family_edges = [(i, j) for i, j in candidates if (i, j) not in mated_pairs and
                    (_families(rows[i]["local"].data.description) & _families(rows[j]["local"].data.description)
                     or _flexible(rows[i]) or _flexible(rows[j]))]
    part_edges += family_edges
    # Stud seating: the receptacle must start at the stud's base plane. LDCad does not
    # orient receptacle axes consistently, so measure its near end along the stud's
    # outward axis: 0 seated, positive a gap, negative sunk.
    seating = []
    for a, b in mates:
        stud, socket = (ports[a], ports[b]) if ports[a]["kind"] == "stud" else (ports[b], ports[a])
        if stud["kind"] != "stud" or socket["gender"] != "F" or socket.get("centered", True):
            continue
        base = stud["P"] - stud["A"] * stud["half"]
        offset = float((socket["P"] - base) @ stud["A"]) - socket["half"]
        if abs(offset) > tolerance:
            seating.append((offset, stud["part"], socket["part"]))
    zones = defaultdict(list)
    for a, b in mates:
        pa, pb = ports[a], ports[b]
        radii = [r for _, r in pa["secs"] + pb["secs"] if r > 0]
        if not radii:
            continue
        along = float((pb["P"] - pa["P"]) @ pa["A"])
        low, high = min(-pa["half"], along - pb["half"]) - 1.0, max(pa["half"], along + pb["half"]) + 1.0
        radius = max(radii) + 1.0
        if any(shape == "G" for shape, _ in pa["secs"] + pb["secs"]):
            low, high = min(low, -radius), max(high, radius)   # ball-like interfaces extend both ways
        key = (min(pa["part"], pb["part"]), max(pa["part"], pb["part"]))
        zones[key].append((pa["P"], pa["A"], radius, low, high))
    collisions, duplicates, reviews = [], [], []
    for i, j in candidates:
        a, b = rows[i], rows[j]
        if a["code"] == b["code"] and np.allclose(a["t"], b["t"], atol=0.05) and np.allclose(a["R"], b["R"], atol=1e-3):
            duplicates.append((i, j))
            continue
        if (i, j) in mated_pairs or "unsupported" in (a["status"], b["status"]):
            continue   # connected parts may interlock (tyre on rim, ring on joiner); seating is checked above
        first, second = (a["local"], a["R"], a["t"]), (b["local"], b["R"], b["t"])
        depth, at = _pair_depth(first, second, zones.get((i, j), ()), tolerance)
        boxes = _boxy_pair(a, b)
        if boxes:
            box, box_at = _box_depth(first, second)
            if box > depth:
                depth, at = box, box_at
        if depth > tolerance:
            # A shallow overlap between shaped parts is a tight fit to review; two boxes overlapping is an error.
            tight = depth <= TIGHT_FIT and not boxes
            special = a["overlap"] or b["overlap"] or tight or _flexible(a) or _flexible(b) or \
                _interlocking(a["local"].data.description, b["local"].data.description)
            (reviews if special else collisions).append((depth, i, j, at))
    collisions.sort(key=lambda c: -c[0])
    reviews.sort(key=lambda c: -c[0])
    groups = _components(len(rows), part_edges)
    unknown_set = set(unknown)
    judged = [g for g in groups if not (len(g) == 1 and g[0] in unknown_set)]
    main = max(judged, key=lambda g: sum(1 for k in g if not rows[k]["free"]), default=[])
    floating_groups = [g for g in judged if g is not main and not all(rows[k]["free"] for k in g)]
    # Minifigures, their accessories and the hoses they hold are not construction: report, do not fail.
    figure_groups = [g for g in floating_groups if all(FIGURE.search(rows[k]["local"].data.description)
                                                        or FLEXIBLE.search(rows[k]["local"].data.description) for k in g)]
    floating_groups = [g for g in floating_groups if g not in figure_groups]
    floating = sum(len(g) for g in floating_groups)
    # Module graph: mates between top-level modules.
    module_edges = Counter()
    for a, b in mates:
        ma, mb = rows[ports[a]["part"]]["module"], rows[ports[b]["part"]]["module"]
        if ma != mb:
            male = ports[a] if ports[a]["gender"] == "M" else ports[b]
            module_edges[(min(ma, mb), max(ma, mb), male["kind"])] += 1
    module_sizes = Counter(row["module"] for row in rows)
    module_floating = Counter(rows[k]["module"] for g in floating_groups for k in g)

    def name(k):
        row = rows[k]
        return dict(id=row["label"], part=row["code"], section=row["section"], line=row["line"], index=int(k))
    def contact(item):
        d, i, j, at = item
        return dict(depth=round(d, 2), a=name(i), b=name(j), at=[round(float(v), 1) for v in at] if at is not None else None)
    return dict(
        clean=not collisions and not duplicates and not floating and not seating,
        collisions=[contact(c) for c in collisions[:limit]], collision_count=len(collisions),
        seating=[dict(offset=round(o, 2), stud=name(s), on=name(t)) for o, s, t in sorted(seating, key=lambda x: -abs(x[0]))[:limit]],
        seating_count=len(seating), rolled_axles=len(rolled),
        reviews=[contact(c) for c in reviews[:limit]], review_count=len(reviews),
        duplicates=[dict(a=name(i), b=name(j)) for i, j in duplicates[:limit]], duplicate_count=len(duplicates),
        floating_count=floating, group_count=len(judged), main_group=len(main),
        floating_groups=[dict(size=len(g), parts=[name(k) for k in g[:limit]]) for g in floating_groups[:limit]],
        free_parts=sum(1 for row in rows if row["free"]),
        figure_parts=sum(len(g) for g in figure_groups),
        unknown=[name(k) for k in unknown[:limit]], unknown_count=len(unknown),
        unsupported_transforms=[name(k) for k, row in enumerate(rows) if row["status"] == "unsupported"][:limit],
        modules=[dict(module=m, parts=n, floating=module_floating.get(m, 0)) for m, n in module_sizes.most_common()],
        module_edges=[dict(a=a, b=b, kind=kind, count=n) for (a, b, kind), n in sorted(module_edges.items(), key=lambda kv: -kv[1])],
        mates=len(mates), candidate_pairs=len(candidates),
    )


# --------------------------------------------------------------------- presentation

def _who(item):
    hops = item["id"].split(">")
    label = ">".join(hops[-2:]) if len(hops) <= 2 else "…>" + ">".join(hops[-2:])
    return f"{label} ({item['part']})"


def format_report(report, limit=8):
    head = f"check {report['file']}" + (f" --section {report['section']}" if report.get("section") else "")
    source = [f"  source {e['code']}: {e['message']} (line {e['line']})" for e in report.get("source_errors", [])[:limit]]
    if "parts" not in report:
        return "\n".join([f"FAIL  {head}: the model could not be parsed ({report['seconds']} s)", *source])
    status = "PASS" if report["checks_passed"] else "FAIL"
    lines = [f"{status}  {head}  {report['parts']} parts, {report['part_types']} types, {report['seconds']} s", *source,
             f"  floating {report['floating_count']} (in {max(0, report['group_count'] - 1)} groups; main group {report['main_group']})"
             f" · collisions {report['collision_count']} (> {report['tolerance']} LDU) · badly seated {report['seating_count']}"
             f" · duplicates {report['duplicate_count']}"]
    for group in report["floating_groups"][:limit]:
        names = ", ".join(_who(p) for p in group["parts"][:4]) + (f", … +{group['size'] - 4}" if group["size"] > 4 else "")
        lines.append(f"  floating [{group['size']}]: {names}")
    for c in report["collisions"][:limit]:
        lines.append(f"  collision {c['depth']} LDU: {_who(c['a'])} × {_who(c['b'])} at {c['at']}")
    for d in report["duplicates"][:limit]:
        lines.append(f"  duplicate: {_who(d['a'])} = {_who(d['b'])}")
    for s in report["seating"][:limit]:
        where = "sunk into" if s["offset"] < 0 else "floating above"
        lines.append(f"  badly seated: {_who(s['on'])} {where} {_who(s['stud'])} by {abs(s['offset'])} LDU")
    if report.get("rolled_axles"):
        lines.append(f"  {report['rolled_axles']} axle(s) turned inside their cross holes (connected; rotate them to align)")
    if report.get("review_count"):
        first = report["reviews"][0]
        lines.append(f"  review {report['review_count']} overlap(s): interlocking parts (gears, clutches, joints, hubs, flexible) or tight fits ≤ {TIGHT_FIT:g} LDU,"
                     f" e.g. {first['depth']} LDU {_who(first['a'])} × {_who(first['b'])}")
    if report["unknown_count"]:
        lines.append(f"  no connector data ({report['unknown_count']}, connectivity not judged): "
                     + ", ".join(_who(u) for u in report["unknown"][:4]))
    if report["free_parts"]:
        lines.append(f"  declared free: {report['free_parts']} parts")
    if report.get("figure_parts"):
        lines.append(f"  loose figures: {report['figure_parts']} minifigure parts and accessories (not judged)")
    if report.get("family"):
        lines.append("  " + format_signature(report["signature"], report["family"]))
    if report.get("transforms", {}).get("normalized"):
        lines.append(f"  {report['transforms']['normalized']} rounded rotations normalized for analysis")
    return "\n".join(lines)


def _node(name):
    return re.sub(r"[^A-Za-z0-9_]", "_", name)


def mermaid_graph(report):
    """Actual module-connection graph: one node per top-level module, edges labelled kind × count."""
    lines = ["flowchart LR"]
    for m in report["modules"]:
        extra = f", {m['floating']} floating" if m["floating"] else ""
        lines.append(f'  {_node(m["module"])}["{m["module"]} ({m["parts"]} parts{extra})"]' + (":::bad" if m["floating"] else ""))
    for e in report["module_edges"]:
        lines.append(f'  {_node(e["a"])} ---|"{e["count"]} {e["kind"]}"| {_node(e["b"])}')
    lines.append("  classDef bad stroke:#d33,stroke-width:3px")
    return "\n".join(lines)


EDGE = re.compile(r"([A-Za-z0-9_-]+)\s*(?:\[[^\]]*\]|\([^)]*\)|\{[^}]*\})?\s*(?:-->|---|-\.->|==>|-\.-)\s*(?:\|[^|]*\|\s*)?([A-Za-z0-9_-]+)")


def intended_edges(text):
    """Module pairs a design brief's Mermaid flowchart says must connect."""
    pairs = set()
    for block in re.findall(r"```mermaid\s*\n(.*?)```", text, re.S) or [text]:
        for line in block.splitlines():
            for a, b in EDGE.findall(line):
                if a.lower() not in {"flowchart", "graph", "classdef"}:
                    pairs.add(tuple(sorted((_node(a), _node(b)))))
    return pairs


def compare_intended(report, text):
    actual = {tuple(sorted((_node(e["a"]), _node(e["b"])))) for e in report["module_edges"]}
    known = {_node(m["module"]) for m in report["modules"]}
    wanted = intended_edges(text)
    return dict(missing=[list(p) for p in sorted(wanted - actual) if set(p) <= known],
                unknown_modules=sorted({n for p in wanted for n in p} - known),
                unplanned=[list(p) for p in sorted(actual - wanted)])
