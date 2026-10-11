"""Attach exact reference-pose evidence to findings; never change checker verdicts.

Matching a reference model is corroboration, not a physical-build certificate.
The four supported poses below are deliberately narrow: names, proximity or
membership of the window family are never sufficient evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from ldraw_tools.check import placed_rows
from ldraw_tools.common import get_parts, library_path
from ldraw_tools.document import section_table
from ldraw_tools.validation import validate_file


ROOT = Path(__file__).resolve().parents[3]
REFERENCE = ROOT / "data/models-annotated/10270-1.mpd"
IDENTITY = np.eye(3)
POSES = [
    ("60592", "60601", [0, 0, 0], IDENTITY),
    ("60596", "57895", [0, 5, 5], IDENTITY),
    ("60594", "60608", [-32, 4, 4], np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]])),
    ("60594", "60608", [32, 4, 4], np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]])),
]


def matches(frame, pane, pose):
    a, b, offset, rotation = pose
    return (frame["code"] == a and pane["code"] == b
            and np.allclose(frame["R"].T @ (pane["t"]-frame["t"]), offset, atol=1e-5, rtol=0)
            and np.allclose(frame["R"].T @ pane["R"], rotation, atol=1e-5, rtol=0))


def reference_evidence(parts):
    model, _ = validate_file(REFERENCE, parts, assembly=True)
    evidence = []
    for pose in POSES:
        found = None
        for section in section_table(model).values():
            rows = [dict(code=p.part, t=np.array([p.position.x, p.position.y, p.position.z]),
                         R=np.array(p.matrix.rows), placement=p.to_ldraw()) for p in section.pieces
                    if p.part in pose[:2]]
            for a in rows:
                for b in rows:
                    if matches(a, b, pose):
                        found = dict(section=section.name, frame=a["placement"], pane=b["placement"])
                        break
                if found:
                    break
            if found:
                break
        if found is None:
            raise ValueError(f"Expected reference pose no longer present: {pose[:3]}")
        evidence.append(dict(frame=pose[0], pane=pose[1], relative_offset=pose[2],
                             relative_rotation=pose[3].tolist(), source_example=found))
    return evidence


def assess(path, report, parts, evidence):
    model, _ = validate_file(path, parts, assembly=True)
    rows, _, _ = placed_rows(model, path, parts, library_path())
    supported, unresolved = [], []
    def record(kind, indices):
        found = None
        for i in indices:
            for j in indices:
                for k, pose in enumerate(POSES):
                    if matches(rows[i], rows[j], pose):
                        found = dict(kind=kind, frame=rows[i]["label"], pane=rows[j]["label"],
                                     reference_pose=k)
                        break
                if found:
                    break
            if found:
                break
        if found:
            supported.append(found)
        else:
            unresolved.append(dict(kind=kind, parts=[rows[i]["label"] for i in indices]))

    # Overlap reports carry both occurrences. Only the exact pair is assessed.
    for finding in report["reviews"]:
        record("overlap", [finding["a"]["index"], finding["b"]["index"]])
    # A disconnected pane must have exactly the expected relative placement to
    # a frame in its own assembly instance. A nearby window elsewhere cannot
    # justify a misplaced pane. Larger disconnected groups remain unresolved.
    for group in report["floating_groups"]:
        if group["size"] != 1:
            unresolved.append(dict(kind="disconnected_group", size=group["size"]))
            continue
        index = group["parts"][0]["index"]
        prefix = rows[index]["label"].rsplit(">", 1)[0]
        candidates = [i for i, r in enumerate(rows) if r["code"] == "60594"
                      and r["label"].rsplit(">", 1)[0] == prefix]
        record("connection", [index, *candidates])
    all_rows_present = (len(report["reviews"]) == report["review_count"]
                        and sum(g["size"] for g in report["floating_groups"]) == report["floating_count"])
    return dict(
        source=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        raw_verdict=report["verdict"], raw_verdict_unchanged=True,
        physical_validity="not_proven", reference=str(REFERENCE.relative_to(ROOT)),
        reference_sha256=hashlib.sha256(REFERENCE.read_bytes()).hexdigest(),
        reference_poses=evidence, reference_supported=supported, unresolved=unresolved,
        all_finding_rows_available=all_rows_present,
        collisions=report["collision_count"], seating=report["seating_count"],
        duplicates=report["duplicate_count"], unknown=report["unknown_count"],
        missing_geometry=report["missing_geometry_count"],
        qualification="Exact reference poses corroborate these fittings; raw findings remain visible. "
                      "No strength, assembly order, inventory or physical fit certification.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folders", type=Path, nargs="+")
    args = parser.parse_args()
    parts = get_parts()
    evidence = reference_evidence(parts)
    for folder in args.folders:
        report = json.loads((folder / "check.json").read_text())
        result = assess(folder / "copper-lane-study.mpd", report, parts, evidence)
        (folder / "reference-evidence.json").write_text(json.dumps(result, indent=2)+"\n")
        print(json.dumps(dict(folder=str(folder), supported=len(result["reference_supported"]),
                              unresolved=len(result["unresolved"]),
                              complete=result["all_finding_rows_available"], raw_verdict=result["raw_verdict"])))


if __name__ == "__main__":
    main()
