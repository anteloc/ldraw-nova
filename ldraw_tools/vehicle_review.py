"""Bounded, explicit review profiles for the taught System vehicle interfaces."""
from __future__ import annotations

import math
import numpy as np
from ldraw import inspect_model

from .common import issue, jsonable
from .document import physical_context
from .geometry import profiles, body_box
from .vehicles import WHEEL_PACKS


PROFILES = ('road', 'motorcycle', 'watercraft', 'aircraft')


def family_evidence(inspection, profile, diagnostics):
    """Check known dedicated assemblies; do not infer physical capability."""
    items = inspection.occurrences
    def find(code):
        return [i for i in items if i.occurrence.part_code.casefold() == code]
    def matched(source, target, offset=(0,0,0)):
        origins = find(source)
        for item in origins:
            o = item.occurrence
            matrix = np.asarray(o.matrix.rows)
            at = np.array(jsonable(o.position)) + matrix @ np.array(offset)
            matches = [i for i in find(target)
                       if np.allclose(jsonable(i.occurrence.position), at, atol=.05, rtol=0)
                       and np.allclose(i.occurrence.matrix.rows, matrix, atol=1e-5)]
            if len(matches) != 1:
                diagnostics.append(issue('vehicle.assembly_fit', 'Expected one matching dedicated part at the measured interface.',
                                         instance=item.index, ref=source+'.dat', mate=target+'.dat', expected_position=at.tolist()))
        return origins
    def symmetric_pair(first, second):
        left, right = find(first), find(second)
        if first == second:
            left = [i for i in left if i.occurrence.position.x < 0]
            right = [i for i in right if i.occurrence.position.x > 0]
        if len(left) != 1 or len(right) != 1:
            diagnostics.append(issue('vehicle.family_pair', 'Expected one supported part on each side.', refs=[first,second]))
            return
        a,b = [np.array(jsonable(i.occurrence.position)) for i in (left[0],right[0])]
        if a[0] >= 0 or b[0] <= 0 or not np.allclose(a*[-1,1,1], b, atol=.05, rtol=0):
            diagnostics.append(issue('vehicle.family_symmetry', 'Dedicated left/right parts must share height and longitudinal station about X=0.', refs=[first,second]))
    if profile == 'motorcycle':
        required = {'frame':'50859b', 'fairing':'85983'}
        matched('85983','50859b',(0,41.5,-60))
        for frame in find('50859b'):
            o = frame.occurrence
            for z in [-43.5,63.5]:
                at = np.array(jsonable(o.position)) + np.array(o.matrix.rows) @ [0,-3.7,z]
                if not any(np.allclose(jsonable(w.occurrence.position),at,atol=.05,rtol=0) for w in find('50862')):
                    diagnostics.append(issue('vehicle.motorcycle_axle', 'Wheel is missing from a measured frame axle.', instance=frame.index, expected_position=at.tolist()))
    elif profile == 'watercraft':
        required = {'hull':'2551', 'seat':'4079', 'helm':'3829c01'}
    else:
        required = {'nose':'87613', 'glazing':'87612', 'nose_floor':'87611',
                    'rear':'87616', 'port_wing':'30355', 'starboard_wing':'30356',
                    'engine_shell':'4868b', 'engine_core':'4869', 'pilot_seat':'4079'}
        matched('87613','87612')
        matched('87613','87611',(0,96,-20))
        matched('4868b','4869')
        symmetric_pair('30355','30356')
        symmetric_pair('4868b','4868b')
        for code, expected in [('30355',90),('30356',-90)]:
            from .builder import rotation
            for item in find(code):
                if not np.allclose(item.occurrence.matrix.rows, rotation('y',expected).rows, atol=1e-5):
                    diagnostics.append(issue('vehicle.wing_orientation', 'Supported swept wing must face across X with its broad root at the fuselage.', instance=item.index))
    evidence = {role: [i.index for i in find(code)] for role,code in required.items()}
    for role, indices in evidence.items():
        if not indices:
            diagnostics.append(issue('vehicle.family_part', 'Required part of this bounded review profile is missing; other designs need their own interface review.', role=role, ref=required[role]+'.dat'))
    return evidence


def review_vehicle(model, parts, *, profile='road', ground_y=0.0, limit=100, instance_limit=100000):
    if profile not in PROFILES:
        raise ValueError('Unknown vehicle review profile: '+str(profile))
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
    tyre_packs = ({'50861':dict(rim='50862',tyre='50861',holder='50859b',tyre_offset=0)}
                  if profile=='motorcycle' else {p['tyre']: p for p in WHEEL_PACKS.values()})
    wheels, unknown, intrusions = [], [], []
    regular = profiles()
    tolerance = .05  # Rounding/tessellation allowance in LDU, not mechanical clearance.
    for item in inspection.occurrences:
        o = item.occurrence
        code = o.part_code.casefold()
        description = parts.by_code.get(code, '')
        if 'technic' in description.casefold():
            diagnostics.append(issue('vehicle.technic_part', 'Technic part outside this System vehicle workflow.',
                                     instance=item.index, ref=o.reference))
        if profile in {'watercraft','aircraft'}:
            continue
        if code not in tyre_packs:
            if 'tyre' in description.casefold() or description.casefold().startswith('wheel '):
                if code not in {p['rim'] for p in tyre_packs.values()}:
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
            body_profile = regular.get(co.part_code.casefold())
            box = body_box(co, body_profile) if body_profile else None
            if box is None:
                continue
            if min(box[1,0], centre[0]+width/2)-max(box[0,0], centre[0]-width/2) <= tolerance:
                continue
            nearest = np.maximum(box[0,1:], np.minimum(centre[1:], box[1,1:]))
            distance = float(np.linalg.norm(nearest-centre[1:]))
            if distance < radius-tolerance:
                intrusions.append(dict(wheel=item.index, body=other.index, ref=co.reference,
                                       radial_intrusion_ldu=radius-distance))
    evidence = family_evidence(inspection, profile, diagnostics) if profile!='road' else {}
    if profile in {'watercraft','aircraft'}:
        return dict(profile=profile, checks_passed=not any(d['severity']=='error' for d in diagnostics),
                    physical_validity='not_proven', diagnostics=diagnostics,
                    family_parts={k:v[:limit] for k,v in evidence.items()},
                    truncated=any(len(v)>limit for v in evidence.values()),
                    coverage=dict(geometry_complete=inspection.complete, occurrences=len(occurrences),
                                  wheel_review='not_applicable',
                                  interfaces='Known atlas hull/cockpit inventory' if profile=='watercraft' else 'Known atlas nose/glazing/core transforms and symmetric wing/engine positions'),
                    limitations=['Profile covers the named atlas part families, not every boat or aircraft.',
                                 'Run assembly geometry/contact checks and open renders; part presence and alignment alone do not prove attachment or clearance.',
                                 'No buoyancy, seaworthiness, flight, balance, landing-gear, strength, minifigure fit or retail colour-availability claim.'])
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
        if profile == 'motorcycle':
            if len(pair)!=1 or abs(pair[0]['centre'][0])>tolerance:
                diagnostics.append(issue('vehicle.motorcycle_wheel', 'Expected one centreline wheel at each motorcycle station.', z_ldu=a['z_ldu']))
            continue
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
    if profile=='motorcycle' and len(wheels)!=2:
        diagnostics.append(issue('vehicle.motorcycle_count', 'Supported motorcycle frame expects exactly two wheels.'))
    wheel_indices = {w['instance'] for w in wheels}
    for item in inspection.occurrences:
        if item.index not in wheel_indices and item.bounds and item.bounds.max.y > ground_y+tolerance:
            diagnostics.append(issue('vehicle.below_road', 'Non-tyre geometry extends below the road plane.',
                                     instance=item.index, ref=item.occurrence.reference))
    return dict(profile=profile, checks_passed=not any(d['severity']=='error' for d in diagnostics),
                family_parts={k:v[:limit] for k,v in evidence.items()},
                physical_validity='not_proven', ground_y=ground_y, diagnostics=diagnostics,
                wheel_count=len(wheels), axle_count=len(axles),
                wheelbase_ldu=axles[-1]['z_ldu']-axles[0]['z_ldu'] if len(axles)>1 else None,
                wheels=wheels[:limit], axles=axles[:limit], unreviewed_wheels=unknown[:limit],
                wheel_space_candidates=intrusions[:limit],
                truncated=any(len(rows)>limit for rows in [wheels,axles,unknown,intrusions]),
                coverage=dict(geometry_complete=inspection.complete, occurrences=len(occurrences),
                              supported_tyres=sorted(tyre_packs),
                              clearance='Circular wheel envelope versus upright curated rectangular bodies only'),
                limitations=['Symmetric road vehicles or the supported two-wheel motorcycle frame in the documented frame only; no steering, suspension, dual wheels or spare-wheel classification.',
                             'Curved fenders, slopes and SNOT bodywork still require material/visual clearance review.',
                             'Rim alignment does not establish wheel-pin retention, clutch, strength or physical rolling freedom.',
                             'No aesthetic score or part/colour availability claim; use assembly validation and opened renders too.'])
