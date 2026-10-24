"""Write ordinary LSynth constraints from measured interfaces; LSynth owns curves.

Endpoint directions point OUT of their fittings. Waypoint directions point along
the route. All coordinates in a block must use the same frame, in LDU.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from ldraw import Matrix, Piece, Vector


def vector(value, name='vector'):
    result = np.asarray(value, dtype=float)
    if result.shape != (3,) or not np.isfinite(result).all():
        raise ValueError(f'{name} must contain three finite numbers')
    return result


def unit(value):
    value = vector(value, 'direction')
    length = np.linalg.norm(value)
    if length < 1e-9:
        raise ValueError('Direction must be nonzero; a reversal needs a deliberate loop')
    return value / length


def rigid(matrix):
    result = np.asarray(matrix, dtype=float)
    if (result.shape != (3, 3) or not np.isfinite(result).all()
            or not np.allclose(result.T @ result, np.eye(3), atol=1e-6, rtol=0)
            or not np.isclose(np.linalg.det(result), 1, atol=1e-6, rtol=0)):
        raise ValueError('Use a proper rotation, never scale, shear or reflection')
    return result


def marker_matrix(direction, up=None):
    """Proper rotation whose local -Y follows travel; optional local Z fixes roll.

Use explicit consistent up vectors for flat cables/straps. The automatic roll is
only a convenience for round material, not a twist or torsion model.
"""
    y = -unit(direction)
    z = vector(up, 'up') if up is not None else np.eye(3)[np.argmin(np.abs(y))]
    z = z - y * (z @ y)
    if np.linalg.norm(z) < 1e-9:
        raise ValueError('Up must not be parallel to the route direction')
    z = unit(z)
    return np.column_stack((np.cross(y, z), y, z))


def placement(part, at, matrix=None, colour=7):
    if not part or any(c in part for c in '\r\n'):
        raise ValueError('Part must be a single reference')
    return Piece.place(part, colour=colour, position=Vector(*vector(at)),
                       matrix=Matrix(rigid(np.eye(3) if matrix is None else matrix).tolist())).to_ldraw()


@dataclass(frozen=True)
class Endpoint:
    at: object
    outward: object
    lead: float = 0.0
    up: object = None

    def __post_init__(self):
        vector(self.at)
        unit(self.outward)
        if not np.isfinite(self.lead) or self.lead < 0:
            raise ValueError('Lead must be a finite nonnegative distance')

    @classmethod
    def on_part(cls, at, matrix, local_at, local_outward, *, lead=0, local_up=None):
        """Transform a measured local fitting frame with the actual part placement."""
        r = rigid(matrix)
        return cls(vector(at) + r @ vector(local_at), r @ unit(local_outward), lead,
                   None if local_up is None else r @ vector(local_up))

    @classmethod
    def from_feature(cls, parts, part, feature_id, *, at=(0, 0, 0), matrix=None, lead=0, local_up=None):
        """Use an explicitly selected connector from `ldraw-agent part PART`.

        The caller must identify the fitting: a generic pin/stud is not necessarily
        a hose nozzle. No automatic guess from radius or colour is made.
        """
        from .common import jsonable
        features = [f for f in parts.geometry(part).connections if f.feature_id == feature_id]
        if len(features) != 1:
            raise ValueError(f'Unknown or ambiguous connector {feature_id!r} on {part}; inspect the part again')
        f = features[0]
        return cls.on_part(at, np.eye(3) if matrix is None else matrix,
                           jsonable(f.position), jsonable(f.axis), lead=lead, local_up=local_up)


@dataclass(frozen=True)
class Waypoint:
    at: object
    direction: object = None
    up: object = None


def hose(start, end, *, via=(), method='TECHNIC_PNEUMATIC_HOSE_BEVELED', colour=4, name='hose'):
    """One editable SYNTH block; directions at the final fitting are reversed here.

Leads are explicit because fittings and end-piece lengths differ between families.
No curve approximation, radius promise or automatic obstacle routing is performed.
"""
    from .flex_knowledge import resolve
    _, definition, kind = resolve(method)
    if kind != 'hose':
        raise ValueError(f'{method} uses wheel constraints; use band()')
    if not isinstance(start, Endpoint) or not isinstance(end, Endpoint):
        raise ValueError('start and end must be Endpoint instances')
    points = [Waypoint(start.at, start.outward, start.up)]
    if start.lead:
        points.append(Waypoint(vector(start.at) + start.lead * unit(start.outward), start.outward, start.up))
    points.extend(w if isinstance(w, Waypoint) else Waypoint(w) for w in via)
    if end.lead:
        points.append(Waypoint(vector(end.at) + end.lead * unit(end.outward), -unit(end.outward), end.up))
    points.append(Waypoint(end.at, -unit(end.outward), end.up))
    coords = [vector(w.at) for w in points]
    if any(np.linalg.norm(b - a) < 1e-6 for a, b in zip(coords, coords[1:])):
        raise ValueError('Consecutive constraints coincide; remove the duplicate or shorten the lead')
    rows = []
    for i, w in enumerate(points):
        direction = w.direction
        if direction is None:
            direction = unit(coords[i] - coords[i - 1]) + unit(coords[i + 1] - coords[i])
        rows.append(placement('LS01.dat', w.at, marker_matrix(direction, w.up), colour))
    return block(method, colour, rows, name=name)


def block(method, colour, rows, *, name='route', hide=False):
    from .flex import engine, preflight
    if any(c in name for c in '\r\n'):
        raise ValueError('Route name must be a single line')
    lines = [f'0 // {name}', f'0 SYNTH BEGIN {method} {colour}']
    if hide:
        lines.append('0 SYNTH HIDE')
    lines.extend(rows)
    lines.append('0 SYNTH END')
    result = '\r\n'.join(lines) + '\r\n'
    preflight(result, engine()[0])
    return result


def band(wheels, *, method='RUBBER_BAND', colour=0, name='loop', hide=False):
    """Wheel placement rows interleaved with INSIDE/OUTSIDE/CROSS control strings.

Use placement() for the actual mounted wheels. hide=True keeps routing wheels
out of the physical assembly when the rigid model already owns them.
"""
    from .flex_knowledge import resolve
    _, _, kind = resolve(method)
    if kind != 'band':
        raise ValueError(f'{method} uses path markers; use hose()')
    return block(method, colour, wheels, name=name, hide=hide)


def document(*blocks, name='constraints.ldr', author='ldraw-nova'):
    if any(c in name + author for c in '\r\n'):
        raise ValueError('Name and author must be single lines')
    return '\r\n'.join([f'0 {name}', f'0 Name: {name}', f'0 Author: {author}',
                        '0 !LDRAW_ORG Model']) + '\r\n' + ''.join(blocks)
