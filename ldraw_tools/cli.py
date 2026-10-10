from __future__ import annotations

import argparse
import shutil
import sqlite3
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path
from tempfile import TemporaryDirectory

from ldraw.errors import PartError

from .common import ROOT, atomic_write, database_path, dumps, get_parts, jsonable, library_path, models_path, shadow_paths
from .document import extract_section, physical_context, selected_source
from .external import prepare_glb, render
from .resources import model_sections, search_models, search_spec
from .validation import validate_file, validate_text

FAMILIES = ["spaceship", "building", "car", "aircraft", "boat", "technic"]


def positive(value):
    value = int(value)
    if value <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return value


def scope_options(c):
    c.add_argument("--section", help="Inspect only this FILE block and its dependency closure; indices become section-local")
    c.add_argument("--colour", type=int, help="Explicit inherited colour for a selected subassembly")


def parser():
    p = argparse.ArgumentParser(
        description="Check, look at and deliver LDraw models built with the Python kit (docs/agent/kit.md) "
                    "from the recipes (docs/reference/README.md). Find parts with search, catalog and ports.")
    p.add_argument("--library", help="LDraw parts library root (default LDRAW_DIR, then LDRAWDIR)")
    shadows = p.add_mutually_exclusive_group()
    shadows.add_argument("--shadow", action="append", help="LDCad directory/zip/csl; repeatable, replaces LDRAW_SHADOW or ./data/offLibShadow")
    shadows.add_argument("--no-shadow", action="store_true", help="Disable external shadow metadata")
    commands = p.add_subparsers(dest="command", required=True)

    c = commands.add_parser("check", help="Fast verdict: floating parts, collisions, stud seating, named by plan id (text; --json for data)")
    c.add_argument("file")
    c.add_argument("--json", action="store_true", help="Print the full JSON report instead of the text summary")
    c.add_argument("--graph", action="store_true", help="Also print the actual module-connection graph (Mermaid)")
    c.add_argument("--intended", help="Markdown/text with a Mermaid flowchart of the intended module connections to compare")
    c.add_argument("--tolerance", type=float, default=0.5, help="Collision and seating tolerance in LDU")
    c.add_argument("--limit", type=positive, default=12, help="Rows per issue list")
    c.add_argument("--report", help="Also write the full JSON report here")
    c.add_argument("--family", choices=FAMILIES,
                   help="Also compare how the model is built with official models of this family (advice, not a failure)")
    scope_options(c)
    c = commands.add_parser("look", help="One labelled contact sheet of several views (parallel renders); prints its path")
    c.add_argument("file")
    c.add_argument("--outdir", help="Default: a look/ folder beside the model")
    c.add_argument("--views", nargs="+", default=["home", "front", "right", "top"])
    c.add_argument("--focus", help="Close-up around this plan id")
    c.add_argument("--highlight", nargs="+", default=[], help="Recolour these plan ids magenta")
    c.add_argument("--problems", action="store_true", help="Run check; floating parts magenta, colliding parts red")
    c.add_argument("--cell", type=positive, default=640, help="Pixel size of each view")
    scope_options(c)
    c = commands.add_parser("deliver", help="Final revision in one call: check, 7-view sheet, BOM comparison, GLB, summary.md")
    c.add_argument("file")
    c.add_argument("--outdir", help="Default: a delivery/ folder beside the model")
    c.add_argument("--no-glb", action="store_true")
    c.add_argument("--family", choices=FAMILIES,
                   help="Also compare how the model is built with official models of this family (advice, not a failure)")
    c = commands.add_parser("ports", help="Named connection ports, body box and description of parts (for kit mate/place)")
    c.add_argument("refs", nargs="+")
    c.add_argument("--json", action="store_true")
    c = commands.add_parser("search", help="Search library parts (several quoted queries at once) or official models")
    c.add_argument("kind", choices=["parts", "models", "submodels"])
    c.add_argument("query", nargs="+", help='One query per argument: search parts "technic beam 7" "axle joiner"')
    c.add_argument("--limit", type=positive, default=10)
    c.add_argument("--offset", type=int, default=0, help="Model/submodel page offset")
    c = commands.add_parser("catalog", help="Browse parts and colours by category (catalog categories, catalog parts QUERY --category C)")
    c.add_argument("kind", choices=["categories", "parts", "colours"])
    c.add_argument("query", nargs="?", default="")
    c.add_argument("--category")
    c.add_argument("--limit", type=positive, default=12)
    c.add_argument("--max-size", type=float, nargs=3, metavar=("X", "Y", "Z"), help="Maximum cached full bounds in LDU; not stacking dimensions")
    c.add_argument("--include-unavailable", action="store_true", help="Include missing, alias and internal entries with status flags")
    c.add_argument("--measure", action="store_true", help="Measure selected part results and flag differences from cached dimensions")
    c = commands.add_parser("colours", help="Look up colour codes and names in the installed LDConfig.ldr")
    c.add_argument("query", nargs="?", default="")
    c = commands.add_parser("sections", help="List the FILE sections of an official model, with source line numbers")
    c.add_argument("file")
    c.add_argument("--section")
    c = commands.add_parser("extract", help="Copy one dependency-closed section of a model with namespacing and attribution")
    c.add_argument("file")
    c.add_argument("--section", required=True)
    c.add_argument("--namespace", required=True)
    c.add_argument("--output", required=True)
    c.add_argument("--repair-bfc-comments", action="store_true", help="Explicitly move annotation comments before INVERTNEXT, recording each edit")
    c.add_argument("--normalize-rotations", action="store_true", help="Project nearly rigid assembly matrices (error <=0.002) to proper rotations; record changes")
    c.add_argument("--force", action="store_true")
    c = commands.add_parser("spec", help="Search the LDraw specification PDF or retrieve a 1-based page")
    c.add_argument("query", nargs="?")
    c.add_argument("--page", type=positive)
    c.add_argument("--limit", type=positive, default=8)
    commands.add_parser("doctor", help="Show dependencies, source paths and where output/ goes")
    commands.add_parser("index", help="Refresh the local parts index; the library itself is unchanged")
    c = commands.add_parser("render", help="Render chosen views and export a LeoCAD BOM (look and deliver do this for you)")
    c.add_argument("file")
    c.add_argument("--outdir", required=True)
    c.add_argument("--views", nargs="+", default=["home", "top", "front"])
    c.add_argument("--timeout", type=positive, default=90)
    scope_options(c)
    c = commands.add_parser("glb", help="Convert a model or part to GLB (deliver does this for you)")
    c.add_argument("file")
    c.add_argument("--output", required=True)
    c.add_argument("--timeout", type=positive, default=180)
    return p


def doctor(args):
    library = library_path(args.library)
    output = Path("output")
    report = dict(python=sys.version.split()[0], packages={n: version(n) for n in ["pyldraw3", "numpy"]},
                  library=str(library), library_present=(library / "parts").is_dir(),
                  models=str(models_path()), database=str(database_path()), pdf=str(ROOT / "docs/ldraw-specs.pdf"),
                  shadow_sources=jsonable(shadow_paths([] if args.no_shadow else args.shadow)),
                  working_directory=str(Path.cwd()),
                  output=str(output.resolve()) if output.exists() else "missing: create output/ in this directory",
                  tools={t: shutil.which(t) for t in ["pdftotext", "leocad", "mpd2glb.sh"]},
                  note="Run every command from this working directory; output/ paths are relative to it. "
                       "Part search is offline: search parts, catalog parts, ports.")
    return report, 0 if report["library_present"] and report["tools"]["pdftotext"] else 2


def ports(args, parts, library):
    from .catalog import resolve_part
    from .kit import stacking_bottom
    from .partcache import PartCache
    cache = PartCache(parts, library)
    names = {(1, 0, 0): "+X", (-1, 0, 0): "-X", (0, 1, 0): "+Y (down)", (0, -1, 0): "-Y (up)", (0, 0, 1): "+Z", (0, 0, -1): "-Z"}
    tables, blocks = [], []
    for ref in args.refs:
        code = (resolve_part(ref, parts) if ref.startswith("@") else ref).casefold().removesuffix(".dat")
        if parts.find_part(code=code) is None:
            raise ValueError(f"Unknown part {ref}; search with ./ldraw-agent search parts 'words'")
        data = cache.get(code)
        tables.append(dict(part=code, description=data.description, coverage=data.coverage, ports=data.ports,
                           body=dict(lo=data.lo.tolist(), hi=data.hi.tolist())))
        lines = [f"{code}  {data.description}  (port data: {data.coverage})",
                 f"  body x {data.lo[0]:g}..{data.hi[0]:g}  y {data.lo[1]:g}..{data.hi[1]:g}  z {data.lo[2]:g}..{data.hi[2]:g}"
                 f"  (stacks on local y={stacking_bottom(data):g}; kit place() puts that plane at y=-8*level)",
                 f"  {'port':18} {'kind':16} {'g':2} {'centre (local)':22} {'axis':10} {'length':>6}  sections"]
        for p in data.ports:
            axis = names.get(tuple(int(round(v)) for v in p["axis"]) if all(abs(abs(v) - round(abs(v))) < 1e-6 for v in p["axis"]) else None,
                             str([round(v, 3) for v in p["axis"]]))
            centre = "(" + ", ".join(f"{v:g}" for v in p["p"]) + ")"
            sections = " ".join(f"{s}{r:g}" for s, r in p["secs"])
            lines.append(f"  {p['name']:18} {p['kind']:16} {p['gender']:2} {centre:22} {axis:10} {2 * p['half']:>6g}  {sections}")
        if not data.ports:
            lines.append("  (no connection data: place it explicitly and inspect the result)")
        blocks.append("\n".join(lines))
    if args.json:
        return dict(parts=tables), 0
    return "\n\n".join(blocks) + "\n\nsections: R round, A axle, S square, F hinge fingers, N wheel rim/tyre, G generic; g: M male, F female, N neutral", 0


def check(args, parts, library):
    from .check import check_model, compare_intended, format_report, mermaid_graph
    report = check_model(args.file, parts, library, section=args.section, colour=args.colour,
                         tolerance=args.tolerance, limit=args.limit, family=args.family)
    if args.intended and "parts" in report:
        report["intended"] = compare_intended(report, Path(args.intended).read_text())
        report["checks_passed"] &= not report["intended"]["missing"]
    if args.report:
        atomic_write(Path(args.report), dumps(report) + "\n")
        args.report = None   # main() must not overwrite the JSON with the text summary
    status = 0 if report["checks_passed"] else 1
    if args.json:
        return report, status
    text = format_report(report, limit=args.limit)
    if "intended" in report:
        missing = report["intended"]["missing"]
        text += "\n  intended connections: " + ("all present" if not missing else
                 "MISSING " + ", ".join(f"{a} -- {b}" for a, b in missing))
        if report["intended"]["unknown_modules"]:
            text += "\n  intended graph names unknown modules: " + ", ".join(report["intended"]["unknown_modules"])
    if args.graph and "parts" in report:
        text += "\n\n```mermaid\n" + mermaid_graph(report) + "\n```"
    return text, status


def extract(args, parts):
    target = Path(args.output)
    manifest_path = target.with_suffix(".manifest.json")
    if target.suffix.casefold() != ".mpd":
        raise ValueError("Output must end in .mpd")
    if target.resolve() == Path(args.file).resolve():
        raise ValueError("Extraction must not overwrite the source")
    if (target.exists() or manifest_path.exists()) and not args.force:
        raise ValueError("Output/manifest exists; use --force")
    text, manifest = extract_section(args.file, args.section, namespace=args.namespace,
                                     repair_bfc=args.repair_bfc_comments, normalize_rotations=args.normalize_rotations)
    _, diagnostics = validate_text(text, parts, assembly=False)
    manifest.update(syntax_checks_passed=not any(d["severity"] == "error" for d in diagnostics), diagnostics=diagnostics)
    # Extraction intentionally retains invalid source for review; never claims a validated build.
    atomic_write(target, text)
    atomic_write(manifest_path, dumps(manifest) + "\n")
    return dict(output=str(target), manifest=str(manifest_path), root=manifest["root"],
                written=True, checks_passed=manifest["syntax_checks_passed"], diagnostics=diagnostics,
                changes=len(manifest["changes"]),
                next="Run check on the output; to build on it with the kit, see docs/agent/reference-discovery.md"), \
        0 if manifest["syntax_checks_passed"] else 1


def render_views(args, parts, library):
    from ldraw import inspect_model
    from ldraw.lines import Line, OptionalLine, Quadrilateral, Triangle
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
            text, _ = selected_source(args.file, args.section, args.colour)
            source = Path(tmp) / "section.mpd"
            atomic_write(source, text)
        report = render(source, library, args.outdir, views=args.views, timeout=args.timeout, bounds=bounds)
    report.update(source=args.file, section=args.section, source_diagnostics=diagnostics)
    return report, 0


def run(args):
    if args.command == "doctor":
        return doctor(args)
    if args.command == "spec":
        return search_spec(args.query, args.page, args.limit), 0
    if args.command == "sections":
        return model_sections(args.file, args.section), 0
    if args.command == "search" and args.kind != "parts":
        return search_models(" ".join(args.query), limit=args.limit, submodels=args.kind == "submodels", offset=args.offset), 0
    library = library_path(args.library)
    parts = get_parts(library, refresh=args.command == "index", shadows=[] if args.no_shadow else args.shadow)
    if args.command == "check":
        return check(args, parts, library)
    if args.command == "look":
        from .look import look
        result = look(args.file, parts, library, args.outdir, views=args.views, focus=args.focus, highlight=args.highlight,
                      problems=args.problems, section=args.section, colour=args.colour, cell=args.cell)
        notes = ("; " + "; ".join(result["notes"])) if result["notes"] else ""
        return f"sheet: {result['sheet']}  ({len(result['views'])} views, {result['seconds']} s{notes}). Open it to review.", 0
    if args.command == "deliver":
        from .deliver import deliver
        result = deliver(args.file, parts, library, args.outdir, glb=not args.no_glb, family=args.family)
        return (f"{result['verdict']}  delivered to {result['outdir']} in {result['seconds']} s\n"
                f"  summary: {result['summary']}\n  views: {result['sheet']}\n"
                f"  BOM {'matches' if result['bom_matches'] else 'DIFFERS'}; GLB {result['glb'] or 'not produced'}"), \
            0 if result["verdict"] == "PASS" else 1
    if args.command == "ports":
        return ports(args, parts, library)
    if args.command == "search":
        from .catalog import search_parts
        found = [search_parts(parts.by_code, q, limit=args.limit) for q in args.query]
        return (found[0] if len(found) == 1 else dict(searches=found)), 0
    if args.command == "catalog":
        from .catalog import search_catalog
        return search_catalog(parts, args.kind, args.query, category=args.category, limit=args.limit,
                              include_unavailable=args.include_unavailable, max_size=args.max_size, measure=args.measure), 0
    if args.command == "colours":
        return [jsonable(c) for k, c in sorted(parts.colours_by_code.items())
                if args.query.casefold() in (str(k) + " " + (c.name or "")).casefold()], 0
    if args.command == "extract":
        return extract(args, parts)
    if args.command == "render":
        return render_views(args, parts, library)
    if args.command == "glb":
        return prepare_glb(args.file, library, args.output, parts, timeout=args.timeout), 0
    if args.command == "index":
        return dict(parts=len(parts.by_code), library=str(library), index=str(parts.path)), 0
    raise ValueError(f"Unknown command {args.command}")


def main():
    args = parser().parse_args()
    try:
        report, status = run(args)
    except (OSError, ValueError, PartError, RecursionError, sqlite3.Error, subprocess.SubprocessError) as exc:
        report, status = dict(checks_passed=False, error=str(exc), error_type=type(exc).__name__), 2
    text = report + "\n" if isinstance(report, str) else dumps(report) + "\n"
    if getattr(args, "report", None):
        atomic_write(args.report, text)
    print(text, end="")
    return status


if __name__ == "__main__":
    sys.exit(main())
