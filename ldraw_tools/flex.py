"""Optional LSynth adapter. LSynth owns synthesis; pyldraw3 owns LDraw parsing.

Continuous material becomes one posed embedded part per SYNTH block. Actual
separate links remain assembly placements, subject to ordinary rigid checks.
"""
from __future__ import annotations

import hashlib
import math
import re
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import numpy as np
from ldraw import parse_model_result

from .common import atomic_write, dumps, normalized
from .validation import validate_text

# These definitions produce separate physical pieces, not sections of one item.
LINK_TYPES = {"BRICK_ARC", "TECHNIC_CHAIN_LINK", "TECHNIC_CHAIN_LINK_WITH_TWO_STUDS",
              "TECHNIC_CHAIN_TREAD", "TECHNIC_CHAIN_TREAD_38", "CHAIN", "PLASTIC_TREAD"}


def availability():
    try:
        return dict(available=True, version=version("lsynth-nova"))
    except PackageNotFoundError:
        return dict(available=False, install="./setup.sh --with-lsynth")


def engine():
    if not availability()["available"]:
        raise ValueError("LSynth is optional and is not installed. Run ./setup.sh --with-lsynth "
                         "with the lsynth-nova checkout beside this repository.")
    from lsynth_nova.config import DEFAULT_CONFIG, load_config
    from lsynth_nova.cli import PARTS_DIR
    return load_config(), DEFAULT_CONFIG, PARTS_DIR


def definitions():
    cfg, _, _ = engine()
    return dict(engine=availability(), types=[
        dict(name=t.type, kind=kind, representation="links" if t.type in LINK_TYPES else "posed_part")
        for kind, types in [("hose", cfg.hose_types), ("band", cfg.band_types)] for t in types],
        products=[dict(name=p.name, nickname=p.nickname, method=p.method) for p in cfg.products],
        hose_constraints=[p.type for p in cfg.hose_constraints],
        band_constraints=[dict(part=p.type, radius_ldu=p.attrib) for p in cfg.band_constraints])


def preflight(text, cfg):
    """Check LSynth control records before calling the CLI.

    Start from visible constraints, never a previous synthesized result: LSynth
    normally comments out hose markers, so such input silently loses its path.
    """
    from lsynth_nova.config import parse_type1, strclean
    active = None
    count = 0
    for number, raw in enumerate(text.splitlines(), 1):
        line = strclean(raw.lstrip())
        tokens = line.split()
        upper = [s.upper() for s in tokens]
        if upper[:3] in (["0", "SYNTH", "SYNTHESIZED"], ["0", "SYNTHESIZED", "BEGIN"]):
            raise ValueError("Use the original unsynthesized constraints, not an LSynth output file")
        if upper[:2] == ["0", "GHOST"]:
            raise ValueError(f"Line {number}: GHOST is not supported in flex assets; use visible constraints")
        if upper[:3] == ["0", "SYNTH", "BEGIN"]:
            if active or len(tokens) < 5:
                raise ValueError(f"Line {number}: nested or incomplete SYNTH BEGIN")
            product = cfg.find_product(tokens[3])
            method = product.method if product else tokens[3]
            if not (cfg.hose_type(method) or cfg.band_type(method)):
                raise ValueError(f"Line {number}: unknown synthesis type {tokens[3]}; see flex types")
            if not re.fullmatch(r"\d+|0x2[0-9A-F]{6}", tokens[4]) or tokens[4] in {"16", "24"}:
                raise ValueError(f"Line {number}: choose an explicit surface colour for synthesis")
            active = number
            count += 1
        elif upper == ["0", "SYNTH", "END"]:
            if not active:
                raise ValueError(f"Line {number}: SYNTH END without BEGIN")
            active = None
        elif active and upper[:2] in (["0", "FILE"], ["0", "NOFILE"]):
            raise ValueError(f"Line {number}: SYNTH block crosses a FILE boundary")
        elif upper[:3] in (["0", "SYNTH", "HOSE_RES"], ["0", "SYNTH", "BAND_RES"]):
            # The port, like the C program, expects resolution before a block.
            raise ValueError(f"Line {number}: custom resolution is not supported by this adapter: "
                             "lsynth-nova 3.1.0 reads the wrong argument positions. Use the default resolution.")
        if tokens[:1] == ["1"]:
            part = parse_type1(line)
            if part is None or len(line.split(None, 14)) != 15 or not all(math.isfinite(v) for v in [*part.offset, *(v for row in part.orient for v in row)]):
                raise ValueError(f"Line {number}: invalid or nonfinite type-1 record")
    if active or not count:
        raise ValueError("Missing SYNTH END" if active else "No SYNTH blocks found")
    return count


def references(text):
    result = parse_model_result(text, name="geometry.dat")
    if result.model is None:
        raise ValueError("Cannot parse LSynth geometry")
    return [normalized(p.reference) for p in result.model.pieces]


def rename_references(lines, names):
    """Only rename FILE dependencies; retain numeric geometry and BFC verbatim."""
    for line in lines:
        fields = line.split(None, 14)
        if len(fields) == 15 and fields[0] == "1" and normalized(fields[14]) in names:
            line = " ".join([*fields[:14], names[normalized(fields[14])]])
        yield line


def rigid_links(segments):
    """Recover only four-decimal serialization roundoff on generated rigid links.

    Never apply to source placements or continuous geometry. Larger changes,
    reflections and actual scale/shear remain errors in assembly validation.
    """
    changes, lines = [], []
    for index, line in enumerate(segments):
        fields = line.split(None, 14)
        matrix = np.array([float(v) for v in fields[5:14]]).reshape(3, 3)
        # Match the strictest consumer (technic review, atol=1e-6): four-decimal links can miss it by ~1e-4.
        if np.isfinite(matrix).all() and np.linalg.det(matrix) > 0 and not np.allclose(matrix.T @ matrix, np.eye(3), atol=1e-6, rtol=0):
            u, _, vt = np.linalg.svd(matrix)
            corrected = u @ vt
            # Each original coefficient was rounded by LSynth to nearest 0.0001.
            if float(np.max(np.abs(corrected - matrix))) <= 0.00005 + 1e-9:
                fields[5:14] = [f"{v:.9f}" for v in corrected.ravel()]
                line = " ".join(fields)
                changes.append(dict(segment=index, before=matrix.tolist(), after=corrected.round(9).tolist()))
        lines.append(line)
    return lines, changes


def package(text, cfg, parts_dir, namespace):
    from lsynth_nova.config import parse_type1
    lines, generated, records = [], [], []
    active = None
    synthesizing = False
    section = None
    piece_count = 0
    for line in text.splitlines():
        tokens = line.split()
        upper = [s.upper() for s in tokens]
        if upper[:2] == ["0", "FILE"]:
            section = line.split(None, 2)[2]
            piece_count = 0
        if upper[:3] == ["0", "SYNTH", "BEGIN"]:
            product = cfg.find_product(tokens[3])
            method = (product.method if product else tokens[3]).upper()
            active = dict(method=method, colour=tokens[4], token=tokens[3],
                          product_hint=product.name if product else None, segments=[])
        elif upper == ["0", "SYNTH", "SYNTHESIZED", "BEGIN"]:
            synthesizing = True
        elif upper == ["0", "SYNTH", "SYNTHESIZED", "END"]:
            synthesizing = False
        elif upper == ["0", "SYNTH", "END"]:
            segments = active.pop("segments")
            if not segments:
                raise ValueError(f"LSynth produced no geometry for {active['token']}")
            linked = active["method"] in LINK_TYPES
            active.update(section=section, first_piece=piece_count)
            if linked:
                segments, changes = rigid_links(segments)
                active["rotation_roundoff_repairs"] = changes
                lines.extend(segments)
            else:
                name = f"{namespace}-flex-{len(records)+1:02d}.dat"
                # Keep synthesized colour and transforms exactly; root placement is rigid.
                generated.extend([f"0 FILE {name}", f"0 Posed {active['method']}", f"0 Name: {name}",
                                  "0 Author: LSynth (generated pose; source credits in manifest)",
                                  "0 !LDRAW_ORG Unofficial_Part", "0 BFC NOCERTIFY",
                                  *segments])
                lines.append(f"1 {active['colour']} 0 0 0 1 0 0 0 1 0 0 0 1 {name}")
                active["part"] = name
            records.append(dict(**active, representation="links" if linked else "posed_part", segment_count=len(segments)))
            piece_count += len(segments) if linked else 1
            active = None
        elif synthesizing:
            if tokens[:1] == ["1"]:
                active["segments"].append(line)
            elif tokens[:1] in (["2"], ["3"], ["4"], ["5"]):
                raise ValueError("Unexpected raw geometry in LSynth output")
        elif upper[:2] == ["0", "SYNTH"] or upper[:3] in (["0", "MLCAD", "BTG"], ["0", "LPUB", "PLI"]) or upper[:2] == ["0", "GROUP"]:
            continue  # Generated grouping/PLI counts no longer describe this packaging.
        else:
            part = parse_type1(line)
            if active and cfg.hose_type(active["method"]) and part and cfg.hose_constraint(part.type):
                continue  # SHOW markers are authoring aids, not physical pieces.
            # Hidden constraint comments remain as provenance, never physical pieces.
            lines.append(line)
            if part:
                piece_count += 1

    if not any(line.split()[:2] == ["0", "FILE"] for line in lines):
        root = f"{namespace}.ldr"
        lines = [f"0 FILE {root}", *[
            f"0 Name: {root}" if line.split()[:2] == ["0", "Name:"] else line for line in lines]]
    else:
        root = next(line.split(None, 2)[2] for line in lines if line.split()[:2] == ["0", "FILE"])
    for record in records:
        if record['section'] is None:
            record['section'] = root

    # Embed only bundled geometry actually used, including transitive LS references.
    bundled = {normalized(p.name): p for p in parts_dir.glob("*.dat")}
    parsed = parse_model_result("\n".join(lines + generated), name=root).model
    if parsed is None:
        raise ValueError("Cannot parse synthesized MPD")
    sections = [parsed, *parsed.submodels.values()]
    declared = {normalized(sub.name) for sub in sections}
    pending = [normalized(p.reference) for sub in sections for p in sub.pieces]
    embedded = {}
    changes = {}
    while pending:
        name = pending.pop()
        if name not in bundled or name in embedded:
            continue
        if name in declared:
            raise ValueError(f"Source overrides bundled LSynth geometry {name}; use unambiguous part names")
        raw = bundled[name].read_bytes()
        changes[name] = []
        try:
            embedded[name] = raw.decode("utf-8")
        except UnicodeDecodeError:
            # Bundled LS22 uses Latin-1 for its author's name (Glöckner).
            if name != "ls22.dat":
                raise
            embedded[name] = raw.decode("latin-1")
            changes[name].append("Transcoded Latin-1 header to UTF-8")
        if "0 BFC CERTIFY INVERTNEXT" in embedded[name]:
            embedded[name] = embedded[name].replace("0 BFC CERTIFY INVERTNEXT", "0 BFC INVERTNEXT")
            changes[name].append("Corrected legacy BFC CERTIFY INVERTNEXT to BFC INVERTNEXT")
        pending.extend(references(embedded[name]))
    names = {name: f"{namespace}-{name}" for name in embedded}
    output = list(rename_references(lines + generated, names))
    sources = []
    for name, body in sorted(embedded.items()):
        output.append("0 FILE " + names[name])
        for line in rename_references(body.splitlines(), names):
            output.append("0 Name: " + names[name] if line.split()[:2] == ["0", "Name:"] else line)
        sources.append(dict(name=name, embedded_as=names[name], sha256=hashlib.sha256(bundled[name].read_bytes()).hexdigest(), changes=changes[name]))
    output.append("0 NOFILE")
    return "\r\n".join(output) + "\r\n", dict(root=root, blocks=records, embedded_sources=sources)


def build(source, output, parts, *, namespace=None, force=False, timeout=90):
    source, output = Path(source).resolve(), Path(output).resolve()
    manifest = output.with_suffix(".manifest.json")
    if output.suffix.lower() != ".mpd":
        raise ValueError("Flex output must be an .mpd asset")
    if source in (output, manifest):
        raise ValueError("Keep the original constraints separate from the generated asset")
    if any(path.exists() and not path.is_file() for path in (output, manifest)):
        raise ValueError("Flex output and manifest must be files, not directories")
    if not force and (output.exists() or manifest.exists()):
        raise ValueError("Flex output already exists; use --force to rebuild")
    namespace = namespace or re.sub(r"[^a-z0-9_-]+", "-", output.stem.lower())
    if not re.fullmatch(r"[a-z][a-z0-9_-]*", namespace):
        raise ValueError("Use --namespace starting with a lowercase letter, then letters, digits, _ or -")
    cfg, config, parts_dir = engine()
    raw = source.read_bytes()
    text = raw.decode("utf-8-sig")
    count = preflight(text, cfg)
    # Invoke this exact installed port, not an unrelated executable on PATH.
    result = subprocess.run([sys.executable, "-m", "lsynth_nova", "-c", str(config), "-"],
                            input=text, text=True, capture_output=True, timeout=timeout)
    if result.returncode or "warning:" in result.stderr.casefold():
        raise ValueError("LSynth did not complete cleanly: " + result.stderr.strip())
    mpd, report = package(result.stdout, cfg, parts_dir, namespace)
    if len(report["blocks"]) != count:
        raise ValueError("LSynth output is missing synthesis blocks")
    _, diagnostics = validate_text(mpd, parts, name=output.name)
    errors = [d for d in diagnostics if d["severity"] == "error"]
    if errors:
        raise ValueError("Synthesized asset failed assembly validation: " + dumps(errors[:8]))
    report.update(engine=availability(), source=str(source), source_sha256=hashlib.sha256(raw).hexdigest(),
                  source_credits=[line for line in text.splitlines() if line.startswith(("0 Author:", "0 !LICENSE"))],
                  config_sha256=hashlib.sha256(config.read_bytes()).hexdigest(), output=str(output),
                  model_sha256=hashlib.sha256(mpd.encode()).hexdigest(), diagnostics=diagnostics,
                  physical_validity="not_proven", review_required=True,
                  limitations=["Posed parts have no verified length, stock identity, bend radius or connector metadata.",
                               "Synthesis does not prove tension, material clearance, link engagement or motion."])
    atomic_write(output, mpd)
    atomic_write(manifest, dumps(report) + "\n")
    return dict(**report, manifest=str(manifest))
