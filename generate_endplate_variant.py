#!/usr/bin/env python3
"""Generate a VARIANT of the wing-tip endplate structure using different parts."""

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

# Part descriptions
descriptions = {
    '32523.dat': 'Technic Axle 3',
    '32524.dat': 'Technic Axle 5',
    '2780.dat': 'Technic Pin with Friction and Slots',
    '6558.dat': 'Technic Pin Long with Friction and Slot',
    '32014.dat': 'Technic Angle Connector #6',
    '32141.dat': 'Technic Beam 2 x 2 Bent 45 Degrees, Liftarm',
    '32291.dat': 'Technic Cross Block 2 x 2 (Axle/Twin Pin)',
    '41677.dat': 'Technic Cross Block 2 x 2 (Axle/Axle)',
    '32000.dat': 'Technic Brick 1 x 2 (Axle)',
    '6536.dat': 'Technic Cross Block 1 x 2 (Axle/Pin)',
    '32034.dat': 'Technic Angle Connector #2 (180 degree)',
    '32293.dat': 'Technic Steering Link 9L',
    '3623.dat': 'Plate 1 x 2',
}

color_names = {
    0: 'black',
    1: 'blue',
    4: 'red',
    71: 'light bluish grey',
}

# VARIANT: Different structural approach - using alternate parts and arrangement
# Still maintains symmetry, steering link asymmetry, and similar envelope

# Plane dz = 0 (Spine variant - using different cross blocks and pins)
plane1_var = [
    (-80, -30, '6536.dat', 4, 'X→-X Y→-Y Z→+Z'),    # End cross block (different placement)
    (-60, -30, '32523.dat', 0, 'X→+X Y→+Y Z→+Z'),    # Shorter axle variant
    (-40, -30, '32014.dat', 4, 'X→-X Y→-Z Z→-Y'),    # Different angle connector
    (0, -30, '32034.dat', 4, 'X→+Z Y→+Y Z→-X'),      # Central connector (unchanged)
    (40, -30, '32014.dat', 4, 'X→-X Y→-Z Z→-Y'),     # Variant mirror
    (60, -30, '32523.dat', 0, 'X→+X Y→+Y Z→+Z'),     # Variant mirror
    (80, -30, '6536.dat', 4, 'X→-X Y→-Y Z→+Z'),      # Variant mirror
    (-70, -10, '2780.dat', 0, 'X→+X Y→-Y Z→-Z'),     # Pin placement (unchanged)
    (70, -10, '2780.dat', 0, 'X→-X Y→+Y Z→-Z'),      # Variant mirror
    (-50, 0, '32524.dat', 4, 'X→+Y Y→+X Z→-Z'),      # Longer axle variant
    (50, 0, '32524.dat', 4, 'X→+Y Y→+X Z→-Z'),       # Variant mirror
    (-70, 10, '2780.dat', 0, 'X→+X Y→-Y Z→-Z'),      # Upper pin
    (-40, 10, '32141.dat', 0, 'X→-X Y→+Y Z→-Z'),     # Different beam (45° liftarm)
    (40, 10, '32141.dat', 0, 'X→+X Y→-Y Z→-Z'),      # Variant mirror
    (70, 10, '2780.dat', 0, 'X→-X Y→+Y Z→-Z'),       # Variant mirror
]

# Plane dz = 20 (Hinge variant - using different cross blocks)
plane2_var = [
    (-80, 0, '41677.dat', 4, 'X→+Y Y→-X Z→+Z'),      # Axle/axle variant
    (-80, 0, '32524.dat', 4, 'X→+Y Y→-X Z→+Z'),      # Longer axle variant
    (-80, 0, '32291.dat', 71, 'X→+Y Y→-X Z→+Z'),     # Standard cross block
    (80, 0, '41677.dat', 4, 'X→-Y Y→+X Z→+Z'),       # Variant mirror
    (80, 0, '32524.dat', 4, 'X→-Y Y→+X Z→+Z'),       # Variant mirror
    (80, 0, '32291.dat', 71, 'X→-Y Y→+X Z→+Z'),      # Variant mirror
]

# Plane dz = 40 (Tip variant - using different beam and pin configuration)
plane3_var = [
    (-120, -50, '32293.dat', 0, 'X→+Z Y→+X Z→+Y'),   # Steering link (unchanged)
    (-110, -50, '6558.dat', 0, 'X→+X Y→+Z Z→-Y'),    # Alternative to towball: long pin
    (-100, -10, '32000.dat', 1, 'X→+Z Y→-Y Z→+X'),   # Technic brick variant (lighter)
    (100, -10, '32000.dat', 1, 'X→+Z Y→+Y Z→-X'),    # Variant mirror
    (-100, 0, '3623.dat', 0, 'X→-X Y→-Z Z→-Y'),      # Plate variant (different approach)
    (100, 0, '3623.dat', 0, 'X→+X Y→-Z Z→+Y'),       # Variant mirror
    (-100, 10, '32000.dat', 1, 'X→+Z Y→-Y Z→+X'),    # Technic brick upper variant
    (100, 10, '32000.dat', 1, 'X→+Z Y→+Y Z→-X'),     # Variant mirror
]

def generate_ldraw():
    """Generate variant LDraw file content."""
    lines = [
        'Wing-tip endplate structure VARIANT with alternate structural approach',
        'Name: endplate-structure-variant.ldr',
    ]

    # Process all planes in order
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

    print(f"Generated variant: {output_path}")
    print(f"\nVariant design features:")
    print("- Different cross blocks (41677 instead of 41678)")
    print("- Alternate axle lengths (32523, 32524 instead of 3705, 32062)")
    print("- Different angle connector (32014 instead of 32013)")
    print("- Alternate beam design (32141 bent 45° instead of bent 90°)")
    print("- Technic brick elements (32000) instead of only pins")
    print("- Plate element (3623) in place of beam at tip")
    print("- Long pin in steering mechanism (6558 instead of 6628)")
    print("\nFirst 50 lines:")
    print('\n'.join(content.split('\n')[:50]))

if __name__ == '__main__':
    main()
