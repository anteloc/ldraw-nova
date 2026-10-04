# Adapted from BrickBuilderAI, copyright (c) 2026 Jake Johnson.
# MIT license: see LICENSE.brickbuilder.
"""Allowed rectangular footprints in studs and their LDraw part filenames."""

BRICK_PARTS = {
    (2, 4): "3001.DAT",
    (2, 6): "2456.DAT",
    (1, 4): "3010.DAT",
    (1, 2): "3004.DAT",
    (1, 1): "3005.DAT",
    (2, 2): "3003.DAT",
}


def part_for_dimensions(h: int, w: int) -> str:
    try:
        return BRICK_PARTS[tuple(sorted((h, w)))]
    except KeyError:
        raise ValueError(f"No brick part for dimensions: {h}x{w}") from None
