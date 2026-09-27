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
from .common import ROOT, DATA, atomic_write, database_path, dumps, get_parts, jsonable, library_path, models_path, shadow_paths
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
    p.add_argument("--library", help="LDraw parts library root (default LDRAW_DIR, then LDRAWDIR)")
    shadows = p.add_mutually_exclusive_group()
    shadows.add_argument("--shadow", action="append", help="LDCad directory/zip/csl; repeatable, replaces LDRAW_SHADOW or ./data/offLibShadow")
    shadows.add_argument("--no-shadow", action="store_true", help="Disable external shadow metadata")
    commands = p.add_subparsers(dest="command", required=True)
    c = commands.add_parser("examples", help="Find generated building, vehicle or detail examples")
    c.add_argument("query", nargs="?", default="")
    c.add_argument("--limit", type=positive, default=5)
    c.add_argument("--scale", choices=["minifigure", "microscale"])
    c.add_argument("--details", action="store_true")
    c.add_argument("--family", choices=["building", "vehicle", "reference", "technic", "mechanism", "spaceship"], default="building")
    c = commands.add_parser("discover", help="Find, measure and visually review parts, source models and submodels")
    discovery = c.add_subparsers(dest="discovery_command", required=True)
    d = discovery.add_parser("index", help="Build a local typed index from the three Jev fields and actual source headers")
    d.add_argument("--refresh", action="store_true")
    d = discovery.add_parser("search", help="Rank eligible references, inspect contents and diversify the shortlist")
    d.add_argument("kind", choices=["parts", "models", "submodels"])
    d.add_argument("query")
    d.add_argument("--engine", choices=["jev", "fts"], default="jev")
    d.add_argument("--limit", type=positive, default=10)
    d.add_argument("--pool", type=positive, default=60)
    d.add_argument("--candidates", type=int, default=500, help="Jev candidate budget; 0 scores all eligible records")
    d.add_argument("--all-families", action="store_true", help="Include Technic and other product families")
    d.add_argument("--construction", choices=['system', 'all', 'technic-structure', 'mechanism'],
                   help="Construction scope; Technic structure filters the selected section and its BOM")
    d.add_argument("--min-parts", type=int, default=2)
    d.add_argument("--max-parts", type=positive)
    d.add_argument("--max-technic-share", type=float, default=0.5)
    d.add_argument("--parent-cap", type=positive, default=2)
    d.add_argument("--yes")
    d.add_argument("--no")
    d.add_argument("--report")
    d = discovery.add_parser("show", help="Resolve a stable identity and inspect its dependencies and BOM")
    d.add_argument("id")
    d = discovery.add_parser("recipe", help="List or export selected parameterized construction recipes")
    d.add_argument("name", nargs='?')
    d.add_argument("--height", type=int)
    d.add_argument("--colour", type=int)
    d.add_argument("--accent", type=int)
    d.add_argument("--output")
    d.add_argument("--force", action="store_true")
    d = discovery.add_parser("parts", help="Suggest actual parts from the constructions in a saved search report")
    d.add_argument("results")
    d.add_argument("--limit", type=positive, default=20)
    d = discovery.add_parser("prepare", help="Extract, measure and render one reference card")
    d.add_argument("id")
    d.add_argument("--outdir", required=True)
    d.add_argument("--views", nargs='+', default=["home","front","right","top"])
    d.add_argument("--colour", type=int, default=7)
    d.add_argument("--contacts", choices=["none","auto","all"], default="none")
    d.add_argument("--refresh", action="store_true")
    d = discovery.add_parser("catalog", help="Build a resumable visual catalog from a manifest or saved search")
    d.add_argument("manifest")
    d.add_argument("--outdir", required=True)
    d.add_argument("--views", nargs='+', default=["home","front","right","top"])
    d.add_argument("--contacts", choices=["none","auto","all"], default="none")
    d.add_argument("--refresh", action="store_true")
    d.add_argument("--jobs", type=int, choices=[1,2,3,4], default=1, help="Independent renderer processes; each owns separate CAD and geometry state")
    d = discovery.add_parser("review", help="Record the agent's visual review after opening the rendered images")
    d.add_argument("id")
    d.add_argument("--catalog", required=True)
    d.add_argument("--decision", choices=["reuse","adapt","technique","reject"], required=True)
    d.add_argument("--note", required=True)
    d.add_argument("--viewed-views", nargs='+', required=True, help="Only the rendered views you actually opened and inspected")
    d = discovery.add_parser("example", help="Export a reviewed reference as an editable example with a placement guide")
    d.add_argument("id")
    d.add_argument("--catalog", required=True)
    d.add_argument("--output", required=True)
    d.add_argument("--title", required=True)
    d.add_argument("--lesson", required=True)
    d.add_argument("--placement-notes", required=True)
    d.add_argument("--scale", choices=["minifigure","microscale","display","unknown"], default="unknown")
    d.add_argument("--force", action="store_true")
    c = commands.add_parser('spaceship', help='Advanced spacecraft design briefs and reusable source constructions')
    ships = c.add_subparsers(dest='spaceship_command', required=True)
    ships.add_parser('list', help='List whole-ship construction and inspiration studies')
    ships.add_parser('details', help='List reusable cockpit, wing, engine and hull studies')
    d = ships.add_parser('brief', help='Start a spaceship design brief with module and visual-review guidance')
    d.add_argument('archetype', choices=['starfighter','freighter','capital-ship'])
    d.add_argument('--output')
    d.add_argument('--force', action='store_true')
    d = ships.add_parser('export', help='Export a reviewed spaceship construction with source and placement plan')
    d.add_argument('name')
    d.add_argument('--outdir', required=True)
    d.add_argument('--force', action='store_true')
    c = commands.add_parser('manual', help='Study any source submodel through build pages and export it for an atlas')
    m = c.add_subparsers(dest='manual_command', required=True)
    d = m.add_parser('prepare', help='Extract a source assembly and make attributed step manuals')
    d.add_argument('file')
    d.add_argument('--section', required=True)
    d.add_argument('--outdir', required=True)
    d.add_argument('--title')
    d.add_argument('--notes', help='JSON study notes: lesson, construction, interfaces, parent_context, reuse_notes')
    d.add_argument('--views', nargs='+', default=['home','back'])
    d.add_argument('--colour', type=int, default=7)
    d.add_argument('--no-render', action='store_true')
    d.add_argument('--overview', action='store_true', help='Render completed-model views; keep source step data for selecting smaller studies')
    d.add_argument('--normalize-rotations', action='store_true')
    d.add_argument('--repair-bfc-comments', action='store_true')
    d.add_argument('--force', action='store_true')
    d.add_argument('--max-instances', type=positive, default=2000)
    d = m.add_parser('review', help='Record the build pages and final preview actually opened')
    d.add_argument('directory')
    d.add_argument('--images', nargs='+', required=True)
    d.add_argument('--note', required=True)
    d = m.add_parser('export', help='Copy a visually reviewed study and placement plan for adaptation')
    d.add_argument('reference', help='Prepared study directory')
    d.add_argument('--outdir', required=True)
    d.add_argument('--force', action='store_true')
    c = commands.add_parser('mechanism', help='Study and reuse mechanisms from source and build pages; no motion analysis')
    m = c.add_subparsers(dest='mechanism_command', required=True)
    m.add_parser('list', help='List the curated mechanism studies')
    d = m.add_parser('prepare', help='Extract a source assembly and make attributed step manuals')
    d.add_argument('file')
    d.add_argument('--section', required=True)
    d.add_argument('--outdir', required=True)
    d.add_argument('--title')
    d.add_argument('--operation', help='JSON notes: function, fixed, moving, input, output, parent_context, reuse_notes')
    d.add_argument('--views', nargs='+', default=['home','back'])
    d.add_argument('--colour', type=int, default=7)
    d.add_argument('--no-render', action='store_true')
    d.add_argument('--normalize-rotations', action='store_true')
    d.add_argument('--repair-bfc-comments', action='store_true')
    d.add_argument('--force', action='store_true')
    d.add_argument('--max-instances', type=positive, default=2000)
    d = m.add_parser('review', help='Record the build pages and final preview actually opened')
    d.add_argument('directory')
    d.add_argument('--images', nargs='+', required=True)
    d.add_argument('--note', required=True)
    d = m.add_parser('export', help='Copy a visually reviewed study and placement plan for adaptation')
    d.add_argument('reference', help='Curated mechanism key or prepared study directory')
    d.add_argument('--outdir', required=True)
    d.add_argument('--force', action='store_true')
    c = commands.add_parser('technic', help='Reviewed structural parts, plans and joint/brace checks for fixed structures')
    t = c.add_subparsers(dest='technic_command', required=True)
    t.add_parser('list', help='List editable structural recipes')
    d = t.add_parser('parts', help='Inspect reviewed nominal ports and geometry fingerprints')
    d.add_argument('code', nargs='?')
    d = t.add_parser('plan', help='Export a structural plan and required-joint contract')
    d.add_argument('name')
    d.add_argument('--levels', type=positive, default=2)
    d.add_argument('--colour', type=int, default=71)
    d.add_argument('--accent', type=int, default=14)
    d.add_argument('--output', required=True)
    d.add_argument('--force', action='store_true')
    d = t.add_parser('check', help='Review seated joints, restraints, required mounts and assembly order')
    d.add_argument('file')
    d.add_argument('--contract')
    d.add_argument('--report')
    d.add_argument('--max-instances', type=positive, default=500)
    scope_options(d)
    c = commands.add_parser("vehicle", help="System road, motorcycle, boat and aircraft designs, dedicated fittings and review")
    vehicle_commands = c.add_subparsers(dest="vehicle_command", required=True)
    vehicle_commands.add_parser("list", help="List editable vehicle starting points")
    v = vehicle_commands.add_parser("wheels", help="Inspect measured, matched wheel packs")
    v.add_argument("name", nargs="?")
    v = vehicle_commands.add_parser("details", help="List or export dedicated vehicle fitting recipes")
    v.add_argument("name", nargs="?")
    v.add_argument("--palette", default="heritage-racing")
    v.add_argument("--output", help="Write an editable detail JSON plan")
    v.add_argument("--force", action="store_true")
    v = vehicle_commands.add_parser("plan", help="Export an editable vehicle plan and its design brief")
    v.add_argument("name")
    v.add_argument("--palette", help="Vehicle palette (default depends on design)")
    v.add_argument("--output", required=True)
    v.add_argument("--force", action="store_true")
    v = vehicle_commands.add_parser("check", help="Review supported vehicle interfaces in a selected family profile")
    v.add_argument("file")
    v.add_argument("--profile", choices=["road", "motorcycle", "watercraft", "aircraft"], default="road")
    v.add_argument("--ground-y", type=float, default=0)
    v.add_argument("--report")
    v.add_argument("--limit", type=positive, default=100)
    v.add_argument("--max-instances", type=positive, default=100000)
    scope_options(v)
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
    c.add_argument("--offset", type=int, default=0, help="Model/submodel FTS page offset")
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
        return search_examples(args.query,limit=args.limit,scale=args.scale,details=args.details,family=args.family),0
    if args.command == "doctor":
        library = library_path(args.library)
        report = dict(python=sys.version.split()[0], packages={n: version(n) for n in ["pyldraw3", "numpy", "jsonschema"]},
                      library=str(library), library_present=(library / "parts").is_dir(),
                      models=str(models_path()), database=str(database_path()), pdf=str(ROOT / "docs/ldraw-specs.pdf"),
                      shadow_sources=jsonable(shadow_paths([] if args.no_shadow else args.shadow)),
                      tools={t: shutil.which(t) for t in ["pdftotext", "leocad", "jev-rerank", "mpd2glb.sh", "ldraw-render-steps.sh"]})
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
        return search_models(args.query, limit=args.limit, submodels=args.kind == "submodels", offset=args.offset), 0
    library = library_path(args.library)
    parts = get_parts(library, refresh=args.command == "index", shadows=[] if args.no_shadow else args.shadow)
    if args.command == 'spaceship':
        from .spaceships import design_brief, export_spaceship
        if args.spaceship_command in {'list','details'}:
            from .examples import search_examples
            return search_examples(family='spaceship', details=args.spaceship_command == 'details', limit=100), 0
        if args.spaceship_command == 'brief':
            brief = design_brief(args.archetype)
            if args.output:
                target = Path(args.output)
                if target.exists() and not args.force:
                    raise ValueError('Output exists; use --force')
                atomic_write(target, dumps(brief)+'\n')
            return brief, 0
        return export_spaceship(args.name, args.outdir, force=args.force), 0
    if args.command == 'manual':
        from .manuals import prepare_manual, review_manual, export_manual
        if args.manual_command == 'prepare':
            notes = json.loads(Path(args.notes).read_text()) if args.notes else None
            report = prepare_manual(args.file, args.section, args.outdir, parts, title=args.title,
                views=args.views, colour=args.colour, notes=notes, renders=not args.no_render,
                normalize_rotations=args.normalize_rotations, repair_bfc=args.repair_bfc_comments,
                force=args.force, max_instances=args.max_instances, kind='construction', overview=args.overview)
            return report, 0 if report['source_checks_passed'] and report['bom_matches'] is not False else 1
        if args.manual_command == 'review':
            return review_manual(args.directory, images=args.images, note=args.note), 0
        return export_manual(args.reference, args.outdir, force=args.force), 0
    if args.command == 'mechanism':
        from .manuals import prepare_manual, review_manual, export_manual
        if args.mechanism_command == 'list':
            from .examples import search_examples
            return search_examples(family='mechanism', limit=100), 0
        if args.mechanism_command == 'prepare':
            notes = json.loads(Path(args.operation).read_text()) if args.operation else None
            report = prepare_manual(args.file, args.section, args.outdir, parts, title=args.title,
                views=args.views, colour=args.colour, notes=notes, renders=not args.no_render,
                normalize_rotations=args.normalize_rotations, repair_bfc=args.repair_bfc_comments,
                force=args.force, max_instances=args.max_instances)
            return report, 0 if report['source_checks_passed'] and report['bom_matches'] is not False else 1
        if args.mechanism_command == 'review':
            return review_manual(args.directory, images=args.images, note=args.note), 0
        reference = Path(args.reference)
        if not reference.is_dir():
            from .discovery import confined
            reference = confined(ROOT/'examples/mechanism-atlas', args.reference)
        return export_manual(reference, args.outdir, force=args.force), 0
    if args.command == "discover":
        from .discovery import DiscoveryIndex, search, part_suggestions
        from .reference_catalog import prepare_reference, build_catalog, export_example, record_review
        index = DiscoveryIndex(parts)
        command = args.discovery_command
        if command == 'recipe':
            from .reference_recipes import RECIPES,recipe_plan
            if args.name is None:
                if args.output:raise ValueError('Choose a recipe name to export')
                return RECIPES,0
            plan=recipe_plan(args.name,height=args.height,colour=args.colour,accent=args.accent)
            _,_,diagnostics=build_plan(plan,parts)
            if any(d['severity']=='error' for d in diagnostics):return dict(written=False,diagnostics=diagnostics),1
            if args.output:
                target=Path(args.output)
                if target.exists() and not args.force:raise ValueError('Output exists; use --force')
                atomic_write(target,dumps(plan)+'\n')
            return dict(plan=plan,output=args.output,recipe=RECIPES[args.name],next='Build, inspect connections, render and review the adapted module.'),0
        if command == 'index':
            return index.ensure(force=args.refresh),0
        if command == 'parts':
            return part_suggestions(json.loads(Path(args.results).read_text())['results'],limit=args.limit),0
        if command == 'search':
            if args.all_families and args.construction not in {None, 'all'}:
                raise ValueError('Choose --construction or --all-families, not conflicting scopes')
            return search(index,args.kind,args.query,engine=args.engine,limit=args.limit,pool=args.pool,candidates=args.candidates,
                          system=not args.all_families,construction=args.construction,min_parts=args.min_parts,max_parts=args.max_parts,
                          max_technic_share=args.max_technic_share,parent_cap=args.parent_cap,yes=args.yes,no=args.no),0
        index.ensure()
        if command == 'show':
            row=index.get(args.id)
            return dict(row,inventory=index.inventory(row)),0
        if command == 'prepare':
            return prepare_reference(index,index.get(args.id),args.outdir,views=args.views,colour=args.colour,contacts=args.contacts,refresh=args.refresh),0
        if command == 'catalog':
            manifest=json.loads(Path(args.manifest).read_text())
            if 'references' not in manifest and 'results' in manifest:
                manifest=dict(title=manifest.get('query','Discovery shortlist'),references=[dict(id=r['id'],role=manifest.get('query','reference')) for r in manifest['results']])
            report=build_catalog(index,manifest,args.outdir,views=args.views,contacts=args.contacts,refresh=args.refresh,
                                 jobs=args.jobs,
                                 progress=lambda value:print(json.dumps(value),file=sys.stderr,flush=True))
            return report,1 if report['failures'] else 0
        if command == 'review':
            return record_review(index,args.id,args.catalog,decision=args.decision,note=args.note,viewed_views=args.viewed_views),0
        if command == 'example':
            return export_example(index,args.id,args.catalog,args.output,title=args.title,lesson=args.lesson,
                                  placement_notes=args.placement_notes,scale=args.scale,force=args.force),0
    if args.command == 'technic':
        from .technic import parts_report
        from .technic_recipes import RECIPES, structure_plan
        from .technic_review import review_structure
        if args.technic_command == 'list':
            return RECIPES, 0
        if args.technic_command == 'parts':
            report = parts_report(parts, args.code)
            return report, 0 if all(p['geometry_matches'] for p in report['parts']) else 1
        if args.technic_command == 'plan':
            target = Path(args.output)
            contract_path = target.with_suffix('.structure.json')
            if not args.force and (target.exists() or contract_path.exists()):
                raise ValueError('Output or structure contract exists; use --force')
            plan, contract = structure_plan(args.name, levels=args.levels, colour=args.colour, accent=args.accent)
            _, model, diagnostics = build_plan(plan, parts)
            review = review_structure(model, parts, contract=contract)
            diagnostics.extend(analyze_geometry(model, parts, detail='summary')['diagnostics'])
            if any(d['severity']=='error' for d in diagnostics) or not review['checks_passed']:
                return dict(written=False, diagnostics=diagnostics, structure=review), 1
            import hashlib
            contract['model_sha256'] = hashlib.sha256(model.to_ldraw().encode()).hexdigest()
            atomic_write(target, dumps(plan)+'\n')
            atomic_write(contract_path, dumps(contract)+'\n')
            return dict(plan=str(target), contract=str(contract_path), scope='technic-structure',
                        next='Build, validate, technic check with the contract, render and review insertion access.'), 0
        source, _ = selected_source(args.file, args.section, args.colour)
        model, diagnostics = validate_text(source, parts, assembly=True, instance_limit=args.max_instances)
        contract = json.loads(Path(args.contract).read_text()) if args.contract else None
        review = review_structure(model, parts, contract=contract, instance_limit=args.max_instances)
        review['source_diagnostics'] = diagnostics
        review['checks_passed'] &= not any(d['severity']=='error' for d in diagnostics)
        if args.report:
            atomic_write(Path(args.report), dumps(review)+'\n')
        return review, 0 if review['checks_passed'] else 1
    if args.command == "vehicle":
        from .vehicles import DESIGNS, vehicle_plan, wheel_report, design_brief
        if args.vehicle_command == "list":
            return DESIGNS, 0
        if args.vehicle_command == "wheels":
            return wheel_report(parts, args.name), 0
        if args.vehicle_command == "details":
            from .vehicle_details import DETAILS, detail_plan
            if not args.name:
                if args.output:raise ValueError('Choose a vehicle detail name to export')
                return DETAILS, 0
            plan = detail_plan(args.name, args.palette)
            _, _, diagnostics = build_plan(plan, parts)
            if any(d['severity']=='error' for d in diagnostics):
                return dict(checks_passed=False, written=False, diagnostics=diagnostics), 1
            if args.output:
                target = Path(args.output)
                if target.suffix.casefold() != '.json':raise ValueError('Plan output must end in .json')
                if target.exists() and not args.force:raise ValueError('Detail plan exists; use --force')
                atomic_write(target, dumps(plan)+'\n')
            return dict(recipe=DETAILS[args.name], plan=plan, output=args.output, diagnostics=diagnostics), 0
        if args.vehicle_command == "plan":
            target = Path(args.output)
            if target.suffix.casefold() != '.json':
                raise ValueError('Plan output must end in .json')
            brief = target.with_name(target.stem+'.brief.json')
            if not args.force and (target.exists() or brief.exists()):
                raise ValueError('Plan/brief exists; use --force')
            plan = vehicle_plan(args.name, args.palette)
            # Resolve and validate before exporting; standard build still does
            # the full geometry/contact pass on the saved editable plan.
            _, _, diagnostics = build_plan(plan, parts)
            if any(d['severity']=='error' for d in diagnostics):
                return dict(checks_passed=False, written=False, diagnostics=diagnostics), 1
            atomic_write(target, dumps(plan)+'\n')
            atomic_write(brief, dumps(design_brief(args.name, args.palette))+'\n')
            return dict(plan=str(target), brief=str(brief), diagnostics=diagnostics,
                        next='Build, validate, vehicle check, render and open all review views.'), 0
        from .vehicle_review import review_vehicle
        model, diagnostics = validate_file(args.file, parts, assembly=True, section=args.section,
                                           colour=args.colour, instance_limit=args.max_instances)
        if model is None or any(d['severity']=='error' for d in diagnostics):
            return dict(checks_passed=False, diagnostics=diagnostics), 1
        report = review_vehicle(model, parts, profile=args.profile, ground_y=args.ground_y, limit=args.limit,
                                instance_limit=args.max_instances)
        report['diagnostics'] = diagnostics+report['diagnostics']
        report.update(file=args.file, section=args.section)
        return report, 0 if report['checks_passed'] else 1
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
