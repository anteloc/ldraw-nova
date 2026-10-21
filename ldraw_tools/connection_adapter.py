"""Version-pinned frame adaptation for pyldraw3 1.7 stud/wheel mating.

LDCad SNAP_CYL female spans point inward (-Y in the meta frame). pyldraw's
strict stud contact query expects an outward receptacle axis instead. Its
generic snap solver aligns axes, so primitive outward sockets need the inverse
adaptation there. Only temporary query frames change, never library metadata.
Remove/retest this adapter when changing the pyldraw3 dependency pin.
"""
from dataclasses import replace

from ldraw import Matrix
from ldraw.connection_types import (ConnectionKind, ConnectionSource, ConnectionRole,
                                    CylindricalProfile, CylindricalCaps, SectionShape)

LDCAD = {ConnectionSource.LDCAD_SHADOW, ConnectionSource.LDCAD_INLINE}
REVERSE_AXIS = Matrix([[1, 0, 0], [0, -1, 0], [0, 0, 1]])

# Inspected closed underside cavities; pyldraw 1.7 labels R 6 cylinders
# longer than a stud as pin holes. Keep this separate from generic pin mating.
# 67329 inherits its underside from 22885. See the parrot SNOT reference.
DEEP_STUD_SOCKETS = {'22885': 36, '67329': 36, '47457': 12}


def query_frames(inspection, *, snapping=False):
    def adapt(feature, item):
        # 6014a/b is wider along Z than its rim diameter. The 1.7 annular
        # heuristic picks the shortest bounding-box axis (X), although the
        # wheel hole and official 6014bc01 shortcut establish local Z as axle.
        # Correct query evidence only, retaining the official shortcut centre
        # at Z=-6 and its compatibility list. Never rewrite source geometry.
        if (item.occurrence.part_code.casefold() in {'6014a', '6014b'}
                and feature.kind is ConnectionKind.RIM_SEAT
                and feature.source is ConnectionSource.SHORTCUT
                and '6015' in feature.compatible_parts):
            bounds = item.local.bounds
            feature = replace(feature,
                              frame=item.occurrence.matrix * Matrix([[1,0,0],[0,0,-1],[0,1,0]]),
                              profile=replace(feature.profile, radius=max(bounds.size.x,bounds.size.y)/2,
                                              width=bounds.size.z),
                              provenance=(*feature.provenance, 'nova:6014-local-Z-wheel-axis'))
        authored = feature.source in LDCAD
        profile = feature.profile
        deep_stud_socket = (
            item.occurrence.part_code.casefold() in DEEP_STUD_SOCKETS
            and feature.kind is ConnectionKind.PIN_HOLE
            and isinstance(profile, CylindricalProfile)
            and len(profile.sections) == 1
            and profile.sections[0].shape is SectionShape.ROUND
            and abs(profile.length - DEEP_STUD_SOCKETS[item.occurrence.part_code.casefold()]) < 1e-6
        )
        # LDCad uses closed S 6 cavities for ordinary 1-wide brick/slope
        # undersides. pyldraw 1.7 classifies long ones as pin holes and rejects
        # round/square profile pairs. The inspected deep round sockets above
        # have the same classification problem. Both projections remain
        # potential evidence; other round/axle/pin interfaces are unchanged.
        if (authored and feature.role is ConnectionRole.FEMALE
                and isinstance(profile, CylindricalProfile) and not profile.centered
                and profile.caps in {CylindricalCaps.ONE, CylindricalCaps.B}
                and profile.length >= 4 and profile.sections
                and all((s.shape is SectionShape.SQUARE or deep_stud_socket) and abs(s.radius-6) < 1e-6
                        and not s.flexible for s in profile.sections)):
            feature = replace(feature, kind=ConnectionKind.STUD_RECEPTACLE,
                              source=ConnectionSource.HEURISTIC, confidence=min(feature.confidence, 0.8),
                              profile=replace(profile, sections=tuple(replace(s, shape=SectionShape.ROUND)
                                                                     for s in profile.sections)),
                              provenance=(*feature.provenance,
                                          'nova:deep-stud-socket' if deep_stud_socket
                                          else 'nova:inscribed-stud-in-square-socket'))
        if feature.kind is ConnectionKind.STUD_RECEPTACLE and (authored != snapping):
            feature = replace(feature, frame=feature.frame * REVERSE_AXIS)
        return feature
    return replace(inspection, occurrences=tuple(
        replace(item, connections=tuple(adapt(f, item) for f in item.connections))
        for item in inspection.occurrences))


def connection_contacts(inspection):
    from .technic import managed, contacts
    ordinary = replace(inspection, occurrences=tuple(replace(o, connections=tuple(
        f for f in o.connections if not managed(f))) for o in inspection.occurrences))
    return (*query_frames(ordinary).connection_contacts(), *contacts(inspection))
