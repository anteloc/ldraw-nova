# What agents read before building, and why examples matter

This is an investigation from 2026-11-09, made from local session logs. The raw logs are not committed: they live under `~/.claude/projects/…`, `~/.codex/sessions/…` and `output/urban-house-run3/logs/`.

## Run-3 task workers (Haiku 5.5, headless)
These figures cover 49 worker and repair calls from pass 1, before the quality pass. Each worker was given a brief of about 2 k tokens and told not to read other files.

| Activity | Count |
|---|---|
| Read the brief | 48 |
| Read its own part files | 22 |
| Opened `check.py --snap` images | about 114 |
| Ran `check.py` | 174 |
| Wrote or edited part files | about 165 |
| Ran `./ldraw-agent part <id>` | 30 calls, on 21 distinct parts |
| Glanced at shared helpers | a handful of times |

The workers never opened earlier builds' MPDs or plan JSON. They never looked at `examples/` or the run-1/run-2 generators, and never used `knowledge search`. That was the brief's instruction, given to keep contexts small.

## Runs 1–2 workers (Haiku 5.5, in-process subagents)
They read what their conventions file listed, about 25 k tokens per worker:
- `conventions.md` and `CONTRACTS.md`;
- `architecture.py`, `common.py` and the SNOT kit;
- `snot.md` and the ldraw-xray docs.

One worker also read `examples/building-atlas/generate.py`, because its prompt named it. None mined raw `.mpd`, `.ldr` or `.dat` files.

## Earlier single-Opus Technic builds (Claude Code sessions `9065c09e` → Goliath, `76745f40` → LSynth jib crane)
Both sessions read for about 20 tool calls before their first write.

1. **They browsed the repo:**
   - `ls examples/ examples/*` and `ls docs/agent docs/agent/technic-patterns`;
   - `ls output | grep crane|excav|pneum|flex`.
2. **They read generator code from the closest example:**
   - `cat examples/atlas-crane/crane_lib.py`, then its `beam()` function and `BEAMS`/`AXLES` tables;
   - `examples/flex/pneumatic-press/generate.py` and `examples/flex/constraint-lab/generate.py`;
   - the start of `examples/atlas-crane/generate.py`.
3. **They read docs:**
   - `docs/agent/technic.md` and `technic-design.md`;
   - `technic-patterns/industrial-assemblies.md` and `mechanisms.md`;
   - `examples/flex/README.md` and `lsynth-examples/README.md`.
4. **They read MPD/LDR files only in narrow slices**, through `sed`/`awk`/`grep`: lines 200–260 of the 42082 crane study's `source.mpd`, and the SYNTH block of a chain-tread `.ldr`. They never opened a `.dat` file; part geometry always came from `./ldraw-agent part` (18 calls in total).
5. **They reused their own previous build heavily.** Goliath referenced `output/titan` 271 times and re-read Titan's `body.py`, `generate.py` and renders.
6. **The curated retrieval commands were barely used:** `knowledge search` and `examples` at most once each. The submodel atlas and other models' plan JSON were not used.

The Sakura Garden and Atlas Crane builds (late September, when the repo was "ldraw-astra") have no surviving Claude transcripts on this machine. Their `research/` folders show the same pattern:
- **a real set studied for technique:** 10315 for the garden, 42082 for the crane;
- **Jev part searches per role;**
- **render boards** of reference submodels.

## Why adding examples improves quality and variety
- **They supply verified mechanics.** Copied helpers carry part origins, hole offsets, axle and beam tables, and hose-endpoint seating that would otherwise cost many failed builds. Because the copied piece already passed review, quality goes up.
- **They set the ceiling on variety.** Agents build from what they find nearby. With one crane library and one pneumatic example, Technic requests drifted towards booms, beams and hoses (Titan, Goliath, the jib crane). Each new kind of example widens that menu.
- **They are cheap only if short and runnable.** Agents consume `generate.py` files and READMEs, not MPDs. A 50–150 line example with a README stating its interface costs 1–3 k tokens to read.
- **They get used if they are named by function.** Agents found examples by `ls` and grep on folder names, not through the knowledge search.

**Gaps that kept recurring:**
- **Mechanisms:** gear trains, differentials, steering, turntables, linear-actuator arms.
- **Shaping:** studless body panels.
- **Buildings:** worked façade details (signs, awnings, window surrounds), furniture and street props.

**Caveat:** whole-model examples pull agents towards copying the silhouette. Many small assembly examples do more for variety than a few large models.
