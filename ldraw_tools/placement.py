"""Connector-based placement: the agent names what connects; the tool computes the pose.

Three operations replace hand-written matrices and ``stud - R * socket``
arithmetic:

* ``orient(up, x)``: the rotation that points a part's studs (local -Y) toward
  ``up`` and its local +X toward ``x``. Directions are ``+X -X +Y -Y +Z -Z``
  (``up`` = -Y, ``down`` = +Y) or vectors.
* ``interfaces(parts, code)``: a part's studs and sockets in its own frame,
  grouped by the face they point out of, in a stable order. ``part`` prints it.
* ``seat(...)``: place a part so one of its sockets sits on a support's stud.
  The socket faces the stud; ``roll`` turns the part about the seated socket's
  axis, right-handed like ``yaw``, so a part seated on top with ``roll: 45``
  matches ``yaw: 45``.

Studs and sockets are the radius-6 stud interfaces of the connector data,
after the same frame adaptation the contact checker uses, so a seat that this
module computes is one the checker can confirm.
"""
from __future__ import annotations

import math

import numpy as np

NAMED = {'+X': (1, 0, 0), '-X': (-1, 0, 0), '+Y': (0, 1, 0), '-Y': (0, -1, 0), '+Z': (0, 0, 1), '-Z': (0, 0, -1),
         'up': (0, -1, 0), 'down': (0, 1, 0), 'top': (0, -1, 0), 'bottom': (0, 1, 0)}
_INTERFACES = {}


def direction(value, name='direction'):
    if isinstance(value, str):
        key = value if value in NAMED else value.upper()
        if key not in NAMED:
            raise ValueError(f'{name} {value!r} must be one of +X -X +Y -Y +Z -Z, up, down or a vector')
        return np.array(NAMED[key], float)
    vector = np.asarray(value, float)
    length = np.linalg.norm(vector)
    if vector.shape != (3,) or not np.isfinite(vector).all() or length < 1e-9:
        raise ValueError(f'{name} must be a nonzero 3-vector')
    return vector / length


def face_name(vector):
    vector = np.asarray(vector, float)
    axis = int(np.argmax(np.abs(vector)))
    if abs(abs(vector[axis]) - 1) > 1e-6:
        return 'oblique'
    return ('+' if vector[axis] > 0 else '-') + 'XYZ'[axis]


def clean(values, digits=9):
    return [[clean_number(v, digits) for v in row] for row in values] if np.ndim(values) == 2 else \
        [clean_number(v, digits) for v in values]


def clean_number(value, digits=9):
    value = round(float(value), digits)
    return 0.0 if value == 0 else value


def proper(matrix):
    return np.allclose(matrix.T @ matrix, np.eye(3), atol=1e-6) and np.linalg.det(matrix) > 0


def orient(up, x=None):
    """Proper rotation: local up (-Y) -> ``up``; local +X -> ``x`` (default +X, else +Z)."""
    u = direction(up, 'orient.up')
    if x is None:
        x = np.array([1.0, 0, 0]) if abs(u[0]) < 0.9 else np.array([0, 0, 1.0])
    else:
        x = direction(x, 'orient.x')
    x = x - (x @ u) * u
    if np.linalg.norm(x) < 1e-6:
        raise ValueError('orient.x must not be parallel to orient.up')
    x /= np.linalg.norm(x)
    y = -u
    return np.column_stack([x, y, np.cross(x, y)])


def about(axis, degrees):
    """Right-handed rotation about a unit axis (Rodrigues), in LDraw coordinates."""
    axis = direction(axis)
    angle = math.radians(degrees)
    k = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    rotation = np.eye(3) + math.sin(angle) * k + (1 - math.cos(angle)) * (k @ k)
    return np.round(rotation, 12)


def turning(source, target):
    """Smallest rotation taking unit ``source`` onto unit ``target``."""
    source, target = direction(source), direction(target)
    cos = float(np.clip(source @ target, -1, 1))
    if cos > 1 - 1e-12:
        return np.eye(3)
    if cos < -1 + 1e-12:
        helper = np.array([1.0, 0, 0]) if abs(source[0]) < 0.9 else np.array([0, 0, 1.0])
        return about(np.cross(source, helper), 180)
    axis = np.cross(source, target)
    return about(axis, math.degrees(math.acos(cos)))


def interfaces(parts, code):
    """Studs and sockets of one part in its own frame, grouped by outward face."""
    code = code.casefold().removesuffix('.dat')
    if code in _INTERFACES:
        return _INTERFACES[code]
    from ldraw import Model, Piece, Vector, inspect_model
    from .connection_adapter import query_frames
    from .technic import curate
    if parts.find_part(code=code) is None:
        raise ValueError(f'Unknown part {code}.dat; search the part database first')
    model = Model(name='interfaces.ldr')
    model.add(Piece.place(code + '.dat', colour=16, position=Vector(0, 0, 0)))
    item = query_frames(curate(inspect_model(model, parts))).occurrences[0]

    def collect(kind, role):
        found = {}
        for feature in item.connections:
            sections = getattr(feature.profile, 'sections', ())
            if (feature.kind.value != kind or feature.role.value != role or len(sections) != 1
                    or abs(sections[0].radius - 6) > 1e-6):
                continue
            position = np.round([feature.position.x, feature.position.y, feature.position.z], 4) + 0.0
            axis = np.round([feature.axis.x, feature.axis.y, feature.axis.z], 6) + 0.0
            found.setdefault((face_name(axis), *position), (position, axis, feature.source.value))
        rows = sorted(found.values(), key=lambda row: (face_name(row[1]), *row[0]))
        return [dict(face=face_name(axis), at=clean(position, 4), axis=clean(axis, 6), source=source)
                for position, axis, source in rows]

    from .appearance import body
    shape = body(item)
    bounds = item.local.bounds
    studs, sockets = collect('stud', 'male'), collect('stud_receptacle', 'female')
    listed = {(r['face'], *r['at']) for r in studs + sockets}
    other = {}
    for feature in item.connections:
        axis = np.round([feature.axis.x, feature.axis.y, feature.axis.z], 6) + 0.0
        position = clean([feature.position.x, feature.position.y, feature.position.z], 3)
        if (face_name(axis), *position) in listed:
            continue
        rows = other.setdefault(f'{feature.kind.value} {feature.role.value}', {}).setdefault(face_name(axis), [])
        if position not in rows and len(rows) < 16:
            rows.append(position)
    result = dict(code=code + '.dat', description=item.local.description,
                  bounds=dict(min=clean([bounds.min.x, bounds.min.y, bounds.min.z], 3),
                              max=clean([bounds.max.x, bounds.max.y, bounds.max.z], 3)) if bounds else None,
                  body=dict(min=clean(shape[1], 3), max=clean(shape[2], 3)) if shape else None,
                  studs=studs, sockets=sockets, other=other, connectors=len(item.connections))
    _INTERFACES[code] = result
    return result


def by_face(rows):
    faces = {}
    for row in rows:
        faces.setdefault(row['face'], []).append(row['at'])
    return faces


def select(rows, face, index, what, part):
    """Pick one interface by face and index, with an error that lists the options."""
    chosen = [r for r in rows if face is None or r['face'] == face]
    if not chosen:
        faces = by_face(rows)
        listed = '; '.join(f'{f}: {len(v)}' for f, v in faces.items()) or 'none'
        raise ValueError(f'{part} has no {what} facing {face}; {what} by face: {listed}')
    if not 0 <= index < len(chosen):
        raise ValueError(f'{part} has {len(chosen)} {what} facing {face or "any way"} (indices 0-{len(chosen) - 1}); got {index}')
    return chosen[index]


def facts(parts, code):
    """Compact part summary for agents: origin, body, studs and sockets by face."""
    data = interfaces(parts, code)
    body_box = data['body'] or data['bounds']
    result = dict(part=data['code'], description=data['description'])
    if body_box:
        low, high = np.array(body_box['min']), np.array(body_box['max'])
        size = high - low
        vertical = 'top' if abs(low[1]) < 0.5 else 'bottom' if abs(high[1]) < 0.5 else f'{clean_number(-low[1], 3)} below the body top'
        centre = (low + high) / 2
        across = 'centred' if abs(centre[0]) < 0.5 and abs(centre[2]) < 0.5 else \
            f'offset {clean([centre[0], centre[2]], 3)} (x, z) from the body centre'
        result.update(origin=f'at the body {vertical}, {across}' if vertical in {'top', 'bottom'} else f'{vertical}, {across}',
                      body=dict(min=body_box['min'], max=body_box['max'], size=clean(size, 3)))
    result['bounds'] = data['bounds']
    result['studs'] = by_face(data['studs'])
    result['sockets'] = by_face(data['sockets'])
    if data['other']:
        result['other_connectors'] = data['other']
    return result


def seat(support_frame, support_code, moving_code, options, parts, orientation=None):
    """Pose that puts a socket of the moving part (or a point of a module) on a support stud.

    ``support_frame`` is (matrix, position) of the support leaf in the section.
    Returns (matrix, position, details).
    """
    rotation, translation = support_frame
    support = interfaces(parts, support_code)
    stud = select(support['studs'], options.get('face', '-Y'), options.get('stud', 0), 'studs', support['code'])
    target = rotation @ np.array(stud['at']) + translation
    stud_axis = rotation @ np.array(stud['axis'])
    if 'socket_at' in options:
        socket_at = np.array(options['socket_at'], float)
        socket_axis = direction(options.get('socket_axis', '+Y'), 'on.socket_axis')
        socket = dict(at=clean(socket_at, 4), axis=clean(socket_axis, 6), face=face_name(socket_axis))
    else:
        if not moving_code.casefold().endswith('.dat'):
            raise ValueError('Seating a section needs on.socket_at: the point of the section that sits on the stud')
        moving = interfaces(parts, moving_code)
        socket = select(moving['sockets'], options.get('socket_face'), options.get('socket', 0), 'sockets', moving['code'])
        socket_at, socket_axis = np.array(socket['at']), np.array(socket['axis'])
    roll = options.get('roll')
    if orientation is None:
        base = turning(socket_axis, -stud_axis)
        if roll is None and moving_code.casefold().endswith('.dat'):
            # Default: the quarter turn that seats the most studs; ties keep the smallest turn.
            best = None
            for turn in (0, 90, 180, 270):
                candidate = about(-stud_axis, turn) @ base
                origin = target - candidate @ socket_at
                count = mated(support_frame, support_code, (candidate, origin), moving_code, parts)
                if best is None or count > best[0]:
                    best = (count, turn)
            roll = best[1]
        orientation = about(-stud_axis, roll or 0) @ base
    elif roll:
        raise ValueError('Use on.roll or orient, not both')
    facing = orientation @ socket_axis
    if facing @ stud_axis > -0.999:
        raise ValueError(f'orient points the socket toward {face_name(np.round(facing, 6))}, but the stud faces '
                         f'{face_name(np.round(stud_axis, 6))}; the socket must face the stud. Omit orient to derive it.')
    position = target - orientation @ socket_at
    details = dict(stud=stud, socket=socket, stud_at=clean(target, 4), facing=face_name(np.round(-stud_axis, 6)),
                   roll=roll if roll is not None else None)
    return np.round(orientation, 12) + 0.0, np.array(clean(position, 9)), details


def mated(support_frame, support_code, moving_frame, moving_code, parts):
    """Count support studs that coincide with an opposed socket of the moving part."""
    if not moving_code.casefold().endswith('.dat'):
        return None
    support, moving = interfaces(parts, support_code), interfaces(parts, moving_code)
    (rs, ts), (rm, tm) = support_frame, moving_frame
    studs = [(rs @ np.array(s['at']) + ts, rs @ np.array(s['axis'])) for s in support['studs']]
    sockets = [(rm @ np.array(s['at']) + tm, rm @ np.array(s['axis'])) for s in moving['sockets']]
    return sum(any(np.linalg.norm(p - q) < 0.05 and a @ b < -0.999 for q, b in sockets) for p, a in studs)
