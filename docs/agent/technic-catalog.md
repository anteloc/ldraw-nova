# Mechanism parts catalog

```sh
./ldraw-agent technic catalog --family gear
./ldraw-agent technic catalog 'constant velocity'
./ldraw-agent technic catalog 85543-f3
./ldraw-agent technic catalog --output output/mechanism-parts.json
./ldraw-agent technic catalog --model MODEL.mpd --connectors --output output/model-parts.json
```

`--output` saves every selected row; `--limit` limits only terminal rows. Use
`--force` to replace a catalog. `--connectors` expands part-local evidence and
may take longer for the whole library; search first for routine inspection.

The catalog combines every assignment in supplied `technic.py`, mechanical
name matches from other supplied categories, installed part names and an
explicit [online watchlist](../../ldraw_tools/data/mechanism-parts-watchlist.json).
Python assignments are read as data, without importing the generated module.
Duplicate sanitized names retain separate source lines and values.

The October 2026 local snapshot contains **5,643 references**, including all
**1,352 Technic assignments**: 5,626 installed, 17 unavailable, 553 aliases and
1,478 shortcuts. Counts include historic, printed, composite and supplementary
mechanical parts; they are not unique current mould counts. Regenerate after
library updates. Completeness is bounded by these inputs, not every LEGO part
ever produced or every tracker file.

Model inventory expects a self-contained MPD/LDR. Unresolved external assemblies
are rejected instead of being counted as one physical part; embed them first.

Rows retain exact references, original descriptions, sanitized symbols and
source lines, headers, licences, hashes, alias chains/transforms, family tags
and existing structural-profile keys. Installed means the file exists, not
complete dependencies or retail colour availability. Missing parts stay visible;
unofficial watchlist entries are not downloaded automatically.

`structural_profile` refers to the measured registry; `technic parts/check`
still enforce its geometry fingerprint. Search families and
[mechanism notes](../../ldraw_tools/data/mechanism-part-notes.json) do not grant
validated animation support. `motion_profile: unreviewed` keeps that gap explicit.

Connector reports include provenance and section profiles, including possible
primitive-inferred false positives. Embedded DAT definitions retain their
physical boundary and need separate review; installed namesakes do not provide
their interfaces. Follow the [advanced workflow](advanced-mechanisms.md) to
establish mobility, torque transfer and constraints.

For new parts, refresh the library through its normal update process and rerun
the command. Add known missing parts to the watchlist with a dated official
LDraw library/tracker URL. Add reviewed local frames only after inspecting the
exact variant, aliases and geometry; keep fixtures for executable support.
