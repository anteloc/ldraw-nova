"""Hero renders of the Sakura Garden: lower cameras and quieter part edges.

The standard review views come from `ldraw-agent render`; these extra shots
use LeoCAD's automated edge colouring so small parts keep their colour.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import hashlib
import json
import subprocess
import sys

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parents[1]))
from ldraw_tools.common import library_path  # noqa: E402

SHOTS = {
    # name: camera xyz, target xyz (LDraw: -Y up, -Z front)
    'hero-pond': ((-1500, -1050, -1650), (40, -230, 40)),
    'hero-axis': ((700, -700, -2100), (200, -300, 0)),
    'hero-pagoda': ((-900, -500, -1100), (200, -420, 200)),
    'hero-high': ((1500, -2100, -1800), (0, -150, 0)),
    'hero-bridge': ((-760, -330, -900), (-210, -70, -250)),
    'hero-torii': ((520, -140, -900), (220, -150, -300)),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', default=str(OUT / 'sakura-garden.mpd'))
    ap.add_argument('--outdir', default=str(OUT / 'hero'))
    ap.add_argument('--shots', nargs='*', default=list(SHOTS))
    args = ap.parse_args()
    source = Path(args.source).resolve()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    manifest = dict(renderer='LeoCAD', source=str(source.relative_to(OUT.parents[1])),
                    source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                    width=1600, height=1200, fov=30, shading='full', line_width=.5,
                    automated_edge_contrast=.3, shots={})
    for name in args.shots:
        camera, target = SHOTS[name]
        with TemporaryDirectory(prefix='.hero-', dir=outdir) as temp:
            image = Path(temp) / f'{name}.png'
            command = ['leocad', '-l', str(library_path()), '-i', str(image),
                       '-w', '1600', '-h', '1200', '--aa-samples', '8',
                       '--shading', 'full', '--line-width', '0.5',
                       '--automate-edge-color', '--color-contrast', '0.3',
                       '--no-highlight', '--no-fade-steps', '--fov', '30',
                       '--camera-position-ldraw', *map(str, (*camera, *target, 0, -1, 0)),
                       str(source)]
            result = subprocess.run(command, capture_output=True, text=True, timeout=240)
            if result.returncode or not image.is_file():
                raise RuntimeError(result.stdout + '\n' + result.stderr)
            image.replace(outdir / f'{name}.png')
        manifest['shots'][name] = dict(image=f'{name}.png', camera_ldraw=camera, target_ldraw=target)
        print(outdir / f'{name}.png')
    (outdir / 'hero-render.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
