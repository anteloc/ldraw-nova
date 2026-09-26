"""Geometry and connection evidence. AABB overlap is never a general collision proof."""
from __future__ import annotations

import json
from itertools import product

import numpy as np
from ldraw import inspect_model

from .common import DATA, issue, jsonable
from .collision import collision_pairs, oriented_box
from .connectivity import metadata_summary, placement_path
from .connection_adapter import connection_contacts


def geometry_complete(inspection):
    """Separate resolved solids from warnings about optional connector metadata.

    pyldraw3's combined completeness flag also fails on connection warnings.
    Keep those warnings visible without reporting missing solid geometry.
    Unknown, geometry and error diagnostics still prevent completeness.
    """
    return not inspection.skipped_geometry and all(
        d.to_dict()['code'].startswith('connection.') and d.to_dict()['severity'] == 'warning'
        for d in inspection.diagnostics)


def profiles():
    return json.loads((DATA / "rectangular-parts.json").read_text())["parts"]


def body_box(occ, profile):
    """Envelope of an upright, unscaled, quarter-turn rectangular brick/plate body."""
    matrix = np.array(occ.matrix.rows)
    if not np.allclose(matrix[:, 1], [0, 1, 0], atol=1e-6) or not np.allclose(matrix, np.round(matrix), atol=1e-6):
        return None
    if not np.allclose(matrix.T @ matrix, np.eye(3), atol=1e-6) or np.linalg.det(matrix) < 0:
        return None
    x, z, h = profile["x_studs"] * 10, profile["z_studs"] * 10, profile["height"]
    vertices = np.array(list(product([-x, x], [0, h], [-z, z])))
    vertices = vertices @ matrix.T + np.array(jsonable(occ.position))
    return np.array([vertices.min(axis=0), vertices.max(axis=0)])


def components(nodes, edges):
    adjacent = {n: set() for n in nodes}
    for a, b in edges:
        adjacent[a].add(b)
        adjacent[b].add(a)
    result = []
    unseen = set(nodes)
    while unseen:
        stack, group = [min(unseen)], set()
        while stack:
            n = stack.pop()
            if n in group:
                continue
            group.add(n)
            stack.extend(adjacent[n] - group)
        unseen -= group
        result.append(sorted(group))
    return result


def analyze_geometry(model, parts, *, pair_limit=200, instance_limit=100000,
                     detail="full", contacts="auto", output_limit=200, offset=0):
    from .document import physical_context
    model, parts = physical_context(model, parts)
    occurrences = []
    for occ in model.iter_occurrences(include_steps=True):
        occurrences.append(occ)
        if len(occurrences) > instance_limit:
            raise ValueError(f"Geometry budget exceeds {instance_limit} occurrences; inspect a submodel.")
    from .technic import curate
    inspection = curate(inspect_model(model, parts, occurrences=occurrences))
    problems = [d.to_dict() for d in inspection.diagnostics]
    from ldraw.lines import Line, OptionalLine, Triangle, Quadrilateral
    for section in [model, *model.submodels.values()]:
        if any(isinstance(obj, (Line, OptionalLine, Triangle, Quadrilateral)) for obj in section.objects):
            problems.append(issue("coverage.raw_geometry", "Assembly bounds exclude custom model polygons/edges; inspect them with a geometry authoring tool.", section=section.name))
    if not geometry_complete(inspection):
        problems.append(issue("geometry.incomplete", "Some library geometry could not be expanded; bounds and contacts are incomplete."))
    regular = profiles()
    bodies = {}
    instances = []
    # Detect unsupported geometry extensions in every referenced library file, not only the MPD.
    checked = set()

    def check_library(code, depth=0):
        key = code.replace("\\", "/").casefold()
        if key in checked:
            return
        if depth > 150:
            raise ValueError("Library dependency depth exceeds 150")
        checked.add(key)
        part = parts.find_part(code=code)
        if part is None:
            return  # pyldraw3 reports unresolved dependencies.
        for line in part.lines:
            tokens = line.split()
            if tokens[:2] in (["0", "!TEXMAP"], ["0", "!DATA"], ["0", "!:"]):
                problems.append(issue("coverage.library_extension", f"{code}: texture/data geometry requires external verification."))
                break
        from ldraw.pieces import Piece
        for obj in part.objects:
            if isinstance(obj, Piece):
                check_library(obj.part, depth + 1)

    path_cache = {}
    for item in inspection.occurrences:
        occ = item.occurrence
        check_library(occ.part_code)
        profile = regular.get(occ.part_code.casefold())
        body = oriented_box(item, profile) if profile else None
        if body is not None:
            bodies[item.index] = body
        instances.append(dict(index=item.index, part=occ.reference, description=item.local.description,
                              colour=jsonable(occ.colour), position=jsonable(occ.position), matrix=jsonable(occ.matrix),
                              bounds=jsonable(item.bounds), section=occ.source_model.name, line_number=occ.source_line,
                              source_path=jsonable(item.attribution.source_line_path), step=occ.step,
                              body_profile=body is not None, connector_count=len(item.connections),
                              placement_path=placement_path(occ, path_cache),
                              connection_metadata=metadata_summary(item.local.connection_metadata)))
    overlaps = []
    overlap_count = 0
    by_index = {o.index: o for o in inspection.occurrences}
    for overlap in collision_pairs(inspection, regular):
        overlap_count += 1
        if overlap['status'] == 'rectangular_body_overlap':
            problems.append(issue("assembly.body_overlap", "Rectangular brick/plate body envelopes overlap; reposition them.",
                instances=overlap['instances'], penetration=overlap['body_penetration'],
                sources=[dict(part=by_index[i].occurrence.reference, section=by_index[i].occurrence.source_model.name,
                              line_number=by_index[i].occurrence.source_line,
                              source_path=jsonable(by_index[i].attribution.source_line_path)) for i in overlap['instances']]))
        if len(overlaps) < pair_limit:
            overlaps.append(overlap)
    contact_mode = "all" if contacts == "auto" and len(occurrences) <= 500 else "none" if contacts == "auto" else contacts
    contact_results = connection_contacts(inspection) if contact_mode == "all" else []
    from .technic import managed
    if contact_mode == 'all' and any(managed(f) for o in inspection.occurrences for f in o.connections):
        from .technic_review import review_inspection
        problems.extend(review_inspection(inspection, seating_only=True))
    mating_pairs = {}
    for contact in contact_results:
        pair = tuple(sorted((contact.first_occurrence.index, contact.second_occurrence.index)))
        mating_pairs[pair] = mating_pairs.get(pair, 0) + 1
    for overlap in overlaps:
        overlap['connection_count'] = mating_pairs.get(tuple(sorted(overlap['instances'])), 0) if contact_mode == 'all' else None
    links = []
    confirmed, optimistic = [], []
    for contact in contact_results:
        edge = (contact.first_occurrence.index, contact.second_occurrence.index)
        optimistic.append(edge)
        if str(contact.status) == "confirmed":
            confirmed.append(edge)
        if len(links) < output_limit:
            links.append(dict(instances=list(edge), status=str(contact.status),
                          kinds=[str(contact.first.kind), str(contact.second.kind)],
                          sources=[str(contact.first.source), str(contact.second.source)],
                          confidence=[contact.first.confidence, contact.second.confidence],
                          feature_ids=[contact.first.feature_id, contact.second.feature_id], residual=jsonable(contact.residual)))
    nodes = list(range(inspection.occurrence_count))
    groups = components(nodes, optimistic)
    confirmed_groups = components(nodes, confirmed)
    if contact_mode == "all" and len(groups) > 1:
        problems.append(issue("assembly.disconnected_evidence", "Connection analysis finds multiple groups. Investigate floating parts, missing connector metadata, or intentional separate objects.", severity="warning", component_count=len(groups)))
    if contact_mode == "none":
        problems.append(issue("coverage.contacts_skipped", "Contacts were not computed. Select a subassembly or request --contacts all; no connectivity conclusion is available.", severity="warning"))
    if len(bodies) < len(occurrences):
        problems.append(issue("coverage.collision_review", "Some parts lack rectangular body checks; oriented bounds refine candidates, while remaining overlaps require material review.", severity="warning"))
    return dict(complete=geometry_complete(inspection) and not any(p["code"].startswith("coverage.") and p["severity"] == "error" for p in problems),
                connection_coverage={coverage: sum(str(o.local.connection_metadata.coverage) == coverage
                    for o in inspection.occurrences if o.local.connection_metadata) for coverage in ('complete', 'partial', 'none')},
                collision_method="AABB broad phase, oriented bounds separation, curated rectangular body SAT",
                physical_validity="not_proven", bounds=jsonable(inspection.bounds), occurrence_count=len(occurrences),
                detail=detail, instance_offset=offset, instances=instances[offset:offset+output_limit] if detail == "full" else [],
                instances_truncated=detail != "full" or offset > 0 or len(instances) > output_limit,
                contacts_checked=contact_mode == "all", contact_count=len(contact_results) if contact_mode == "all" else None,
                contacts=links if detail == "full" else [], contacts_truncated=len(contact_results) > (len(links) if detail == "full" else 0),
                confirmed_components=[g[:output_limit] for g in confirmed_groups[:output_limit]] if contact_mode == "all" and detail == "full" else None,
                optimistic_components=[g[:output_limit] for g in groups[:output_limit]] if contact_mode == "all" and detail == "full" else None,
                optimistic_component_count=len(groups) if contact_mode == "all" else None,
                confirmed_component_count=len(confirmed_groups) if contact_mode == "all" else None,
                components_truncated=contact_mode == "all" and (detail != "full" or max([len(groups),len(confirmed_groups),*[len(g) for g in groups+confirmed_groups]],default=0) > output_limit),
                overlap_candidate_count=overlap_count, overlaps=overlaps if detail == "full" else [],
                overlaps_truncated=overlap_count > (len(overlaps) if detail == "full" else 0), diagnostics=problems,
                limitations=["AABB candidates do not prove collisions; stud/socket bounding boxes normally overlap.",
                             "Connector matches, including 'confirmed', are computational evidence, not buildability certification.",
                             "No material intersection, clutch strength, stability, legal connection stress, or real colour availability proof."])


def snap(model, parts, moving, fixed=None, limit=5, **options):
    """Compatibility list API; snap_report also exposes budgets and coverage."""
    from .connectivity import snap_report
    return snap_report(model, parts, moving, fixed, limit=limit, **options)['candidates']
