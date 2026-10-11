"""Construction boundaries, calibrated fittings, and fail-closed delivery evidence."""
import copy
import itertools
import json
from pathlib import Path
import subprocess

import numpy as np
import pytest

from conftest import mpd, ref
from ldraw_tools.builder import build_plan
from ldraw_tools.check import check_model, placed_rows
from ldraw_tools.common import library_path
from ldraw_tools.constructions import CATALOG, construction, export_construction
from ldraw_tools.fittings import catalog, fitting
from ldraw_tools.partcache import LibraryFiles, PartCache, TriangleExpander
from ldraw_tools.requirements import check_requirements
from ldraw_tools import stages
from ldraw_tools.validation import validate_file


COMBINATIONS = [(name, dict(zip(definition["parameters"], values)))
                for name, definition in CATALOG.items()
                for values in itertools.product(*definition["parameters"].values())]


@pytest.mark.parametrize("name,parameters", COMBINATIONS)
def test_every_supported_construction_size(official, tmp_path, name, parameters):
    result = export_construction(name, tmp_path, official, library_path(), parameters=parameters)
    assert result["checks_passed"], (tmp_path/"check.json").read_text()
    plan = json.loads((tmp_path/"model.plan.json").read_text())
    assert all(step for section in plan["sections"] for step in section["steps"])
    assert result["parameters"] == parameters


@pytest.mark.parametrize("parameters", [{"width": 10}, {"width": 8.0}, {"width": True}, {"width": 100}, {"stretch": 2}])
def test_constructions_do_not_scale_or_accept_unchecked_dimensions(official, parameters):
    with pytest.raises(ValueError):
        construction("bonded-floor", official, library_path(), parameters=parameters)


def evaluate_plan(plan, path, official):
    path.write_text(build_plan(plan, official)[0])
    checked = check_model(path, official, library_path())
    model, _ = validate_file(path, official, assembly=True)
    return checked, placed_rows(model, path, official, library_path())[0]


def test_floor_requires_cross_seam_bonds(official, tmp_path):
    plan, _, _ = construction("bonded-floor", official, library_path())
    plan["sections"][0]["steps"].pop()
    checked, _ = evaluate_plan(plan, tmp_path/"unbonded.mpd", official)
    assert not checked["checks_passed"] and checked["floating_count"] > 0


def test_connected_canopy_can_still_miss_its_door(official, tmp_path):
    plan, spec, _ = construction("entrance-canopy", official, library_path())
    # Move the complete door behind the canopy, but keep it on the foundation studs.
    entrance = next(p for step in plan["sections"][0]["steps"] for p in step if p["id"] == "entrance")
    entrance["at"][2] += 20
    checked, rows = evaluate_plan(plan, tmp_path/"uncovered.mpd", official)
    assert checked["checks_passed"]
    features = check_requirements(spec, rows, checked)
    assert not features["checks_passed"]
    assert not next(r for r in features["requirements"] if r["id"] == "covers-door")["passed"]


def test_unknown_selectors_and_occupied_clearance_fail(official, tmp_path):
    plan, _, _ = construction("entrance-canopy", official, library_path())
    checked, rows = evaluate_plan(plan, tmp_path/"canopy.mpd", official)
    spec = dict(version=1, requirements=[
        dict(id="missing", kind="extent", parts=["missing"], axis="x", min=0, max=1000),
        dict(id="opening", kind="clearance", parts=["pillars"], min=[-1000, -1000, -1000], max=[1000, 1000, 1000]),
        dict(id="missing-join", kind="connection", modules=["roof", "absent"]),
    ])
    features = check_requirements(spec, rows, checked)
    assert all(not r["passed"] for r in features["requirements"])
    with pytest.raises(ValueError):
        check_requirements(dict(version=1, requirements=[dict(id="invalid", kind=[])]), rows, checked)


@pytest.mark.parametrize("rule", catalog()["fittings"], ids=lambda r: r["id"])
def test_calibration_requires_exact_pose_and_sources(official, tmp_path, rule):
    def body(offset=0, duplicate=False, neighbour=False):
        t = np.array(rule["offset"])+[offset, 0, 0]
        pane = ref(rule["insert"]+".dat", position=" ".join(map(str, t)),
                   matrix=" ".join(str(v) for row in rule["rotation"] for v in row))
        return "\n".join([ref(rule["frame"]+".dat"), pane, *([pane] if duplicate else []),
                          *([ref("3001.dat", position="0 -12 0")] if neighbour else [])])
    path = tmp_path/"fitting.mpd"
    path.write_text(mpd(body()))
    checked = check_model(path, official, library_path())
    assert checked["checks_passed"] and checked["fitting_count"] == 1
    model, _ = validate_file(path, official, assembly=True)
    rows = placed_rows(model, path, official, library_path())[0]
    assert fitting(*rows)["id"] == rule["id"]
    # Rotate/translate the entire construction: evidence is local to the pair.
    transformed = copy.deepcopy(rows)
    rotation = np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]])
    for row in transformed:
        row["R"], row["t"] = rotation @ row["R"], rotation @ row["t"]+[120, -80, 40]
    assert fitting(*transformed)["id"] == rule["id"]
    changed = copy.deepcopy(rows)
    changed[0]["local"].data.source_sha256 = "changed primitive"
    assert fitting(*changed) is None
    changed = copy.deepcopy(rows)
    changed[1]["status"] = "normalized"
    assert fitting(*changed) is None
    for options in (dict(offset=10), dict(duplicate=True), dict(neighbour=True)):
        path.write_text(mpd(body(**options)))
        bad = check_model(path, official, library_path())
        assert not bad["checks_passed"], options
        if "offset" in options:
            assert bad["fitting_count"] == 0
        elif "duplicate" in options:
            assert bad["duplicate_count"] == 1
        else:
            assert bad["fitting_count"] == 1 and bad["collision_count"] > 0


def test_shared_primitive_changes_invalidate_cache_keys(parts, tmp_path):
    (tmp_path/"parts").mkdir()
    (tmp_path/"p").mkdir()
    top = tmp_path/"parts/test.dat"
    primitive = tmp_path/"p/shared.dat"
    top.write_text("0 Test\n"+ref("shared.dat"))
    primitive.write_text("0 Stud\n3 16 0 0 0 10 0 0 0 0 10\n")
    first = PartCache(parts, tmp_path)._file("test")
    before = TriangleExpander(LibraryFiles(tmp_path)).source_signature("test.dat")
    # Even male stud primitives omitted from collision triangles belong to the signature.
    primitive.write_text(primitive.read_text()+"0 Revision\n")
    second = PartCache(parts, tmp_path)._file("test")
    assert first != second
    assert before != TriangleExpander(LibraryFiles(tmp_path)).source_signature("test.dat")


@pytest.fixture
def stage_draft(tmp_path, monkeypatch):
    source = tmp_path/"source.mpd"
    source.write_text(mpd(ref()))

    def fake_render(path, library, outdir, *, views, timeout, bounds):
        # Unit tests exercise evidence control without starting CAD. A separate real
        # LeoCAD integration run checks actual rendering and BOMs.
        assert bounds is not None and bounds.max.x > bounds.min.x
        outdir = Path(outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        images = []
        for view in views:
            image = outdir/f"{view}.png"
            image.write_bytes(b"unit-test image")
            images.append(str(image))
        bom = outdir/"leocad-bom.csv"
        bom.write_text("Part ID,Color Code,Quantity\n3001,4,1\n")
        return dict(images=images, bom=str(bom))
    monkeypatch.setattr(stages, "render", fake_render)
    return source, tmp_path/"stage"


def accepted(stage_draft, official, **kwargs):
    source, folder = stage_draft
    report = stages.prepare_stage(source, folder, official, library_path(), **kwargs)
    assert report["status"] == "READY_FOR_REVIEW"
    stages.review_stage(folder, images=report["images"], note="Unit-test review", decision="accept")
    return report


def test_stage_exports_exact_snapshot_after_review(stage_draft, official, tmp_path):
    source, folder = stage_draft
    report = accepted(stage_draft, official)
    output = tmp_path/"delivery.mpd"
    stages.export_stage(folder, output, official, library_path())
    assert output.read_bytes() == source.read_bytes()
    assert report["physical_validity"] == "not_proven"


@pytest.mark.parametrize("changed", ["source", "model.mpd", "check.json", "views/front.png", "visual-review.json", "stage.json"])
def test_stale_evidence_never_replaces_previous_delivery(stage_draft, official, tmp_path, changed):
    source, folder = stage_draft
    accepted(stage_draft, official)
    target = source if changed == "source" else folder/changed
    if changed == "visual-review.json":
        review = stages.read_json(target)
        review["decision"] = "revise"
        target.write_text(json.dumps(review))
    else:
        target.write_bytes(target.read_bytes()+b"\n")
    output = tmp_path/"delivery.mpd"
    output.write_text("Previous reviewed model")
    with pytest.raises(ValueError):
        stages.export_stage(folder, output, official, library_path(), force=True)
    assert output.read_text() == "Previous reviewed model"


def test_unrendered_and_incomplete_reviews_cannot_promote(stage_draft, official):
    source, folder = stage_draft
    report = stages.prepare_stage(source, folder, official, library_path(), no_render=True)
    assert report["status"] == "REVIEW" and report["technical_checks_passed"]
    with pytest.raises(ValueError):
        stages.review_stage(folder, images=[], note="No views", decision="accept")
    report = stages.prepare_stage(source, folder, official, library_path(), force=True)
    with pytest.raises(ValueError):
        stages.review_stage(folder, images=report["images"][:1], note="Only one view", decision="accept")


@pytest.mark.parametrize("failure", ["geometry", "requirements", "render", "bom"])
def test_failed_stages_remain_inspectable_but_cannot_export(stage_draft, official, tmp_path, monkeypatch, failure):
    source, folder = stage_draft
    kwargs = {}
    if failure == "geometry":
        source.write_text(mpd(ref()+"\n"+ref(position="200 0 0")))
    elif failure == "requirements":
        spec = tmp_path/"requirements.json"
        spec.write_text(json.dumps(dict(version=1, requirements=[dict(id="width", kind="extent", parts=["missing"], axis="x", min=1, max=2)])))
        kwargs["requirements"] = spec
    elif failure == "render":
        def fail(*args, **kwargs):
            raise subprocess.TimeoutExpired("leocad", 1)
        monkeypatch.setattr(stages, "render", fail)
    else:
        source.write_text(mpd(ref(colour=1)))
    report = stages.prepare_stage(source, folder, official, library_path(), **kwargs)
    assert report["status"] != "READY_FOR_REVIEW"
    assert (folder/"model.mpd").exists() and (folder/"check.json").exists()
    with pytest.raises(ValueError):
        stages.review_stage(folder, images=report["images"], note="Review", decision="accept")
    with pytest.raises(ValueError):
        stages.export_stage(folder, tmp_path/"delivery.mpd", official, library_path())


def test_refresh_invalidates_review_and_failed_prepare_is_recoverable(stage_draft, official, monkeypatch):
    source, folder = stage_draft
    accepted(stage_draft, official)
    real_check = stages.check_model
    monkeypatch.setattr(stages, "check_model", lambda *a, **kw: (_ for _ in ()).throw(ValueError("interrupted check")))
    with pytest.raises(ValueError):
        stages.prepare_stage(source, folder, official, library_path(), force=True)
    assert not (folder/"stage.json").exists() and not (folder/"visual-review.json").exists()
    monkeypatch.setattr(stages, "check_model", real_check)
    assert stages.prepare_stage(source, folder, official, library_path(), force=True)["status"] == "READY_FOR_REVIEW"


def test_plan_includes_are_bound_to_review(stage_draft, official, tmp_path):
    _, folder = stage_draft
    source = tmp_path/"root.plan.json"
    included = tmp_path/"child.plan.json"
    child = dict(version=1, author="Tests", sections=[dict(name="child.ldr", description="Child", steps=[[
        dict(id="brick", ref="3001.dat", colour=4, at=[0, 0, 0])]])])
    included.write_text(json.dumps(child))
    source.write_text(json.dumps(dict(version=1, author="Tests", includes=[included.name], sections=[
        dict(name="main.ldr", description="Parent", steps=[[dict(id="child", ref="child.ldr", colour=16, at=[0, 0, 0])]])])))
    accepted((source, folder), official)
    child["sections"][0]["steps"][0][0]["colour"] = 1
    included.write_text(json.dumps(child))
    with pytest.raises(ValueError, match="Authoring source changed"):
        stages.export_stage(folder, tmp_path/"delivery.mpd", official, library_path())


def test_changed_part_evidence_and_feature_spec_require_repreparing(stage_draft, official, tmp_path, monkeypatch):
    _, folder = stage_draft
    accepted(stage_draft, official)
    original_environment = stages.environment
    monkeypatch.setattr(stages, "environment", lambda *a: {**original_environment(*a), "colours": "new colours"})
    with pytest.raises(ValueError, match="checking code changed"):
        stages.export_stage(folder, tmp_path/"delivery.mpd", official, library_path())
    monkeypatch.setattr(stages, "environment", original_environment)
    # Test requirement source binding independently of the mocked one-brick BOM.
    source, folder = stage_draft
    feature = tmp_path/"features.json"
    feature.write_text(json.dumps(dict(version=1, requirements=[dict(id="extent", kind="extent", parts=["3001"], axis="x", min=80, max=80)])))
    model, _ = validate_file(source, official, assembly=True)
    label = placed_rows(model, source, official, library_path())[0][0]["label"]
    value = stages.read_json(feature)
    value["requirements"][0]["parts"] = [label]
    feature.write_text(json.dumps(value))
    accepted(stage_draft, official, requirements=feature, force=True)
    feature.write_text(feature.read_text()+"\n")
    with pytest.raises(ValueError, match="Feature requirements changed"):
        stages.export_stage(folder, tmp_path/"delivery.mpd", official, library_path())
