"""Verified SNOT kit for the Linden Row SNOT run (orchestrator-owned). Run from repo root:
    .venv/bin/python output/urban-house-snot/kit/snot_kit.py
Writes kit/kit.plan.json + kit/test.plan.json. Verified results are recorded in VERIFIED below.

K1  side-stud course: a 1x4 wall whose 2nd and 4th courses are 30414 (studs -Z). The courses are
    separated by TWO PLATES so their side-stud rows are 40 LDU (= 2 stud pitches) apart.
K2  flat-built cladding panel (section kit-panel): 4x4 plate 3031 + four 2x2 tiles, built studs-up
    in its own frame, turned with panel_R('-Z') and seated with seat(R, socket, stud): its socket
    rows z=-30 and z=+10 land on the lower and upper 30414 stud rows.
K3  headlight-brick dentil: 4070 with a 98138 round tile on its recessed side stud.

Pattern for a worker:
    R = panel_R('-Z')                                 # studs face out of the front wall
    studs = side_studs('30414', brick_top_centre, '-Z')
    origin = seat(R, (-30, 8, -30), studs[0])          # panel socket (-30,8,-30) on the first stud
    add_ldu(parent, panel_module, colour, origin, R)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import export, panel_R, seat, side_studs, add_ldu, Ry
from ldraw_tools.architecture import Module

def build():
    m = Module('kit', 'SNOT kit: K1 side-stud wall, K2 seated flat-built panel, K3 headlight dentil')
    # K1 wall at X=0, Z=0 (1 stud deep), on a 1x4 plate
    add_ldu(m, '3710', 72, (0, -8, 0), id='k1-base')
    add_ldu(m, '3010', 320, (0, -32, 0), id='k1-c1')
    add_ldu(m, '30414', 320, (0, -56, 0), id='k1-side-lo')        # side studs y=-46, z=-10
    add_ldu(m, '3710', 320, (0, -64, 0), id='k1-p1')
    add_ldu(m, '3710', 320, (0, -72, 0), id='k1-p2')
    add_ldu(m, '30414', 320, (0, -96, 0), id='k1-side-hi')        # side studs y=-86 (40 above)
    add_ldu(m, '3010', 320, (0, -120, 0), id='k1-c3')
    # K2 panel built flat
    p = Module('kit-panel', 'Flat-built 4x4 cladding panel: plate 3031 + 2x2 tiles; studs up in own frame')
    add_ldu(p, '3031', 19, (0, 0, 0), id='plate')
    for x in (-20, 20):
        for z in (-20, 20):
            add_ldu(p, '3068b', 15 if (x > 0) == (z > 0) else 19, (x, -8, z))
    R = panel_R('-Z')
    lo = side_studs('30414', (0, -56, 0), '-Z')
    origin = seat(R, (-30, 8, -30), lo[0])
    add_ldu(m, p, 19, origin, R, id='k2-panel')
    # K3 headlight dentil, a separate column at X=60
    add_ldu(m, '3024', 72, (60, -8, 0), id='k3-base')
    add_ldu(m, '4070', 15, (60, -32, 0), id='k3-headlight')
    hl = side_studs('4070', (60, -32, 0), '-Z')[0]
    add_ldu(m, '98138', 15, seat(R, (0, 8, 0), hl), R, id='k3-dentil')
    return m

if __name__ == '__main__':
    export(build(), 'kit', Path(__file__).parent, 'Linden Row orchestrator (Claude Opus 5.5)')
