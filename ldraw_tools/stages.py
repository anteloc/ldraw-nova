"""One review/export gate for MPDs emitted by any authoring tool or JSON plans."""
from __future__ import annotations

import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import subprocess
import time

from ldraw import inspect_model

from .builder import build_plan, load_plan
from .check import check_model, placed_rows
from .common import DATA, atomic_write, dumps
from .document import physical_context
from .external import render, compare_bom
from .requirements import check_requirements
from .validation import validate_file


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(), parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"Nonfinite JSON {value}")))


def source_state(path):
    path = Path(path)
    result = dict(file=sha(path))
    if path.suffix.lower() == ".json":
        plan = load_plan(path)
        result.update(plan=hashlib.sha256(dumps(plan).encode()).hexdigest(),
                      assets={name: sha(name) for name in plan.get("assets", [])})
    return result


def environment(rows, library):
    """Bind evidence to actual part dependencies, connectors and checking code."""
    types = {r["code"]: r["local"].data for r in rows}
    return dict(library=str(Path(library).resolve()), pyldraw3=version("pyldraw3"),
                colours=sha(Path(library)/"LDConfig.ldr"),
                parts={code: dict(source=data.source_sha256,
                                  connectors=hashlib.sha256(dumps(data.ports).encode()).hexdigest())
                       for code, data in sorted(types.items())},
                code={p.name: sha(p) for p in sorted(Path(__file__).parent.glob("*.py"))},
                fittings=sha(DATA/"fittings.json"))


def _confined(folder, name):
    path = (folder/name).resolve()
    if not path.is_relative_to(folder) or path == folder:
        raise ValueError("Stage artifacts must stay inside their directory")
    return path


def prepare_stage(source, folder, parts, library, *, requirements=None, views=("home", "front", "right", "top"),
                  no_render=False, force=False, timeout=90):
    start = time.perf_counter()
    if not views or len(set(views)) != len(views) or any(v not in {"home", "front", "back", "left", "right", "top", "bottom"} for v in views):
        raise ValueError("Choose distinct supported viewpoints")
    source, folder = Path(source).resolve(), Path(folder).resolve()
    if source.is_relative_to(folder) or (requirements is not None and Path(requirements).resolve().is_relative_to(folder)):
        raise ValueError("Choose a stage directory separate from its source and requirements")
    if folder.exists() and any(folder.iterdir()):
        if not force or not ((folder/"stage.json").is_file() or (folder/".stage-owned").is_file()):
            raise ValueError("Stage directory is not empty; use --force only to refresh an existing stage")
    folder.mkdir(parents=True, exist_ok=True)
    # A failed preparation can be retried without accepting an unrelated directory.
    atomic_write(folder/".stage-owned", "ldraw-tools stage v1\n")
    # Invalidate old evidence before any operation that can fail.
    (folder/"stage.json").unlink(missing_ok=True)
    (folder/"visual-review.json").unlink(missing_ok=True)
    inputs = source_state(source)
    if source.suffix.lower() == ".json":
        text, _, diagnostics = build_plan(load_plan(source), parts)
        if any(d["severity"] == "error" for d in diagnostics):
            raise ValueError("The plan cannot produce a valid MPD")
    else:
        text = source.read_bytes().decode("utf-8")
    target = folder/"model.mpd"
    atomic_write(target, text)
    construction = check_model(target, parts, library, limit=1000)
    atomic_write(folder/"check.json", dumps(construction)+"\n")
    model, diagnostics = validate_file(target, parts, assembly=True)
    rows = placed_rows(model, target, parts, library)[0] if model is not None else []
    context = environment(rows, library)
    feature = dict(checks_passed=True, requirements=[], coverage="No feature requirements supplied")
    artifacts = ["model.mpd", "check.json", "requirements-check.json"]
    if requirements is not None:
        spec = read_json(requirements)
        feature = check_requirements(spec, rows, construction)
        atomic_write(folder/"requirements.json", dumps(spec)+"\n")
        artifacts.append("requirements.json")
    atomic_write(folder/"requirements-check.json", dumps(feature)+"\n")
    checked = time.perf_counter()
    render_error, comparison, images = None, None, []
    valid_source = model is not None and not any(d["severity"] == "error" for d in diagnostics)
    if not no_render and valid_source:
        try:
            render_model, render_parts = physical_context(model, parts)
            inspected = inspect_model(render_model, render_parts)
            preview = render(target, library, folder/"views", views=views, timeout=timeout,
                             bounds=inspected.bounds if inspected.complete else None)
            images = [str(Path(p).relative_to(folder)) for p in preview["images"]]
            comparison = compare_bom(model, parts, preview["bom"])
            atomic_write(folder/"bom-comparison.json", dumps(comparison)+"\n")
            artifacts += [*images, "views/leocad-bom.csv", "bom-comparison.json"]
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            render_error = str(error)
    technical = construction["checks_passed"] and feature["checks_passed"]
    failed = construction["verdict"] == "FAIL" or not feature["checks_passed"] or comparison is not None and not comparison["matches"]
    ready = technical and bool(images) and comparison is not None and comparison["matches"] and not render_error
    report = dict(version=1, source=str(source), source_sha256=inputs["file"], inputs=inputs,
                  requirements_source=str(Path(requirements).resolve()) if requirements else None,
                  requirements_sha256=sha(requirements) if requirements else None,
                  status="READY_FOR_REVIEW" if ready else "FAIL" if failed else "REVIEW",
                  technical_checks_passed=technical, physical_validity="not_proven",
                  construction_verdict=construction["verdict"], parts=construction.get("parts", 0),
                  feature_requirements=len(feature["requirements"]), images=images,
                  rendered=bool(images) and not render_error, render_error=render_error,
                  bom_matches=comparison["matches"] if comparison is not None else None,
                  preparation="checks_only" if no_render else "render_failed" if render_error else "complete",
                  review_state="pending_review" if ready else "pending_images" if technical and no_render else "blocked",
                  next_action="Open every image, then stage review; export requires acceptance" if ready else
                              "Prepare again with rendering, open the images and record a review" if technical and no_render else
                              "Inspect check.json, requirements-check.json and render_error; repair or resolve findings",
                  environment=context, artifact_hashes={name: sha(folder/name) for name in artifacts},
                  seconds=dict(checks=round(checked-start, 3), render=round(time.perf_counter()-checked, 3)),
                  note="Open all views before recording a review; a technical pass does not judge beauty or prove buildability")
    atomic_write(folder/"stage.json", dumps(report)+"\n")
    return report


def current_stage(folder):
    folder = Path(folder).resolve()
    report = read_json(folder/"stage.json")
    required = {"model.mpd", "check.json", "requirements-check.json"}
    if report.get("feature_requirements"):
        required.add("requirements.json")
    if report.get("rendered"):
        required.update([*report["images"], "views/leocad-bom.csv", "bom-comparison.json"])
    hashes = report.get("artifact_hashes", {})
    if report.get("version") != 1 or not required.issubset(hashes):
        raise ValueError("Stage evidence is incomplete; prepare it again")
    for name, digest in hashes.items():
        path = _confined(folder, name)
        if not path.is_file() or sha(path) != digest:
            raise ValueError(f"Stage artifact changed: {name}; prepare and review again")
    return folder, report


def review_stage(folder, *, images, note, decision):
    folder, report = current_stage(folder)
    if decision not in {"accept", "revise"}:
        raise ValueError("Review decision must be accept or revise")
    if (not report["rendered"] or not note.strip() or len(images) != len(set(images))
            or set(images) != set(report["images"])):
        raise ValueError("Review requires a note and every rendered image actually opened")
    if decision == "accept" and report["status"] != "READY_FOR_REVIEW":
        raise ValueError("Unresolved technical checks cannot be accepted for export")
    review = dict(decision=decision, note=note, viewed_images=images, stage_sha256=sha(folder/"stage.json"),
                  physical_validity="not_proven", evidence="Self-reported visual inspection")
    atomic_write(folder/"visual-review.json", dumps(review)+"\n")
    return review


def export_stage(folder, output, parts, library, *, force=False):
    folder, report = current_stage(folder)
    review_path = folder/"visual-review.json"
    review = read_json(review_path) if review_path.is_file() else {}
    if (report["status"] != "READY_FOR_REVIEW" or review.get("decision") != "accept"
            or review.get("stage_sha256") != sha(folder/"stage.json")
            or set(review.get("viewed_images", [])) != set(report["images"]) or not review.get("note", "").strip()):
        raise ValueError("Export requires passing checks and a current accepting visual review")
    target = Path(output).resolve()
    if target.is_relative_to(folder) or target.suffix.lower() != ".mpd":
        raise ValueError("Export to an .mpd outside the stage directory")
    if target.exists() and not force:
        raise ValueError("Output exists; use --force to replace after passing checks")
    if source_state(report["source"]) != report["inputs"]:
        raise ValueError("Authoring source changed; prepare and review again")
    if report.get("requirements_source") and sha(report["requirements_source"]) != report["requirements_sha256"]:
        raise ValueError("Feature requirements changed; prepare and review again")
    model, _ = validate_file(folder/"model.mpd", parts, assembly=True)
    rows = placed_rows(model, folder/"model.mpd", parts, library)[0]
    if environment(rows, library) != report["environment"]:
        raise ValueError("Parts, connectors, colours or checking code changed; prepare and review again")
    checked = check_model(folder/"model.mpd", parts, library)
    if not checked["checks_passed"]:
        raise ValueError("Current construction checks do not pass; prepare the stage again")
    if (folder/"requirements.json").name in report["artifact_hashes"]:
        if not check_requirements(read_json(folder/"requirements.json"), rows, checked)["checks_passed"]:
            raise ValueError("Feature requirements no longer pass")
    atomic_write(target, (folder/"model.mpd").read_bytes().decode("utf-8"))
    return dict(output=str(target), sha256=sha(target), stage=str(folder), checks_passed=True,
                physical_validity="not_proven", visual_review=review["note"])
