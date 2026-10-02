"""Review-only close-up renders through LeoCAD with custom cameras (same switches as `render`).

Usage: .venv/bin/python output/atlas-crane/tools/closeup.py MODEL.mpd OUTDIR name:tx,ty,tz:dx,dy,dz:dist[:fov] ...
  target (tx,ty,tz) in LDraw world units; the camera sits at target + dist * unit(dx,dy,dz).
These images are for design review; delivered previews come from `ldraw-agent render`.
"""
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

from ldraw_tools.common import library_path
from ldraw_tools.external import cad_source


def main():
    model, outdir = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix='.closeup-', dir=outdir) as temp:
        path, library, _ = cad_source(model, library_path(), temp)
        for spec in sys.argv[3:]:
            parts = spec.split(':')
            name = parts[0]
            t = np.array([float(v) for v in parts[1].split(',')])
            d = np.array([float(v) for v in parts[2].split(',')])
            dist = float(parts[3])
            fov = parts[4] if len(parts) > 4 else '30'
            cam = t + d / np.linalg.norm(d) * dist
            target = outdir / f'{name}.png'
            cmd = ['leocad', '-l', str(library), '-i', str(target), '-w', '1400', '-h', '1000',
                   '--aa-samples', '4', '--shading', 'full', '--line-width', '1', '--no-highlight',
                   '--no-fade-steps', str(Path(path).resolve()), '--fov', fov,
                   '--camera-position-ldraw', *map(str, (*cam, *t, 0, -1, 0))]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            print(name, 'ok' if target.exists() and not r.returncode else 'FAILED ' + r.stderr[-300:])


if __name__ == '__main__':
    main()
