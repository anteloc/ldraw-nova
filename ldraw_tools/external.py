"""Use the installed CAD renderers with argument lists, timeouts and unique files."""
from __future__ import annotations

import subprocess
import math
from pathlib import Path
from tempfile import TemporaryDirectory


def cad_check(path, library, *, timeout=90):
    with TemporaryDirectory(prefix="ldraw-check-") as temp:
        render(path, library, temp, views=("home",), timeout=timeout)
        return dict(tool="LeoCAD", passed=True, snapshot_created=True, bom_created=True,
                    note="Import/export smoke test; Python diagnostics provide syntax/reference checks. Temporary artifacts removed after checking.")


def prepare_glb(path, library, output, parts, *, timeout=180):
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".glb-", dir=output.parent) as temp:
        descriptions = Path(temp) / "descriptions.tsv"
        descriptions.write_text("".join(f"{code}.dat\t{description}\n" for code, description in parts.by_code.items()), encoding="utf-8")
        target = Path(temp) / output.name
        command = ["mpd2glb.sh", "-l", str(library), "-c", "draco", "--descriptions", str(descriptions),
                   "--map-color", "16,Pearl_Dark_Grey", "-o", str(target), str(Path(path).resolve())]
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        if result.returncode or not target.exists():
            raise ValueError(f"GLB conversion failed: {result.stdout}\n{result.stderr}")
        target.replace(output)
    return dict(output=str(output), log=(result.stdout + "\n" + result.stderr)[-8000:],
                note="Preview maps unresolved colour 16 to Pearl Dark Grey. In source, 16 means inherited current colour. MPD remains authoritative.")


def render(path, library, outdir, *, views=("home", "top", "front"), timeout=90, bounds=None):
    outdir = Path(outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    results = []
    # Unique temporary outputs ensure an old artifact cannot make a failed run pass.
    with TemporaryDirectory(prefix=".render-", dir=outdir) as temp:
        for view in views:
            if view not in {"home", "front", "back", "left", "right", "top", "bottom"}:
                raise ValueError(f"Unknown view {view}")
            target = Path(temp) / f"{view}.png"
            command = ["leocad", "-l", str(library), "-i", str(target), "-w", "1000", "-h", "800", str(Path(path).resolve())]
            if bounds is None:
                command += ["--viewpoint", view]
            if bounds is not None:
                # Frame a conservative bounding sphere, independent of saved viewport zoom.
                low, high = bounds.min, bounds.max
                center = [(getattr(low, axis) + getattr(high, axis)) / 2 for axis in "xyz"]
                radius = max(1.0, math.sqrt(sum((getattr(high, axis)-getattr(low, axis))**2 for axis in "xyz")) / 2)
                direction = {"home": (1,-1,-1), "front": (0,0,-1), "back": (0,0,1),
                             "left": (-1,0,0), "right": (1,0,0), "top": (0,-1,0), "bottom": (0,1,0)}[view]
                distance = radius / math.sin(math.radians(15)) * 1.15
                norm = math.sqrt(sum(v*v for v in direction))
                camera = [c + v / norm * distance for c,v in zip(center,direction)]
                up = (0,0,1) if view == "top" else (0,0,-1) if view == "bottom" else (0,-1,0)
                command += ["--fov", "30", "--camera-position-ldraw", *map(str, (*camera, *center, *up))]
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
            if result.returncode or not target.exists():
                raise ValueError(f"LeoCAD render failed: {result.stdout}\n{result.stderr}")
            destination = outdir / target.name
            target.replace(destination)
            results.append(str(destination))
        bom = Path(temp) / "leocad-bom.csv"
        result = subprocess.run(["leocad", "-l", str(library), "-csv", str(bom), str(Path(path).resolve())], capture_output=True, text=True, timeout=timeout)
        if result.returncode or not bom.exists():
            raise ValueError(f"LeoCAD BOM failed: {result.stdout}\n{result.stderr}")
        bom.replace(outdir / bom.name)
    return dict(images=results, bom=str(outdir / "leocad-bom.csv"), visual_review="required: open and inspect the images")
