#!/usr/bin/env python3
"""Generate LDraw endplate structure from specification."""

def parse_orientation(orientation_str):
    """Parse orientation like 'X→-X Y→-Y Z→+Z' into a 3x3 matrix.

    The orientation specifies where each local axis points in world space.
    The 3x3 matrix has local X as column 1, local Y as column 2, local Z as column 3.
    """
    parts = orientation_str.split()

    # Map of direction specification to world vector
    directions = {
        'X→+X': (1, 0, 0), 'X→-X': (-1, 0, 0),
        'X→+Y': (0, 1, 0), 'X→-Y': (0, -1, 0),
        'X→+Z': (0, 0, 1), 'X→-Z': (0, 0, -1),
        'Y→+X': (1, 0, 0), 'Y→-X': (-1, 0, 0),
        'Y→+Y': (0, 1, 0), 'Y→-Y': (0, -1, 0),
        'Y→+Z': (0, 0, 1), 'Y→-Z': (0, 0, -1),
        'Z→+X': (1, 0, 0), 'Z→-X': (-1, 0, 0),
        'Z→+Y': (0, 1, 0), 'Z→-Y': (0, -1, 0),
        'Z→+Z': (0, 0, 1), 'Z→-Z': (0, 0, -1),
    }

    cols = [directions[p] for p in parts]

    # Transpose: rows are formed from the vectors
    matrix = []
    for i in range(3):
        row = [col[i] for col in cols]
        matrix.append(row)

    return matrix

# Part descriptions (from BOM)
descriptions = {
    '2780.dat': 'Technic Pin with Friction and Slots',
    '32062.dat': 'Technic Axle 2 Notched',
    '6558.dat': 'Technic Pin Long with Friction and Slot',
    '32013.dat': 'Technic Angle Connector #1',
    '32140.dat': 'Technic Beam 2 x 4 Liftarm Bent 90',
    '32291.dat': 'Technic Cross Block 2 x 2 (Axle/Twin Pin)',
    '3705.dat': 'Technic Axle 4',
    '41678.dat': 'Technic Cross Block 2 x 2 Split (Axle/Twin Pin)',
    '43857.dat': 'Technic Beam 2',
    '6536.dat': 'Technic Cross Block 1 x 2 (Axle/Pin)',
    '32034.dat': 'Technic Angle Connector #2 (180 degree)',
    '32293.dat': 'Technic Steering Link 9L',
    '6628.dat': 'Technic Pin Towball with Friction',
}

# Color names
color_names = {
    0: 'black',
    1: 'blue',
    4: 'red',
    71: 'light bluish grey',
}

# Plane dz = 0 (15 parts, in order from spec)
plane1 = [
    (-80, -30, '6536.dat', 4, 'X→-X Y→-Y Z→+Z'),
    (-50, -30, '3705.dat', 0, 'X→-X Y→+Y Z→-Z'),
    (-40, -30, '32013.dat', 4, 'X→-X Y→-Z Z→-Y'),
    (0, -30, '32034.dat', 4, 'X→+Z Y→+Y Z→-X'),
    (40, -30, '32013.dat', 4, 'X→-X Y→-Z Z→-Y'),
    (50, -30, '3705.dat', 0, 'X→-X Y→+Y Z→-Z'),
    (80, -30, '6536.dat', 4, 'X→-X Y→-Y Z→+Z'),
    (-70, -10, '2780.dat', 0, 'X→+X Y→-Y Z→-Z'),
    (70, -10, '2780.dat', 0, 'X→-X Y→+Y Z→-Z'),
    (-40, 0, '32062.dat', 4, 'X→+Y Y→+X Z→-Z'),
    (40, 0, '32062.dat', 4, 'X→+Y Y→+X Z→-Z'),
    (-70, 10, '2780.dat', 0, 'X→+X Y→-Y Z→-Z'),
    (-40, 10, '32140.dat', 0, 'X→-X Y→+Y Z→-Z'),
    (40, 10, '32140.dat', 0, 'X→+X Y→-Y Z→-Z'),
    (70, 10, '2780.dat', 0, 'X→-X Y→+Y Z→-Z'),
]

# Plane dz = 20 (6 parts, in order from spec)
plane2 = [
    (-80, 0, '41678.dat', 4, 'X→+Y Y→-X Z→+Z'),
    (-80, 0, '32062.dat', 4, 'X→+Y Y→-X Z→+Z'),
    (-80, 0, '32291.dat', 71, 'X→+Y Y→-X Z→+Z'),
    (80, 0, '41678.dat', 4, 'X→-Y Y→+X Z→+Z'),
    (80, 0, '32062.dat', 4, 'X→-Y Y→+X Z→+Z'),
    (80, 0, '32291.dat', 71, 'X→-Y Y→+X Z→+Z'),
]

# Plane dz = 40 (8 parts, in order from spec)
plane3 = [
    (-120, -50, '32293.dat', 0, 'X→+Z Y→+X Z→+Y'),
    (-110, -50, '6628.dat', 0, 'X→+X Y→+Z Z→-Y'),
    (-100, -10, '6558.dat', 1, 'X→+Z Y→-Y Z→+X'),
    (100, -10, '6558.dat', 1, 'X→+Z Y→+Y Z→-X'),
    (-100, 0, '43857.dat', 0, 'X→-X Y→-Z Z→-Y'),
    (100, 0, '43857.dat', 0, 'X→+X Y→-Z Z→+Y'),
    (-100, 10, '6558.dat', 1, 'X→+Z Y→-Y Z→+X'),
    (100, 10, '6558.dat', 1, 'X→+Z Y→+Y Z→-X'),
]

def generate_ldraw():
    """Generate LDraw file content in order of specification."""
    lines = [
        'Wing-tip endplate structure with steering link stub',
        'Name: endplate-structure.ldr',
    ]

    # Process all planes in order: plane 1, plane 2, plane 3
    for plane in [plane1, plane2, plane3]:
        for dx, dy, dz_offset, part, color, orientation in [
            (p[0], p[1], (0 if plane == plane1 else (20 if plane == plane2 else 40)), p[2], p[3], p[4])
            for p in plane
        ]:
            dz = dz_offset
            matrix = parse_orientation(orientation)
            description = f"{descriptions[part]} ({color_names[color]})"

            lines.append(f"0 // {description}")

            # Format the LDraw type-1 line
            # 1 <colour> <x> <y> <z> <a> <b> <c> <d> <e> <f> <g> <h> <i> <part>.dat
            ldraw_line = (
                f"1 {color} "
                f"{dx} {dy} {dz} "
                f"{matrix[0][0]} {matrix[0][1]} {matrix[0][2]} "
                f"{matrix[1][0]} {matrix[1][1]} {matrix[1][2]} "
                f"{matrix[2][0]} {matrix[2][1]} {matrix[2][2]} "
                f"{part}"
            )
            lines.append(ldraw_line)

    return '\n'.join(lines)

def main():
    content = generate_ldraw()

    # Write to output directory
    import os
    os.makedirs('output', exist_ok=True)

    output_path = 'output/endplate-structure.ldr'
    with open(output_path, 'w') as f:
        f.write(content)

    print(f"Generated {output_path}")
    print(f"\nFile content preview (first 50 lines):")
    print('\n'.join(content.split('\n')[:50]))

if __name__ == '__main__':
    main()
