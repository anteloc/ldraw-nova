"""Deterministic, schema-checked assembly plans using pyldraw3's writer."""
from __future__ import annotations

import json
import math
from pathlib import Path

import jsonschema
import numpy as np
from ldraw import Model, Piece, Vector, Matrix
from ldraw.lines import Comment

from .common import DATA, normalized
from .geometry import profiles
from .validation import validate_text


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


def build_plan(plan, parts):
    jsonschema.Draft202012Validator(json.loads((DATA / "plan.schema.json").read_text())).validate(plan)
    names = [s["name"] for s in plan["sections"]]
    if len(set(map(normalized, names))) != len(names):
        raise ValueError("Section names must be unique ignoring case")
    known = set(map(normalized, names))
    models = {s["name"]: Model(name=s["name"]) for s in plan["sections"]}
    regular = profiles()
    for section in plan["sections"]:
        model = models[section["name"]]
        model.set_header(description=section["description"], name=model.name, author=plan["author"], ldraw_org="Model")
        if plan.get("license"):
            model.set_header(license=plan["license"])
        placed = {}
        for step_index, step in enumerate(section["steps"]):
            if step_index:
                model.add_step()
            for entry in step:
                if entry["id"] in placed:
                    raise ValueError(f"Duplicate placement id {entry['id']} in {model.name}")
                ref = entry["ref"]
                code = ref.casefold().removesuffix(".dat")
                if normalized(ref) not in known and parts.find_part(code=code) is None:
                    raise ValueError(f"Unknown reference {ref}; search/inspect the library first")
                if entry["colour"] not in parts.colours_by_code or entry["colour"] == 24:
                    raise ValueError(f"Unknown or unsuitable placement colour {entry['colour']}")
                matrix = Matrix(entry["matrix"]) if "matrix" in entry else rotation("y", entry.get("yaw", 0))
                if "on" in entry:
                    support_id = entry["on"]
                    if support_id not in placed:
                        raise ValueError(f"on: {support_id} must refer to an earlier placement in the same section")
                    support, support_code = placed[support_id]
                    if code not in regular or support_code not in regular:
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
    parsed, diagnostics = validate_text(text, parts, name=names[0])
    if any(d["severity"] == "error" for d in diagnostics):
        return text, parsed, diagnostics
    return text, parsed, diagnostics
