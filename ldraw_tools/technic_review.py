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
                      conflicts, nearby_ports, Kind, MALE, TOL)

MECHANISMS = re.compile(r'\b(gear|differential|universal joint|motor|actuator|pneumatic|shock absorber|steering)\b', re.I)


def contract_check(contract, model, count):
    jsonschema.Draft202012Validator(json.loads((DATA/'structure.schema.json').read_text())).validate(contract)
    if contract.get('model_sha256') and contract['model_sha256'] != hashlib.sha256(model.to_ldraw().encode()).hexdigest():
        raise ValueError('Structure contract belongs to a different model revision')
    indices = [i for j in contract.get('required_joints', []) for i in j['between']]
    indices += [i for step in contract.get('assembly', []) for i in [step['connector'], *step['before']]]
    indices += contract.get('retained_axles', [])
    if any(i >= count for i in indices):
        raise ValueError('Structure contract references an absent physical occurrence')


def review_structure(model, parts, *, contract=None, instance_limit=500):
    inspection = inspect_connections(model, parts, instance_limit)
    if contract is not None:
        contract_check(contract, model, inspection.occurrence_count)
    return review_inspection(inspection, contract=contract)


def review_inspection(inspection, *, contract=None, seating_only=False, found=None):
    contract = contract or {}
    diagnostics = []
    joints_only = contract.get("scope") == "joints"

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
    if mechanism_parts and not joints_only:
        issue('technic.mechanism_scope', 'This check is for fixed structures. Use mechanism studies for moving assemblies; their function is outside structural review.', mechanism_parts, 'error')
    found = connection_contacts(inspection) if found is None else found
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
    close = defaultdict(list)
    for owner, male, receiver, hole in nearby_ports(inspection):
        i, j = owner.index, receiver.index
        if tuple(sorted((i, j))) in valid_pairs:
            continue
        delta = hole.position-male.position
        along = delta.dot(male.axis)
        radial = abs(delta-male.axis*along)
        overlap = min(male.length/2, along+hole.length/2)-max(-male.length/2, along-hole.length/2)
        if radial <= TOL and abs(male.axis.dot(hole.axis)) > .9999 and overlap >= -TOL:
            close[i, j].append((male.feature_id, hole.feature_id))
    order = {index: n for n, index in enumerate(items)}
    for (i, j), ports in sorted(close.items(), key=lambda row: tuple(order[k] for k in row[0])):
        issue('technic.invalid_seating', 'Aligned interfaces fail seating, engagement, family or keyed-roll rules.', [i, j], 'error', ports=ports)

    if seating_only:
        return [d for d in diagnostics if d['severity'] == 'error' and d['code'] != 'technic.mechanism_scope']

    # Axles need actual stops on both sides of their supported stack.
    # Retainer parts are keyed to the shaft; they do not create structural edges
    # between otherwise unrestrained members merely by being nearby.
    retention_checked = set()
    for owner, mates in shaft_contacts.items():
        if not any(mf.kind is Kind.AXLE for _, _, mf, _ in mates):
            continue
        axles = [f for f in items[owner].connections if managed(f) and f.kind is Kind.AXLE]
        for axle in axles:
            selected = [(h, hf, d) for h, hf, mf, d in mates if mf.feature_id == axle.feature_id]
            supports = [d['interval'] for h, hf, d in selected if definitions[h.index]['role'] != 'retainer']
            stops = [d['interval'] for h, hf, d in selected if definitions[h.index]['role'] == 'retainer']
            if supports:
                retention_checked.add(owner)
                low, high = min(s[0] for s in supports), max(s[1] for s in supports)
                retained = any(abs(s[1]-low) <= TOL for s in stops) and any(abs(s[0]-high) <= TOL for s in stops)
                if not retained:
                    issue('technic.axial_retention', 'Axle support lacks reviewed stops against both ends of the supported stack.', [owner], 'error' if owner in contract.get('retained_axles', []) else 'warning')
                if any(d['behavior'] == 'bearing' for h, hf, d in selected):
                    issue('technic.bearing_rotation', 'A round-hole bearing permits shaft rotation; this is not a fixed keyed joint.', [owner])

    for owner in set(contract.get('retained_axles', [])) - retention_checked:
        issue('technic.axial_retention', 'Required retained axle has no reviewed receiving supports.', [owner], 'error')

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
    if unresolved and not joints_only:
        issue('technic.pivot_support', 'Single pin axes leave relative rotation; add another spaced attachment or reviewed bracing.', sorted({i for p in unresolved for i in p['members']}))
    if len(unresolved) >= len(groups) and len(groups) > 1 and not joints_only:
        issue('technic.unbraced_loop', 'A loop of pin joints is connected but has no recognized rigid corner or bracing pattern.', sorted(members))
    if len(groups) > 1 and not joints_only:
        issue('technic.structural_restraint', 'The multiple-pin rule does not establish restraint between all structural members.', sorted(members),
              'error' if contract.get('require_rigid') else 'warning')
    for required in contract.get('required_joints', []):
        pair = tuple(sorted(required['between']))
        matching = [c for c in found if tuple(sorted((c.first_occurrence.index, c.second_occurrence.index))) == pair]
        unique = {(c.first.feature_id, c.second.feature_id) for c in matching}
        if len(unique) < required.get('minimum', 1):
            issue('technic.missing_required_joint', 'A declared mounting connection is absent.', pair, 'error',
                  required_contacts=required.get('minimum', 1), observed_contacts=len(unique),
                  action='Inspect these named parts and their local mating interfaces; restore seating or the required attachment count.')
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
    if not members and not joints_only:
        issue('technic.no_structural_members', 'No reviewed structural members were found.')
    return dict(scope='technic-joints' if joints_only else 'technic-structure', checks_passed=inspection.complete and not any(d['severity']=='error' for d in diagnostics),
        complete=inspection.complete, physical_validity='not_proven', occurrence_count=len(items),
        coverage=dict(reviewed_occurrences=sum(v is not None for v in definitions.values()),
                      unknown_technic=unknown, required_joints=len(contract.get('required_joints', [])),
                      assembly_constraints=len(contract.get('assembly', [])),
                      insertion_paths='manual_review_required', material_collisions='interface_seating_only'),
        joint_count=len(joints), joints=joints, restrained_groups=[] if joints_only else list(groups.values()),
        locked_member_pairs=locked, pivot_member_pairs=pivots, diagnostics=diagnostics,
        limitations=['Multiple spaced pins provide a conservative restraint pattern, not a general rigidity proof.',
                     'No stress, stiffness, load capacity, manufacturing tolerance or mechanism simulation.',
                     'STEP constraints check ordering, not swept insertion paths; inspect hidden joints and build order.',
                     'Run normal geometry validation too; hole seating does not waive unrelated material overlaps.'])
