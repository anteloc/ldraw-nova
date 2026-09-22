from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path
from tempfile import TemporaryDirectory

import jsonschema
from ldraw.errors import PartError

from .builder import build_plan, load_plan, rotation
from .common import ROOT, DATA, atomic_write, dumps, get_parts, jsonable, library_path, models_path, shadow_paths
from .external import cad_check, render, prepare_glb, compare_bom
from .geometry import analyze_geometry, profiles
from .resources import search_spec, search_models, model_sections
from .validation import validate_file, validate_text
from .document import study_model, extract_section, physical_context, selected_source
from .connectivity import connection_report, metadata_summary, snap_report, apply_snap


def positive(value):
    value = int(value)
    if value <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return value


def geometry_options(c):
    c.add_argument("--detail", choices=["summary", "full"], default="full")
    c.add_argument("--contacts", choices=["auto", "all", "none"], default="auto", help="auto computes contacts for at most 500 physical placements; scope larger models to sections")
    c.add_argument("--limit", type=positive, default=200, help="Maximum instance/contact/pair/component rows (does not limit checks)")
    c.add_argument("--offset", type=int, default=0, help="First physical occurrence to display")
    c.add_argument("--max-instances", type=positive, default=100000, help="Physical expansion budget")


def geometry_report(model, parts, args):
    if args.offset < 0:
        raise ValueError("--offset must be nonnegative")
    return analyze_geometry(model, parts, detail=args.detail, contacts=args.contacts,
                            output_limit=args.limit, pair_limit=args.limit, offset=args.offset, instance_limit=args.max_instances)


def scope_options(c):
    c.add_argument("--section", help="Inspect only this FILE block and its dependency closure; indices become section-local")
    c.add_argument("--colour", type=int, help="Explicit inherited colour for a selected subassembly")


def parser():
    p = argparse.ArgumentParser(description="Generate, inspect and review LDraw MPD assemblies. All reports are JSON. See docs/agent/tooling.md.")
    p.add_argument("--library", help="LDraw library root (default LDRAW_DIR or ../ldraw-lib/ldraw)")
    p.add_argument("--models", help="Annotated model directory (default MODELS_DIR)")
    shadows = p.add_mutually_exclusive_group()
    shadows.add_argument("--shadow", action="append", help="LDCad directory/zip/csl; repeatable, replaces LDRAW_SHADOW or ./offLibShadow")
    shadows.add_argument("--no-shadow", action="store_true", help="Disable external shadow metadata")
    commands = p.add_subparsers(dest="command", required=True)
    c = commands.add_parser("examples", help="Find relevant generated building or detail examples")
    c.add_argument("query", nargs="?", default="")
    c.add_argument("--limit", type=positive, default=5)
    c.add_argument("--scale", choices=["minifigure", "microscale"])
    c.add_argument("--details", action="store_true")
    c = commands.add_parser("catalog", help="Search the supplied part/colour categories using descriptive symbols")
    c.add_argument("kind", choices=["categories", "parts", "colours"])
    c.add_argument("query", nargs="?", default="")
    c.add_argument("--category")
    c.add_argument("--limit", type=positive, default=12)
    c.add_argument("--max-size", type=float, nargs=3, metavar=("X","Y","Z"), help="Maximum cached full bounds in LDU; not stacking dimensions")
    c.add_argument("--include-unavailable", action="store_true", help="Include missing, alias and internal entries with status flags")
    c.add_argument("--measure", action="store_true", help="Measure selected part results and flag differences from cached dimensions")
    c = commands.add_parser("design", help="Role-based palettes and reusable architectural detail plans")
    c.add_argument("kind", choices=["palettes", "details"])
    c.add_argument("name", nargs="?")
    c.add_argument("--palette", default="botanical-bookshop")
    c.add_argument("--output", help="Write a detail JSON plan")
    c.add_argument("--force", action="store_true")
    c = commands.add_parser("part-board", help="Render 1–12 real part candidates into an offline visual shortlist")
    c.add_argument("refs", nargs='+')
    c.add_argument("--outdir", required=True)
    c.add_argument("--colour", default='19', help="Installed colour code or @colours.Name")
    c.add_argument("--timeout", type=positive, default=90)
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
    c = commands.add_parser("study", help="Inventory an OMR assembly hierarchy, physical BOM, and source issues")
    c.add_argument("file")
    c.add_argument("--report")
    c.add_argument("--max-instances", type=positive, default=100000)
    c.add_argument("--detail", choices=["summary", "full"], default="summary")
    c.add_argument("--limit", type=positive, default=30, help="Summary section/diagnostic rows")
    c = commands.add_parser("extract", help="Copy one dependency-closed section with namespacing and attribution manifest")
    c.add_argument("file")
    c.add_argument("--section", required=True)
    c.add_argument("--namespace", required=True)
    c.add_argument("--output", required=True)
    c.add_argument("--repair-bfc-comments", action="store_true", help="Explicitly move annotation comments before INVERTNEXT, recording each edit")
    c.add_argument("--normalize-rotations", action="store_true", help="Project nearly rigid assembly matrices (error <=0.002) to proper rotations; record changes")
    c.add_argument("--force", action="store_true")
    c = commands.add_parser("matrix", help="Compute a right-handed rotation in LDraw coordinates")
    c.add_argument("axis", choices=["x", "y", "z"])
    c.add_argument("degrees", type=float)
    commands.add_parser("profiles", help="List curated ordinary brick/plate dimensions for on placement")
    c = commands.add_parser("build", help="Build a validated MPD from a JSON plan")
    c.add_argument("plan")
    c.add_argument("--output", required=True)
    c.add_argument("--report")
    c.add_argument("--force", action="store_true", help="Replace an existing MPD after successful validation")
    geometry_options(c)
    for command in ["validate", "inspect", "bom", "compare-bom", "snap", "connectors"]:
        c = commands.add_parser(command)
        c.add_argument("file")
        c.add_argument("--report")
        scope_options(c)
        if command in {"validate", "inspect"}:
            geometry_options(c)
        if command == "compare-bom":
            c.add_argument("--csv", required=True, help="LeoCAD-exported BOM")
        if command == "validate":
            c.add_argument("--profile", choices=["assembly", "syntax"], default="assembly")
            c.add_argument("--geometry", action="store_true")
            c.add_argument("--strict", action="store_true", help="Warnings also fail (does not extend check coverage)")
        if command == "snap":
            c.add_argument("--moving", type=int, required=True)
            c.add_argument("--fixed", type=int, help="Fixed leaf index; omitted searches other occurrences")
            c.add_argument("--limit", type=positive, default=5)
            c.add_argument("--moving-depth", type=int, help="Move this ancestor of the moving leaf: 0 is outermost placement; omitted moves the leaf")
            c.add_argument("--moving-feature", help="Stable connector ID from connectors")
            c.add_argument("--fixed-feature", help="Stable connector ID from connectors")
            c.add_argument("--max-candidates", type=positive, default=100)
            c.add_argument("--max-instances", type=positive, default=100000)
            c.add_argument("--allow-occupied", action="store_true", help="Allow deliberate reuse of occupied interfaces, e.g. sliding bars")
            c.add_argument("--output", help="Apply a candidate to a new MPD after validation")
            c.add_argument("--candidate", type=int, default=0, help="Zero-based candidate to apply")
            c.add_argument("--force", action="store_true")
        if command == "connectors":
            c.add_argument("--occurrence", type=int, required=True)
            c.add_argument("--limit", type=positive, default=50)
            c.add_argument("--offset", type=int, default=0)
            c.add_argument("--max-instances", type=positive, default=100000)
    c = commands.add_parser("cad-check", help="Run Python validation and a LeoCAD snapshot/BOM import check")
    c.add_argument("file")
    c.add_argument("--timeout", type=positive, default=90)
    scope_options(c)
    c = commands.add_parser("render", help="Render review views and export a LeoCAD BOM")
    c.add_argument("file")
    c.add_argument("--outdir", required=True)
    c.add_argument("--views", nargs="+", default=["home", "top", "front"])
    c.add_argument("--timeout", type=positive, default=90)
    scope_options(c)
    c = commands.add_parser("glb", help="Convert a local model or part with semantic descriptions")
    c.add_argument("file")
    c.add_argument("--output", required=True)
    c.add_argument("--timeout", type=positive, default=180)
    return p


def run(args):
    if args.command == "examples":
        from .examples import search_examples
        if args.details and args.scale:raise ValueError('--scale applies to building examples')
        return search_examples(args.query,limit=args.limit,scale=args.scale,details=args.details),0
    library = library_path(args.library)
    if args.command == "doctor":
        report = dict(python=sys.version.split()[0], packages={n: version(n) for n in ["pyldraw3", "numpy", "jsonschema"]},
                      library=str(library), library_present=(library / "parts").is_dir(),
                      models=str(models_path(args.models)), pdf=str(ROOT / "docs/ldraw-specs.pdf"),
                      shadow_sources=jsonable(shadow_paths([] if args.no_shadow else args.shadow)),
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
    parts = get_parts(library, refresh=args.command == "index", shadows=[] if args.no_shadow else args.shadow)
    if args.command == "part-board":
        from .boards import part_board
        return part_board(args.refs,parts,library,args.outdir,colour=args.colour,timeout=args.timeout), 0
    if args.command == "catalog":
        from .catalog import search_catalog
        return search_catalog(parts,args.kind,args.query,category=args.category,limit=args.limit,
                              include_unavailable=args.include_unavailable,max_size=args.max_size,measure=args.measure), 0
    if args.command == "design":
        from .details import RECIPES, detail_plan, palette_report
        if args.kind == 'palettes':
            if args.output:raise ValueError('--output is for detail plans')
            return palette_report(parts,args.name), 0
        if not args.name:
            if args.output:raise ValueError('Choose a detail name to export')
            return RECIPES, 0
        plan=detail_plan(args.name,args.palette)
        if args.output:
            if Path(args.output).exists() and not args.force:raise ValueError('Output exists; use --force')
            atomic_write(args.output,dumps(plan)+'\n')
        return dict(plan=plan,output=args.output,review='Build, inspect and render this detail before placing it; reserve its envelope at the interface.'), 0
    if args.command == "study":
        # An informational inventory is useful even when the reference has errors.
        report=study_model(args.file, parts, instance_limit=args.max_instances)
        report["detail"]=args.detail
        if args.detail=="summary":
            report.pop("bom")
            report["sections_truncated"]=len(report["sections"])>args.limit
            report["sections"]=[{k:v for k,v in s.items() if k in {"name","kind","direct_placements","physical_placements","scene_instances","reachable","steps"}}
                                for s in report["sections"][:args.limit]]
            report["diagnostics_truncated"]=len(report["diagnostics"])>args.limit
            report["diagnostics"]=report["diagnostics"][:args.limit]
        return report, 0
    if args.command == "extract":
        target = Path(args.output)
        manifest_path = target.with_suffix(".manifest.json")
        if target.suffix.casefold() != ".mpd":
            raise ValueError("Output must end in .mpd")
        if target.resolve() == Path(args.file).resolve():
            raise ValueError("Extraction must not overwrite the source")
        if (target.exists() or manifest_path.exists()) and not args.force:
            raise ValueError("Output/manifest exists; use --force")
        text, manifest = extract_section(args.file,args.section,namespace=args.namespace,
                                        repair_bfc=args.repair_bfc_comments, normalize_rotations=args.normalize_rotations)
        _, diagnostics = validate_text(text, parts, assembly=False)
        manifest.update(syntax_checks_passed=not any(d["severity"] == "error" for d in diagnostics), diagnostics=diagnostics)
        # Extraction intentionally retains invalid source for review; never claims a validated build.
        atomic_write(target,text)
        atomic_write(manifest_path,dumps(manifest)+"\n")
        return dict(output=str(target),manifest=str(manifest_path),root=manifest["root"],
                    written=True,checks_passed=manifest["syntax_checks_passed"],diagnostics=diagnostics,
                    changes=len(manifest["changes"])), 0 if manifest["syntax_checks_passed"] else 1
    if args.command == "render":
        from ldraw import inspect_model
        from ldraw.lines import Line, OptionalLine, Triangle, Quadrilateral
        model, diagnostics = validate_file(args.file, parts, assembly=False, section=args.section, colour=args.colour)
        bounds = None
        if model and not any(d["severity"] == "error" for d in diagnostics):
            model, render_parts = physical_context(model, parts)
            raw_geometry = any(isinstance(obj, (Line, OptionalLine, Triangle, Quadrilateral))
                               for m in [model, *model.submodels.values()] for obj in m.objects)
            if not raw_geometry:
                inspection = inspect_model(model, render_parts)
                if inspection.complete:
                    bounds = inspection.bounds
        with TemporaryDirectory(prefix="ldraw-section-") as tmp:
            source = args.file
            if args.section:
                text, _ = selected_source(args.file,args.section,args.colour)
                source = Path(tmp)/"section.mpd"
                atomic_write(source,text)
            report = render(source, library, args.outdir, views=args.views, timeout=args.timeout, bounds=bounds)
        report.update(source=args.file, section=args.section, source_diagnostics=diagnostics)
        return report, 0
    if args.command == "cad-check":
        model, diagnostics = validate_file(args.file, parts, assembly=Path(args.file).suffix.casefold() == ".mpd", section=args.section, colour=args.colour)
        if model and not any(d["severity"] == "error" for d in diagnostics):
            with TemporaryDirectory(prefix="ldraw-section-") as tmp:
                source = args.file
                if args.section:
                    text,_ = selected_source(args.file,args.section,args.colour)
                    source = Path(tmp)/"section.mpd"
                    atomic_write(source,text)
                report = cad_check(source, library, timeout=args.timeout)
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
        from .catalog import resolve_part
        code = (resolve_part(args.code,parts) if args.code.startswith('@') else args.code).casefold().removesuffix(".dat")
        part = parts.part(code=code)
        g = parts.geometry(code)
        return dict(code=code + ".dat", path=str(part.path.resolve()), metadata=jsonable(part.metadata),
                    complete=g.complete, bounds=jsonable(g.bounds), size=jsonable(g.bounds.size) if g.bounds else None,
                    stud_positions=[jsonable(s.position) for s in g.top_studs],
                    connector_count=len(g.connections), connectors=jsonable(g.connections[:args.limit]),
                    connectors_truncated=len(g.connections) > args.limit, diagnostics=jsonable(g.diagnostics),
                    connection_metadata=metadata_summary(g.connection_metadata),
                    rectangular_profile=profiles().get(code),
                    note="All coordinates are local LDU. Connector inference is evidence; inspect uncertain fits."), 0 if g.complete else 1
    if args.command == "build":
        target = Path(args.output)
        if target.suffix.casefold() != ".mpd":
            raise ValueError("Output must end in .mpd")
        if target.exists() and not args.force:
            raise ValueError("Output exists; use --force to replace after successful validation")
        plan = load_plan(args.plan)
        text, model, diagnostics = build_plan(plan, parts, instance_limit=args.max_instances)
        geometry = None
        if not any(d["severity"] == "error" for d in diagnostics):
            geometry = geometry_report(model, parts, args)
            diagnostics += geometry["diagnostics"]
        passed = not any(d["severity"] == "error" for d in diagnostics)
        report = dict(profile="assembly", checks_passed=passed, physical_validity="not_proven", output=str(target),
                      written=passed, diagnostics=diagnostics, geometry=geometry)
        if passed:
            atomic_write(target, text)
        return report, 0 if passed else 1
    assembly = args.command == "validate" and args.profile == "assembly"
    model, diagnostics = validate_file(args.file, parts, assembly=assembly, section=args.section, colour=args.colour,
                                       instance_limit=getattr(args,"max_instances",100000))
    report = dict(file=args.file, section=args.section, profile="assembly" if assembly else "syntax", checks_passed=False,
                  physical_validity="not_proven", diagnostics=diagnostics)
    if model and not any(d["severity"] == "error" for d in diagnostics):
        if args.command == "bom":
            model, parts = physical_context(model, parts)
            report["bom"] = jsonable(model.bill_of_materials(parts=parts))
            report["physical_placements"] = sum(row["quantity"] for row in report["bom"])
        elif args.command == "compare-bom":
            report["comparison"] = compare_bom(model,parts,args.csv)
            report["checks_passed"] = report["comparison"]["matches"]
            return report, 0 if report["checks_passed"] else 1
        elif args.command == "snap":
            result = snap_report(model, parts, args.moving, args.fixed, limit=args.limit,
                moving_depth=args.moving_depth, moving_feature=args.moving_feature, fixed_feature=args.fixed_feature,
                max_candidates=args.max_candidates, instance_limit=args.max_instances, allow_occupied=args.allow_occupied)
            report.update(result)
            if args.output:
                from .builder import serialize_mpd
                target = Path(args.output)
                if target.resolve() == Path(args.file).resolve():
                    raise ValueError('Snap output must differ from the source file')
                if target.suffix.casefold() != '.mpd':
                    raise ValueError('Snap output must end in .mpd')
                if target.exists() and not args.force:
                    raise ValueError('Output exists; use --force')
                updated = apply_snap(model, result, args.candidate)
                text = serialize_mpd(updated)
                parsed, checked = validate_text(text, parts, assembly=True, instance_limit=args.max_instances)
                diagnostics.extend(checked)
                if not any(d['severity']=='error' for d in diagnostics):
                    geometry = analyze_geometry(parsed, parts, detail='summary', instance_limit=args.max_instances)
                    report['geometry'] = geometry
                    diagnostics.extend(geometry['diagnostics'])
                report.update(output=str(target), written=not any(d['severity']=='error' for d in diagnostics))
                if report['written']:
                    atomic_write(target, text)
            elif not result['candidates']:
                report.update(checks_passed=False, reason='No eligible verified snap candidates; inspect connector coverage, occupancy, and search limits')
                return report, 1
        elif args.command == "connectors":
            report['connections'] = connection_report(model, parts, args.occurrence, limit=args.limit,
                offset=args.offset, instance_limit=args.max_instances)
            if not report['connections']['complete']:
                report.update(checks_passed=False)
                return report, 1
        elif args.command == "inspect" or (args.command == "validate" and args.geometry):
            report["geometry"] = geometry_report(model, parts, args)
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
