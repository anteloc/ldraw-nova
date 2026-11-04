#!/usr/bin/env python3
"""text2ldr.py - turn text into flat LDraw type-4 quads (no parts needed)."""
import argparse
import sys

FONT = {
 "A":"01110 10001 10001 11111 10001 10001 10001",
 "B":"11110 10001 10001 11110 10001 10001 11110",
 "C":"01110 10001 10000 10000 10000 10001 01110",
 "D":"11110 10001 10001 10001 10001 10001 11110",
 "E":"11111 10000 10000 11110 10000 10000 11111",
 "F":"11111 10000 10000 11110 10000 10000 10000",
 "G":"01110 10001 10000 10111 10001 10001 01111",
 "H":"10001 10001 10001 11111 10001 10001 10001",
 "I":"01110 00100 00100 00100 00100 00100 01110",
 "J":"00111 00010 00010 00010 00010 10010 01100",
 "K":"10001 10010 10100 11000 10100 10010 10001",
 "L":"10000 10000 10000 10000 10000 10000 11111",
 "M":"10001 11011 10101 10101 10001 10001 10001",
 "N":"10001 11001 10101 10011 10001 10001 10001",
 "O":"01110 10001 10001 10001 10001 10001 01110",
 "P":"11110 10001 10001 11110 10000 10000 10000",
 "Q":"01110 10001 10001 10001 10101 10010 01101",
 "R":"11110 10001 10001 11110 10100 10010 10001",
 "S":"01111 10000 10000 01110 00001 00001 11110",
 "T":"11111 00100 00100 00100 00100 00100 00100",
 "U":"10001 10001 10001 10001 10001 10001 01110",
 "V":"10001 10001 10001 10001 10001 01010 00100",
 "W":"10001 10001 10001 10101 10101 11011 10001",
 "X":"10001 10001 01010 00100 01010 10001 10001",
 "Y":"10001 10001 01010 00100 00100 00100 00100",
 "Z":"11111 00001 00010 00100 01000 10000 11111",
 "0":"01110 10001 10011 10101 11001 10001 01110",
 "1":"00100 01100 00100 00100 00100 00100 01110",
 "2":"01110 10001 00001 00010 00100 01000 11111",
 "3":"11110 00001 00001 01110 00001 00001 11110",
 "4":"00010 00110 01010 10010 11111 00010 00010",
 "5":"11111 10000 11110 00001 00001 10001 01110",
 "6":"00110 01000 10000 11110 10001 10001 01110",
 "7":"11111 00001 00010 00100 01000 01000 01000",
 "8":"01110 10001 10001 01110 10001 10001 01110",
 "9":"01110 10001 10001 01111 00001 00010 01100",
 " ":"00000 00000 00000 00000 00000 00000 00000",
 "-":"00000 00000 00000 11111 00000 00000 00000",
 "_":"00000 00000 00000 00000 00000 00000 11111",
 ".":"00000 00000 00000 00000 00000 00110 00110",
 ",":"00000 00000 00000 00000 00110 00100 01000",
 ":":"00000 00110 00110 00000 00110 00110 00000",
 "!":"00100 00100 00100 00100 00100 00000 00100",
 "?":"01110 10001 00001 00010 00100 00000 00100",
 "/":"00001 00001 00010 00100 01000 10000 10000",
 "(":"00010 00100 01000 01000 01000 00100 00010",
 ")":"01000 00100 00010 00010 00010 00100 01000",
 "+":"00000 00100 00100 11111 00100 00100 00000",
 "=":"00000 00000 11111 00000 11111 00000 00000",
 "'":"00100 00100 01000 00000 00000 00000 00000",
}
FONT = {k: v.split() for k, v in FONT.items()}
GLYPH_W, GLYPH_H, GAP = 5, 7, 1


def text_to_quads(text, px=10, color=4, ox=0, oy=0, oz=0):
    """Return a list of LDraw type-4 lines for the given text."""
    lines = []
    for i, ch in enumerate(text.upper()):
        glyph = FONT.get(ch, FONT["?"])
        col0 = i * (GLYPH_W + GAP)
        for r, row in enumerate(glyph):
            c = 0
            while c < GLYPH_W:
                if row[c] != "1":
                    c += 1
                    continue
                start = c
                while c < GLYPH_W and row[c] == "1":
                    c += 1                      # merge horizontal run
                x1 = ox + (col0 + start) * px
                x2 = ox + (col0 + c) * px
                y1 = oy + r * px
                y2 = y1 + px
                lines.append(
                    f"4 {color} {x1} {y1} {oz} {x2} {y1} {oz} "
                    f"{x2} {y2} {oz} {x1} {y2} {oz}"
                )
    return lines


def main():
    p = argparse.ArgumentParser(description="Convert text to LDraw quads.")
    p.add_argument("text", help='text to render, e.g. "AI-GENERATED"')
    p.add_argument("--px", type=int, default=10, help="pixel size in LDU (default 10)")
    p.add_argument("--color", type=int, default=4, help="LDraw color code (default 4 = red)")
    p.add_argument("--x", type=int, default=0, help="X offset")
    p.add_argument("--y", type=int, default=0, help="Y offset")
    p.add_argument("--z", type=int, default=0, help="Z offset")
    p.add_argument("--name", help="wrap output as an MPD subfile with this name, e.g. watermark.ldr")
    p.add_argument("-o", "--output", help="write to file instead of stdout")
    a = p.parse_args()

    quads = text_to_quads(a.text, a.px, a.color, a.x, a.y, a.z)
    out = []
    if a.name:
        out += [f"0 FILE {a.name}", f"0 {a.text}", f"0 Name: {a.name}",
                "0 Author: text2ldr"]
    out += quads

    result = "\n".join(out) + "\n"
    if a.output:
        with open(a.output, "w", encoding="utf-8") as f:
            f.write(result)
    else:
        sys.stdout.write(result)


if __name__ == "__main__":
    main()
