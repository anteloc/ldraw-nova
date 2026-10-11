"""Small architectural constructions with bounded parameters and real interfaces.

These are assembly vocabulary, not whole-building templates. Exported source is
editable and must be checked again when composed with its actual parent.
"""
import hashlib
from pathlib import Path

import numpy as np

from .builder import build_plan, repeated
from .check import check_model, placed_rows, world_box
from .common import atomic_write, dumps
from .details import detail_section, palettes
from .kit import Model, PLATES_1, PLATES_2
from .requirements import check_requirements
from .validation import validate_file


CATALOG = {
    "bonded-floor": dict(description="Two plate layers with offset seams in both axes", parameters=dict(width=[8, 12, 16], depth=[6, 8, 12]),
                         defaults=dict(width=12, depth=8), parent="Support the underside at Y=0; top studs are at Y=-16. Larger spans need supports.",
                         steps=["Lay the lower 2x4 plates", "Bridge both seam directions with the offset upper layer"]),
    "glazed-bay": dict(description="Six-stud glazed bay, with arched or straight projecting trim", parameters=dict(style=["arched", "straight"]),
                       defaults=dict(style="arched"), parent="Includes a 6x4 foundation plate; attach its underside to real studs. Keep the complete six-stud bay opening clear.",
                       steps=["Foundation", "Projecting sill, piers, window frame and matching panes", "Arch or straight cornice"]),
    "entrance-canopy": dict(description="A real door covered by a bonded canopy on four pillars", parameters=dict(depth=[3, 4], courses=[7, 8, 9]),
                            defaults=dict(depth=4, courses=7), parent="Includes an 8x6 foundation. Preserve the door opening, all pillars and both canopy layers.",
                            steps=["Foundation and hinged door", "Four pillars", "First roof layer", "Cross-seam roof plates"]),
}


def construction(name, parts, library, *, parameters=None, palette="botanical-bookshop"):
    if name not in CATALOG:
        raise ValueError(f"Unknown construction {name!r}")
    definition = CATALOG[name]
    parameters = {} if parameters is None else parameters
    if not isinstance(parameters, dict) or set(parameters) - set(definition["parameters"]):
        raise ValueError("Unknown construction parameters")
    options = {**definition["defaults"], **parameters}
    for key, value in options.items():
        choices = definition["parameters"][key]
        if type(value) is not type(choices[0]) or value not in choices:
            raise ValueError(f"{key} must be one of {definition['parameters'][key]}")
    if palette not in palettes() or palettes()[palette].get("family") == "vehicle":
        raise ValueError("Choose an architectural design palette")
    c = palettes()[palette]["roles"]
    m = Model(name, definition["description"], parts=parts, library=library)
    m.anchor("base", at=(0, 0, 0))
    contracts = []
    if name == "bonded-floor":
        width, depth = options["width"], options["depth"]
        m.anchor("top", at=(0, -16, 0))
        for z in range(0, depth, 2):
            for x in range(0, width, 4):
                m.place("3020", c["wood"], cell=(x, z), id=f"lower-{x}-{z}")
        m.next_step()
        x_segments = [2, *([4]*((width-4)//4)), 2]
        z_segments = [1, *([2]*((depth-2)//2)), 1]
        z = 0
        for d in z_segments:
            x = 0
            for w in x_segments:
                m.place((PLATES_1 if d == 1 else PLATES_2)[w], c["wood"], cell=(x, z), level=1, id=f"upper-{x}-{z}")
                x += w
            z += d
        selectors = [e["id"] for e in m.entries]
        contracts = [dict(id="floor-width", kind="extent", parts=selectors, axis="x", min=width*20, max=width*20),
                     dict(id="floor-depth", kind="extent", parts=selectors, axis="z", min=depth*20, max=depth*20)]
    elif name == "glazed-bay":
        m.place("3032", c["wood"], id="foundation")
        recipe = detail_section("arched-window", palette)
        bay = m.section("bay", "Inspected frame, pane, sill and pier positions from Copper Lane")
        for index, step in enumerate(recipe["steps"]):
            if index:
                bay.next_step()
            for p in repeated(step):
                if p["id"] == "arch" and options["style"] == "straight":
                    continue
                bay.add(p["ref"], p["colour"], at=p["at"], turn=p.get("yaw", 0), id=p["id"])
        if options["style"] == "straight":
            bay.add("3666", c["trim"], at=(0, -88, 0), id="lintel")
            bay.add("3795", c["trim"], at=(0, -96, -10), id="cornice")
        m.next_step()
        m.add(bay, None, at=(50, -8, 20), id="bay")
        contracts = [dict(id="six-stud-bay", kind="extent", parts=["bay"], axis="x", min=120, max=120)]
    else:
        depth, courses = options["depth"], options["courses"]
        m.place("3036", c["paving"], id="foundation")
        door = m.section("entrance", "Four-stud glazed hinged door")
        frame = door.place("60596", c["trim"], cell=(2, 4), level=1, id="frame")
        door.add("60623", c["shopfront"], at=frame.t+[-32, 0, 5], id="door")
        m.add(door, None, id="entrance")
        pillars = m.section("pillars", "Supported corners leave the doorway open")
        front = 5-depth
        for y in range(courses):
            if y:
                pillars.next_step()
            for x in (1, 6):
                for z in (front, 4):
                    pillars.place("3005", c["trim"], cell=(x, z), level=1+3*y, id=f"pillar-{x}-{z}-{y}")
        m.next_step()
        m.add(pillars, None, id="pillars")
        roof = m.section("roof", "Two connected roof layers spanning the entrance")
        roof.fill(c["shopfront"], cell=(0, front), size=(8, depth), level=1+3*courses, prefix="roof")
        roof.next_step()
        for x in range(8):
            roof.place(PLATES_1[depth], c["trim"] if x % 2 else c["shopfront"], cell=(x, front),
                       turn=90, level=2+3*courses, id=f"bridge-{x}")
        m.next_step()
        m.add(roof, None, id="roof")
        contracts = [dict(id="covers-door", kind="envelope_covers", cover=["roof"], target=["entrance"], axes=["x", "z"]),
                     dict(id="headroom", kind="above", upper=["roof"], lower=["entrance"], min_gap=8),
                     dict(id="canopy-depth", kind="extent", parts=["roof"], axis="z", min=60, max=80),
                     dict(id="roof-on-pillars", kind="connection", modules=["roof", "pillars"]),
                     dict(id="entrance-path", kind="clearance", parts=["pillars", "roof"],
                          min=[30, -152, front*20-10], max=[110, -8, 70])]
    footprint = [options["width"], options["depth"]] if name == "bonded-floor" else [6, 4] if name == "glazed-bay" else [8, 6]
    manifest = dict(name=name, parameters=options, palette=palette, parameter_ranges=definition["parameters"],
                    **{key: value for key, value in definition.items() if key != "parameters"},
                    mounting=dict(anchor="base", underside_y=0, first_stud=[0, 0, 0], pitch_ldu=20,
                                  footprint_studs=footprint, front="-Z",
                                  qualification="Align with real parent studs and recheck; an anchor alone proves no connection"))
    return m.plan(), dict(version=1, requirements=contracts), manifest


def export_construction(name, folder, parts, library, *, parameters=None, palette="botanical-bookshop", force=False):
    folder = Path(folder)
    if folder.exists() and any(folder.iterdir()) and not force:
        raise ValueError("Construction output exists; choose another directory or --force")
    plan, spec, manifest = construction(name, parts, library, parameters=parameters, palette=palette)
    text, _, diagnostics = build_plan(plan, parts)
    if any(d["severity"] == "error" for d in diagnostics):
        raise ValueError("Construction source validation failed")
    folder.mkdir(parents=True, exist_ok=True)
    atomic_write(folder/"model.mpd", text)
    atomic_write(folder/"model.plan.json", dumps(plan)+"\n")
    atomic_write(folder/"requirements.json", dumps(spec)+"\n")
    report = check_model(folder/"model.mpd", parts, library, limit=1000)
    model, _ = validate_file(folder/"model.mpd", parts, assembly=True)
    rows = placed_rows(model, folder/"model.mpd", parts, library)[0]
    feature = check_requirements(spec, rows, report)
    boxes = [world_box(row) for row in rows]
    manifest.update(physical_validity="not_proven", checks_passed=report["checks_passed"] and feature["checks_passed"],
                    bounds=dict(min=np.min([b[0] for b in boxes], axis=0).tolist(), max=np.max([b[1] for b in boxes], axis=0).tolist()),
                    reuse="Recheck in the actual parent; parameters are bounded, parts are never scaled")
    def digest(path):
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    manifest["evidence"] = dict(model_sha256=digest(folder/"model.mpd"), plan_sha256=digest(folder/"model.plan.json"),
                                requirements_sha256=digest(folder/"requirements.json"),
                                part_sources={r["code"]: r["local"].data.source_sha256 for r in rows},
                                fitting_rules=report["fitting_rules"],
                                generator=dict(path="ldraw_tools/constructions.py", sha256=digest(__file__)))
    if name == "glazed-bay":
        manifest["evidence"]["recipe"] = dict(path="ldraw_tools/details.py", name="arched-window",
                                                sha256=digest(Path(__file__).with_name("details.py")),
                                                adaptation="Added support plate and optional straight cornice; preserve master recipe provenance")
        frame = next(r for r in rows if r["label"] == "bay>frame")
        lo, hi = world_box(frame)
        manifest["reserved_spaces"] = [dict(min=lo.tolist(), max=hi.tolist(),
                                            purpose="Reserve the complete frame opening from neighbouring wall bricks; only matching panes belong inside")]
    elif name == "entrance-canopy":
        clearance = next(r for r in spec["requirements"] if r["id"] == "entrance-path")
        manifest["reserved_spaces"] = [dict(min=clearance["min"], max=clearance["max"],
                                            purpose="Approach to the doorway; door swing still needs separate review")]
    else:
        manifest["reserved_spaces"] = []
    atomic_write(folder/"construction.json", dumps(manifest)+"\n")
    atomic_write(folder/"check.json", dumps(report)+"\n")
    atomic_write(folder/"requirements-check.json", dumps(feature)+"\n")
    return dict(output=str(folder), **manifest)
