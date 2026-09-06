from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

import jsonschema
from ldraw.errors import PartError

from .builder import build_plan, rotation
from .common import ROOT, DATA, atomic_write, dumps, get_parts, jsonable, library_path, models_path
from .external import cad_check, render, prepare_glb
from .geometry import analyze_geometry, profiles, snap
from .resources import search_spec, search_models, model_sections
from .validation import validate_file


def positive(value):
    value = int(value)
    if value <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return value


def parser():
    p = argparse.ArgumentParser(description="Generate, inspect and review LDraw MPD assemblies. All reports are JSON. See docs/agent/tooling.md.")
    p.add_argument("--library", help="LDraw library root (default LDRAW_DIR or ../ldraw-lib/ldraw)")
    p.add_argument("--models", help="Annotated model directory (default MODELS_DIR)")
    p.add_argument("--shadow", action="append", default=[], help="Optional LDCad connector directory/zip/csl; repeatable")
    commands = p.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="Show dependencies and source paths")
    commands.add_parser("index", help="Refresh the local parts index; source library remains unchanged")
    c = commands.add_parser("search", help="Search actual library parts or annotated models")
    c.add_argument("kind", choices=["parts", "models", "submodels"])
    c.add_argument("query")
    c.add_argument("--limit", type=positive, default=10)
    c = commands.add_parser("part", help="Inspect one real part's metadata, local bounds and connectors")
    c.add_argument("code")
    c.add_argument("--limit", type=positive, default=30, help="Connector output limit (total is always reported)")
    c = commands.add_parser("colours", help="Look up codes in the installed LDConfig.ldr")
    c.add_argument("query", nargs="?", default="")
    c = commands.add_parser("spec", help="Search the mandatory PDF or retrieve a 1-based page")
    c.add_argument("query", nargs="?")
    c.add_argument("--page", type=positive)
    c.add_argument("--limit", type=positive, default=8)
    c = commands.add_parser("sections", help="Read original annotated model sections with source line numbers")
    c.add_argument("file")
    c.add_argument("--section")
    c = commands.add_parser("matrix", help="Compute a right-handed rotation in LDraw coordinates")
    c.add_argument("axis", choices=["x", "y", "z"])
    c.add_argument("degrees", type=float)
    commands.add_parser("profiles", help="List curated ordinary brick/plate dimensions for on placement")
    c = commands.add_parser("build", help="Build a validated MPD from a JSON plan")
    c.add_argument("plan")
    c.add_argument("--output", required=True)
    c.add_argument("--report")
    c.add_argument("--force", action="store_true", help="Replace an existing MPD after successful validation")
    for command in ["validate", "inspect", "bom", "snap"]:
        c = commands.add_parser(command)
        c.add_argument("file")
        c.add_argument("--report")
        if command == "validate":
            c.add_argument("--profile", choices=["assembly", "syntax"], default="assembly")
            c.add_argument("--geometry", action="store_true")
            c.add_argument("--strict", action="store_true", help="Warnings also fail (does not extend check coverage)")
        if command == "snap":
            c.add_argument("--moving", type=int, required=True)
            c.add_argument("--fixed", type=int, required=True)
            c.add_argument("--limit", type=positive, default=5)
    c = commands.add_parser("cad-check", help="Run Python validation and a LeoCAD snapshot/BOM import check")
    c.add_argument("file")
    c.add_argument("--timeout", type=positive, default=90)
    c = commands.add_parser("render", help="Render review views and export a LeoCAD BOM")
    c.add_argument("file")
    c.add_argument("--outdir", required=True)
    c.add_argument("--views", nargs="+", default=["home", "top", "front"])
    c.add_argument("--timeout", type=positive, default=90)
    c = commands.add_parser("glb", help="Convert a local model or part with semantic descriptions")
    c.add_argument("file")
    c.add_argument("--output", required=True)
    c.add_argument("--timeout", type=positive, default=180)
    return p


def run(args):
    library = library_path(args.library)
    if args.command == "doctor":
        report = dict(python=sys.version.split()[0], packages={n: version(n) for n in ["pyldraw3", "numpy", "jsonschema"]},
                      library=str(library), library_present=(library / "parts").is_dir(),
                      models=str(models_path(args.models)), pdf=str(ROOT / "docs/ldraw-specs.pdf"),
                      tools={t: shutil.which(t) for t in ["pdftotext", "leocad", "mpd2glb.sh"]})
        return report, 0 if report["library_present"] and report["tools"]["pdftotext"] else 2
    if args.command == "spec":
        return search_spec(args.query, args.page, args.limit), 0
    if args.command == "sections":
        return model_sections(args.file, args.section), 0
    if args.command == "matrix":
        return dict(axis=args.axis, degrees=args.degrees, matrix=jsonable(rotation(args.axis, args.degrees))), 0
    if args.command == "profiles":
        return json.loads((DATA / "rectangular-parts.json").read_text()), 0
    if args.command == "search" and args.kind != "parts":
        return search_models(args.query, root=args.models, limit=args.limit, submodels=args.kind == "submodels"), 0
    parts = get_parts(library, refresh=args.command == "index")
    for shadow in args.shadow:
        parts.add_connection_shadow(shadow)
    if args.command == "render":
        from ldraw import inspect_model
        from ldraw.lines import Line, OptionalLine, Triangle, Quadrilateral
        model, diagnostics = validate_file(args.file, parts, assembly=False)
        bounds = None
        if model and not any(d["severity"] == "error" for d in diagnostics):
            raw_geometry = any(isinstance(obj, (Line, OptionalLine, Triangle, Quadrilateral))
                               for m in [model, *model.submodels.values()] for obj in m.objects)
            if not raw_geometry:
                inspection = inspect_model(model, parts)
                if inspection.complete:
                    bounds = inspection.bounds
        return render(args.file, library, args.outdir, views=args.views, timeout=args.timeout, bounds=bounds), 0
    if args.command == "cad-check":
        model, diagnostics = validate_file(args.file, parts, assembly=Path(args.file).suffix.casefold() == ".mpd")
        if model and not any(d["severity"] == "error" for d in diagnostics):
            report = cad_check(args.file, library, timeout=args.timeout)
            return dict(checks_passed=True, diagnostics=diagnostics, cad=report), 0
        return dict(checks_passed=False, diagnostics=diagnostics, cad=None), 1
    if args.command == "glb":
        return prepare_glb(args.file, library, args.output, parts, timeout=args.timeout), 0
    if args.command == "index":
        return dict(parts=len(parts.by_code), library=str(library), index=str(parts.path)), 0
    if args.command == "search":
        # Match all plain terms; retain original filenames and descriptions.
        query = args.query.casefold().split()
        matches = [dict(code=c + ".dat", description=d) for c, d in parts.by_code.items()
                   if all(t in (c + ".dat " + d).casefold() for t in query)]
        matches.sort(key=lambda r: (r["code"].casefold().removesuffix(".dat") != args.query.casefold().removesuffix(".dat"),
                                    r["description"].startswith(("~", "=")), len(r["description"]), r["code"]))
        return dict(total=len(matches), results=matches[:args.limit]), 0
    if args.command == "colours":
        return [jsonable(c) for k, c in sorted(parts.colours_by_code.items())
                if args.query.casefold() in (str(k) + " " + (c.name or "")).casefold()], 0
    if args.command == "part":
        code = args.code.casefold().removesuffix(".dat")
        part = parts.part(code=code)
        g = parts.geometry(code)
        return dict(code=code + ".dat", path=str(part.path.resolve()), metadata=jsonable(part.metadata),
                    complete=g.complete, bounds=jsonable(g.bounds), size=jsonable(g.bounds.size) if g.bounds else None,
                    stud_positions=[jsonable(s.position) for s in g.top_studs],
                    connector_count=len(g.connections), connectors=jsonable(g.connections[:args.limit]),
                    connectors_truncated=len(g.connections) > args.limit, diagnostics=jsonable(g.diagnostics),
                    rectangular_profile=profiles().get(code),
                    note="All coordinates are local LDU. Connector inference is evidence; inspect uncertain fits."), 0 if g.complete else 1
    if args.command == "build":
        target = Path(args.output)
        if target.suffix.casefold() != ".mpd":
            raise ValueError("Output must end in .mpd")
        if target.exists() and not args.force:
            raise ValueError("Output exists; use --force to replace after successful validation")
        plan = json.loads(Path(args.plan).read_text(), parse_constant=lambda v: (_ for _ in ()).throw(ValueError(f"Nonfinite JSON value {v}")))
        text, model, diagnostics = build_plan(plan, parts)
        geometry = None
        if not any(d["severity"] == "error" for d in diagnostics):
            geometry = analyze_geometry(model, parts)
            diagnostics += geometry["diagnostics"]
        passed = not any(d["severity"] == "error" for d in diagnostics)
        report = dict(profile="assembly", checks_passed=passed, physical_validity="not_proven", output=str(target),
                      written=passed, diagnostics=diagnostics, geometry=geometry)
        if passed:
            atomic_write(target, text)
        return report, 0 if passed else 1
    assembly = args.command == "validate" and args.profile == "assembly"
    model, diagnostics = validate_file(args.file, parts, assembly=assembly)
    report = dict(file=args.file, profile="assembly" if assembly else "syntax", checks_passed=False,
                  physical_validity="not_proven", diagnostics=diagnostics)
    if model and not any(d["severity"] == "error" for d in diagnostics):
        if args.command == "bom":
            report["bom"] = jsonable(model.bill_of_materials(parts=parts))
        elif args.command == "snap":
            report["candidates"] = snap(model, parts, args.moving, args.fixed, args.limit)
        elif args.command == "inspect" or (args.command == "validate" and args.geometry):
            report["geometry"] = analyze_geometry(model, parts)
            diagnostics += report["geometry"]["diagnostics"]
        report["checks_passed"] = not any(d["severity"] == "error" for d in diagnostics)
    failed = not report["checks_passed"] or (getattr(args, "strict", False) and bool(diagnostics))
    return report, 1 if failed else 0


def main():
    args = parser().parse_args()
    try:
        report, status = run(args)
    except (OSError, ValueError, PartError, RecursionError, sqlite3.Error, subprocess.SubprocessError, jsonschema.ValidationError) as exc:
        report, status = dict(checks_passed=False, error=str(exc), error_type=type(exc).__name__), 2
    text = dumps(report) + "\n"
    if getattr(args, "report", None):
        atomic_write(args.report, text)
    print(text, end="")
    return status


if __name__ == "__main__":
    sys.exit(main())
