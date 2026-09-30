"""Agent-facing connection discovery and rigid occurrence/submodel snapping."""
from __future__ import annotations

import copy
import hashlib
from dataclasses import replace

import numpy as np
from ldraw import Matrix, Vector, inspect_model
from ldraw.part_geometry_types import BoundingBox

from .collision import collision_pairs
from .common import jsonable, normalized
from .document import physical_context
from .connection_adapter import connection_contacts, query_frames


def metadata_summary(metadata):
    if metadata is None:
        return dict(coverage='none', source_count=0, diagnostics=[])
    return {key: jsonable(getattr(metadata, key)) for key in (
        'coverage', 'source_count', 'recognized_record_count',
        'unsupported_record_count', 'invalid_record_count', 'diagnostics')}


def inspect_connections(model, parts, instance_limit=100000):
    model, parts = physical_context(model, parts)
    occurrences = []
    for occurrence in model.iter_occurrences(include_steps=True):
        occurrences.append(occurrence)
        if len(occurrences) > instance_limit:
            raise ValueError(f'Connection budget exceeds {instance_limit} occurrences; select a section')
    from .technic import curate
    return curate(inspect_model(model, parts, occurrences=occurrences))


def occurrence_at(inspection, index):
    if not isinstance(index, int) or isinstance(index, bool) or index < 0:
        raise ValueError('Occurrence indices must be nonnegative integers')
    for item in inspection.occurrences:
        if item.index == index:
            return item
    raise ValueError(f'No physical occurrence {index}; inspect the same section to find valid indices')


def placement_path(occurrence, cache=None):
    """Indices of type-1 placements, independent of source line availability."""
    cache = {} if cache is None else cache
    path = []
    for hop in occurrence.path:
        if id(hop.model) not in cache:
            cache[id(hop.model)] = {id(p): i for i, p in enumerate(hop.model.pieces)}
        path.append(cache[id(hop.model)][id(hop.piece)])
    return path


def connection_report(model, parts, occurrence, *, limit=50, offset=0, instance_limit=100000):
    if limit <= 0 or offset < 0:
        raise ValueError('limit must be positive and offset nonnegative')
    inspection = inspect_connections(model, parts, instance_limit)
    item = occurrence_at(inspection, occurrence)
    contacts = connection_contacts(inspection)
    occupied = {}
    for contact in contacts:
        for owner, feature, peer in ((contact.first_occurrence, contact.first, contact.second_occurrence),
                                     (contact.second_occurrence, contact.second, contact.first_occurrence)):
            if owner.index == occurrence:
                occupied.setdefault(feature.feature_id, []).append(dict(occurrence=peer.index, status=str(contact.status)))
    adapted = occurrence_at(query_frames(inspection), occurrence)
    interpretations = {f.feature_id: f for f in adapted.connections}
    features = [dict(**jsonable(f), contacts=occupied.get(f.feature_id, []),
                     mating_kind=str(interpretations[f.feature_id].kind),
                     mating_source=str(interpretations[f.feature_id].source)) for f in item.connections[offset:offset+limit]]
    return dict(complete=inspection.complete, occurrence=occurrence, part=item.occurrence.reference,
                placement_path=placement_path(item.occurrence), coordinate_space='world',
                metadata=metadata_summary(item.local.connection_metadata), diagnostics=jsonable(inspection.diagnostics),
                connector_count=len(item.connections), connectors=features,
                offset=offset, truncated=offset > 0 or len(item.connections) > offset+limit)


def pose(position, matrix):
    transform = np.eye(4)
    transform[:3, :3] = jsonable(matrix)
    transform[:3, 3] = jsonable(position)
    return transform


def transform_dict(transform):
    return dict(position=transform[:3, 3].tolist(), matrix=transform[:3, :3].tolist())


def moved_inspection(inspection, indices, delta):
    position, matrix = Vector(*delta[:3, 3]), Matrix(delta[:3, :3].tolist())
    moved = []
    for item in inspection.occurrences:
        if item.index not in indices:
            moved.append(item)
            continue
        occurrence = replace(item.occurrence, position=position + matrix * item.occurrence.position,
                             matrix=matrix * item.occurrence.matrix)
        # Transform actual expanded points, not an already enlarged world AABB.
        points = np.array([jsonable(p) for p in item.local.points])
        points = points @ np.asarray(occurrence.matrix.rows).T + np.array(jsonable(occurrence.position))
        moved.append(replace(item, attribution=replace(item.attribution, occurrence=occurrence),
                             bounds=BoundingBox(Vector(*points.min(axis=0)), Vector(*points.max(axis=0))),
                             connections=tuple(f.transformed(position=position, matrix=matrix, inherit=False)
                                               for f in item.connections)))
    return replace(inspection, occurrences=tuple(moved))


def snap_report(model, parts, moving, fixed=None, *, limit=5, moving_depth=None,
                moving_feature=None, fixed_feature=None, max_candidates=100,
                instance_limit=100000, allow_occupied=False):
    """Rank distinct placements and check the entire moving subtree against peers.

    A depth is zero-based in the selected leaf's root-to-leaf path. Omitted
    depth moves the leaf; depth 0 moves its outermost assembly occurrence.
    """
    from .geometry import profiles
    if limit <= 0 or max_candidates <= 0:
        raise ValueError('limit and max_candidates must be positive')
    inspection = inspect_connections(model, parts, instance_limit)
    if not inspection.complete:
        raise ValueError('Cannot snap incomplete geometry/metadata; inspect diagnostics first')
    subject = occurrence_at(inspection, moving)
    path = subject.occurrence.path
    depth = len(path)-1 if moving_depth is None else moving_depth
    if not isinstance(depth, int) or depth < 0 or depth >= len(path):
        raise ValueError(f'moving depth must be between 0 and {len(path)-1}')
    path_cache = {}
    selected_path = placement_path(subject.occurrence, path_cache)[:depth+1]
    moving_indices = {o.index for o in inspection.occurrences
                      if placement_path(o.occurrence, path_cache)[:depth+1] == selected_path}
    if fixed is not None:
        occurrence_at(inspection, fixed)
        if fixed in moving_indices:
            raise ValueError('The fixed occurrence belongs to the moving part/submodel')
    targets = [o for o in inspection.occurrences if o.index not in moving_indices and (fixed is None or o.index == fixed)]
    if len(subject.connections) * sum(len(o.connections) for o in targets) > 100000:
        raise ValueError('More than 100000 connector pairs; select --fixed or a smaller section')
    for name, value, features in [('moving', moving_feature, subject.connections),
                                  ('fixed', fixed_feature, [f for o in targets for f in o.connections])]:
        if value is not None and not any(f.feature_id == value for f in features):
            raise ValueError(f'Unknown {name} feature ID {value!r}; use connectors to list stable IDs')
    contacts = connection_contacts(inspection)
    occupied = set()
    for contact in contacts:
        a, b = contact.first_occurrence.index, contact.second_occurrence.index
        # Existing cross-boundary contacts can detach during a move. Internal
        # assembly contacts and stationary-to-stationary contacts remain occupied.
        if (a in moving_indices) == (b in moving_indices):
            occupied.update(((a, contact.first.feature_id), (b, contact.second.feature_id)))
    from itertools import chain
    from .technic import managed, candidates as technic_candidates, conflicts as technic_conflicts
    selection = replace(inspection, occurrences=(subject, *targets))
    ordinary = replace(selection, occurrences=tuple(replace(o, connections=tuple(
        f for f in o.connections if not managed(f))) for o in selection.occurrences))
    raw = chain(query_frames(ordinary, snapping=True).snap_candidates(moving, fixed=fixed),
                technic_candidates(selection, moving, fixed))
    candidates, rejected, seen = [], {}, set()
    checked, truncated = 0, False
    old_world = pose(subject.occurrence.position, subject.occurrence.matrix)
    parent = np.eye(4)
    for hop in path[:depth]:
        parent = parent @ pose(hop.piece.position, hop.piece.matrix)
    target_world = parent @ pose(path[depth].piece.position, path[depth].piece.matrix)
    regular = profiles()
    for candidate in raw:
        if candidate.fixed_occurrence.index in moving_indices:
            continue
        if moving_feature is not None and candidate.moving.feature_id != moving_feature:
            continue
        if fixed_feature is not None and candidate.fixed.feature_id != fixed_feature:
            continue
        if not allow_occupied and not managed(candidate.moving) and ((moving, candidate.moving.feature_id) in occupied or
                                  (candidate.fixed_occurrence.index, candidate.fixed.feature_id) in occupied):
            rejected['occupied_feature'] = rejected.get('occupied_feature', 0) + 1
            continue
        new_world = pose(candidate.transform.position, candidate.transform.matrix)
        delta = new_world @ np.linalg.inv(old_world)
        key = tuple(delta.round(7).flat)
        if key in seen:
            continue
        seen.add(key)
        if checked >= max_candidates:
            truncated = True
            break
        checked += 1
        transformed = moved_inspection(inspection, moving_indices, delta)
        pairs = list(collision_pairs(transformed, regular, moving=moving_indices))
        blocked = [p for p in pairs if p['status'] == 'rectangular_body_overlap']
        new_contacts = connection_contacts(transformed)
        from .technic_review import review_inspection
        interface_errors = []
        if managed(candidate.moving):
            interface_errors = [d for d in review_inspection(transformed, seating_only=True)
                                if moving_indices.intersection(d['instances'])]
            blocked.extend(interface_errors)
        for conflict in technic_conflicts(new_contacts):
            if moving_indices.intersection(conflict['instances']):
                blocked.append(dict(**conflict, status='technic_occupation_conflict'))
        # Query just the selected endpoints as well: strict stud queries choose
        # one best receptor when several authored/primitive IDs are colocated.
        endpoints = {moving: candidate.moving.feature_id, candidate.fixed_occurrence.index: candidate.fixed.feature_id}
        mating = connection_contacts(replace(transformed, occurrences=tuple(
            replace(o, connections=tuple(f for f in o.connections if f.feature_id == endpoints[o.index]))
            for o in transformed.occurrences if o.index in endpoints)))
        if not mating:
            rejected['unverified_contact'] = rejected.get('unverified_contact', 0) + 1
            continue
        connected_pairs = {tuple(sorted((c.first_occurrence.index, c.second_occurrence.index))) for c in new_contacts}
        for pair in pairs:
            pair['connection_present'] = tuple(sorted(pair['instances'])) in connected_pairs
        review = [p for p in pairs if p['status'] in {'review_aabb_only', 'review_oriented_bounds'}
                  or (p['status']=='stud_zone_overlap_review_connections' and not p['connection_present'])]
        local = np.linalg.inv(parent) @ delta @ target_world
        candidates.append(dict(moving=moving, fixed=candidate.fixed_occurrence.index,
            **transform_dict(new_world), delta=transform_dict(delta),
            local_placement=dict(ref=path[depth].piece.reference, at=local[:3, 3].tolist(), matrix=local[:3, :3].tolist()),
            moving_feature=jsonable(next(f for f in subject.connections if f.feature_id == candidate.moving.feature_id)),
            fixed_feature=jsonable(next(f for f in occurrence_at(inspection, candidate.fixed_occurrence.index).connections
                                        if f.feature_id == candidate.fixed.feature_id)),
            residual_before=jsonable(candidate.residual), contact_status=str(mating[0].status),
            collision=dict(status='blocked' if blocked else 'review_required' if review else 'no_collision_found',
                           checked_pairs=len(pairs), body_overlap_count=sum(p.get('status') == 'rectangular_body_overlap' for p in blocked),
                           blocking_issue_count=len(blocked), interface_errors=interface_errors, review_count=len(review),
                           pairs=pairs[:50], pairs_truncated=len(pairs)>50),
            distance=float(np.linalg.norm(new_world[:3, 3]-old_world[:3, 3]))))
    candidates.sort(key=lambda c: (c['collision']['status']=='blocked', c['collision']['review_count'],
                                   c['contact_status']!='confirmed', c['distance']))
    for index, candidate in enumerate(candidates):
        candidate['candidate'] = index
    return dict(source_fingerprint=hashlib.sha256(model.to_ldraw().encode()).hexdigest(),
                coordinate_space='world', moving=moving, fixed=fixed, moving_depth=depth,
                placement_path=selected_path, moving_instances=sorted(moving_indices),
                metadata=metadata_summary(subject.local.connection_metadata),
                candidates=candidates[:limit], candidate_count=len(candidates), checked_candidates=checked,
                search_truncated=truncated, candidates_truncated=len(candidates)>limit,
                rejected=rejected, physical_validity='not_proven',
                limitations=['Shadow metadata describes mating interfaces, not solid collision volumes.',
                             'General part envelope overlaps require review; contacts never waive body collisions.',
                             'Reviewed Technic interfaces reserve engaged spans; conflicting occupation cannot be overridden.',
                             'Other occupied interfaces are conservatively excluded; allow_occupied enables deliberate reuse.',
                             'Search preserves free roll; it does not enumerate all articulation or insertion paths.'])


def apply_snap(model, report, candidate=0):
    """Return a copy with one occurrence changed; clone nested section ancestors.

    Cloning keeps other uses of a repeated submodel in their original poses.
    Validation and collision review remain the caller's responsibility.
    """
    from .document import section_table
    if report.get('source_fingerprint') != hashlib.sha256(model.to_ldraw().encode()).hexdigest():
        raise ValueError('Snap report belongs to a different model revision; regenerate candidates')
    if candidate < 0 or candidate >= len(report['candidates']):
        raise ValueError('Candidate index is outside the returned candidate list')
    chosen = report['candidates'][candidate]
    if chosen['collision']['status'] == 'blocked':
        raise ValueError('Cannot apply a snap with a body collision or structural interface error')
    result = copy.deepcopy(model)
    table = section_table(result)
    section = result
    for depth, index in enumerate(report['placement_path']):
        piece = section.pieces[index]
        if depth == len(report['placement_path'])-1:
            piece.position = Vector(*chosen['local_placement']['at'])
            piece.matrix = Matrix(chosen['local_placement']['matrix'])
            break
        original = table[normalized(piece.reference)]
        number = 1
        while normalized(name := f'nova-snap-{number}.ldr') in table:
            number += 1
        clone = copy.deepcopy(replace(original, submodels={}))
        clone.name = name
        clone.set_header(name=name)
        table[normalized(name)] = clone
        result.submodels[normalized(name)] = clone
        piece.part, piece.suffix = name.removesuffix('.ldr'), '.ldr'
        section = clone
    return result
