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
    from .technic import managed
    shape = body(item)
    bounds = item.local.bounds
    studs, sockets = collect('stud', 'male'), collect('stud_receptacle', 'female')
    listed = {(r['face'], *r['at']) for r in studs + sockets}
    technic = [dict(id=f.feature_id.removeprefix('technic:'), kind=f.kind.value,
                    at=clean([f.position.x, f.position.y, f.position.z], 3),
                    axis=clean([f.axis.x, f.axis.y, f.axis.z], 6), length=clean_number(f.length, 3))
               for f in item.connections if managed(f)]
    other = {}
    for feature in item.connections:
        if managed(feature):
            continue
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
                  studs=studs, sockets=sockets, technic=technic, other=other, connectors=len(item.connections))
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
    if data['technic']:
        from .technic import canonical, registry
        listed = {p['id']: p for p in registry()['parts'].get(canonical(data['code']), {}).get('ports', [])}
        result['technic_ports'] = port_runs([dict(p, **{k: listed.get(p['id'], {}).get(k) for k in ('stops', 'friction')
                                                       if listed.get(p['id'], {}).get(k)}) for p in data['technic']])
    if data['other']:
        result['other_connectors'] = data['other']
    return result


def port_runs(ports):
    """Ports as short lines; equally spaced ports of one kind collapse into a run.

    ``hole-0..hole-8: pin_hole axis Y length 20, at [0, 0, -80] then every [0, 0, 20]``
    """
    def text(port, step=None):
        line = f"{port['kind']} axis {face_name(np.array(port['axis'], float))} length {clean_number(port['length'], 3)}, at {clean(port['at'], 3)}"
        line += f" then every {clean(step, 3)}" if step is not None else ''
        if port.get('friction'):
            line += ', friction'
        if port.get('stops'):
            line += ', stop at the ' + ' and '.join(port['stops']) + ' end'
        return line

    def number(port):
        head, _, tail = port['id'].rpartition('-')
        return (head, int(tail)) if tail.isdigit() else (port['id'], None)

    result, index = {}, 0
    while index < len(ports):
        first = ports[index]
        head, start = number(first)
        end = index
        step = None
        while start is not None and end + 1 < len(ports):
            following = ports[end + 1]
            name, value = number(following)
            delta = np.array(following['at'], float) - np.array(ports[end]['at'], float)
            same = (name == head and value == start + (end - index) + 1 and following['kind'] == first['kind']
                    and following['length'] == first['length'] and np.allclose(following['axis'], first['axis'], atol=1e-6)
                    and not following.get('stops') and not first.get('stops'))
            if not same or (step is not None and not np.allclose(delta, step, atol=1e-6)):
                break
            step = delta
            end += 1
        if end - index >= 2:
            result[f"{first['id']}..{ports[end]['id']}"] = text(first, step)
            index = end + 1
        else:
            result[first['id']] = text(first)
            index += 1
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


def mated(support_frame, support_code, moving_frame, moving_code, parts, hanging=False):
    """Count the support's studs (or, hanging, its sockets) that coincide with an
    opposed socket (or stud) of the moving part."""
    if not moving_code.casefold().endswith('.dat'):
        return None
    support, moving = interfaces(parts, support_code), interfaces(parts, moving_code)
    (rs, ts), (rm, tm) = support_frame, moving_frame
    fixed = support['sockets'] if hanging else support['studs']
    loose = moving['studs'] if hanging else moving['sockets']
    fixed = [(rs @ np.array(s['at']) + ts, rs @ np.array(s['axis'])) for s in fixed]
    loose = [(rm @ np.array(s['at']) + tm, rm @ np.array(s['axis'])) for s in loose]
    return sum(any(np.linalg.norm(p - q) < 0.05 and a @ b < -0.999 for q, b in loose) for p, a in fixed)


def hang(support_frame, support_code, moving_code, options, parts, orientation=None):
    """Pose that pushes a stud of the moving part up (or sideways) into a support socket.

    The mirror of ``seat``: ``socket``/``socket_face`` pick the support's socket
    (default its underside, +Y) and ``stud``/``face`` the moving part's stud
    (default its top, -Y). ``roll`` turns about the socket's axis, like ``yaw``
    for a part hanging under another.
    """
    rotation, translation = support_frame
    support = interfaces(parts, support_code)
    socket = select(support['sockets'], options.get('socket_face', '+Y'), options.get('socket', 0), 'sockets',
                    support['code'])
    target = rotation @ np.array(socket['at']) + translation
    socket_axis = rotation @ np.array(socket['axis'])
    if 'stud_at' in options:
        stud_at = np.array(options['stud_at'], float)
        stud_axis = direction(options.get('stud_axis', '-Y'), 'under.stud_axis')
        stud = dict(at=clean(stud_at, 4), axis=clean(stud_axis, 6), face=face_name(stud_axis))
    else:
        if not moving_code.casefold().endswith('.dat'):
            raise ValueError('Hanging a section needs under.stud_at: the point of the section that goes into the socket')
        moving = interfaces(parts, moving_code)
        stud = select(moving['studs'], options.get('face', '-Y'), options.get('stud', 0), 'studs', moving['code'])
        stud_at, stud_axis = np.array(stud['at']), np.array(stud['axis'])
    roll = options.get('roll')
    if orientation is None:
        base = turning(stud_axis, -socket_axis)
        if roll is None and moving_code.casefold().endswith('.dat'):
            best = None
            for turn in (0, 90, 180, 270):
                candidate = about(socket_axis, turn) @ base
                origin = target - candidate @ stud_at
                count = mated(support_frame, support_code, (candidate, origin), moving_code, parts, hanging=True)
                if best is None or count > best[0]:
                    best = (count, turn)
            roll = best[1]
        orientation = about(socket_axis, roll or 0) @ base
    elif roll:
        raise ValueError('Use under.roll or orient, not both')
    if (orientation @ stud_axis) @ socket_axis > -0.999:
        raise ValueError(f'orient points the stud toward {face_name(np.round(orientation @ stud_axis, 6))}, but the socket '
                         f'opens toward {face_name(np.round(socket_axis, 6))}; the stud must point into it. Omit orient.')
    position = target - orientation @ stud_at
    details = dict(socket=socket, stud=stud, socket_at=clean(target, 4), facing=face_name(np.round(socket_axis, 6)),
                   roll=roll)
    return np.round(orientation, 12) + 0.0, np.array(clean(position, 9)), details


def technic_ports(parts, code):
    ports = {p['id']: p for p in interfaces(parts, code)['technic']}
    if not ports:
        raise ValueError(f'{code} has no Technic ports; use stud seats, snap or at')
    return ports


PIN_COLOURS = {'2780': 0, '6558': 1, '3673': 71, '43093': 1, '3749': 19, '4274': 71, '32054': 0,
               '32556': 19, '11214': 4, '18651': 0, '32002': 19, '6628': 0}
MALES, HOLES = ('pin', 'axle'), ('pin_hole', 'axle_hole')


def _listed(ports):
    return ', '.join(f"{name} ({port['kind']})" for name, port in ports.items())


def _world_feature(code, port_id, frame):
    """The checker's own feature for one port of a placed part."""
    from ldraw import Matrix, Vector
    from .technic import canonical, local_features, registry
    key = canonical(code)
    feature = next(f for f in local_features(key, registry()['parts'][key]) if f.feature_id == 'technic:' + port_id)
    return feature.transformed(position=Vector(*frame[1]), matrix=Matrix(np.asarray(frame[0]).tolist()), inherit=False)


def _along(axis, value, name):
    """+1 or -1 for a direction that must run along ``axis``."""
    chosen = direction(value, name)
    dot = float(chosen @ axis)
    if abs(dot) < 0.999:
        raise ValueError(f"{name} {value!r} must run along the hole axis: use {face_name(np.round(axis, 6))} "
                         f"or {face_name(np.round(-axis, 6))}")
    return 1.0 if dot > 0 else -1.0


def _seat_port(fixed_frame, fixed_code, fixed, moving_code, moved, base, offset, rolls):
    """Rotation and position that put ``moved`` on ``fixed``, checked by the fit rules.

    ``offset`` moves the placed port along the fixed port's world axis. Each
    roll in ``rolls`` (degrees about that axis, None for none) is tried in turn;
    the first that fits wins.
    """
    from .technic import fit, fit_failure
    rotation, translation = fixed_frame
    target = rotation @ np.array(fixed['at'], float) + translation
    axis = rotation @ np.array(fixed['axis'], float)
    axis = axis / np.linalg.norm(axis)
    anchor = _world_feature(fixed_code, fixed['id'], fixed_frame)
    last = None
    for roll in rolls:
        rot = base if roll is None else about(axis, roll) @ base
        rot = np.round(rot, 12) + 0.0
        pos = np.array(clean(target + offset * axis - rot @ np.array(moved['at'], float), 9))
        placed = _world_feature(moving_code, moved['id'], (rot, pos))
        fitted = fit(anchor, placed)
        if fitted is not None:
            return rot, pos, fitted, roll
        last = (anchor, placed)
    raise ValueError('Technic seat fails ' + (fit_failure(*last) or 'the fit rules'))


def technic_seat(support_frame, support_code, moving_code, options, parts, orientation=None, resolve=None):
    """Pose that puts a pin grip or axle in a hole, or a hole on a pin or axle.

    ``hole`` and ``pin`` are port IDs (from ``part``); each belongs to whichever
    part has it. By default the two port centres coincide. Along the shared axis:

    * ``slide``: LDU along the support port's axis;
    * ``end`` (+ ``past``): the named end of the pin or axle stands ``past`` LDU
      beyond the face of the part with the hole (0 is flush);
    * ``next_to`` + ``side``: a part with a hole sits flush against a neighbour
      on the same axle, on the named side of it.

    ``side`` on a pin or axle says which way the rest of it extends from the
    hole; ``flip`` turns a part with a hole end for end; ``roll`` turns the
    placed part about the axis. The result must pass the Technic fit rules.
    """
    if not moving_code.casefold().endswith('.dat'):
        raise ValueError('Technic seats place a part; place a section with join, attach or at')
    rotation, translation = support_frame
    hole_id, pin_id = options.get('hole'), options.get('pin')
    support_ports, moving_ports = technic_ports(parts, support_code), technic_ports(parts, moving_code)
    listing = f"{support_code} ports: {_listed(support_ports)}; {moving_code} ports: {_listed(moving_ports)}"
    if not hole_id or not pin_id:
        raise ValueError('A Technic seat names both hole and pin. ' + listing)
    if hole_id in support_ports and pin_id in moving_ports and support_ports[hole_id]['kind'] in HOLES \
            and moving_ports[pin_id]['kind'] in MALES:
        fixed, moved = support_ports[hole_id], moving_ports[pin_id]
    elif pin_id in support_ports and hole_id in moving_ports and support_ports[pin_id]['kind'] in MALES \
            and moving_ports[hole_id]['kind'] in HOLES:
        fixed, moved = support_ports[pin_id], moving_ports[hole_id]
    else:
        raise ValueError(f'hole {hole_id!r} and pin {pin_id!r} must name a hole on one part and a pin or axle on the other. '
                         + listing)
    male = moved['kind'] in MALES
    axis = rotation @ np.array(fixed['axis'], float)
    axis = axis / np.linalg.norm(axis)
    target = rotation @ np.array(fixed['at'], float) + translation
    local_axis = np.array(moved['axis'], float)
    moved_at = np.array(moved['at'], float)
    side, flip = options.get('side'), options.get('flip', False)
    if sum(key in options for key in ('slide', 'end', 'next_to')) > 1:
        raise ValueError('Use one of slide, end or next_to to position along the axis')
    if 'past' in options and 'end' not in options:
        raise ValueError('past needs end: the end of the pin or axle it measures from')
    # Along the axis.
    offset = options.get('slide', 0)
    half_fixed, half_moved = fixed['length'] / 2, moved['length'] / 2
    if 'end' in options:
        sign = _along(axis, options['end'], 'on.end')
        past = options.get('past', 0)
        offset = sign * (half_fixed + past - half_moved) if male else sign * (half_fixed - past - half_moved)
    elif 'next_to' in options:
        if male:
            raise ValueError('next_to places a part with a hole along an axle; position a pin or axle with slide or end')
        if side is None or resolve is None:
            raise ValueError('next_to needs side: which side of the neighbour this part sits on, along the axle')
        sign = _along(axis, side, 'on.side')
        neighbour_code, (nr, nt) = resolve(options['next_to'])
        faces = []
        for port in technic_ports(parts, neighbour_code).values():
            centre = nr @ np.array(port['at'], float) + nt
            line = centre - target
            if abs(float((nr @ np.array(port['axis'], float)) @ axis)) > 0.999 and \
                    np.linalg.norm(line - (line @ axis) * axis) <= 0.5:
                faces.append(sign * float(line @ axis) + port['length'] / 2)
        if not faces:
            raise ValueError(f"next_to {options['next_to']!r} has no hole, pin or axle on this axis; "
                             f"{neighbour_code} ports: {_listed(technic_ports(parts, neighbour_code))}")
        offset = sign * (max(faces) + half_moved)
    # Orientation.
    if orientation is not None:
        if side is not None and 'next_to' not in options or flip:
            raise ValueError('Use orient or side/flip, not both')
        if abs((orientation @ local_axis) @ axis) < 0.999:
            raise ValueError('orient does not align the port with the hole axis; omit orient or change it')
        rolls, base = [None], orientation
    else:
        if male and side is not None:
            centres = np.array([p['at'] for p in moving_ports.values()], float)
            extent = float((centres.mean(axis=0) - moved_at) @ local_axis)
            base = turning((-1.0 if extent < -1e-6 else 1.0) * local_axis, _along(axis, side, 'on.side') * axis)
        else:
            if side is not None and 'next_to' not in options:
                raise ValueError('side says which way a pin or axle extends, or where a part sits next_to a neighbour; '
                                 'turn a part with a hole end for end with flip')
            toward = axis if local_axis @ axis >= 0 else -axis
            base = turning(local_axis, -toward if flip else toward)
        given = options.get('roll')
        rolls = [given] if given is not None else [0, 45]  # cross axles: the 45 degree alternative keys them
    rot, pos, fitted, roll = _seat_port(support_frame, support_code, fixed, moving_code, moved, base, offset, rolls)
    details = dict(hole=hole_id, pin=pin_id, at=clean(target, 4), behavior=fitted['behavior'], roll=roll,
                   slide=clean_number(offset, 4))
    return rot, pos, details


def join(support_frame, support_code, options, parts, *, moving_code=None, my_port=None):
    """Pose that lays a part or module on another by matching holes, and the pins that hold it.

    ``options['holes']`` maps holes of the support to holes of the placed
    object. ``my_port(name)`` returns ``(leaf_code, port, (rotation, position))``
    for one of the placed object's holes, the frame being the leaf's pose inside
    the object (identity for a part). Returns ``(rotation, position, pins,
    details)``; each pin is ``dict(ref, matrix, position, colour)``.
    """
    rotation, translation = support_frame
    support_ports = technic_ports(parts, support_code)
    if my_port is None:
        own = technic_ports(parts, moving_code)

        def my_port(name):
            if name not in own:
                raise ValueError(f'{moving_code} has no port {name!r}; ports: {_listed(own)}')
            return moving_code, own[name], (np.eye(3), np.zeros(3))
    pairs = []
    for theirs, mine in options['holes'].items():
        if theirs not in support_ports:
            raise ValueError(f'{support_code} has no port {theirs!r}; ports: {_listed(support_ports)}')
        leaf, port, frame = my_port(mine)
        if support_ports[theirs]['kind'] not in HOLES or port['kind'] not in HOLES:
            raise ValueError(f'join matches holes; {theirs} is a {support_ports[theirs]["kind"]} and {mine} a {port["kind"]}. '
                             'Seat a pin or axle with on: {to, hole, pin}')
        centre = frame[0] @ np.array(port['at'], float) + frame[1]
        direction_ = frame[0] @ np.array(port['axis'], float)
        pairs.append(dict(theirs=theirs, mine=mine, support=support_ports[theirs], leaf=leaf, port=port, frame=frame,
                          at=centre, axis=direction_ / np.linalg.norm(direction_)))
    first = pairs[0]
    axis = rotation @ np.array(first['support']['axis'], float)
    axis = axis / np.linalg.norm(axis)
    if 'side' not in options:
        raise ValueError(f"join needs side: which side of {options['to']} the part lies on, "
                         f"{face_name(np.round(axis, 6))} or {face_name(np.round(-axis, 6))}")
    normal = _along(axis, options['side'], 'join.side') * axis
    for pair in pairs:
        pair['target'] = rotation @ np.array(pair['support']['at'], float) + translation + \
            normal * (pair['support']['length'] + pair['port']['length']) / 2
        if abs(float((rotation @ np.array(pair['support']['axis'], float)) @ axis)) < 0.999 or \
                abs(float(pair['axis'] @ first['axis'])) < 0.999:
            raise ValueError(f"join holes must be parallel; {pair['theirs']} -> {pair['mine']} is not parallel to "
                             f"{first['theirs']} -> {first['mine']}")
    # A hole has no direction: keep the placed object the way up its hole already points
    # along the joined side, rather than turning it over; flip turns it over on purpose.
    toward = normal if float(first['axis'] @ normal) >= 0 else -normal
    base = turning(first['axis'], -toward if options.get('flip') else toward)
    if len(pairs) > 1:
        if 'roll' in options:
            raise ValueError('Two matched holes fix the turn; remove roll')
        far = max(pairs[1:], key=lambda p: np.linalg.norm(p['at'] - first['at']))
        own = far['at'] - first['at']
        own = own - (own @ first['axis']) * first['axis']
        want = far['target'] - first['target']
        want = want - (want @ normal) * normal
        if abs(np.linalg.norm(own) - np.linalg.norm(want)) > 0.2 or np.linalg.norm(own) < 1e-6:
            raise ValueError(f"{first['theirs']} and {far['theirs']} are {clean_number(np.linalg.norm(want), 2)} LDU apart, "
                             f"but {first['mine']} and {far['mine']} are {clean_number(np.linalg.norm(own), 2)}; "
                             'match holes with the same spacing')
        turned = base @ own
        angle = math.degrees(math.atan2(float(np.cross(turned, want) @ normal), float(turned @ want)))
        rot = about(normal, angle) @ base
    else:
        rot = about(normal, options.get('roll', 0)) @ base
    rot = np.round(rot, 12) + 0.0
    position = np.array(clean(first['target'] - rot @ first['at'], 9))
    for pair in pairs:
        miss = np.linalg.norm(rot @ pair['at'] + position - pair['target'])
        if miss > 0.2:
            raise ValueError(f"{pair['theirs']} -> {pair['mine']} is {clean_number(miss, 2)} LDU off once the first pair "
                             'is matched; these holes do not line up together')
    pins = []
    chosen = options.get('pins', '2780.dat')
    if chosen:
        code = chosen if chosen.casefold().endswith('.dat') else chosen + '.dat'
        connector = technic_ports(parts, code)
        males = [p for p in connector.values() if p['kind'] in MALES]
        if len(males) < 2:
            raise ValueError(f'{code} cannot join two holes; it has ports: {_listed(connector)}')
        line = np.array(males[0]['axis'], float)
        males.sort(key=lambda p: float(np.array(p['at'], float) @ line))

        def suits(port, hole):
            return (port['kind'] == 'pin' and hole['kind'] == 'pin_hole') or port['kind'] == 'axle'

        for pair in pairs:
            options_ = [(a, b) for i in range(len(males) - 1) for a, b in ((males[i], males[i + 1]), (males[i + 1], males[i]))
                        if suits(a, pair['support']) and suits(b, pair['port'])]
            options_.sort(key=lambda ab: (ab[0]['kind'] == 'axle' and pair['support']['kind'] != 'axle_hole')
                          + (ab[1]['kind'] == 'axle' and pair['port']['kind'] != 'axle_hole'))
            if not options_:
                raise ValueError(f"{code} does not fit {pair['theirs']} ({pair['support']['kind']}) and {pair['mine']} "
                                 f"({pair['port']['kind']}); a pin needs a pin hole, an axle end an axle hole. "
                                 'Choose another connector with pins, or pins: false')
            inner, outer = options_[0]
            outward = np.array(outer['at'], float) - np.array(inner['at'], float)
            heading = line if outward @ line > 0 else -line
            offset = float(axis @ normal) * (pair['support']['length'] - inner['length']) / 2
            pin_rot, pin_pos, _, _ = _seat_port(support_frame, support_code, pair['support'], code, inner,
                                                turning(heading, normal), offset, [0, 45])
            leaf_frame = (rot @ pair['frame'][0], rot @ pair['frame'][1] + position)
            from .technic import fit, fit_failure
            ends = (_world_feature(pair['leaf'], pair['port']['id'], leaf_frame), _world_feature(code, outer['id'], (pin_rot, pin_pos)))
            if fit(*ends) is None:
                raise ValueError(f"{code} does not hold {pair['mine']}: " + (fit_failure(*ends) or 'the fit rules')
                                 + '. Choose another connector with pins, or pins: false')
            pins.append(dict(ref=code, matrix=pin_rot, position=pin_pos,
                             colour=options.get('pin_colour', PIN_COLOURS.get(code.casefold().removesuffix('.dat'), 0))))
    details = dict(holes=[(p['theirs'], p['mine']) for p in pairs], side=face_name(np.round(normal, 6)), pins=len(pins))
    return rot, position, pins, details
