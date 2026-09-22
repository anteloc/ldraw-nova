"""Deterministic, schema-checked assembly plans using pyldraw3's writer."""
from __future__ import annotations

import json
import math
import copy
from pathlib import Path

import jsonschema
import numpy as np
from ldraw import Model, Piece, Vector, Matrix
from ldraw.lines import Comment

from .common import DATA, normalized, jsonable
from .geometry import profiles
from .validation import validate_text


def check_schema(plan):
    jsonschema.Draft202012Validator(json.loads((DATA / "plan.schema.json").read_text())).validate(plan)


def load_plan(path):
    """Resolve relative plan includes once; retain each module's authorship."""
    loaded, sections, assets = set(), [], []
    root_plan = None

    def visit(path, active):
        nonlocal root_plan
        path = Path(path).resolve()
        if path in active:
            raise ValueError("Plan include cycle: " + " -> ".join(map(str, (*active,path))))
        if path in loaded:
            return
        if len(loaded) >= 200:
            raise ValueError("Plan exceeds 200 included files")
        loaded.add(path)
        plan = json.loads(path.read_text(), parse_constant=lambda v: (_ for _ in ()).throw(ValueError(f"Nonfinite JSON {v}")))
        check_schema(plan)
        if root_plan is None:
            root_plan = plan
        for section in plan["sections"]:
            section = copy.deepcopy(section)
            section.setdefault("author",plan["author"])
            if plan.get("license"):
                section.setdefault("license",plan["license"])
            sections.append(section)
        for asset in plan.get("assets",[]):
            asset = str((path.parent / asset).resolve())
            if asset not in assets:
                assets.append(asset)
        for child in plan.get("includes",[]):
            visit(path.parent / child, (*active,path))
    visit(path, ())
    # Licences were copied to the sections owned by each declaring plan. Keeping
    # the root licence here would incorrectly apply it to unlicensed includes.
    result = {k:v for k,v in root_plan.items() if k not in {"includes","assets","sections","license"}}
    result.update(sections=sections, assets=assets)
    check_schema(result)
    return result


def frame(value):
    result = np.eye(4)
    result[:3, 3] = value["at"]
    result[:3, :3] = value.get("matrix", np.eye(3))
    a = result[:3, :3]
    if not np.isfinite(result).all() or not np.allclose(a.T @ a,np.eye(3),atol=1e-4,rtol=0) or np.linalg.det(a) < 0:
        raise ValueError("An anchor frame must use a finite proper rotation")
    return result


def repeated(entries):
    for entry in entries:
        if "repeat" not in entry:
            yield entry
            continue
        for i in range(entry["repeat"]["count"]):
            yield {**{k:v for k,v in entry.items() if k != "repeat"}, "id":f"{entry['id']}-{i}",
                   "at":(np.array(entry["at"]) + i*np.array(entry["repeat"]["step"])).tolist()}


def rotation(axis="y", degrees=0):
    """Active right-handed rotation on column vectors, in LDraw's coordinate frame."""
    if axis not in {"x", "y", "z"} or not math.isfinite(degrees):
        raise ValueError("Rotation needs axis x/y/z and finite degrees")
    a = math.radians(degrees)
    c, s = round(math.cos(a), 12), round(math.sin(a), 12)
    return Matrix({"x": [[1, 0, 0], [0, c, -s], [0, s, c]],
                   "y": [[c, 0, s], [0, 1, 0], [-s, 0, c]],
                   "z": [[c, -s, 0], [s, c, 0], [0, 0, 1]]}[axis])


def serialize_mpd(model):
    """Always emit a main FILE block, UTF-8 without BOM, and specification CRLF."""
    text = model.to_ldraw()
    if not model.submodels:
        text = f"0 FILE {model.name}\n{text}\n0 NOFILE"
    return text.replace("\r\n", "\n").replace("\n", "\r\n") + "\r\n"


def dependency_order(sections):
    """Build referenced modules before using their physical snap interfaces."""
    table = {normalized(s['name']): s for s in sections}
    ordered, done, active = [], set(), set()
    def visit(key):
        if key in active:
            raise ValueError(f'Plan submodel cycle at {key}')
        if key in done:
            return
        active.add(key)
        for step in table[key]['steps']:
            for entry in step:
                child = normalized(entry['ref'])
                if child in table:
                    visit(child)
        active.remove(key)
        done.add(key)
        ordered.append(table[key])
    for key in table:
        visit(key)
    return ordered


def snap_placement(entry, model, models, placed, parts, matrix, instance_limit):
    from .connectivity import inspect_connections, snap_report
    from dataclasses import replace
    options = entry['snap']
    if options['to'] not in placed:
        raise ValueError('snap.to must identify an earlier placement in the same section')
    support, _ = placed[options['to']]
    moving = Piece.place(entry['ref'], colour=entry['colour'],
                         position=Vector(*options.get('near', jsonable(support.position))), matrix=matrix)
    preview = replace(model, objects=[*model.objects, moving],
                      submodels={normalized(m.name): m for m in models.values() if m is not model})
    inspection = inspect_connections(preview, parts, instance_limit)
    groups = [[o.index for o in inspection.occurrences if o.occurrence.path[0].piece is piece]
              for piece in (moving, support)]
    try:
        moving_index = groups[0][options.get('moving_leaf', 0)]
        fixed_index = groups[1][options.get('fixed_leaf', 0)]
    except IndexError as exc:
        raise ValueError('snap leaf index is outside the selected part/submodel') from exc
    candidate_index = options.get('candidate', 0)
    report = snap_report(preview, parts, moving_index, fixed_index, moving_depth=0,
                         limit=candidate_index+1, instance_limit=instance_limit,
                         moving_feature=options.get('moving_feature'), fixed_feature=options.get('fixed_feature'))
    if candidate_index >= len(report['candidates']):
        raise ValueError(f"snap {entry['id']}: no candidate {candidate_index}; inspect connector coverage/occupancy")
    candidate = report['candidates'][candidate_index]
    if candidate['collision']['status'] == 'blocked':
        raise ValueError(f"snap {entry['id']}: candidate collides with a rectangular body")
    local = candidate['local_placement']
    return Vector(*local['at']), Matrix(local['matrix'])


def build_plan(plan, parts, *, instance_limit=100000):
    check_schema(plan)
    from .catalog import resolve_plan
    plan = resolve_plan(plan, parts)
    if plan.get("includes"):
        raise ValueError("Resolve includes with load_plan(path) before build_plan")
    names = [s["name"] for s in plan["sections"]]
    if len(set(map(normalized, names))) != len(names):
        raise ValueError("Section names must be unique ignoring case")
    models = {s["name"]: Model(name=s["name"]) for s in plan["sections"]}
    from .document import parse_source, section_table
    for asset in plan.get("assets", []):
        for sub in section_table(parse_source(asset)).values():
            if normalized(sub.name) in {normalized(n) for n in models}:
                raise ValueError(f"Duplicate section {sub.name}; extract assets with unique namespaces")
            from dataclasses import replace
            models[sub.name] = replace(sub, submodels={})
    known = set(map(normalized, models))
    anchors = {normalized(s["name"]): {name:frame(value) for name,value in s.get("anchors",{}).items()} for s in plan["sections"]}
    regular = profiles()
    for section in dependency_order(plan["sections"]):
        model = models[section["name"]]
        model.set_header(description=section["description"], name=model.name, author=section.get("author",plan["author"]), ldraw_org="Model")
        if section.get("license",plan.get("license")):
            model.set_header(license=section.get("license",plan.get("license")))
        placed = {}
        for step_index, step in enumerate(section["steps"]):
            if step_index:
                model.add_step()
            for entry in repeated(step):
                if len(placed) >= instance_limit:
                    raise ValueError(f"More than {instance_limit} direct placements in a section")
                if entry["id"] in placed:
                    raise ValueError(f"Duplicate placement id {entry['id']} in {model.name}")
                ref = entry["ref"]
                code = ref.casefold().removesuffix(".dat")
                if normalized(ref) not in known and parts.find_part(code=code) is None:
                    raise ValueError(f"Unknown reference {ref}; search/inspect the library first")
                if entry["colour"] not in parts.colours_by_code or entry["colour"] == 24:
                    raise ValueError(f"Unknown or unsuitable placement colour {entry['colour']}")
                matrix = Matrix(entry["matrix"]) if "matrix" in entry else rotation("y", entry.get("yaw", 0))
                if "snap" in entry:
                    position, matrix = snap_placement(entry, model, models, placed, parts, matrix, instance_limit)
                elif "on" in entry:
                    support_id = entry["on"]
                    if support_id not in placed:
                        raise ValueError(f"on: {support_id} must refer to an earlier placement in the same section")
                    support, support_code = placed[support_id]
                    if (code not in regular or support_code not in regular
                            or not regular[code]['studs'] or not regular[support_code]['studs']):
                        raise ValueError("on placement only supports curated rectangular studded bricks/plates; use part inspection and explicit at for other parts")
                    if not np.allclose(np.array(support.matrix.rows)[:, 1], [0, 1, 0], atol=1e-6) or not np.allclose(np.array(matrix.rows)[:, 1], [0, 1, 0], atol=1e-6):
                        raise ValueError("on requires upright parts")
                    offset = entry.get("offset_studs", [0, 0])
                    delta = support.matrix * Vector(offset[0] * 20, -regular[code]["height"], offset[1] * 20)
                    position = support.position + delta
                    def stud_centres(profile, pose, orient):
                        return [pose + orient * Vector(20 * (x - (profile["x_studs"]-1)/2), 0, 20 * (z - (profile["z_studs"]-1)/2))
                                for x in range(profile["x_studs"]) for z in range(profile["z_studs"])]
                    lower = stud_centres(regular[support_code], support.position, support.matrix)
                    upper = stud_centres(regular[code], position, matrix)
                    if not any(abs(a.x-b.x) < 1e-5 and abs(a.z-b.z) < 1e-5 for a in lower for b in upper):
                        raise ValueError(f"on: {entry['id']} has no aligned stud/socket with {support_id}; check half-stud offsets and part axes")
                elif "attach" in entry:
                    attach = entry["attach"]
                    if attach["to"] not in placed:
                        raise ValueError("attach.to must identify an earlier placement in the same section")
                    support, _ = placed[attach["to"]]
                    try:
                        fixed_frame = anchors[normalized(support.reference)][attach["anchor"]]
                        moving_frame = anchors[normalized(ref)][attach["using"]]
                    except KeyError as exc:
                        raise ValueError(f"Unknown module anchor {exc.args[0]}; declare both interfaces in the plans") from exc
                    support_frame = frame(dict(at=[support.position.x,support.position.y,support.position.z],matrix=support.matrix.rows))
                    offset = frame(dict(at=attach.get("offset",[0,0,0])))
                    transform = support_frame @ fixed_frame @ offset @ np.linalg.inv(moving_frame)
                    position = Vector(*transform[:3,3])
                    matrix = Matrix(transform[:3,:3].tolist())
                else:
                    position = Vector(*entry["at"])
                model.add(Comment(f"// {entry['id']}: {entry.get('purpose', ref)}"))
                piece = Piece.place(ref, colour=entry["colour"], position=position, matrix=matrix)
                model.add(piece)
                placed[entry["id"]] = (piece, code)
    root = models[names[0]]
    # MPD namespace is shared across all sections; serializer emits each section once.
    root.submodels = {normalized(m.name): m for m in list(models.values())[1:]}
    text = serialize_mpd(root)
    parsed, diagnostics = validate_text(text, parts, name=names[0], instance_limit=instance_limit)
    if any(d["severity"] == "error" for d in diagnostics):
        return text, parsed, diagnostics
    return text, parsed, diagnostics
