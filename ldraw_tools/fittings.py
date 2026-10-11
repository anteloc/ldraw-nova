"""Narrow calibration for inspected, versioned part fittings.

Only exact part identities, complete source hashes and relative poses qualify.
Matched pairs remain in reports; other collisions and transforms are checked.
"""
from functools import lru_cache
import json

import numpy as np

from .common import DATA


@lru_cache(maxsize=1)
def catalog():
    return json.loads((DATA / "fittings.json").read_text())


def fitting(first, second):
    for rule in catalog()["fittings"]:
        a, b = (first, second) if first["code"] == rule["frame"] else (second, first)
        if (a["code"], b["code"]) != (rule["frame"], rule["insert"]):
            continue
        if any(r["status"] != "exact" or r["local"].data.missing for r in (a, b)):
            continue
        if any(r["local"].data.source_sha256 != rule["source_sha256"][r["code"]] for r in (a, b)):
            continue
        if (np.allclose(a["R"].T @ (b["t"] - a["t"]), rule["offset"], atol=0.01, rtol=0)
                and np.allclose(a["R"].T @ b["R"], rule["rotation"], atol=1e-6, rtol=0)):
            return rule
    return None
