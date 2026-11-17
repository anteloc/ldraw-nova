"""Mirror a built section without mirrored matrices.

LDraw forbids reflected placements, so a left/right copy of a module cannot be
a mirrored reference. Instead every part is placed as its own mirror image:
for a part that is symmetric about one of its local planes (most beams,
liftarms, gears and connectors), the reflected pose ``M R`` composed with that
local reflection ``S`` is a proper rotation that shows the same plastic; a
part without such a plane is replaced by its Left/Right partner. Sub-sections
are mirrored recursively.
"""
from __future__ import annotations

import re
from dataclasses import replace

import numpy as np
from ldraw import Matrix, Model, Piece, Vector
from ldraw.lines import Comment

from .common import jsonable, normalized

AXES = dict(x=0, y=1, z=2)
REFLECTIONS = (np.diag([-1.0, 1, 1]), np.diag([1.0, -1, 1]), np.diag([1.0, 1, -1]))
_SYMMETRY = {}


def _points(parts, code):
    geometry = parts.geometry(code)
    points = np.array([(p.x, p.y, p.z) for p in geometry.points], float).reshape(-1, 3)
    return np.unique(np.round(points, 2), axis=0)


def _share(points, other):
    keys = {tuple(np.round(p / 0.05).astype(int)) for p in other}
    return sum(tuple(np.round(p / 0.05).astype(int)) in keys for p in points) / max(len(points), 1)


def _ports_kept(code, reflection):
    """Every Technic port maps onto a port of the same kind under the reflection."""
    from .technic import canonical, registry
    entry = registry()['parts'].get(canonical(code))
    if not entry:
        return False
    ports = [(p['kind'], np.array(p['at'], float), np.array(p['axis'], float)) for p in entry['ports']]
    return all(any(kind == k and np.linalg.norm(reflection @ at - a) < 0.1 and abs(abs(float((reflection @ axis) @ x)) - 1) < 1e-6
                   for k, a, x in ports) for kind, at, axis in ports)


# Parts whose only asymmetry is a coil spring or a moulded thread that does no work.
SPRUNG = re.compile(r'Shock Absorber|Pneumatic Cylinder|Linear Actuator|Spring', re.I)


def _matches(points, other, share=0.98):
    """Share of ``points`` that lie on ``other`` (to 0.05 LDU)."""
    if not len(points) or len(points) != len(other) and abs(len(points) - len(other)) > 0.01 * len(points):
        return False
    keys = {tuple(np.round(p / 0.05).astype(int)) for p in other}
    found = sum(tuple(np.round(p / 0.05).astype(int)) in keys for p in points)
    return found >= share * len(points)


def symmetry(parts, code):
    """(replacement code, local reflection) that draws the mirror image of ``code``, or None."""
    key = code.casefold()
    if key in _SYMMETRY:
        return _SYMMETRY[key]
    points = _points(parts, key)
    result = None
    for reflection in REFLECTIONS:
        if _matches(points @ reflection, points):
            result = (code, reflection)
            break
    description = parts.by_code.get(key, '') if hasattr(parts, 'by_code') else ''
    if result is None and SPRUNG.search(description):
        kept = [r for r in REFLECTIONS if _ports_kept(key, r)]
        if kept:
            result = (code, max(kept, key=lambda r: _share(points @ r, points)))
    if result is None:
        swapped = re.sub(r'\b(Left|Right)\b', lambda m: 'Right' if m.group(1) == 'Left' else 'Left', description)
        partner = None
        if swapped != description:
            partner = next((c for c, d in parts.by_code.items() if d == swapped), None)
        if partner:
            other = _points(parts, partner)
            for reflection in REFLECTIONS:
                if _matches(points @ reflection, other):
                    result = (partner, reflection)
                    break
    _SYMMETRY[key] = result
    return result


def mirror_model(model, axis, models, parts, made):
    """A mirrored copy of ``model`` (registered in ``models`` and ``made``) and its name."""
    name = f"{Path_stem(model.name)}-mirror-{axis}.ldr"
    if name in made:
        return made[name]
    flip = np.eye(3)
    flip[AXES[axis], AXES[axis]] = -1
    copy = Model(name=name)
    copy.set_header(description=(model.description or model.name) + f' (mirrored in {axis})', name=name,
                    author=model.author or 'ldraw-nova', ldraw_org='Model')
    if model.license:
        copy.set_header(license=model.license)
    by_name = {normalized(n): m for n, m in models.items()}
    for obj in model.objects:
        if not isinstance(obj, Piece):
            copy.objects.append(obj)
            continue
        rotation = np.asarray(obj.matrix.rows, float)
        position = flip @ np.asarray(jsonable(obj.position), float)
        reference = obj.reference
        child = by_name.get(normalized(reference))
        if child is not None and not reference.casefold().endswith('.dat'):
            mirrored = mirror_model(child, axis, models, parts, made)
            reference, rotation = mirrored.name, flip @ rotation @ flip
        else:
            found = symmetry(parts, reference.casefold().removesuffix('.dat'))
            if found is None:
                raise ValueError(f"{reference} has no plane of symmetry and no Left/Right partner, so it cannot be "
                                 f"mirrored; place the other side's {reference} by hand")
            code, reflection = found
            reference, rotation = code if code.casefold().endswith('.dat') else code + '.dat', flip @ rotation @ reflection
        copy.objects.append(Piece.place(reference, colour=getattr(obj.colour, 'code', obj.colour), position=Vector(*position),
                                        matrix=Matrix(np.round(rotation, 12).tolist())))
    made[name] = copy
    models[name] = copy
    return copy


def Path_stem(name):
    return name[:-4] if name.casefold().endswith('.ldr') else name
