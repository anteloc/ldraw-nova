"""Construction kit: place real parts on the stud grid or by connecting ports.

Agents should not compute rotation matrices or stacking heights. Two verbs cover
nearly every placement, and each one is checked against the parts already placed
(collisions, stud seating). A problem raises KitError at the generator line that
caused it, naming the ids involved and suggesting a fix.

* ``place(ref, colour, cell=(x, z), level=n, turn=deg)``: System grid. ``cell`` is the
  stud cell of the footprint's minimum corner (20 LDU per stud); ``level`` is the
  part's bottom in plate heights above the ground (8 LDU; a brick is 3 plates).
  Stack with ``level=below.top``.
* ``mate(ref, colour, port, to=other.port(name))``: connect two real interfaces: a pin
  into a hole, an axle through a hole, a stud into a socket, hinge, clip or wheel.
  ``ldraw-agent ports PART`` lists the port names of any part.

``add`` places explicitly in LDU when nothing else fits; ``axes={"y": "X", "z": "-Z"}``
says where two local axes point instead of writing a matrix. ``section`` builds a
submodel with the same verbs. ``save`` writes the MPD and an equivalent JSON plan
(rebuildable with ``ldraw-agent build``), then prints the full ``check`` verdict.

World axes (LDraw): X right, Y down (negative Y is up), Z toward the viewer.

    from ldraw_tools.kit import Model
    m = Model("pier", "A small pier")
    deck = m.place("3034", "Reddish_Brown", cell=(0, 0), level=3)
    post = m.place("3005", "Dark_Bluish_Grey", cell=(0, 0), level=0)
    m.save("output/pier/pier.mpd")
"""
from __future__ import annotations

import json
import math
import re
import sqlite3
from pathlib import Path

import numpy as np
from ldraw import Matrix, Model as LDrawModel, Piece, Vector
from ldraw.lines import Comment

from . import check as checker
from .builder import serialize_mpd
from .common import ROOT, atomic_write, get_parts, library_path, normalized
from .partcache import PartCache

STUD, PLATE = 20.0, 8.0
DIRECTIONS = {"X": (1, 0, 0), "-X": (-1, 0, 0), "Y": (0, 1, 0), "-Y": (0, -1, 0), "Z": (0, 0, 1), "-Z": (0, 0, -1),
              "UP": (0, -1, 0), "DOWN": (0, 1, 0)}


# Common rectangular parts by length in studs (1-wide unless named _2).
BRICKS = {1: "3005", 2: "3004", 3: "3622", 4: "3010", 6: "3009", 8: "3008"}
PLATES_1 = {1: "3024", 2: "3023", 3: "3623", 4: "3710", 6: "3666", 8: "3460"}
PLATES_2 = {2: "3022", 3: "3021", 4: "3020", 6: "3795", 8: "3034"}
TILES_1 = {1: "3070b", 2: "3069b", 3: "63864", 4: "2431", 6: "6636", 8: "4162"}


class KitError(ValueError):
    """A placement that would collide, sit badly or reference something unknown."""


def _split(length, offset, sizes):
    """Lengths summing to ``length`` from ``sizes``: an optional first piece of ``offset``, then longest first."""
    pieces, left = [], length
    if offset and offset in sizes and length > offset:
        pieces.append(offset)
        left -= offset
    available = sorted(sizes, reverse=True)
    while left:
        size = next((s for s in available if s <= left and (left - s == 0 or any(t <= left - s for t in available))), None)
        if size is None:
            raise KitError(f"cannot split {length} studs into lengths {sorted(sizes)}")
        pieces.append(size)
        left -= size
    return pieces


def _unit(vector):
    vector = np.asarray(vector, dtype=float)
    return vector / np.linalg.norm(vector)


def _direction(value):
    return _unit(DIRECTIONS[value.upper()] if isinstance(value, str) else value)


def yaw(degrees):
    """Rotation about the vertical axis; positive turns +X toward -Z (counter-clockwise seen from above)."""
    a = math.radians(degrees)
    c, s = round(math.cos(a), 12), round(math.sin(a), 12)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def axes_matrix(axes):
    """Rotation from two named axes, e.g. {"y": "X", "z": "-Z"}: local y points to world +X."""
    given = {k.lower(): _direction(v) for k, v in axes.items()}
    if len(given) != 2 or not set(given) <= {"x", "y", "z"}:
        raise KitError("axes needs exactly two of x, y, z, e.g. {'y': 'X', 'z': '-Z'}")
    x, y, z = given.get("x"), given.get("y"), given.get("z")
    if x is None:
        x = np.cross(y, z)
    elif y is None:
        y = np.cross(z, x)
    else:
        z = np.cross(x, y)
    rotation = np.column_stack([x, y, z])
    if not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-9):
        raise KitError(f"axes {axes} are not perpendicular")
    return rotation


def _reference(axis):
    """Deterministic perpendicular to a port axis: roll 0 aligns these between mated parts."""
    for candidate in ((0, 1, 0), (0, 0, 1), (1, 0, 0)):
        candidate = np.array(candidate, dtype=float)
        if abs(candidate @ axis) < 0.9:
            return _unit(candidate - (candidate @ axis) * axis)


def _rodrigues(axis, degrees):
    a = math.radians(degrees)
    k = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    return np.eye(3) + math.sin(a) * k + (1 - math.cos(a)) * k @ k


class Port:
    """A named interface of a placed part, in its section's coordinates."""

    def __init__(self, handle, record):
        self.handle, self.record, self.name = handle, record, record["name"]
        self.kind, self.gender = record["kind"], record["gender"]
        self.P = handle.R @ np.array(record["p"]) + handle.t
        self.A = handle.R @ np.array(record["axis"])
        self.reference = handle.R @ _reference(np.array(record["axis"]))

    def __repr__(self):
        return f"<{self.handle.id}.{self.name} {self.kind} at {np.round(self.P, 2).tolist()} axis {np.round(self.A, 3).tolist()}>"


class Handle:
    """A placed part (or submodel instance) returned by every verb."""

    def __init__(self, section, entry):
        self.section, self.entry = section, entry
        self.id, self.ref, self.R, self.t = entry["id"], entry["ref"], entry["R"], entry["t"]
        self.data = entry.get("data")

    def port(self, name):
        if self.data is None:
            raise KitError(f"{self.id} is a submodel; mate to a part inside it")
        for record in self.data.ports:
            if record["name"] == name:
                return Port(self, record)
        raise KitError(f"{self.ref} has no port {name!r}; it has: {', '.join(r['name'] for r in self.data.ports) or 'none'}")

    def ports(self, kind=None):
        return [r["name"] for r in (self.data.ports if self.data else []) if kind is None or r["kind"] == kind]

    @property
    def box(self):
        corners = checker._box_corners(self.data.lo, self.data.hi) @ self.R.T + self.t
        return corners.min(axis=0), corners.max(axis=0)

    @property
    def top(self):
        """Level (plates above ground) of this part's top surface: stack the next part with level=part.top."""
        return round(-self.box[0][1] / PLATE, 4) + 0.0

    @property
    def bottom(self):
        return round(-self.box[1][1] / PLATE, 4) + 0.0

    def __repr__(self):
        return f"<{self.id}: {self.ref} at {np.round(self.t, 2).tolist()}>"


class Section:
    """One FILE block of the model; every verb returns a Handle."""

    def __init__(self, model, name, description):
        self.model, self.name, self.description = model, name if name.endswith(".ldr") else name + ".ldr", description
        self.entries, self.rows, self.counts, self.step = [], [], {}, 0

    # ----------------------------------------------------------------- verbs
    def place(self, ref, colour, cell=(0, 0), level=0, turn=0, on=None, **options):
        """Put a studded part on a stud grid: footprint corner at ``cell``, bottom at ``level`` plates.

        Without ``on`` the grid is the ground. With ``on=part.port("stud[k]")`` it is the face that
        stud stands on, at any angle (a bracket's side, a hinged plate, an upside-down part):
        cell (0, 0) is that stud and ``level`` counts plates out from the face. On a top or
        bottom face, even a tilted one, cells run like the ground (x toward +X, z toward +Z);
        on a side face cell z points up. ``turn`` rotates about the stud's axis.
        """
        data = self.model.part(ref)
        rotation = yaw(turn)
        points = _footprint(data)
        rotated = points @ rotation.T
        t = np.array([STUD * cell[0] - rotated[:, 0].min(), -PLATE * level - stacking_bottom(data), STUD * cell[1] - rotated[:, 2].min()])
        verb = f"place(cell={tuple(cell)}, level={level})"
        if on is not None:
            frame, origin = _face(on, self)
            rotation, t = frame @ rotation, origin + frame @ t
            verb = f"place(on={on.handle.id}.{on.name}, cell={tuple(cell)}, level={level})"
        return self._admit(ref, data, colour, rotation, t, options, verb=verb)

    def mirror(self, handles, about=None, plane="X", at=0.0):
        """Place the mirror image of parts across a plane: build one side, then mirror it.

        ``about=hull`` mirrors across that placed part's centre line; otherwise across x=at
        (``plane="X"``, the default: left/right) or z=at (``plane="Z"``: front/back).
        Left and right parts swap (41769 Wing Right becomes 41770 Wing Left); symmetric parts are
        turned so the copy is a true mirror image. Parts lying on the plane are their own mirror
        and are skipped. Returns the new handles in order; ids swap left/right or get "-mirror".
        """
        flip = {"X": np.diag([-1.0, 1, 1]), "Z": np.diag([1.0, 1, -1])}.get(plane.upper())
        if flip is None:
            raise KitError("mirror plane must be 'X' (left/right, across x) or 'Z' (front/back, across z)")
        axis = 0 if plane.upper() == "X" else 2
        centre = np.zeros(3)
        if about is not None:
            if not isinstance(about, Handle) or about.data is None:
                raise KitError("about= must be a placed part, e.g. about=hull")
            low, high = about.box
            centre[axis] = (low[axis] + high[axis]) / 2
        else:
            centre[axis] = at
        made = []
        for handle in handles if isinstance(handles, (list, tuple)) else [handles]:
            if handle.data is None:
                raise KitError(f"{handle.id} is a submodel; mirror the parts inside it")
            ref, local = self.model.counterpart(handle.ref)
            rotation = flip @ handle.R @ local
            t = flip @ (handle.t - centre) + centre
            if normalized(ref) == normalized(handle.ref) and np.allclose(rotation, handle.R, atol=1e-6) and np.allclose(t, handle.t, atol=0.01):
                continue
            swapped = re.sub(r"left|right", lambda m: {"left": "right", "right": "left"}[m.group(0)], handle.id)
            options = dict(id=swapped if swapped != handle.id else f"{handle.id}-mirror")
            if handle.entry.get("purpose"):
                options["purpose"] = handle.entry["purpose"]
            made.append(self._admit(ref, self.model.part(ref), handle.entry["colour"], rotation, t, options,
                                    verb=f"mirror({handle.id})"))
        return made

    def add(self, ref, colour, at=(0, 0, 0), turn=0, axes=None, matrix=None, **options):
        """Explicit placement in LDU. ``ref`` may also be a Section (a submodel instance)."""
        rotation = np.array(matrix, dtype=float) if matrix is not None else axes_matrix(axes) if axes else yaw(turn)
        if isinstance(ref, Section):
            return self._instance(ref, colour, rotation, np.array(at, dtype=float), options)
        return self._admit(ref, self.model.part(ref), colour, rotation, np.array(at, dtype=float), options, verb=f"add(at={tuple(at)})")

    def mate(self, ref, colour, port, to, roll=0, along=None, slide=0, toward=None, flip=None, **options):
        """Connect ``port`` of a new part to a placed part's port (``to=handle.port(name)``).

        ``along`` ("X", "Z", "UP", ...) points the new part's length (its reference
        direction across the port axis) that way; otherwise ``roll`` turns it about
        the shared axis relative to the target part. ``slide`` moves it along the axis
        (LDU), in the direction ``toward`` when given; ``flip`` reverses its direction
        (default: the collision-free choice). Studs seat at the socket mouth; other
        ports centre on each other.
        """
        if toward is not None and slide:
            slide = abs(slide) * (1 if float(to.A @ _direction(toward)) >= 0 else -1)
        if not isinstance(to, Port) or to.handle.section is not self:
            raise KitError("to= must be a port of a part in this same section, e.g. to=beam.port('pin_hole[2]')")
        data = self.model.part(ref)
        record = next((r for r in data.ports if r["name"] == port), None)
        if record is None:
            raise KitError(f"{ref} has no port {port!r}; it has: {', '.join(r['name'] for r in data.ports) or 'none'}")
        local_axis, local_mid = np.array(record["axis"]), np.array(record["p"])
        target_reference = _rodrigues(to.A, roll) @ to.reference
        if along is not None:
            wanted = _direction(along)
            if abs(float(wanted @ to.A)) > 0.99:
                raise KitError(f"along={along!r} is parallel to the port axis; give a direction across it")
            target_reference = _unit(wanted - (wanted @ to.A) * to.A)
        failures = []
        for sign in ((1, -1) if flip is None else ((-1,) if flip else (1,))):
            rotation, t = _pose(record, to, target_reference, sign, slide)
            try:
                return self._admit(ref, data, colour, rotation, t, options, verb=f"mate({port} to {to.handle.id}.{to.name})",
                                   partner=to.handle)
            except KitError as error:
                failures.append(str(error))
        raise KitError(" / ".join(failures))

    def hinge(self, ref, colour, port, to, angle=0, **options):
        """Join the other half of a hinge (``port`` to ``to=base.port("hinge[0]")``) at ``angle`` degrees.

        0 extends the new part flat, straight out from the base part; a positive angle
        tilts it toward the base's top side (a wing raised in dihedral, a ramp lifted),
        negative toward its underside. Build on the tilted part with
        ``place(..., on=part.port("stud[k]"))``.
        """
        if not isinstance(to, Port) or to.handle.section is not self:
            raise KitError("to= must be a hinge port of a part in this same section, e.g. to=root.port('hinge[0]')")
        data = self.model.part(ref)
        record = next((r for r in data.ports if r["name"] == port), None)
        if record is None:
            raise KitError(f"{ref} has no port {port!r}; it has: {', '.join(r['name'] for r in data.ports) or 'none'}")
        axis = _unit(to.A)
        low, high = to.handle.box
        out = to.P - (low + high) / 2
        out = out - (out @ axis) * axis
        if np.linalg.norm(out) < 1e-6:
            raise KitError(f"{to.handle.id}.{to.name} is at the base part's centre; hinge() needs a hinge on its edge")
        out = _unit(out)
        up = to.handle.R @ np.array([0.0, -1.0, 0.0])
        up = up - (up @ axis) * axis - (up @ out) * out
        up = _unit(up) if np.linalg.norm(up) > 1e-6 else np.cross(axis, out)
        wanted = math.cos(math.radians(angle)) * out + math.sin(math.radians(angle)) * up
        lo, hi = data.lo, data.hi
        upright = -math.sin(math.radians(angle)) * out + math.cos(math.radians(angle)) * up
        poses = []
        for sign in (1, -1):
            rotation, t = _pose(record, to, to.reference, sign, 0.0)
            centre = rotation @ ((lo + hi) / 2) + t - to.P
            centre = centre - (centre @ axis) * axis
            if np.linalg.norm(centre) > 1e-6:
                turn = math.atan2(float(np.cross(_unit(centre), wanted) @ axis), float(_unit(centre) @ wanted))
                spin = _rodrigues(axis, math.degrees(turn))
                rotation, t = spin @ rotation, spin @ (t - to.P) + to.P
            poses.append((rotation, t))
        # Studs up (the base's top side, turned by the angle) first; upside down only if that is blocked.
        poses.sort(key=lambda pose: -float(pose[0] @ np.array([0.0, -1.0, 0.0]) @ upright))
        failures = []
        for rotation, t in poses:
            try:
                return self._admit(ref, data, colour, rotation, t, options,
                                   verb=f"hinge({port} to {to.handle.id}.{to.name}, angle={angle})", partner=to.handle)
            except KitError as error:
                failures.append(str(error))
        raise KitError(" / ".join(failures))

    def pin(self, colour, between, ref="2780", **options):
        """A Technic pin through two aligned holes ``between=(a.port(...), b.port(...))``; closes frames.

        The holes must share one axis line and be one pin length apart (20 LDU for
        2780/3673, 40 for the long pins 6558/32556 spanning three layers).
        """
        first, second = between
        if not all(isinstance(p, Port) and p.handle.section is self for p in between):
            raise KitError("pin(between=...) needs two ports of parts in this section")
        axis = _unit(second.P - first.P)
        gap = float(np.linalg.norm(second.P - first.P))
        offline = max(float(np.linalg.norm(np.cross(axis, first.A))), float(np.linalg.norm(np.cross(axis, second.A))))
        if gap < 1 or offline > 0.02:
            raise KitError(f"holes {first.handle.id}.{first.name} and {second.handle.id}.{second.name} are not on one axis "
                           f"(gap {gap:.1f} LDU); pins need coaxial holes")
        data = self.model.part(ref)
        full = max((r for r in data.ports if r["kind"] == "pin"), key=lambda r: r["half"], default=None)
        if full is None or abs(gap - (2 * full["half"] - 20)) > 0.5:
            raise KitError(f"holes are {gap:.1f} LDU apart; {ref} joins holes {2 * full['half'] - 20 if full else '?'} LDU apart")
        local_axis = np.array(full["axis"])
        frame_local = np.column_stack([local_axis, _reference(local_axis), np.cross(local_axis, _reference(local_axis))])
        reference = _reference(axis)
        frame_world = np.column_stack([axis, reference, np.cross(axis, reference)])
        rotation = frame_world @ frame_local.T
        t = (first.P + second.P) / 2 - rotation @ np.array(full["p"])
        return self._admit(ref, data, colour, rotation, t, options, verb=f"pin(between {first.handle.id}, {second.handle.id})")

    def wall(self, colour, start, length, courses, level=0, along="X", bond="running", openings=(), prefix="wall"):
        """A straight wall of 1xN bricks; running bond staggers the joints so the courses lock together.

        ``start`` is the first stud cell, ``length`` in studs, ``along`` "X" or "Z".
        ``openings=[(offset, width, first_course, last_course)]`` leaves gaps for doors
        and windows (offset in studs from ``start``, courses counted from 0); place the
        door or window part into the gap at ``level + 3 * first_course``.
        Returns the handles; the wall's top is at ``level + 3 * courses``.
        """
        if along.upper() not in ("X", "Z") or length < 1 or courses < 1:
            raise KitError("wall needs along='X' or 'Z', length >= 1 and courses >= 1")
        handles = []
        for course in range(courses):
            blocked = sorted((o, o + w) for o, w, first, last in openings if first <= course <= last)
            segments, cursor = [], 0
            for low, high in blocked:
                if low > cursor:
                    segments.append((cursor, low))
                cursor = max(cursor, high)
            if cursor < length:
                segments.append((cursor, length))
            for low, high in segments:
                size_left = high - low
                offset = 1 if bond == "running" and course % 2 and size_left > 2 else 0
                position = low
                for size in _split(size_left, offset, BRICKS):
                    cell = (start[0] + position, start[1]) if along.upper() == "X" else (start[0], start[1] + position)
                    handles.append(self.place(BRICKS[size], colour, cell=cell, level=level + 3 * course,
                                              turn=0 if along.upper() == "X" else 90, id=f"{prefix}-{course}-{position}"))
                    position += size
        return handles

    def fill(self, colour, cell, size, level=0, part="plate", prefix="fill"):
        """Cover a rectangle of ``size=(w, d)`` studs at ``cell`` with the largest 2xN (then 1xN) plates or tiles.

        Plates side by side are not joined to each other: put a part across each seam
        (or use one large plate) or check will report the pieces as floating.
        """
        table = {"plate": (PLATES_2, PLATES_1), "tile": ({}, TILES_1)}[part]
        handles, (width, depth) = [], size
        for z in range(0, depth, 2):
            rows = 2 if depth - z >= 2 and table[0] else 1
            sizes = table[0] if rows == 2 else table[1]
            position = 0
            for length in _split(width, 0, sizes):
                handles.append(self.place(sizes[length], colour, cell=(cell[0] + position, cell[1] + z), level=level,
                                          id=f"{prefix}-{z}-{position}"))
                position += length
            if rows == 1 and depth - z >= 2:
                position = 0
                for length in _split(width, 0, sizes):
                    handles.append(self.place(sizes[length], colour, cell=(cell[0] + position, cell[1] + z + 1),
                                              level=level, id=f"{prefix}-{z + 1}-{position}"))
                    position += length
        return handles

    def section(self, name, description):
        return self.model.section(name, description)

    def next_step(self):
        """Start a new building step (LDraw STEP) for later placements."""
        self.step += 1

    # ----------------------------------------------------------------- internals
    def _entry(self, ref, colour, rotation, t, options):
        code = normalized(ref).removesuffix(".dat").removesuffix(".ldr")
        identifier = options.get("id")
        if identifier is None:
            self.counts[code] = self.counts.get(code, -1) + 1
            identifier = f"{code}-{self.counts[code]}"
        if not re.fullmatch(r"[A-Za-z0-9_-]+", identifier) or any(e["id"] == identifier for e in self.entries):
            raise KitError(f"id {identifier!r} must be unique in {self.name} and use letters, digits, - or _")
        unknown = set(options) - {"id", "purpose", "free", "overlap"}
        if unknown:
            raise KitError(f"unknown option(s) {sorted(unknown)}; use id, purpose, free, overlap")
        return dict(id=identifier, ref=ref, code=code, colour=self.model.colour(colour), R=rotation, t=t,
                    purpose=options.get("purpose"), free=options.get("free"), overlap=options.get("overlap"), step=self.step)

    def _instance(self, section, colour, rotation, t, options):
        entry = self._entry(section.name, colour if colour is not None else 16, rotation, t, options)
        entry["section"] = section
        self.entries.append(entry)
        return Handle(self, entry)

    def _admit(self, ref, data, colour, rotation, t, options, *, verb, partner=None):
        entry = self._entry(ref if ref.lower().endswith((".dat", ".ldr")) else ref + ".dat", colour, rotation, t, options)
        entry["data"] = data
        row = dict(code=entry["code"], label=entry["id"], free=entry["free"], overlap=entry["overlap"], status="exact",
                   module=self.name, section=self.name, line=None, local=self.model.local(entry["code"]), R=rotation, t=t)
        problems = list(dict.fromkeys(self._problems(row, partner)))   # one message per neighbour
        if problems and self.model.strict:
            raise KitError(f"{verb} {entry['ref']} as {entry['id']!r}: " + "; ".join(problems))
        self.entries.append(entry)
        self.rows.append(row)
        return Handle(self, entry)

    def _problems(self, row, partner):
        """Collisions with, and stud seating on, the parts already placed in this section."""
        row["box"] = lo, hi = checker.world_box(row)
        boxes_lo = np.array([other["box"][0] for other in self.rows]).reshape(-1, 3)
        boxes_hi = np.array([other["box"][1] for other in self.rows]).reshape(-1, 3)
        neighbours = np.nonzero(np.all(boxes_lo < hi - 0.05, axis=1) & np.all(boxes_hi > lo + 0.05, axis=1))[0].tolist()
        nearby = np.nonzero(np.all(boxes_lo < hi + 1, axis=1) & np.all(boxes_hi > lo - 1, axis=1))[0].tolist()
        ports = checker.world_ports(row, -1)
        for k in nearby:
            ports.extend(checker.world_ports(self.rows[k], k))
        mated, problems = set(), []
        for a, b, _ in checker._mates(ports):
            pa, pb = ports[a], ports[b]
            if -1 not in (pa["part"], pb["part"]):
                continue
            other = pb["part"] if pa["part"] == -1 else pa["part"]
            mated.add(other)
            stud, socket = (pa, pb) if pa["kind"] == "stud" else (pb, pa)
            if stud["kind"] == "stud" and socket["gender"] == "F" and not socket.get("centered", True):
                offset = float((socket["P"] - (stud["P"] - stud["A"] * stud["half"])) @ stud["A"]) - socket["half"]
                if abs(offset) > self.model.tolerance:
                    problems.append(f"{'sunk' if offset < 0 else 'floating'} {abs(round(offset, 2))} LDU on the stud of "
                                    f"{self.rows[other]['label']!r} ({self.rows[other]['code']}); seat it at level={self._handle(other).top}")
        for k in neighbours:
            other = self.rows[k]
            if k in mated or (partner is not None and other["label"] == partner.id):
                continue
            first, second = (row["local"], row["R"], row["t"]), (other["local"], other["R"], other["t"])
            depth, at = checker._pair_depth(first, second, (), self.model.tolerance)
            if row["local"].data.boxy and other["local"].data.boxy:
                depth = max(depth, checker._box_depth(first, second)[0])
            tight = depth <= checker.TIGHT_FIT and not (row["local"].data.boxy and other["local"].data.boxy)
            if depth <= self.model.tolerance or tight or row["overlap"] or other["overlap"] or \
                    checker._interlocking(row["local"].data.description, other["local"].data.description):
                continue
            handle = self._handle(k)
            problems.append(f"collides with {other['label']!r} ({other['code']}) by ~{depth:g} LDU"
                            + (f" near {np.round(at, 1).tolist()}" if at is not None else "")
                            + f"; that part spans levels {handle.bottom}..{handle.top}")
        return problems

    def _handle(self, k):
        label = self.rows[k]["label"]
        return Handle(self, next(e for e in self.entries if e["id"] == label))


def _codes_described(description):
    """Library part numbers whose description is exactly ``description`` (whitespace-insensitive)."""
    database = ROOT / "data/ldraw-info.db"
    if not database.is_file():
        return []
    with sqlite3.connect(f"file:{database}?mode=ro", uri=True) as connection:
        rows = connection.execute("SELECT alias, description FROM PART_INFOS WHERE description LIKE ?",
                                  (description.split()[0] + "%",)).fetchall()
    return [alias.removesuffix(".dat") for alias, text in rows if " ".join((text or "").split()) == description]


def _mirrors(original, candidate, local):
    """Candidate's body and ports equal the original's flipped by the local axis matrix."""
    lo, hi = np.minimum(original.lo @ local, original.hi @ local), np.maximum(original.lo @ local, original.hi @ local)
    if not (np.allclose(lo, candidate.lo, atol=0.6) and np.allclose(hi, candidate.hi, atol=0.6)):
        return False
    def keys(ports, matrix):
        return sorted((r["kind"], r["gender"], *np.round(np.array(r["p"]) @ matrix * 2).astype(int).tolist()) for r in ports)
    return keys(original.ports, local) == keys(candidate.ports, np.eye(3))


def stacking_bottom(data):
    """Local y of the plane a part stacks on: its sockets' mouth, else its lowest body point.

    Body bounds can hang below that plane (wheel pins, clips), so they are a fallback only.
    """
    mouths = [r["p"][1] + r["half"] * abs(r["axis"][1]) for r in data.ports
              if r["gender"] == "F" and abs(abs(r["axis"][1]) - 1) < 1e-6 and r["kind"] in ("stud_receptacle", "pin_hole")
              and not r.get("centered", True)]
    return max(mouths) if mouths else float(data.hi[1])


def _footprint(data):
    """Local stud-grid points of a part: its sockets and studs together, else its body corners.

    Both lie on the part's stud grid. Together they stay complete when a library revision
    leaves one of them partial: the 2026-05 wing plates 41769a/41770a have sockets only on
    their back half, which moved their anchor corner by two cells.
    """
    points = [r["p"] for r in data.ports if abs(abs(r["axis"][1]) - 1) < 1e-6
              and r["kind"] in ("stud_receptacle", "pin_hole", "stud") and (r["kind"] != "pin_hole" or not r.get("centered", True))]
    if points:
        return np.array(points, dtype=float) * np.array([1, 0, 1])
    return np.array([[data.lo[0] + STUD / 2, 0, data.lo[2] + STUD / 2]])


def _pose(record, to, target_reference, sign, slide):
    """Rotation and translation putting port ``record`` of a new part on port ``to``."""
    local_axis, local_mid = np.array(record["axis"]), np.array(record["p"])
    frame_local = np.column_stack([local_axis, _reference(local_axis), np.cross(local_axis, _reference(local_axis))])
    axis = sign * to.A
    ref_world = target_reference - (target_reference @ axis) * axis
    frame_world = np.column_stack([axis, _unit(ref_world), np.cross(axis, _unit(ref_world))])
    rotation = frame_world @ frame_local.T
    t = to.P + slide * to.A - rotation @ local_mid
    return rotation, _seat(record, rotation, t, to)


def _face(port, section):
    """The stud face a port stands on, as (frame, origin): columns map ground x, y (down), z onto it."""
    if not isinstance(port, Port) or port.handle.section is not section:
        raise KitError("on= must be a stud of a part in this same section, e.g. on=bracket.port('stud[2]')")
    if port.kind != "stud" or port.gender != "M":
        raise KitError(f"on= needs a stud; {port.handle.id}.{port.name} is a {port.kind}. "
                       "Use mate() for pins, axles, hinges, clips and bars")
    up = _unit(port.A)
    if abs(up[1]) > 0.7:          # a top or bottom face, flat or tilted: cells run like the ground (x to +X)
        across = np.array([1.0, 0, 0]) - up[0] * up
        across = _unit(across)
        depth = np.cross(up, across)
    else:                         # a side face: cell z points up, cell x along the face
        depth = np.array([0.0, -1, 0]) - (-up[1]) * up
        depth = _unit(depth)
        across = np.cross(depth, up)
    return np.column_stack([across, -up, depth]), port.P - up * port.record["half"]


def _seat(record, rotation, t, target):
    """Stud into socket: put the socket mouth on the stud base, whatever way LDCad points the socket axis."""
    pair = {record["kind"], target.kind}
    if "stud" not in pair or record["gender"] == target.gender:
        return t
    mid = rotation @ np.array(record["p"]) + t
    axis = rotation @ np.array(record["axis"])
    if record["kind"] == "stud":   # new part brings the stud; the target is the socket
        stud_base, stud_axis = mid - axis * record["half"], axis
        socket_mid, socket_half = target.P, target.record["half"]
    else:
        stud_base, stud_axis = target.P - target.A * target.record["half"], target.A
        socket_mid, socket_half = mid, record["half"]
    offset = float((socket_mid - stud_base) @ stud_axis) - socket_half
    return t - offset * stud_axis if record["kind"] != "stud" else t + offset * stud_axis


class Model(Section):
    """The main FILE block plus any sections; owns the part cache and writes the MPD."""

    def __init__(self, name, description, *, author="ldraw-nova kit", strict=True, tolerance=0.5, library=None, family=None):
        self.parts = get_parts(library)
        self.library = library_path(library)
        self.cache = PartCache(self.parts, self.library)
        self._locals, self.sections, self._mirrors = {}, [], {}
        self.author, self.strict, self.tolerance, self.family = author, strict, tolerance, family
        super().__init__(self, name, description)
        self.sections.append(self)

    def counterpart(self, ref):
        """(mirror part, local flip): the part that is ref's mirror image and the local axis it flips.

        LDCad's MIRROR_INFO names the counterpart when it exists; otherwise "Left" and "Right" swap
        in the description, or the part is its own mirror. The flip is the local axis (x, z or y)
        under which the counterpart's ports and body match the original's mirror image.
        """
        code = normalized(ref).removesuffix(".dat")
        if code in self._mirrors:
            return self._mirrors[code]
        original = self.part(code)
        candidates, axes = [], "xzy"
        for shadow in getattr(self.parts, "_connection_shadow_libraries", []):
            path = Path(str(getattr(shadow, "source", ""))) / "parts" / f"{code}.dat"
            info = re.search(r"MIRROR_INFO(.*)", path.read_text(errors="replace")) if path.is_file() else None
            if info:
                other = re.search(r"\[counterPart=([^\]]+)\]", info.group(1))
                if other:
                    candidates.append(code if other.group(1).lower() == "self" else normalized(other.group(1)).removesuffix(".dat"))
                base = re.search(r"\[baseFlip=([XYZ])\]", info.group(1), re.I)
                if base:
                    axes = base.group(1).lower() + axes.replace(base.group(1).lower(), "")
        description = original.description
        moved = re.match(r"~Moved to (\S+)", description)            # a renamed part: read its new description
        if moved and self.parts.find_part(code=normalized(moved.group(1)).removesuffix(".dat")) is not None:
            description = self.part(normalized(moved.group(1)).removesuffix(".dat")).description
        swapped = re.sub(r"\b(Left|Right)\b", lambda m: "Right" if m.group(1) == "Left" else "Left", description)
        if swapped != description:
            candidates += _codes_described(" ".join(swapped.split()))
        candidates.append(code)
        number = re.fullmatch(r"(\d+)([a-z]*)", code)               # left/right pairs are usually consecutive
        if number:
            candidates += [f"{int(number.group(1)) + step}{number.group(2)}" for step in (-1, 1)]
        for candidate in dict.fromkeys(candidates):
            if self.parts.find_part(code=candidate) is None:
                continue
            data = self.part(candidate)
            for axis in axes:
                local = np.diag([-1.0 if a == axis else 1.0 for a in "xyz"])
                if _mirrors(original, data, local):
                    self._mirrors[code] = (candidate, local)
                    return self._mirrors[code]
        raise KitError(f"cannot mirror {ref}: no part matches its mirror image; place the other side explicitly")

    def part(self, ref):
        code = normalized(ref).removesuffix(".dat")
        if self.parts.find_part(code=code) is None:
            raise KitError(f"unknown part {ref!r}; search with ./ldraw-agent search parts 'words' or catalog parts")
        return self.cache.get(code)

    def local(self, code):
        if code not in self._locals:
            self._locals[code] = checker._Local(self.cache.get(code))
        return self._locals[code]

    def colour(self, value):
        if isinstance(value, int):
            if value not in self.parts.colours_by_code or value == 24:
                raise KitError(f"unknown colour code {value}")
            return value
        wanted = re.sub(r"[\s-]+", "_", str(value).strip()).casefold()
        for code, colour in self.parts.colours_by_code.items():
            if (colour.name or "").casefold() == wanted:
                return code
        raise KitError(f"unknown colour {value!r}; list them with ./ldraw-agent colours NAME")

    def section(self, name, description):
        section = Section(self, name, description)
        if any(normalized(s.name) == normalized(section.name) for s in self.sections):
            raise KitError(f"section {section.name} already exists")
        self.sections.append(section)
        return section

    def plan(self):
        """The equivalent version-1 JSON plan (explicit at + matrix placements)."""
        sections = []
        for section in self.sections:
            steps = {}
            for e in section.entries:
                placement = dict(id=e["id"], ref=e["ref"], colour=e["colour"],
                                 at=[round(float(v), 4) + 0.0 for v in e["t"]],
                                 matrix=[[round(float(v), 9) + 0.0 for v in row] for row in e["R"]])
                for key in ("purpose", "free", "overlap"):
                    if e.get(key):
                        placement[key] = e[key]
                steps.setdefault(e["step"], []).append(placement)
            if steps:
                sections.append(dict(name=section.name, description=section.description,
                                     steps=[steps[k] for k in sorted(steps)]))
        return dict(version=1, author=self.author, sections=sections)

    def save(self, path, *, check=True, quiet=False):
        """Write PATH (.mpd) and PATH.plan.json, then run the full check and print its verdict."""
        path = Path(path)
        if path.suffix.lower() != ".mpd":
            raise KitError("save to a .mpd path")
        models = {}
        for section in self.sections:
            if not section.entries:
                continue
            ldraw = LDrawModel(name=section.name)
            ldraw.set_header(description=section.description, name=section.name, author=self.author, ldraw_org="Model")
            step = 0
            for e in section.entries:
                while step < e["step"]:
                    ldraw.add_step()
                    step += 1
                ldraw.add(Comment(f"// {e['id']}: {e.get('purpose') or e['ref']}"))
                for key in ("free", "overlap"):
                    if e.get(key):
                        ldraw.add(Comment(f"!NOVA {key.upper()} {e[key]}"))
                ldraw.add(Piece.place(e["ref"], colour=e["colour"], position=Vector(*map(float, e["t"])),
                                      matrix=Matrix([[float(v) for v in row] for row in e["R"]])))
            models[section.name] = ldraw
        if self.name not in models:
            raise KitError("the main section is empty")
        root = models[self.name]
        root.submodels = {normalized(n): m for n, m in models.items() if n != self.name}
        atomic_write(path, serialize_mpd(root))
        atomic_write(path.with_suffix(".plan.json"), json.dumps(self.plan(), indent=1) + "\n")
        if not check:
            return None
        report = checker.check_model(path, self.parts, self.library, tolerance=self.tolerance, family=self.family)
        if not quiet:
            print(checker.format_report(report))
        return report
