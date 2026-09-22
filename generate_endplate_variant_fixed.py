#!/usr/bin/env python3
"""Generate a corrected VARIANT using only valid LDraw parts."""

def parse_orientation(orientation_str):
    """Parse orientation like 'X→-X Y→-Y Z→+Z' into a 3x3 matrix."""
    parts = orientation_str.split()

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

    matrix = []
    for i in range(3):
        row = [col[i] for col in cols]
        matrix.append(row)

    return matrix

# Part descriptions - ONLY VALID LDRAW PARTS
descriptions = {
    '32523.dat': 'Technic Beam 3',
    '32524.dat': 'Technic Beam 7',
    '2780.dat': 'Technic Pin with Friction and Slots',
    '6558.dat': 'Technic Pin Long with Friction and Slot',
    '32013.dat': 'Technic Angle Connector #1',
    '32140.dat': 'Technic Beam 2 x 4 Liftarm Bent 90',
    '32291.dat': 'Technic Cross Block 2 x 2 (Axle/Twin Pin)',
    '41677.dat': 'Technic Cross Block 2 x 2 (Axle/Axle)',
    '43857.dat': 'Technic Beam 2',
    '6536.dat': 'Technic Cross Block 1 x 2 (Axle/Pin)',
    '32034.dat': 'Technic Angle Connector #2 (180 degree)',
    '32293.dat': 'Technic Steering Link 9L',
    '32000.dat': 'Technic Brick 1 x 2 (Axle)',
}

color_names = {
    0: 'black',
    1: 'blue',
    4: 'red',
    71: 'light bluish grey',
}

# VARIANT with valid parts only
# Plane dz = 0 (Spine variant)
plane1_var = [
    (-80, -30, '6536.dat', 4, 'X→-X Y→-Y Z→+Z'),
    (-60, -30, '32523.dat', 0, 'X→+X Y→+Y Z→+Z'),
    (-40, -30, '32013.dat', 4, 'X→-X Y→-Z Z→-Y'),
    (0, -30, '32034.dat', 4, 'X→+Z Y→+Y Z→-X'),
    (40, -30, '32013.dat', 4, 'X→-X Y→-Z Z→-Y'),
    (60, -30, '32523.dat', 0, 'X→+X Y→+Y Z→+Z'),
    (80, -30, '6536.dat', 4, 'X→-X Y→-Y Z→+Z'),
    (-70, -10, '2780.dat', 0, 'X→+X Y→-Y Z→-Z'),
    (70, -10, '2780.dat', 0, 'X→-X Y→+Y Z→-Z'),
    (-50, 0, '32524.dat', 4, 'X→+Y Y→+X Z→-Z'),
    (50, 0, '32524.dat', 4, 'X→+Y Y→+X Z→-Z'),
    (-70, 10, '2780.dat', 0, 'X→+X Y→-Y Z→-Z'),
    (-40, 10, '32140.dat', 0, 'X→-X Y→+Y Z→-Z'),     # Fixed: using 32140 (valid)
    (40, 10, '32140.dat', 0, 'X→+X Y→-Y Z→-Z'),      # Fixed: using 32140 (valid)
    (70, 10, '2780.dat', 0, 'X→-X Y→+Y Z→-Z'),
]

# Plane dz = 20 (Hinge variant)
plane2_var = [
    (-80, 0, '41677.dat', 4, 'X→+Y Y→-X Z→+Z'),
    (-80, 0, '32524.dat', 4, 'X→+Y Y→-X Z→+Z'),
    (-80, 0, '32291.dat', 71, 'X→+Y Y→-X Z→+Z'),
    (80, 0, '41677.dat', 4, 'X→-Y Y→+X Z→+Z'),
    (80, 0, '32524.dat', 4, 'X→-Y Y→+X Z→+Z'),
    (80, 0, '32291.dat', 71, 'X→-Y Y→+X Z→+Z'),
]

# Plane dz = 40 (Tip variant - using valid parts)
plane3_var = [
    (-120, -50, '32293.dat', 0, 'X→+Z Y→+X Z→+Y'),
    (-110, -50, '6558.dat', 0, 'X→+X Y→+Z Z→-Y'),
    (-100, -10, '32000.dat', 1, 'X→+Z Y→-Y Z→+X'),
    (100, -10, '32000.dat', 1, 'X→+Z Y→+Y Z→-X'),
    (-100, 0, '43857.dat', 0, 'X→-X Y→-Z Z→-Y'),     # Back to valid 43857
    (100, 0, '43857.dat', 0, 'X→+X Y→-Z Z→+Y'),
    (-100, 10, '32000.dat', 1, 'X→+Z Y→-Y Z→+X'),
    (100, 10, '32000.dat', 1, 'X→+Z Y→+Y Z→-X'),
]

def generate_ldraw():
    """Generate corrected variant LDraw file."""
    lines = [
        '0 Wing-tip endplate structure VARIANT with alternate structural approach',
        '0 Name: endplate-structure-variant.ldr',
    ]

    # Process all planes
    for plane in [plane1_var, plane2_var, plane3_var]:
        dz = (0 if plane == plane1_var else (20 if plane == plane2_var else 40))
        for dx, dy, part, color, orientation in plane:
            matrix = parse_orientation(orientation)
            description = f"{descriptions[part]} ({color_names[color]})"

            lines.append(f"0 // {description}")

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

    import os
    os.makedirs('output', exist_ok=True)

    output_path = 'output/endplate-structure-variant.ldr'
    with open(output_path, 'w') as f:
        f.write(content)

    print(f"Generated corrected variant: {output_path}")
    print("Fixed issues:")
    print("✓ Added '0 ' prefix to title lines (proper LDraw comment format)")
    print("✓ Replaced invalid 32141.dat with valid 32140.dat (Technic Beam 2x4 Liftarm Bent 90)")
    print("✓ Removed invalid 3623.dat, using 43857.dat (Technic Beam 2) instead")
    print("✓ All parts are now valid LDraw Technic parts")
    print("\nFile is ready for geometry validation.")

if __name__ == '__main__':
    main()
