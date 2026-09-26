"""Conservative structural review of curated joints, required mounts and bracing."""
from __future__ import annotations

from collections import defaultdict
from itertools import combinations
import hashlib
import json
import re

import jsonschema
import numpy as np

from .common import DATA, jsonable
from .connectivity import inspect_connections
from .connection_adapter import connection_contacts
from .technic import (definition, canonical, registry, managed, endpoints, fit,
                      conflicts, Kind, MALE, HOLES, TOL)

MECHANISMS = re.compile(r'\b(gear|differential|universal joint|motor|actuator|pneumatic|shock absorber|steering)\b', re.I)


def contract_check(contract, model, count):
    jsonschema.Draft202012Validator(json.loads((DATA/'structure.schema.json').read_text())).validate(contract)
    if contract.get('model_sha256') and contract['model_sha256'] != hashlib.sha256(model.to_ldraw().encode()).hexdigest():
        raise ValueError('Structure contract belongs to a different model revision')
    indices = [i for j in contract.get('required_joints', []) for i in j['between']]
    indices += [i for step in contract.get('assembly', []) for i in [step['connector'], *step['before']]]
    if any(i >= count for i in indices):
        raise ValueError('Structure contract references an absent physical occurrence')


def review_structure(model, parts, *, contract=None, instance_limit=500):
    inspection = inspect_connections(model, parts, instance_limit)
    if contract is not None:
        contract_check(contract, model, inspection.occurrence_count)
    return review_inspection(inspection, contract=contract)


def review_inspection(inspection, *, contract=None, seating_only=False):
    contract = contract or {}
    diagnostics = []

    def issue(code, message, instances=(), severity='warning', **extra):
        diagnostics.append(dict(code=code, message=message, severity=severity,
                                instances=list(instances), **extra))

    items = {o.index: o for o in inspection.occurrences}
    definitions = {i: definition(o.local) for i, o in items.items()}
    unknown, mechanism_parts = [], []
    for i, o in items.items():
        title = o.local.description
        matrix = np.asarray(o.occurrence.matrix.rows)
        if not np.isfinite(matrix).all() or not np.allclose(matrix.T @ matrix, np.eye(3), atol=1e-6) or np.linalg.det(matrix) < 0:
            issue('technic.invalid_transform', 'Structural placements require finite proper rotations without scaling or reflection.', [i], 'error')
        if MECHANISMS.search(title):
            mechanism_parts.append(i)
        if definitions[i] is None and (title.startswith('Technic') or canonical(o.local.code) in registry()['parts']):
            unknown.append(i)
    if unknown:
        issue('technic.unreviewed_parts', 'These Technic parts or geometry revisions lack reviewed structural interfaces.', unknown,
              'error' if contract.get('require_rigid') else 'warning')
    if mechanism_parts:
        issue('technic.mechanism_scope', 'This check is for fixed structures. Use mechanism studies for moving assemblies; their function is outside structural review.', mechanism_parts, 'error')
    found = connection_contacts(inspection)
    joints, male_spans, shaft_contacts, member_links = [], defaultdict(list), defaultdict(list), defaultdict(list)
    tech = [c for c in found if managed(c.first) and managed(c.second)]
    for c in tech:
        m, mf, h, hf = endpoints(c)
        details = fit(mf, hf)
        joints.append(dict(connector=m.index, port=mf.feature_id, receiver=h.index, hole=hf.feature_id,
                           **details, position=jsonable(hf.position), axis=jsonable(mf.axis)))
        male_spans[m.index, mf.feature_id].append(details['interval'])
        shaft_contacts[m.index].append((h, hf, mf, details))
    for conflict in conflicts(found):
        issue(conflict['code'], 'Two parts occupy the same receiving hole or shaft span.', conflict['instances'], 'error', port=conflict['port'])

    # A pin grip split over thin layers is retained only after their union fills it.
    for (owner, port), spans in male_spans.items():
        f = next(f for f in items[owner].connections if f.feature_id == port)
        if f.kind is not Kind.PIN:
            continue
        cursor = -f.length/2
        for low, high in sorted(spans):
            if low > cursor+TOL:
                break
            cursor = max(cursor, high)
        if cursor < f.length/2-TOL:
            issue('technic.incomplete_grip', 'A pin grip is only partly supported; complete the layer stack and retaining seat.', [owner], 'error', port=port)

    valid_pairs = {tuple(sorted((c.first_occurrence.index, c.second_occurrence.index))) for c in tech}
    # Diagnose almost-mates without interpreting every nearby bounding box as a hole.
    for i, a in items.items():
        for j, b in items.items():
            if i == j or tuple(sorted((i, j))) in valid_pairs:
                continue
            close = []
            for male in a.connections:
                if not managed(male) or male.kind not in MALE:
                    continue
                for hole in b.connections:
                    if not managed(hole) or hole.kind not in HOLES:
                        continue
                    delta = hole.position-male.position
                    along = delta.dot(male.axis)
                    radial = abs(delta-male.axis*along)
                    overlap = min(male.length/2, along+hole.length/2)-max(-male.length/2, along-hole.length/2)
                    if radial <= TOL and abs(male.axis.dot(hole.axis)) > .9999 and overlap >= -TOL:
                        close.append((male.feature_id, hole.feature_id))
            if close:
                issue('technic.invalid_seating', 'Aligned interfaces fail seating, engagement, family or keyed-roll rules.', [i, j], 'error', ports=close)

    if seating_only:
        return [d for d in diagnostics if d['severity'] == 'error' and d['code'] != 'technic.mechanism_scope']

    # Axles need actual stops on both sides of their supported stack.
    # Retainer parts are keyed to the shaft; they do not create structural edges
    # between otherwise unrestrained members merely by being nearby.
    for owner, mates in shaft_contacts.items():
        if not any(mf.kind is Kind.AXLE for _, _, mf, _ in mates):
            continue
        axles = [f for f in items[owner].connections if managed(f) and f.kind is Kind.AXLE]
        for axle in axles:
            selected = [(h, hf, d) for h, hf, mf, d in mates if mf.feature_id == axle.feature_id]
            supports = [d['interval'] for h, hf, d in selected if definitions[h.index]['role'] != 'retainer']
            stops = [d['interval'] for h, hf, d in selected if definitions[h.index]['role'] == 'retainer']
            if supports:
                low, high = min(s[0] for s in supports), max(s[1] for s in supports)
                retained = any(abs(s[1]-low) <= TOL for s in stops) and any(abs(s[0]-high) <= TOL for s in stops)
                if not retained:
                    issue('technic.axial_retention', 'Axle support lacks reviewed stops against both ends of the supported stack.', [owner])
                if any(d['behavior'] == 'bearing' for h, hf, d in selected):
                    issue('technic.bearing_rotation', 'A round-hole bearing permits shaft rotation; this is not a fixed keyed joint.', [owner])

    members = {i for i, entry in definitions.items() if entry and entry['role'] == 'member'}
    # A pin body may span several layers/ports: count its axis only once per pair.
    for owner, mates in shaft_contacts.items():
        receivers = {h.index: (h, hf, mf) for h, hf, mf, d in mates
                     if h.index in members and mf.kind is Kind.PIN}
        for a, b in combinations(sorted(receivers), 2):
            hf, mf = receivers[a][1:]
            member_links[a, b].append((owner, hf.position, mf.axis))
    parent = {i: i for i in members}

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    locked, pivots = [], []
    for pair, axes in member_links.items():
        restrained = any(abs(a.dot(b)) > .9999 and abs((q-p)-a*(q-p).dot(a)) > 5
                         for (_, p, a), (_, q, b) in combinations(axes, 2))
        record = dict(members=list(pair), connectors=sorted({a[0] for a in axes}))
        if restrained:
            parent[find(pair[0])] = find(pair[1])
            locked.append(record)
        else:
            pivots.append(record)
    groups = defaultdict(list)
    for member in sorted(members):
        groups[find(member)].append(member)
    unresolved = [p for p in pivots if find(p['members'][0]) != find(p['members'][1])]
    if unresolved:
        issue('technic.pivot_support', 'Single pin axes leave relative rotation; add another spaced attachment or reviewed bracing.', sorted({i for p in unresolved for i in p['members']}))
    if len(unresolved) >= len(groups) and len(groups) > 1:
        issue('technic.unbraced_loop', 'A loop of pin joints is connected but has no recognized rigid corner or bracing pattern.', sorted(members))
    if len(groups) > 1:
        issue('technic.structural_restraint', 'The multiple-pin rule does not establish restraint between all structural members.', sorted(members),
              'error' if contract.get('require_rigid') else 'warning')
    for required in contract.get('required_joints', []):
        pair = tuple(sorted(required['between']))
        matching = [c for c in found if tuple(sorted((c.first_occurrence.index, c.second_occurrence.index))) == pair]
        unique = {(c.first.feature_id, c.second.feature_id) for c in matching}
        if len(unique) < required.get('minimum', 1):
            issue('technic.missing_required_joint', 'A declared mounting connection is absent.', pair, 'error')
    for step in contract.get('assembly', []):
        index = step['connector']
        if not any(managed(f) and f.kind in MALE for f in items[index].connections):
            issue('technic.assembly_connector', 'Assembly instruction must identify a reviewed pin or axle.', [index], 'error')
        for later in step['before']:
            if items[index].occurrence.step >= items[later].occurrence.step:
                issue('technic.insertion_order', 'The connector must be inserted before the declared closing member is added.', [index, later], 'error')
    if not contract.get('assembly'):
        issue('technic.assembly_access_unreviewed', 'No connector-before-closure steps supplied; insertion paths need review.')
    if not contract.get('required_joints'):
        issue('technic.mounts_undeclared', 'No required mounting pairs supplied; partial attachment can still connect the whole graph.')
    if not members:
        issue('technic.no_structural_members', 'No reviewed structural members were found.')
    return dict(scope='technic-structure', checks_passed=inspection.complete and not any(d['severity']=='error' for d in diagnostics),
        complete=inspection.complete, physical_validity='not_proven', occurrence_count=len(items),
        coverage=dict(reviewed_occurrences=sum(v is not None for v in definitions.values()),
                      unknown_technic=unknown, required_joints=len(contract.get('required_joints', [])),
                      assembly_constraints=len(contract.get('assembly', [])),
                      insertion_paths='manual_review_required', material_collisions='interface_seating_only'),
        joint_count=len(joints), joints=joints, restrained_groups=list(groups.values()),
        locked_member_pairs=locked, pivot_member_pairs=pivots, diagnostics=diagnostics,
        limitations=['Multiple spaced pins provide a conservative restraint pattern, not a general rigidity proof.',
                     'No stress, stiffness, load capacity, manufacturing tolerance or mechanism simulation.',
                     'STEP constraints check ordering, not swept insertion paths; inspect hidden joints and build order.',
                     'Run normal geometry validation too; hole seating does not waive unrelated material overlaps.'])
