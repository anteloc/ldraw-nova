"""Expand an MPD into physical inventory, optionally checking a parts palette.

Run with the toolkit interpreter: python -m ldraw_tools.catalog_inventory
MODEL LIBRARY [--palette CSV]. Unknown dependencies and custom parts fail closed.
"""
from __future__ import annotations

import argparse
import json
import math
import tempfile
from collections import Counter
from pathlib import Path

from .parts_catalog import PartsCatalog, normalize_part_id, reject_custom_parts


def check_rigid_transform(rows) -> None:
    """Accept rounded rotations, rejecting resized or sheared palette parts."""
    for i in range(3):
        for j in range(3):
            dot = sum(rows[k][i] * rows[k][j] for k in range(3))
            if not math.isfinite(dot) or abs(dot - (1 if i == j else 0)) > 1e-4:
                raise ValueError("Palette parts must use rigid rotations")
    a, b, c = rows
    determinant = (a[0] * (b[1] * c[2] - b[2] * c[1])
                   - a[1] * (b[0] * c[2] - b[2] * c[0])
                   + a[2] * (b[0] * c[1] - b[1] * c[0]))
    if determinant < 0:
        raise ValueError("Palette parts cannot be mirrored")


def model_inventory(source: Path, library: Path) -> dict[tuple[str, int], int]:
    from . import common, document

    if source.stat().st_size > 32 * 1024 * 1024:
        raise ValueError("Model exceeds the 32 MB inventory limit")
    reject_custom_parts(source.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="nova-inventory-") as temporary:
        original_cache = common.CACHE, document.CACHE
        common.CACHE = document.CACHE = Path(temporary) / "cache"
        try:
            library_parts = common.get_parts(library)
            physical, _ = document.physical_context(document.parse_source(source), library_parts)
            inventory = Counter()
            for index, occurrence in enumerate(physical.iter_occurrences()):
                if index >= 100_000:
                    raise ValueError("Model exceeds the 100,000 physical parts limit")
                if not occurrence.reference.lower().endswith(".dat"):
                    raise ValueError("Unresolved dependency in physical inventory")
                values = [occurrence.position.x, occurrence.position.y, occurrence.position.z,
                          *(number for row in occurrence.matrix.rows for number in row)]
                if not all(math.isfinite(float(number)) for number in values):
                    raise ValueError("Invalid physical placement")
                check_rigid_transform(occurrence.matrix.rows)
                part_id = normalize_part_id(occurrence.reference)
                if part_id not in library_parts.by_code:
                    raise ValueError(f"Unknown library part: {occurrence.reference}")
                inventory[(part_id, occurrence.colour.code)] += 1
            if not inventory:
                raise ValueError("Model contains no physical parts")
            return dict(inventory)
        finally:
            common.CACHE, document.CACHE = original_cache


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("library", type=Path)
    parser.add_argument("--palette", "--catalog", dest="palette", type=Path,
                        help="Require parts/colors and quantities from this CSV, LDR, XML, or Studio IO inventory")
    args = parser.parse_args()
    inventory = model_inventory(args.source, args.library)
    if args.palette:
        PartsCatalog.load(args.palette).validate(inventory)
    print(json.dumps([[part, color, quantity] for (part, color), quantity in inventory.items()]))


if __name__ == "__main__":
    main()
