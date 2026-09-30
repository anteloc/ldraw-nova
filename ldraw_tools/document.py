"""MPD namespaces, physical-part boundaries, and dependency-closed source reuse.

pyldraw3 owns record parsing and geometry. This adapter distinguishes embedded
part definitions from model assemblies, which must not be counted the same way.
"""
from __future__ import annotations

import hashlib
import re
from collections import Counter
from dataclasses import replace
from pathlib import Path

import numpy as np

from ldraw import Model, Parts, Piece, parse_model_result
from ldraw.part import Part

from .common import CACHE, atomic_write, normalized


def is_part(model):
    return normalized(model.name).endswith(".dat")


def section_table(model):
    return {normalized(s.name): s for s in [model, *model.submodels.values()]}


def resolve_section(model, section=None):
    """Match a source/header identity to the parser without guessing ambiguities."""
    table = section_table(model)
    wanted = normalized(section if section is not None else model.name)
    if wanted in table:
        return table[wanted]
    matches = [s for k, s in table.items() if k.strip() == wanted.strip()]
    if len(matches) != 1:
        raise ValueError(f"{'Ambiguous' if matches else 'Unknown'} section {section!r}")
    return matches[0]


def dependency_closure(model, section=None):
    table = section_table(model)
    start = normalized(resolve_section(model, section).name)
    ordered, done = [], set()

    def visit(key, path):
        if key in path:
            raise ValueError("MPD dependency cycle: " + " -> ".join((*path, key)))
        if key in done:
            return
        done.add(key)
        ordered.append(table[key])
        for p in table[key].pieces:
            child = normalized(p.reference)
            if child in table:
                visit(child, (*path, key))
    visit(start, ())
    return ordered


def assembly_view(model, section=None, colour=None):
    """Root-relative model view that stops at embedded .dat physical boundaries."""
    closure = dependency_closure(model, section)
    selected = closure[0]
    table = {normalized(s.name): s for s in closure if not is_part(s)}
    view = replace(selected, submodels={k: s for k, s in table.items() if k != normalized(selected.name)})
    if is_part(selected) or colour is not None:
        wrapper = Model(name="nova-preview-root.ldr", objects=[Piece.place(selected.name, colour=colour if colour is not None else 7)])
        wrapper.submodels = table
        return wrapper
    return view


class DocumentParts(Parts):
    """Per-document overlay; original library and other documents remain untouched."""

    def __init__(self, base, model):
        super().__init__(base.path)
        self._connection_shadow_libraries = list(base._connection_shadow_libraries)
        self._studio_connection_libraries = list(base._studio_connection_libraries)
        self._connection_overrides = dict(base._connection_overrides)
        self.embedded = {}
        self.embedded_names = {}
        for section in section_table(model).values():
            if not is_part(section):
                continue
            # Hash filenames in the cache: a source name never becomes a filesystem path.
            body = replace(section, submodels={}).to_ldraw() + "\n"
            digest = hashlib.sha256(body.encode()).hexdigest()
            path = CACHE / "embedded" / (digest + ".dat")
            if not path.exists():
                atomic_write(path, body)
            key = normalized(section.name).removesuffix(".dat")
            self.embedded[key] = Part(path)
            self.embedded_names[key] = section.name
            self.by_code[key] = section.description or section.name
            self.by_name[section.description or section.name] = key

    def _load_part(self, code):
        key = normalized(code)
        if key in self.embedded:
            return self.embedded[key]
        return super()._load_part(code)


def physical_context(model, parts, section=None, colour=None):
    overlay = DocumentParts(parts, model) if any(is_part(s) for s in section_table(model).values()) else parts
    return assembly_view(model, section, colour), overlay


def parse_source(path):
    path = Path(path)
    raw = path.read_bytes()
    result = parse_model_result(raw.decode("utf-8-sig"), name=path.name, source=path)
    if result.model is None or any(str(d.severity) == "error" for d in result.diagnostics):
        raise ValueError("Cannot recover a structurally invalid MPD: " + "; ".join(d.message for d in result.diagnostics))
    return result.model


def source_blocks(path):
    """Block boundaries only; operational records are parsed by pyldraw3."""
    result, active = {}, None
    for number, line in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1):
        fields = line.split(None, 2)
        if fields[:2] == ["0", "FILE"] and len(fields) == 3:
            active = normalized(fields[2].strip())
            if active in result:
                raise ValueError(f"Ambiguous FILE identity {fields[2]!r}")
            result[active] = []
        elif fields[:2] == ["0", "NOFILE"]:
            active = None
        elif active is not None:
            result[active].append((number, line))
    if not result:
        model = parse_source(path)
        result[normalized(model.name)] = list(enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1))
    return result


def selected_source(path, section, colour=None):
    """Dependency-closed text and a map back to original source line numbers."""
    model = parse_source(path)
    closure = dependency_closure(model, section)
    blocks = source_blocks(path)
    lines, line_map = [], {}
    if colour is not None or is_part(closure[0]):
        wrapper = "nova-selection-root.ldr"
        while normalized(wrapper) in section_table(model):
            wrapper = "_" + wrapper
        lines.extend(["0 FILE " + wrapper, "0 Section preview", "0 Name: " + wrapper,
                      "0 Author: LDraw tooling (preview wrapper)", "0 !LDRAW_ORG Model",
                      f"1 {7 if colour is None else colour} 0 0 0 1 0 0 0 1 0 0 0 1 {closure[0].name}"])
    for sub in closure:
        lines.append("0 FILE " + sub.name)
        for original, line in blocks[normalized(sub.name).strip()]:
            lines.append(line)
            line_map[len(lines)] = original
    lines.append("0 NOFILE")
    return "\r\n".join(lines) + "\r\n", line_map


def extract_section(path, section, *, namespace, repair_bfc=False, normalize_rotations=False):
    """Return a renamed, dependency-closed MPD plus an attribution/change manifest."""
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", namespace):
        raise ValueError("Namespace must start with a letter and contain letters, digits, _ or -")
    model = parse_source(path)
    closure = dependency_closure(model, section)
    blocks = source_blocks(path)
    renames = {}
    for index, sub in enumerate(closure):
        stem = re.sub(r"[^A-Za-z0-9_-]+", "-", Path(sub.name.replace("\\", "/")).stem).strip("-")
        renames[normalized(sub.name)] = f"{namespace}-{index:02d}-{stem}{'.dat' if is_part(sub) else '.ldr'}"
    lines, changes = [], []
    for sub in closure:
        new_name = renames[normalized(sub.name)]
        lines.append("0 FILE " + new_name)
        content = list(blocks[normalized(sub.name).strip()])
        if repair_bfc:
            i = 0
            while i < len(content):
                if content[i][1].split() == ["0", "BFC", "INVERTNEXT"]:
                    j = i + 1
                    while j < len(content) and (not content[j][1].strip() or content[j][1].lstrip().startswith("0 //")):
                        j += 1
                    if j < len(content) and content[j][1].split()[:1] == ["1"] and any(t.strip() for _, t in content[i+1:j]):
                        changes.append(dict(kind="move_comments_before_invertnext", section=sub.name, source_line=content[i][0], comment_lines=[n for n,t in content[i+1:j] if t.strip()]))
                        content[i:j] = [*content[i+1:j], content[i]]
                    i = j
                i += 1
        for number, line in content:
            tokens = line.split(None, 14)
            if tokens[:2] == ["0", "Name:"]:
                line = "0 Name: " + new_name
            elif tokens[:1] == ["1"] and len(tokens) == 15:
                if normalize_rotations and not is_part(sub):
                    matrix = np.array([float(v) for v in tokens[5:14]]).reshape(3, 3)
                    deviation = float(np.max(np.abs(matrix.T @ matrix - np.eye(3))))
                    if 1e-4 < deviation <= 0.002 and np.linalg.det(matrix) > 0:
                        u, _, vt = np.linalg.svd(matrix)
                        corrected = u @ vt
                        changes.append(dict(kind="normalize_rounded_rotation", section=sub.name, source_line=number,
                                            before=matrix.tolist(), after=corrected.round(9).tolist(),
                                            max_coefficient_change=float(np.max(np.abs(corrected-matrix)))))
                        tokens[5:14] = [f"{v:.9f}" for v in corrected.ravel()]
                        line = " ".join(tokens)
                child = renames.get(normalized(tokens[14]).strip())
                if child:
                    line = " ".join(tokens[:14]) + " " + child
            lines.append(line)
        lines.append("0 NOFILE")
    text = "\r\n".join(lines) + "\r\n"
    raw = Path(path).read_bytes()
    manifest = dict(source=str(Path(path).resolve()), source_sha256=hashlib.sha256(raw).hexdigest(),
                    source_section=section, parser_section=closure[0].name, root=renames[normalized(closure[0].name)],
                    renames={s.name: renames[normalized(s.name)] for s in closure},
                    attribution=[dict(section=s.name, author=s.author, license=s.license) for s in closure],
                    changes=changes, output_sha256=hashlib.sha256(text.encode()).hexdigest(),
                    note="Original authors and licences retained. Source bytes unchanged. Extraction is not validation or permission to relicense.")
    return text, manifest


def study_model(path, parts, *, instance_limit=100000):
    model = parse_source(path)
    table = section_table(model)
    physical, overlay = physical_context(model, parts)
    occurrences = []
    for occ in physical.iter_occurrences(include_steps=True):
        occurrences.append(occ)
        if len(occurrences)>instance_limit:
            raise ValueError(f"Study exceeds {instance_limit} physical placements; increase --max-instances")
    reachable = {normalized(s.name) for s in dependency_closure(model)}
    uses = Counter()

    def count_uses(s):
        uses[normalized(s.name)] += 1
        for p in s.pieces:
            child = table.get(normalized(p.reference))
            if child is not None and not is_part(child):
                count_uses(child)
    count_uses(model)
    counts, visiting = {}, set()

    def leaf_count(key):
        if key in counts:
            return counts[key]
        if key in visiting:
            raise ValueError(f"Cycle at {key}")
        visiting.add(key)
        counts[key] = sum(leaf_count(normalized(p.reference)) if normalized(p.reference) in table and not is_part(table[normalized(p.reference)]) else 1 for p in table[key].pieces)
        visiting.remove(key)
        return counts[key]
    rows = []
    for key, s in table.items():
        refs = Counter(p.reference for p in s.pieces)
        rows.append(dict(name=s.name, kind="part_definition" if is_part(s) else "assembly", description=s.description,
                         author=s.author, license=s.license, ldraw_org=s.ldraw_org,
                         reachable=key in reachable, scene_instances=uses[key] if not is_part(s) else None,
                         direct_placements=len(s.pieces),
                         physical_placements=None if is_part(s) else leaf_count(key), steps=len(s.steps),
                         children=[dict(name=ref, count=n) for ref,n in refs.items() if normalized(ref) in table],
                         library_parts=[dict(name=ref, count=n) for ref,n in refs.most_common(12) if normalized(ref) not in table]))
    from .validation import validate_file
    _, diagnostics = validate_file(path, parts, assembly=True, instance_limit=instance_limit)
    return dict(source=str(Path(path).resolve()), source_sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),
                main=model.name, section_count=len(table), assembly_count=sum(not is_part(s) for s in table.values()),
                embedded_definition_count=sum(is_part(s) for s in table.values()), physical_placements=len(occurrences),
                reachable_section_count=len(reachable), unreachable_sections=[s.name for k,s in table.items() if k not in reachable],
                unique_parts=len({normalized(o.reference) for o in occurrences}),
                max_assembly_depth=max((len(o.path) for o in occurrences), default=0),
                sections=rows, bom=physical.bill_of_materials(parts=overlay),
                source_checks_passed=not any(d["severity"] == "error" for d in diagnostics),
                diagnostic_counts=dict(Counter(d["code"] for d in diagnostics)),
                diagnostics=diagnostics)
