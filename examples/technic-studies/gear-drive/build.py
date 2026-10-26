"""Original 8:24 supported spur drive; run from any directory with Nova's Python."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from ldraw_tools.builder import build_plan, rotation  # noqa: E402
from ldraw_tools.common import get_parts, jsonable  # noqa: E402


def construction():
    def part(name, ref, colour, at, purpose, matrix=None):
        p = dict(id=name, ref=ref, colour=colour, at=at, purpose=purpose)
        if matrix is not None:
            p["matrix"] = matrix
        return p

    supports = [[part("base", "3958.dat", 71, [20, 0, 0], "6 x 6 base")]]
    for y in (-24, -48):
        supports.append(
            [
                part(
                    f"rail_{y}_{z}",
                    "3009.dat",
                    1,
                    [20, y, z],
                    "1 x 6 rail bonded across both bearing towers",
                )
                for z in (-40, 40)
            ]
        )
    supports.append(
        [
            part(
                f"bearing_{x}_{z}",
                "3700.dat",
                1,
                [x, -72, z],
                "Round bearing; axle may rotate, hole centre is Y + 10",
            )
            for z in (-40, 40)
            for x in (0, 40)
        ]
    )
    supports.append(
        [
            part(
                f"cap_{z}",
                "3666.dat",
                1,
                [20, -80, z],
                "1 x 6 cap binds the two bearing bricks",
            )
            for z in (-40, 40)
        ]
    )

    def shaft(name, gear, colour):
        pieces = [
            part(
                "axle",
                "3707.dat",
                0,
                [0, 0, 0],
                "8L keyed shaft along Z",
                [[0, 0, -1], [0, 1, 0], [1, 0, 0]],
            ),
            part(
                "gear", gear, colour, [0, 0, 0], "Keyed spur gear, tooth midplane Z = 0"
            ),
        ]
        pieces += [
            part(
                f"inner_{z}",
                "32123a.dat",
                14,
                [0, 0, z],
                "Half bush retains gear against its 20-LDU hub",
            )
            for z in (-15, 15)
        ]
        pieces += [
            part(
                f"outer_{z}",
                "3713.dat",
                4,
                [0, 0, z],
                "Full bush retains shaft outside bearing rail",
            )
            for z in (-60, 60)
        ]
        return dict(
            name=name,
            description="Rigid shaft with keyed gear, two inner gear stops and two outer retaining bushes",
            steps=[pieces],
        )

    return dict(
        version=1,
        author="LDraw Nova / Mecha original example",
        sections=[
            dict(
                name="gear-drive.ldr",
                description="Supported 8:24 spur reduction; one input drives a slower reverse output on two retained shafts",
                steps=[
                    [
                        part(
                            "frame",
                            "frame.ldr",
                            16,
                            [0, 0, 0],
                            "Fixed base and two bearing rails",
                        )
                    ],
                    [
                        part(
                            "input", "input.ldr", 16, [0, -62, 0], "8-tooth input shaft"
                        ),
                        part(
                            "output",
                            "output.ldr",
                            16,
                            [40, -62, 0],
                            "24-tooth output shaft; half-tooth phase preserves cross-hole alignment",
                            jsonable(rotation("z", 7.5)),
                        ),
                    ],
                ],
            ),
            dict(
                name="frame.ldr",
                description="Fixed base, stacked rails, four round bearings and bonded top caps; holes have centres at Y -62 and Z +/-40",
                steps=supports,
            ),
            shaft("input.ldr", "3647.dat", 7),
            shaft("output.ldr", "3648b.dat", 7),
        ],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(ROOT / "output/gear-drive-source"))
    args = parser.parse_args()
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=False)
    source = construction()
    text, _, diagnostics = build_plan(source, get_parts())
    if any(d["severity"] == "error" for d in diagnostics):
        raise ValueError(f"Construction failed validation: {diagnostics}")
    for section in source["sections"]:
        header = "0 FILE " + section["name"] + "\r\n"
        text = text.replace(
            header, header + "0 DESCRIPTION " + section["description"] + "\r\n"
        )
    (out / "construction.plan.json").write_text(json.dumps(source, indent=2) + "\n")
    (out / "gear-drive.mpd").write_bytes(text.encode())
    (out / "source-validation.json").write_text(
        json.dumps(jsonable(diagnostics), indent=2) + "\n"
    )
    print(out)


if __name__ == "__main__":
    main()
