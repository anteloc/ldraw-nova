"""Small reproducible owl bust. Run from the toolkit root; no provider credentials."""

import json
from pathlib import Path

cells = {}  # Subject only: no display base, stand, plinth or ground plate.
for x in range(16):
    for y in range(12):
        for z in range(2, 19):
            if ((x - 7.5) / 6) ** 2 + ((y - 5.5) / 4.5) ** 2 + ((z - 9) / 9) ** 2 <= 1:
                cells[x, y, z] = 6
# Two upright ear tufts stay attached to the head.
for x in (4, 5, 10, 11):
    for y in range(4, 7):
        for z in range(14, 20):
            cells[x, y, z] = 6
# Pale face and dark eyes on the front-facing surface.
for x, y, z in list(cells):
    if z >= 11 and (x, y - 1, z) not in cells:
        cells[x, y, z] = 15
        if z in (13, 14) and x in (5, 6, 9, 10):
            cells[x, y, z] = 0
        if x in (7, 8) and z in (11, 12):
            cells[x, y, z] = 14
path = Path("output/sculpture-example/owl.voxels.json")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(
    json.dumps({"voxels": [[x, y, z, c] for (x, y, z), c in sorted(cells.items())]})
)
print(path)
