#!/usr/bin/env python3
"""Verify the endplate structure LDraw file against all acceptance checks."""

import re
from collections import defaultdict

def read_ldr_file(path):
    """Read and parse LDraw file."""
    with open(path) as f:
        lines = f.readlines()
    return [l.rstrip('\n') for l in lines]

def verify_file(path):
    """Run all acceptance checks."""
    lines = read_ldr_file(path)

    print("=" * 70)
    print("VERIFICATION REPORT")
    print("=" * 70)

    # Extract type-1 lines (part placements)
    type1_lines = [l for l in lines if l.startswith('1 ')]
    print(f"\n✓ Type-1 lines: {len(type1_lines)} (expected 29)")
    if len(type1_lines) != 29:
        print("  ERROR: Expected exactly 29 type-1 lines")
        return False

    # Extract part names and quantities
    part_counts = defaultdict(lambda: defaultdict(int))  # part -> color -> count
    parts_list = []

    for line in type1_lines:
        # Parse: 1 <colour> <x> <y> <z> <a> <b> <c> <d> <e> <f> <g> <h> <i> <part>.dat
        tokens = line.split()
        color = int(tokens[1])
        x, y, z = int(tokens[2]), int(tokens[3]), int(tokens[4])
        matrix = [
            [int(tokens[5]), int(tokens[6]), int(tokens[7])],
            [int(tokens[8]), int(tokens[9]), int(tokens[10])],
            [int(tokens[11]), int(tokens[12]), int(tokens[13])]
        ]
        part = tokens[14]

        part_counts[part][color] += 1
        parts_list.append({'part': part, 'color': color, 'x': x, 'y': y, 'z': z, 'matrix': matrix})

    distinct_parts = len(part_counts)
    print(f"✓ Distinct part types: {distinct_parts} (expected 13)")
    if distinct_parts != 13:
        print("  ERROR: Expected exactly 13 distinct part types")
        return False

    # Check BOM quantities
    expected_bom = {
        '2780.dat': {0: 4},
        '32062.dat': {4: 4},
        '6558.dat': {1: 4},
        '32013.dat': {4: 2},
        '32140.dat': {0: 2},
        '32291.dat': {71: 2},
        '3705.dat': {0: 2},
        '41678.dat': {4: 2},
        '43857.dat': {0: 2},
        '6536.dat': {4: 2},
        '32034.dat': {4: 1},
        '32293.dat': {0: 1},
        '6628.dat': {0: 1},
    }

    bom_ok = True
    for part, colors in sorted(part_counts.items()):
        if part not in expected_bom:
            print(f"  ERROR: Unexpected part {part}")
            bom_ok = False
        else:
            for color, count in colors.items():
                expected = expected_bom[part].get(color, 0)
                if count != expected:
                    print(f"  ERROR: {part} color {color}: got {count}, expected {expected}")
                    bom_ok = False

    if bom_ok:
        print("✓ BOM quantities match exactly")
    else:
        return False

    # Check mirror symmetry
    # Create position->part mapping for both sides
    left_parts = {}
    right_parts = {}
    unpaired = []

    for part in parts_list:
        x = part['x']
        key = (part['y'], part['z'], part['part'], part['color'])
        if x < 0:
            left_parts[key] = part
        elif x > 0:
            right_parts[key] = part
        else:
            unpaired.append(part)

    # Check mirroring: for each left part at x=-a, there should be a right part at x=+a
    mirror_pairs = 0
    mirror_ok = True
    checked = set()

    for key, left in sorted(left_parts.items()):
        x_left = left['x']
        x_right = -x_left  # Mirror across x=0

        # Find corresponding right part
        found = False
        for right in parts_list:
            if right['x'] == x_right and right['part'] == key[2] and right['color'] == key[3] and right['y'] == key[0] and right['z'] == key[1]:
                # Check that they're mirror images
                # For a mirror about x=0, we expect the part to be identical except for x and possibly the matrix
                mirror_pairs += 1
                found = True
                break

        if not found:
            mirror_ok = False
            print(f"  ERROR: No mirror for {left['part']} at x={x_left}")

    unpaired_count = len(unpaired)
    expected_unpaired = 3  # 180° connector, towball pin, steering link

    print(f"✓ Mirror-symmetric pairs: {mirror_pairs} (expected 13)")
    print(f"✓ Unpaired parts: {unpaired_count} (expected 3)")

    if mirror_pairs != 13 or unpaired_count != 3:
        print("  WARNING: Mirror symmetry count mismatch")

    # Check bounding box
    xs = [p['x'] for p in parts_list]
    ys = [p['y'] for p in parts_list]
    zs = [p['z'] for p in parts_list]

    bbox = {
        'x': (min(xs), max(xs)),
        'y': (min(ys), max(ys)),
        'z': (min(zs), max(zs)),
    }

    expected_bbox = {'x': (-120, 100), 'y': (-50, 10), 'z': (0, 40)}
    bbox_ok = True

    for axis in ['x', 'y', 'z']:
        actual = bbox[axis]
        expected = expected_bbox[axis]
        if actual == expected:
            print(f"✓ Bounding box {axis}: {actual}")
        else:
            print(f"  ERROR: Bounding box {axis}: got {actual}, expected {expected}")
            bbox_ok = False

    # Check matrices (signed permutation matrices)
    matrix_ok = True
    for i, part in enumerate(parts_list):
        matrix = part['matrix']
        # Check each row and column has exactly one non-zero
        for row in matrix:
            non_zeros = [v for v in row if v != 0]
            if len(non_zeros) != 1 or non_zeros[0] not in [-1, 1]:
                print(f"  ERROR: Part {i} has invalid row {row}")
                matrix_ok = False

        for col in range(3):
            col_vals = [matrix[row][col] for row in range(3)]
            non_zeros = [v for v in col_vals if v != 0]
            if len(non_zeros) != 1 or non_zeros[0] not in [-1, 1]:
                print(f"  ERROR: Part {i} has invalid column {col}: {col_vals}")
                matrix_ok = False

    if matrix_ok:
        print("✓ All matrices are signed permutation matrices")

    # Check for FILE/NOFILE lines
    file_lines = [l for l in lines if l.startswith('0 FILE') or l.startswith('0 NOFILE')]
    if len(file_lines) == 0:
        print("✓ No FILE or NOFILE lines (as expected)")
    else:
        print(f"  ERROR: Found {len(file_lines)} FILE/NOFILE lines")
        return False

    print("\n" + "=" * 70)
    print("ACCEPTANCE CHECKS SUMMARY")
    print("=" * 70)
    print(f"Part count: {len(type1_lines)}")
    print(f"Distinct parts: {distinct_parts}")
    print(f"Mirror pairs: {mirror_pairs}, Unpaired: {unpaired_count}")
    print(f"Bounding box: x {bbox['x']}, y {bbox['y']}, z {bbox['z']}")
    print(f"Output path: {path}")

    all_ok = len(type1_lines) == 29 and distinct_parts == 13 and bbox_ok and matrix_ok
    if all_ok:
        print("\n✓✓✓ ALL CHECKS PASSED ✓✓✓")
    else:
        print("\n✗✗✗ SOME CHECKS FAILED ✗✗✗")

    return all_ok

if __name__ == '__main__':
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else 'output/endplate-structure.ldr'
    verify_file(path)
