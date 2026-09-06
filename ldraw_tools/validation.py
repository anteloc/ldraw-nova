"""Additional PDF-derived checks around pyldraw3, not a second LDraw parser."""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
from ldraw import parse_model_result
from ldraw.lines import Line, OptionalLine, Triangle, Quadrilateral

from .common import issue, normalized

ROTATION_TOLERANCE = 1e-4  # Permits six-place trigonometric rounding, not shear.
BFC = {"CERTIFY", "CERTIFY CCW", "CERTIFY CW", "NOCERTIFY", "CW", "CCW",
       "CLIP", "CLIP CW", "CLIP CCW", "CW CLIP", "CCW CLIP", "NOCLIP", "INVERTNEXT"}
UNSUPPORTED = {"!TEXMAP", "!DATA", "!:", "!COLOUR", "CLEAR"}


def polygon_issues(obj, line, section, *, part_geometry=False):
    p = np.array([[v.x, v.y, v.z] for v in obj.points], dtype=float)
    if not np.isfinite(p).all():
        return [issue("number.nonfinite", "Coordinates must be finite.", line=line, section=section)]
    if isinstance(obj, (Line, OptionalLine)):
        return [] if np.linalg.norm(p[1] - p[0]) > 1e-9 else [
            issue("geometry.zero_length", "Line endpoints coincide.", line=line, section=section)]
    # Scale-relative degeneracy and planarity tolerance; not Parts Tracker certification.
    scale = max(float(np.ptp(p, axis=0).max()), 1.0)
    cross = np.cross(p[1] - p[0], p[2] - p[0])
    if np.linalg.norm(cross) <= 1e-9 * scale**2:
        return [issue("geometry.degenerate", "Polygon contains collinear/coincident vertices.", line=line, section=section)]
    if isinstance(obj, Quadrilateral):
        normal = cross / np.linalg.norm(cross)
        if part_geometry:
            # PDF p.142 requires testing BOTH diagonals. Under 1 degree is the
            # ordinary part tolerance; 1–3 requires justification, >3 is invalid.
            angles = []
            for indices in [(0,1,2,0,2,3), (0,1,3,1,2,3)]:
                a,b,c,d,e,f = p[list(indices)]
                n, q = np.cross(b-a,c-a), np.cross(e-d,f-d)
                length = np.linalg.norm(n) * np.linalg.norm(q)
                angles.append(180.0 if length == 0 else float(np.degrees(np.arccos(np.clip(n @ q / length, -1, 1)))))
            if max(angles) > 3:
                return [issue("geometry.nonplanar", "Part quad exceeds 3-degree tolerance (PDF p.142).", line=line, section=section, angle_degrees=max(angles))]
            if max(angles) >= 1:
                return [issue("geometry.quad_warp_review", "Part quad needs author justification for 1–3 degree warp (PDF p.142).", line=line, section=section, severity="warning", angle_degrees=max(angles))]
        elif abs(np.dot(p[3] - p[0], normal)) > 1e-5 * scale:
            return [issue("geometry.nonplanar", "Quad is not planar; split it into triangles.", line=line, section=section)]
        turns = [np.dot(np.cross(p[(i+1)%4]-p[i], p[(i+2)%4]-p[(i+1)%4]), normal) for i in range(4)]
        if min(turns) <= 1e-9 * scale**2:
            return [issue("geometry.quad_winding", "Quad is concave, crossed, or has a collinear corner.", line=line, section=section)]
    return []


def validate_text(text, parts, *, name="model.mpd", assembly=True, raw=None, instance_limit=100000):
    problems = []
    raw = text.encode("utf-8") if raw is None else raw
    if raw.startswith(b"\xef\xbb\xbf"):
        problems.append(issue("encoding.bom", "UTF-8 BOM is forbidden (PDF p.61)."))
        text = text.removeprefix("\ufeff")
    if b"\n" in raw.replace(b"\r\n", b"") or b"\r" in raw.replace(b"\r\n", b""):
        problems.append(issue("encoding.line_endings", "Use CRLF when delivering new files (PDF p.62).", severity="warning"))
    has_file = bool(re.search(r"(?m)^[ \t]*0[ \t]+FILE(?:[ \t]|$)", text))
    if assembly and not has_file:
        problems.append(issue("assembly.mpd_required", "Deliver an MPD with main 0 FILE block first."))
    section = None
    active = not has_file
    started = False
    pending_bfc = None
    certified = False
    operated = False
    seen_bfc = False
    sanitized = []
    for number, line in enumerate(text.splitlines(), 1):
        tokens = line.split()
        if not tokens:
            sanitized.append("")
            continue
        if tokens[:2] == ["0", "FILE"]:
            if pending_bfc:
                problems.append(issue("bfc.invertnext", "INVERTNEXT must be followed by type 1.", line=pending_bfc, section=section))
            section = line.strip().split(None, 2)[2] if len(tokens) > 2 else ""
            if not section:
                problems.append(issue("mpd.filename", "FILE needs a filename.", line=number))
            if len(section) > 255:
                problems.append(issue("mpd.filename", "Filename exceeds 255 characters.", line=number))
            if assembly and not section.lower().endswith((".ldr", ".dat")):
                problems.append(issue("assembly.section_name", "Use .ldr for assemblies and classified .dat for embedded definitions.", line=number))
            if parts.find_part(code=normalized(section).removesuffix(".dat")) is not None:
                problems.append(issue("mpd.library_shadow", "Embedded filename shadows a library part/primitive.", line=number, section=section))
            active = started = True
            pending_bfc = None
            certified = operated = seen_bfc = False
            sanitized.append(line)
            continue
        if tokens[:2] == ["0", "NOFILE"]:
            if len(tokens) != 2:
                problems.append(issue("mpd.nofile_arguments", "NOFILE takes no arguments.", line=number, section=section))
            if pending_bfc:
                problems.append(issue("bfc.invertnext", "INVERTNEXT must be followed by type 1.", line=pending_bfc, section=section))
            pending_bfc = None
            active = False
            sanitized.append(line)
            continue
        if not active and has_file:
            if tokens[:2] == ["0", "!DATA"]:
                problems.append(issue("coverage.unsupported_meta", "Embedded !DATA requires external review; it is outside this checker's profile.", line=number))
            if not started and tokens[0] in {"1", "2", "3", "4", "5"}:
                problems.append(issue("mpd.preamble_geometry", "Geometry before the first FILE is an error (PDF p.126).", line=number))
            # MPD text outside blocks is discarded by the specification.
            sanitized.append("")
            continue
        if pending_bfc:
            if tokens[0] != "1":
                problems.append(issue("bfc.invertnext", "Only blank lines may intervene before INVERTNEXT's type 1.", line=pending_bfc, section=section))
            pending_bfc = None
        if tokens[0] == "0":
            keyword = tokens[1] if len(tokens) > 1 else ""
            if keyword in UNSUPPORTED:
                problems.append(issue("coverage.unsupported_meta", f"{keyword} semantics require external review; this checker cannot certify them. See PDF/source index.", line=number, section=section))
            if keyword == "STEP" and len(tokens) != 2:
                problems.append(issue("meta.step_arguments", "STEP takes no arguments.", line=number, section=section))
            if keyword == "BFC":
                options = " ".join(tokens[2:])
                if options not in BFC:
                    problems.append(issue("bfc.syntax", "Unknown BFC option combination (PDF pp.94–96).", line=number, section=section))
                if options.startswith(("CERTIFY", "NOCERTIFY")):
                    if certified or operated or seen_bfc:
                        problems.append(issue("bfc.certification_order", "Certification must occur once, before all other BFC/geometry.", line=number, section=section))
                    certified = True
                if options == "INVERTNEXT":
                    pending_bfc = number
                    if assembly and not (section or name).lower().endswith(".dat"):
                        problems.append(issue("assembly.invertnext", "Do not invert physical parts. Mirroring and BFC inversion are distinct (PDF pp.96–98).", line=number, section=section))
                seen_bfc = True
            sanitized.append(line)
            continue
        operated = True
        expected = {"1": 15, "2": 8, "3": 11, "4": 14, "5": 14}
        kind = tokens[0]
        fields = line.split(None, 14) if kind == "1" else tokens
        if kind == "1" and len(fields) == 15 and re.search(r"[ \t]{2,}|\t", fields[14].strip()):
            problems.append(issue("coverage.filename_whitespace", "The pinned parser normalizes repeated filename whitespace; use simple section names and exact matching references or review externally.", line=number, section=section))
        if kind in expected and len(fields) != expected[kind]:
            problems.append(issue("syntax.field_count", f"Type {kind} requires {expected[kind]} fields including type and colour; filename is the entire remainder.", line=number, section=section))
        if kind in expected and len(fields) == expected[kind]:
            if not (re.fullmatch(r"\d+", fields[1]) or re.fullmatch(r"0x2[0-9A-F]{6}", fields[1])):
                problems.append(issue("colour.syntax", "Use an integer colour or uppercase 0x2RRGGBB.", line=number, section=section))
            if fields[1] == "24" and kind in {"1", "3", "4"}:
                problems.append(issue("colour.edge_on_surface", "Use colour 24 only for edges in the supported profile.", line=number, section=section))
            values = fields[2:14] if kind == "1" else fields[2:]
            try:
                if not all(np.isfinite(float(v)) for v in values):
                    raise ValueError
            except ValueError:
                problems.append(issue("number.nonfinite", "Every transform/coordinate must be a finite number.", line=number, section=section))
                sanitized.append("")  # Keep line numbers; don't pass NaN to geometry code.
                continue
        sanitized.append(line)
    if pending_bfc:
        problems.append(issue("bfc.invertnext", "Dangling INVERTNEXT at end of file.", line=pending_bfc, section=section))
    result = parse_model_result("\n".join(sanitized), name=name, source=name, parts=parts)
    # Our tolerance accepts serialized rotations rounded to six decimals.
    problems.extend(d.to_dict() for d in result.diagnostics if str(d.code) not in {
        "model.non_orthonormal_matrix", "model.singular_matrix"})
    model = result.model
    if model is None:
        return model, problems
    all_models = [model, *model.submodels.values()]
    from .document import is_part, section_table, assembly_view, dependency_closure
    table = section_table(model)
    for sub in all_models:
        part_scope = is_part(sub)
        if assembly and part_scope and not any(word in (sub.ldraw_org or "").casefold() for word in ("part", "primitive", "shortcut")):
            problems.append(issue("part.missing_classification", "Embedded .dat definitions require an accurate !LDRAW_ORG part/subpart/primitive/shortcut classification.", section=sub.name))
        if assembly:
            for value, label in [(sub.description, "title"), (sub.header_name, "Name:"), (sub.author, "Author:")]:
                if not value:
                    problems.append(issue("header.missing", f"Add a descriptive {label} header.", section=sub.name, severity="warning"))
            if sub.header_name and normalized(sub.header_name) != normalized(sub.name):
                problems.append(issue("header.name_mismatch", "Name: must match its FILE block.", section=sub.name))
        for obj in sub.objects:
            line = sub.source_line_for(obj)
            if isinstance(obj, (Line, OptionalLine, Triangle, Quadrilateral)):
                problems.extend(polygon_issues(obj, line, sub.name, part_geometry=part_scope))
                if assembly and not part_scope:
                    problems.append(issue("coverage.raw_geometry", "Assembly analysis requires library parts; custom type 2–5 geometry needs external review.", line=line, section=sub.name))
        for piece in sub.pieces:
            line = sub.source_line_for(piece)
            a = np.array(piece.matrix.rows)
            if not np.isfinite(a).all() or abs(np.linalg.det(a)) < 1e-9:
                problems.append(issue("matrix.singular", "Singular transform collapses geometry.", line=line, section=sub.name))
            elif assembly and not part_scope and (not np.allclose(a.T @ a, np.eye(3), atol=ROTATION_TOLERANCE, rtol=0) or np.linalg.det(a) < 0):
                problems.append(issue("assembly.nonrigid", "Use a proper rotation: physical parts must not be scaled, sheared, or mirrored.", line=line, section=sub.name))
            embedded = table.get(normalized(piece.reference))
            if assembly and not part_scope and embedded is not None and is_part(embedded):
                kind = (embedded.ldraw_org or "").casefold()
                if "primitive" in kind or "subpart" in kind or normalized(embedded.name).startswith("s/"):
                    problems.append(issue("assembly.library_internal", "Do not place embedded primitives/subparts as physical parts.", line=line, section=sub.name))
            if embedded is None and assembly and not part_scope:
                part = parts.find_part(code=piece.part)
                if part:
                    filetype = part.metadata.file_kind
                    description = part.description
                    if "/" in normalized(piece.reference) or str(filetype) not in {"part", "shortcut"}:
                        problems.append(issue("assembly.library_internal", "Place physical library parts, not subparts or primitives.", line=line, section=sub.name))
                    if description.startswith(("~", "=")):
                        problems.append(issue("part.alias_or_internal", "Inspect this alias/internal part and prefer a current physical part.", line=line, section=sub.name, severity="warning"))
    if not any(p["severity"] == "error" for p in problems):
        occurrences = []
        for occurrence in assembly_view(model).iter_occurrences():
            occurrences.append(occurrence)
            if len(occurrences) > instance_limit:
                problems.append(issue("coverage.instance_budget", f"More than {instance_limit} physical occurrences; increase --max-instances or select a section."))
                return model, problems
        used = {normalized(s.name) for s in dependency_closure(model)}
        placements = {}
        for occ in occurrences:
            used.update(normalized(p.model.name) for p in occ.path)
            if assembly and occ.colour.code == 16:
                problems.append(issue("colour.unresolved_current", "Choose an explicit colour on the root placement; this leaf still inherits 16.", line=occ.source_line, section=occ.source_model.name))
            key = (normalized(occ.reference), tuple(np.round([occ.position.x, occ.position.y, occ.position.z], 6)), tuple(np.round(np.array(occ.matrix.rows).ravel(), 6)))
            if key in placements:
                problems.append(issue("assembly.duplicate", "Same part is placed twice at the same world transform (including across submodels).", line=occ.source_line, section=occ.source_model.name, severity="error" if assembly else "warning"))
            placements[key] = occ
        for sub in all_models[1:]:
            if normalized(sub.name) not in used:
                problems.append(issue("mpd.unreachable", "Section is unreachable from the main model.", section=sub.name, severity="warning"))
        if assembly and not occurrences:
            problems.append(issue("assembly.empty", "The main model must contain at least one physical part."))
    return model, problems


def validate_file(path, parts, *, assembly=True, instance_limit=100000, section=None, colour=None):
    if section is not None:
        from .document import selected_source, section_table
        text, line_map = selected_source(path, section, colour)
        model, diagnostics = validate_text(text, parts, name=str(path), assembly=assembly, instance_limit=instance_limit)
        for d in diagnostics:
            if d.get("line_number") is not None:
                d["line_number"] = line_map.get(d["line_number"])
        if model:
            # Keep instance/source paths useful after selecting/reordering FILE blocks.
            for sub in section_table(model).values():
                sub._source_lines = {obj: line_map.get(n) for obj,n in sub._source_lines.items()}
                sub._object_source_lines = {obj: line_map.get(n) for obj,n in sub._object_source_lines.items()}
        return model, diagnostics
    if colour is not None:
        raise ValueError("--colour requires --section")
    raw = Path(path).read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None, [issue("encoding.utf8", "New files must be UTF-8 (PDF p.61).")]
    return validate_text(text, parts, name=str(path), assembly=assembly, raw=raw, instance_limit=instance_limit)
