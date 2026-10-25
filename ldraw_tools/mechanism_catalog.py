"""Discover mechanism parts without mistaking a name for a joint definition.

The supplied Python categories are data, never imported. Every assignment is
retained, including overwritten names. Installed headers add newer parts and
explicit aliases; neither discovery source grants kinematic support.
"""

from __future__ import annotations

import ast
from collections import Counter, defaultdict
import hashlib
import json
import re

from .catalog import assignments, category_path
from .common import DATA, jsonable, normalized
from .document import assembly_view, is_part, parse_source, section_table


# Multiple tags are intentional: a worm belongs to gears and worm drives, a
# pneumatic cylinder to actuators and pneumatics. These are search hints only.
FAMILIES = {
    "gear": r"\bgear|\bcog\b",
    "rack": r"\brack\b",
    "worm": r"\bworm\b",
    "differential": r"\bdifferential\b",
    "clutch": r"\bclutch|driving ring|changeover|wave selector|gear shifter|ratchet|one way",
    "shaft": r"\baxle\b|crankshaft",
    "coupling": r"universal joint|constant velocity|axle (?:joiner|connector|coupling)",
    "bearing": r"\bbush\b|\bbearing\b|axle ?hole|axle hole|\bhub\b",
    "cam": r"\bcam\b|\beccentric\b",
    "link": r"\blink\b|\blever\b|\bcrank\b|\bliftarm\b|\bsteering\b|\bball\b|\bsocket\b",
    "structure": r"\bbeam\b|\bframe\b|\bbrick\b|\bplate\b|\bpanel\b|\bconnector\b|\bpin\b",
    "turntable": r"\bturntable\b",
    "hinge": r"\bhinge\b|\barticulat|\bpivot\b",
    "actuator": r"\bactuator\b|\bpiston\b|\bcylinder\b|\bpump\b",
    "pneumatic": r"\bpneumatic\b|\bvalve\b|air tank",
    "spring": r"\bspring\b|shock absorber|suspension",
    "motor": r"\bmotor\b|\bservo\b",
    "electric": r"\belectric\b|\bsensor\b|\bbattery\b",
    "belt": r"\bbelt\b|rubber band|\bpulley\b",
    "chain": r"\bchain\b|\bsprocket\b",
    "tread": r"\btread\b|\btrack\b|\bcaterpillar\b",
    "hose": r"\bhose\b|\btube\b",
    "cable": r"\bcable\b|\bstring\b|\brope\b|\bwinch\b|\breel\b",
    "wheel": r"\bwheel\b|\btyre\b|\btire\b",
    "propeller": r"\bpropeller\b|\brotor\b",
}
# All Technic entries, plus construction families that can supply mechanism
# interfaces. Deliberately broad; decorative/printed variants stay visible.
MECHANICAL = re.compile(
    r"technic|gear|rack|worm|clutch|hinge|turntable|motor|pneumatic|actuator|"
    r"pulley|belt|rubber band|chain|sprocket|tread|hose|winch|spring|axle|"
    r"wheel|tyre|tire|propeller|rotor|crank|piston|cylinder|electric|cable|"
    r"string|rope|universal joint|constant velocity",
    re.I,
)


def families(description):
    return [
        key
        for key, pattern in FAMILIES.items()
        if re.search(pattern, description, re.I)
    ]


def _identity():
    return [[float(i == j) for j in range(4)] for i in range(4)]


def _multiply(a, b):
    return [
        [sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)
    ]


def _header(parts, code):
    part = parts.find_part(code=code)
    if part is None:
        return None
    raw = part.path.read_bytes()
    lines = raw.decode("utf-8-sig").splitlines()
    fields = {}
    for key in ("!LDRAW_ORG", "!LICENSE", "!CATEGORY", "Author:"):
        fields[key] = next(
            (s.split(key, 1)[1].strip() for s in lines if s.startswith("0 " + key)),
            None,
        )
    title = lines[0].removeprefix("0 ").strip() if lines else ""
    alias = None
    # A shortcut is not an alias: its children may articulate. Follow only an
    # explicit moved/alias/physical-colour declaration with one type-1 record.
    declared = (
        title.startswith(("~Moved to ", "="))
        or "Alias" in (fields["!LDRAW_ORG"] or "")
        or "Physical_Colour" in (fields["!LDRAW_ORG"] or "")
    )
    geometry = [s.split() for s in lines if s[:2] in {"1 ", "2 ", "3 ", "4 ", "5 "}]
    if declared and len(geometry) == 1 and geometry[0][0] == "1":
        f = geometry[0]
        if len(f) == 15:
            v = list(map(float, f[2:14]))
            alias = dict(
                ref=normalized(f[14]),
                colour=int(f[1]),
                transform=[v[3 + i * 3 : 6 + i * 3] + [v[i]] for i in range(3)]
                + [[0.0, 0.0, 0.0, 1.0]],
            )
    return dict(
        description=title,
        org=fields["!LDRAW_ORG"],
        license=fields["!LICENSE"],
        author=fields["Author:"],
        category=fields["!CATEGORY"],
        sha256=hashlib.sha256(raw).hexdigest(),
        alias=alias,
    )


def inventory(parts, *, categories=None, extra_refs=()):
    """Complete discovery inventory for the supplied categories + this library.

    Does not expand geometry or connectors: building the catalog is cheap and
    cannot accidentally declare every detected cylinder to be a joint.
    """
    root = categories or category_path()
    symbols = defaultdict(list)
    for path in sorted((root / "parts").rglob("*.py")):
        category = ".".join(path.relative_to(root / "parts").with_suffix("").parts)
        for name, value, line in assignments(path):
            if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
                continue
            words = re.sub(r"([a-z])([A-Z])", r"\1 \2", name).replace("_", " ")
            if category == "technic" or MECHANICAL.search(words):
                code = normalized(value.value).removesuffix(".dat")
                symbols[code].append(
                    dict(
                        symbol=category + "." + name,
                        source=str(path.relative_to(root)),
                        line=line,
                    )
                )
    remote = json.loads((DATA / "mechanism-parts-watchlist.json").read_text())
    watch = {r["ref"].removesuffix(".dat"): r for r in remote["parts"]}
    codes = (
        set(symbols)
        | set(watch)
        | {normalized(r).removesuffix(".dat") for r in extra_refs}
    )
    codes.update(
        c
        for c, title in parts.by_code.items()
        if MECHANICAL.search(title) and "/" not in c and "\\" not in c
    )
    headers = {}

    def header(code):
        if code not in headers:
            headers[code] = _header(parts, code)
        return headers[code]

    # Reverse aliases matter too: a moved file may have no useful title at all.
    while True:
        previous = len(codes)
        for code, title in parts.by_code.items():
            if (
                title.startswith("~Moved to ")
                and title.removeprefix("~Moved to ").casefold().removesuffix(".dat")
                in codes
            ):
                codes.add(code)
        if len(codes) == previous:
            break
    from .technic import registry

    structural = registry()
    notes = json.loads((DATA / "mechanism-part-notes.json").read_text())["parts"]
    rows = []
    for code in sorted(codes):
        h = header(code)
        chain, transform, target, seen = [], _identity(), code, set()
        problem = None
        while (current := header(target)) and current["alias"]:
            if target in seen:
                problem = "alias_cycle"
                break
            seen.add(target)
            step = dict(
                source=target + ".dat", sha256=current["sha256"], **current["alias"]
            )
            chain.append(step)
            transform = _multiply(transform, step["transform"])
            target = step["ref"].removesuffix(".dat")
        if chain and header(target) is None:
            problem = "missing_alias_target"
        final = header(target)
        description = (final or h or watch.get(code) or {}).get("description", "")
        if not description and symbols[code]:
            hint = symbols[code][0]["symbol"].split(".")[-1]
            description = re.sub(r"([a-z])([A-Z])", r"\1 \2", hint).replace("_", " ")
        reviewed_code = structural["aliases"].get(code, code)
        row = dict(
            ref=code + ".dat",
            description=(h or {}).get("description") or description,
            canonical_ref=target + ".dat" if not problem else None,
            canonical_description=description,
            installed=h is not None,
            families=families(description),
            symbols=symbols[code],
            header=h,
            alias_chain=chain,
            alias_transform=transform if chain else None,
            alias_problem=problem,
            structural_profile=reviewed_code
            if reviewed_code in structural["parts"]
            else None,
            motion_profile="unreviewed",
            shortcut=bool(h and "Shortcut" in (h["org"] or "")),
            internal=bool(h and (h["description"].startswith("~") and not chain)),
        )
        if code in watch:
            row["online_record"] = watch[code]
        if target in notes and not problem:
            row["mechanism_notes"] = notes[target]
            row["notes_coordinate_space"] = (
                "Canonical part local frame; compose alias_transform for original reference. Notes are not a validated motion profile."
            )
        rows.append(row)
    return dict(
        version=1,
        scope="All supplied Technic assignments and mechanical-name matches in supplied categories/installed library; explicit online watchlist. Not all LEGO parts ever made.",
        classification="Names supply search tags only. Structural profiles require geometry fingerprint validation by technic parts/check. Motion frames, degrees of freedom and engagement require review.",
        online_checked=remote["checked"],
        parts=rows,
        summary=dict(
            parts=len(rows),
            installed=sum(r["installed"] for r in rows),
            unavailable=sum(not r["installed"] for r in rows),
            aliases=sum(bool(r["alias_chain"]) for r in rows),
            shortcuts=sum(r["shortcut"] for r in rows),
            supplied_technic_assignments=sum(
                s["symbol"].startswith("technic.") for r in rows for s in r["symbols"]
            ),
            families=dict(
                sorted(Counter(f for r in rows for f in r["families"]).items())
            ),
        ),
    )


def model_inventory(path, *, limit=100000):
    model = parse_source(path)
    occurrences = []
    for o in assembly_view(model).iter_occurrences():
        if len(occurrences) >= limit:
            raise ValueError(f"Model exceeds {limit} physical occurrences")
        if not normalized(o.reference).endswith(".dat"):
            raise ValueError(
                f"Unresolved assembly {o.reference}; embed external assemblies in the MPD before inventorying it"
            )
        occurrences.append(normalized(o.reference))
    return Counter(occurrences)


def catalog(parts, query="", *, family=None, model=None, connectors=False):
    if family and family not in FAMILIES:
        raise ValueError("Unknown mechanism family: " + family)
    counts = model_inventory(model) if model else None
    report = inventory(parts, extra_refs=counts or ())
    rows = report["parts"]
    if counts is not None:
        embedded = {
            normalized(s.name)
            for s in section_table(parse_source(model)).values()
            if is_part(s)
        }
        rows = [
            dict(r, occurrences=counts[r["ref"]], embedded=r["ref"] in embedded)
            for r in rows
            if r["ref"] in counts
        ]
        report["model"] = dict(
            path=str(model),
            physical_parts=sum(counts.values()),
            distinct_refs=len(counts),
            missing=[
                r["ref"] for r in rows if not r["installed"] and not r["embedded"]
            ],
            embedded=sorted(embedded & counts.keys()),
            motion_unreviewed=[
                r["ref"] for r in rows if r["motion_profile"] == "unreviewed"
            ],
        )
    terms = query.casefold().split()
    rows = [
        r
        for r in rows
        if (not family or family in r["families"])
        and all(
            t
            in " ".join(
                [
                    r["ref"],
                    r["description"],
                    r["canonical_description"],
                    *[s["symbol"] for s in r["symbols"]],
                ]
            ).casefold()
            for t in terms
        )
    ]
    report["parts"] = rows
    report["selected"] = len(rows)
    if connectors:
        for row in rows:
            if not row["installed"] or row.get("embedded"):
                row["interfaces"] = dict(
                    status="embedded_requires_review"
                    if row.get("embedded")
                    else "unavailable",
                    features=[],
                )
                continue
            metadata = parts.connection_metadata(row["ref"].removesuffix(".dat"))
            row["interfaces"] = dict(
                status="evidence_only",
                features=[
                    dict(
                        kind=str(f.kind),
                        at=jsonable(f.position),
                        axis=[r[1] for r in f.frame.rows],
                        profile=jsonable(f.profile),
                        source=str(f.source),
                        feature_id=f.feature_id,
                        provenance=jsonable(f.connection_provenance),
                    )
                    for f in metadata.features
                ],
                diagnostics=jsonable(metadata.diagnostics),
                note="Part-local frames, already composed through aliases. Primitive inference can misclassify holes as axles. SNAP freedoms are placement metadata, not torque/mobility constraints. Mixed round/keyed sections must be assessed at the actual engagement interval.",
            )
        report["interface_summary"] = dict(
            with_features=sum(bool(r["interfaces"]["features"]) for r in rows),
            without_features=[
                r["ref"] for r in rows if not r["interfaces"]["features"]
            ],
        )
    return report
