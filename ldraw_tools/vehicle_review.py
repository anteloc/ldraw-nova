"""Bounded review evidence for symmetric, fixed-axle System road vehicles."""
from __future__ import annotations

import math
import numpy as np
from ldraw import inspect_model

from .common import issue, jsonable
from .document import physical_context
from .geometry import profiles, body_box
from .vehicles import WHEEL_PACKS


def review_vehicle(model, parts, *, ground_y=0.0, limit=100, instance_limit=100000):
    if not math.isfinite(ground_y):
        raise ValueError('Ground Y must be finite')
    if limit < 1 or instance_limit < 1:
        raise ValueError('Review limits must be positive')
    model, parts = physical_context(model, parts)
    occurrences = []
    for occurrence in model.iter_occurrences():
        occurrences.append(occurrence)
        if len(occurrences) > instance_limit:
            raise ValueError('Vehicle review instance budget exceeded; select a subassembly')
    inspection = inspect_model(model, parts, occurrences=occurrences)
    diagnostics = [d.to_dict() for d in inspection.diagnostics]
    if not inspection.complete:
        diagnostics.append(issue('vehicle.incomplete', 'Part geometry is incomplete.'))
    tyre_packs = {p['tyre']: p for p in WHEEL_PACKS.values()}
    wheels, unknown, intrusions = [], [], []
    regular = profiles()
    tolerance = .05  # Rounding/tessellation allowance in LDU, not mechanical clearance.
    for item in inspection.occurrences:
        o = item.occurrence
        code = o.part_code.casefold()
        description = parts.by_code.get(code, '')
        if description.lstrip('~=').strip().casefold().startswith('technic '):
            diagnostics.append(issue('vehicle.technic_part', 'Technic part outside this System vehicle workflow.',
                                     instance=item.index, ref=o.reference))
        if code not in tyre_packs:
            if 'tyre' in description.casefold() or description.casefold().startswith('wheel '):
                if code not in {p['rim'] for p in WHEEL_PACKS.values()}:
                    unknown.append(dict(instance=item.index, ref=o.reference))
            continue
        matrix = np.asarray(o.matrix.rows)
        position = np.array(jsonable(o.position))
        if not np.allclose(np.abs(matrix[:, 2]), [1,0,0], atol=1e-5):
            diagnostics.append(issue('vehicle.wheel_axis', 'Road wheel axis must run across X; inspect wheel orientation.',
                                     instance=item.index, ref=o.reference))
            continue
        bounds = item.local.bounds
        if bounds is None:
            continue
        local = np.array([jsonable(bounds.min), jsonable(bounds.max)])
        centre = matrix @ local.mean(axis=0) + position
        radius = float(max(local[1, :2]-local[0, :2])/2)
        width = float(local[1, 2]-local[0, 2])
        bottom = centre[1]+radius
        wheel = dict(instance=item.index, ref=o.reference, centre=centre.tolist(),
                     radius_ldu=radius, width_ldu=width, ground_error_ldu=float(bottom-ground_y))
        wheels.append(wheel)
        if abs(bottom-ground_y) > tolerance:
            diagnostics.append(issue('vehicle.ground_contact', 'Tyre does not meet the declared road plane.',
                                     instance=item.index, ground_error_ldu=float(bottom-ground_y)))
        # Verify the shortcut's actual mating offset, including outward face.
        pack = tyre_packs[code]
        rim_position = position - matrix @ np.array([0,0,pack['tyre_offset']])
        candidates = [other for other in inspection.occurrences
                      if other.occurrence.part_code.casefold() == pack['rim']
                      and np.allclose(jsonable(other.occurrence.position), rim_position, atol=tolerance, rtol=0)
                      and np.allclose(np.asarray(other.occurrence.matrix.rows)[:,2], matrix[:,2], atol=1e-5)]
        if len(candidates) != 1:
            diagnostics.append(issue('vehicle.rim_fit', 'Expected one matching rim at the official shortcut offset.',
                                     instance=item.index, rim=pack['rim']+'.dat', expected_position=rim_position.tolist()))
        # Conservative full circular swept space, with an axial slab. This
        # reserves rolling room, not the rubber's actual hollow material volume.
        for other in inspection.occurrences:
            co = other.occurrence
            if co.part_code.casefold() in {pack['tyre'], pack['rim'], pack['holder']}:
                continue
            profile = regular.get(co.part_code.casefold())
            box = body_box(co, profile) if profile else None
            if box is None:
                continue
            if min(box[1,0], centre[0]+width/2)-max(box[0,0], centre[0]-width/2) <= tolerance:
                continue
            nearest = np.maximum(box[0,1:], np.minimum(centre[1:], box[1,1:]))
            distance = float(np.linalg.norm(nearest-centre[1:]))
            if distance < radius-tolerance:
                intrusions.append(dict(wheel=item.index, body=other.index, ref=co.reference,
                                       radial_intrusion_ldu=radius-distance))
    if not wheels:
        diagnostics.append(issue('vehicle.no_supported_wheels', 'No supported transverse tyres found; use vehicle wheels.'))
    if unknown:
        diagnostics.append(issue('vehicle.unreviewed_wheels', 'Additional wheels/tyres need manual fit and ground review.',
                                 severity='warning', count=len(unknown)))
    if intrusions:
        diagnostics.append(issue('vehicle.wheel_space', 'Rectangular body envelopes enter circular wheel space; review rolling clearance.',
                                 severity='warning', count=len(intrusions)))
    axles = []
    for wheel in sorted(wheels, key=lambda w: (w['centre'][2], w['centre'][0])):
        group = next((a for a in axles if abs(a['z_ldu']-wheel['centre'][2]) <= tolerance), None)
        if group is None:
            group = dict(z_ldu=wheel['centre'][2], wheels=[])
            axles.append(group)
        group['wheels'].append(wheel)
    for a in axles:
        pair = a.pop('wheels')
        a['instances'] = [w['instance'] for w in pair]
        if len(pair) != 2:
            diagnostics.append(issue('vehicle.axle_pair', 'Expected a left/right wheel pair at this axle station.',
                                     z_ldu=a['z_ldu'], instances=a['instances']))
            continue
        left, right = sorted(pair, key=lambda w: w['centre'][0])
        a['track_ldu'] = right['centre'][0]-left['centre'][0]
        if (left['centre'][0] >= 0 or right['centre'][0] <= 0 or
                abs(left['centre'][0]+right['centre'][0]) > tolerance or
                abs(left['centre'][1]-right['centre'][1]) > tolerance or
                abs(left['radius_ldu']-right['radius_ldu']) > tolerance):
            diagnostics.append(issue('vehicle.axle_symmetry', 'Wheel pair is not symmetric about X=0 at equal height/radius.',
                                     instances=a['instances']))
    if wheels and len(axles) < 2:
        diagnostics.append(issue('vehicle.axle_count', 'Whole road-vehicle review expects at least two axle stations.'))
    wheel_indices = {w['instance'] for w in wheels}
    for item in inspection.occurrences:
        if item.index not in wheel_indices and item.bounds and item.bounds.max.y > ground_y+tolerance:
            diagnostics.append(issue('vehicle.below_road', 'Non-tyre geometry extends below the road plane.',
                                     instance=item.index, ref=item.occurrence.reference))
    return dict(checks_passed=not any(d['severity']=='error' for d in diagnostics),
                physical_validity='not_proven', ground_y=ground_y, diagnostics=diagnostics,
                wheel_count=len(wheels), axle_count=len(axles),
                wheelbase_ldu=axles[-1]['z_ldu']-axles[0]['z_ldu'] if len(axles)>1 else None,
                wheels=wheels[:limit], axles=axles[:limit], unreviewed_wheels=unknown[:limit],
                wheel_space_candidates=intrusions[:limit],
                truncated=any(len(rows)>limit for rows in [wheels,axles,unknown,intrusions]),
                coverage=dict(geometry_complete=inspection.complete, occurrences=len(occurrences),
                              supported_tyres=sorted(tyre_packs),
                              clearance='Circular wheel envelope versus upright curated rectangular bodies only'),
                limitations=['Symmetric road vehicles in the documented frame only; no steering, suspension, dual wheels or spare-wheel classification.',
                             'Curved fenders, slopes and SNOT bodywork still require material/visual clearance review.',
                             'Rim alignment does not establish wheel-pin retention, clutch, strength or physical rolling freedom.',
                             'No aesthetic score or part/colour availability claim; use assembly validation and opened renders too.'])
