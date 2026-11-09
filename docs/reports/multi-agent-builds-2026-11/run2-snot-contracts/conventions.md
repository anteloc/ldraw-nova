# Linden Row House (SNOT) — worker conventions (read fully before starting)

Repo root: `/Users/captain/workspaces/workspace-ai/ldraw-nova` — run every command from there.
Project folder: `output/urban-house-snot/`. Your folder: `output/urban-house-snot/modules/<module>/`.
**Write only inside your own module folder** (plus your log file `output/urban-house-snot/logs/<ID>-<module>.md`).
Never edit `common.py`, `contracts*.{py,json}`, `contract_check.py`, `kit/`, other modules, `ldraw_tools/`, docs.

## LDraw facts
- LDU units. **Negative Y is up.** Stud pitch 20 LDU; brick body 24; plate body 8.
- Most bricks/plates/tiles have their origin at the TOP face of the body (a brick placed with origin Y=-24
  spans -24..0). Check every unfamiliar part with `./ldraw-agent part <id>` (bounds + connectors).
- Rotate only with proper rotations (`yaw` or a 3x3 matrix with det +1); never mirror or stretch.
- Every placement has an explicit real colour (no 16 inside your module, never 24).

## Authoring API
Read `ldraw_tools/architecture.py` (Module, room, line, slab, ring, window4, door4, display4, planter, lamp,
bench, ...) and `output/urban-house-snot/common.py`. `m.add(ref, colour, x, h, z, yaw=..., matrix=...)` uses
x/z in studs and h in LDU upward. **SNOT helpers in common.py** (LDU coordinates):
- `Ry(deg)`, `panel_R(face)` — rotation for a FLAT-built section/part whose studs must face `face`
  ('-Z' front, '+Z' back, '-X', '+X'); local +X stays along the wall, local +Z becomes world UP.
- `side_studs(ref, top_centre_ldu, face)` — world stud-base points of a side-stud brick (30414, 11211, 87087,
  4070) whose origin (top centre) is at `top_centre_ldu` and whose studs face `face`.
- `seat(R, socket, stud)` — origin that puts the moving part's local `socket` on `stud` (= stud - R·socket).
  Plates/tiles: sockets at local y=+8 (e.g. a 4x4 plate's sockets (±10/±30, 8, ±10/±30)).
- `add_ldu(module, ref_or_Module, colour, [X,Y,Z], R)` — place with an LDU position and a matrix.
- **Vertical rule:** side studs sit 10 LDU below their brick's top. One flat panel can mate two side-stud
  courses only if their stud rows are a multiple of 20 LDU apart (e.g. 40 = brick + 2 plates); bricks
  stacked directly are 24 apart → mount a panel on ONE course (≥2 studs) or insert plates.
- **Verified kit:** `output/urban-house-snot/kit/snot_kit.py` (+ `kit/kit.mpd`, `kit/xray/`): K1 side-stud
  wall, K2 flat-built 4x4 panel seated with 8 contacts, K3 98138 dentil on a 4070 headlight brick (1 contact).
  Copy its pattern exactly; it was built and contact-checked.
- SNOT references in the repo: `docs/agent/guides/snot.md`; atlas entries (`./ldraw-agent examples --family
  submodel --details snot`): 10272-glazed-wall, 21046-recessed-entrance, 10278-vine-column, 10294 hull panels.

Your `generate.py` must:
```python
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))   # output/urban-house-snot
from common import export, PALETTE, panel_R, seat, side_studs, add_ldu, Ry
from ldraw_tools.architecture import Module, slab, line, ring, window4, ...
root = Module('<module>', '...'); root.anchor('next', h=160)       # storeys only
sign = Module('<module>-sign', '...')                               # one Module per contracted submodel
...; root.add(sign, colour, x, h, z, ...) or add_ldu(root, sign, colour, [X,Y,Z], R)
export(root, '<module>', Path(__file__).parent, 'Linden Row SNOT worker <ID> (Claude Haiku 5.5)')
```
The root may place ONLY contracted submodels. Section names must equal the contract names exactly.

## Build-inspect loop — PER SUBMODEL, in contract order
Order: structure (slab, walls) → mounts (side-stud courses) → SNOT panels → details → interior → ring.
For each submodel, before starting the next:
```sh
.venv/bin/python output/urban-house-snot/modules/<m>/generate.py
./ldraw-agent build output/urban-house-snot/modules/<m>/test.plan.json --output output/urban-house-snot/modules/<m>/<m>.mpd --detail summary --force
.venv/bin/python output/urban-house-snot/contract_check.py output/urban-house-snot/modules/<m>/<m>.mpd --submodel <m>-<sub>
ldraw-xray render output/urban-house-snot/modules/<m>/<m>.mpd --section <m>-<sub>.ldr --view home --view front -o output/urban-house-snot/modules/<m>/xray/<sub>-r<N> --force
ldraw-xray render ... --section <m>-<sub>.ldr --parent --highlight section --ghost --view home -o .../xray/<sub>-parent-r<N> --force
ldraw-xray board stud-map output/urban-house-snot/modules/<m>/<m>.mpd --section <m>-<sub>.ldr -o .../xray/<sub>-studs-r<N> --force   # ✦ only
```
(Several submodels can share one build if they are independent; keep build count ≈ 10.)
**Open every PNG with Read and look.** A submodel is done when contract_check says PASS for it AND the
images show nothing wrong. Fix in generate.py; after two failed fixes of the same thing, isolate it in a tiny
test plan (like the kit) and inspect connectors/contacts there.

Interior/front parts of other floors are not visible in your harness — you can also check your module in
the real house: `.venv/bin/python output/urban-house-snot/generate.py` (writes scene.plan.json, no --regen),
then `./ldraw-agent build output/urban-house-snot/scene.plan.json --output output/urban-house-snot/modules/<m>/scene-check.mpd --force`
and run `contract_check.py` on that file (scene mode) + `ldraw-xray render ... --section <m>.ldr --parent`.

## Pre-delivery audit (mandatory, before your final message)
Re-run `contract_check.py` on the whole module (no --submodel) and on a scene-check build. Then for EACH
contracted submodel apply the audit checklist: floating/unsupported parts, parts on smooth tiles,
interpenetration (`./ldraw-agent validate <mpd> --geometry`), gaps in walls/rails/bands, off-grid parts,
envelope (by owning part), colour/palette, mirror symmetry, facing direction of furniture, build order
(`ldraw-xray render ... --steps`), SNOT seating (stud-map + contact count), and "does it read as what it is".
Write `modules/<m>/defects.md`:
`| id | submodel | kind (structural/geometric/visual/contract) | description | evidence | severity | fix | status |`
— include defects you found and fixed DURING the per-submodel loop (status fixed) and any found in the audit.
Fix what you can (max ~4 more builds); mark the rest honestly.

## Timing log (mandatory)
At start, after each build/check/render batch, at the audit and at the end: `date '+%F %T'` + one line
appended to `output/urban-house-snot/logs/<ID>-<module>.md`, e.g.
`- 2026-11-08 20:31:05 | sub ground-sign r2 | contract FAIL interface 2<4 | fix: moved panel up 10 LDU`.

## Final report (your last message, ≤220 words)
Start/end timestamps; builds (failed); placements; contract_check result per submodel (PASS/FAIL);
self-found defects count by kind and how many fixed; images opened (folders); remaining defects/limits.
