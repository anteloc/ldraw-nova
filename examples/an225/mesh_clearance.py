#!/usr/bin/env python3
"""Targeted material-intersection check for selected part pairs (review aid).

The toolkit reports AABB/oriented-box candidates for irregular parts. This script
expands the two parts' real library triangles (types 3/4 through nested type-1
references, read-only), places them with the MPD's world transforms from an
`inspect --detail full` report, and tests every edge of each mesh against the
other mesh's triangles. A proper crossing (both endpoints strictly on opposite
sides, intersection strictly inside the triangle) is material interpenetration;
coplanar/touching contact is not counted. `max_penetration_ldu` is the largest
shallower-endpoint depth of a crossing edge: hundredths of an LDU on a rotating pin
indicate faceted coincident cylinders, not interference. It is evidence for the
listed pairs only, not a general solid-modelling proof.

    .venv/bin/python examples/an225/mesh_clearance.py REPORT.json IDX_A IDX_B [IDX_A IDX_B ...]
"""
from __future__ import annotations

import json
import os
import sys
from functools import lru_cache

import numpy as np

LIB = os.environ.get('LDRAW_DIR', str(__import__('pathlib').Path(__file__).resolve().parents[3] / 'ldraw-lib' / 'ldraw'))
EPS = 0.02  # LDU; crossings closer than this to a surface count as contact


def find(name):
    name = name.replace('\\', '/').lower()
    for d in ('parts', 'p', 'parts/s', 'p/48', 'p/8'):
        f = os.path.join(LIB, d, name)
        if os.path.exists(f):
            return f
    raise FileNotFoundError(name)


@lru_cache(maxsize=None)
def triangles(name):
    tris = []
    for line in open(find(name), errors='ignore'):
        t = line.split()
        if not t:
            continue
        if t[0] == '1' and len(t) >= 15:
            x, y, z, a, b, c, d, e, f, g, h, i = map(float, t[2:14])
            M = np.array([[a, b, c], [d, e, f], [g, h, i]])
            try:
                sub = triangles(' '.join(t[14:]))
            except FileNotFoundError:
                continue
            if len(sub):
                tris.append(sub @ M.T + np.array([x, y, z]))
        elif t[0] == '3' and len(t) >= 11:
            tris.append(np.array(list(map(float, t[2:11]))).reshape(1, 3, 3))
        elif t[0] == '4' and len(t) >= 14:
            q = np.array(list(map(float, t[2:14]))).reshape(4, 3)
            tris.append(np.stack([q[[0, 1, 2]], q[[0, 2, 3]]]))
    return np.concatenate(tris) if tris else np.zeros((0, 3, 3))


def world(inst):
    M = np.array(inst['matrix'], float)
    return triangles(inst['part']) @ M.T + np.array(inst['position'], float)


def crossings(A, B):
    """Count edges of A that properly cross triangles of B."""
    lo_b, hi_b = B.min(axis=1), B.max(axis=1)
    count = 0
    depth = 0.0
    examples = []
    for tri in A:
        for p, q in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            lo, hi = np.minimum(p, q) - EPS, np.maximum(p, q) + EPS
            sel = np.all((hi_b >= lo) & (lo_b <= hi), axis=1)
            if not sel.any():
                continue
            for t in B[sel]:
                n = np.cross(t[1] - t[0], t[2] - t[0])
                norm = np.linalg.norm(n)
                if norm < 1e-9:
                    continue
                n /= norm
                dp, dq = np.dot(p - t[0], n), np.dot(q - t[0], n)
                if not (dp > EPS and dq < -EPS or dp < -EPS and dq > EPS):
                    continue
                x = p + (q - p) * (dp / (dp - dq))
                # Barycentric inside test with a margin away from the triangle's edges.
                v0, v1, v2 = t[1] - t[0], t[2] - t[0], x - t[0]
                d00, d01, d11 = v0 @ v0, v0 @ v1, v1 @ v1
                d20, d21 = v2 @ v0, v2 @ v1
                den = d00 * d11 - d01 * d01
                v = (d11 * d20 - d01 * d21) / den
                w = (d00 * d21 - d01 * d20) / den
                margin = EPS / max(np.sqrt(d00), np.sqrt(d11))
                if v > margin and w > margin and v + w < 1 - margin:
                    count += 1
                    depth = max(depth, min(abs(dp), abs(dq)))
                    if len(examples) < 3:
                        examples.append([round(float(c), 2) for c in x])
    return count, examples, depth


def main(report, *pairs):
    g = json.load(open(report))['geometry']
    inst = {i['index']: i for i in g['instances']}
    results = []
    for a, b in zip(pairs[::2], pairs[1::2]):
        A, B = world(inst[int(a)]), world(inst[int(b)])
        n1, e1, d1 = crossings(A, B)
        n2, e2, d2 = crossings(B, A)
        results.append(dict(a=int(a), b=int(b), parts=[inst[int(a)]['part'], inst[int(b)]['part']],
                            sections=[inst[int(a)]['section'], inst[int(b)]['section']],
                            triangles=[len(A), len(B)], crossing_edges=n1 + n2,
                            max_penetration_ldu=round(max(d1, d2), 3), examples=(e1 + e2)[:3]))
        print(json.dumps(results[-1]))
    return results


if __name__ == '__main__':
    main(*sys.argv[1:])
