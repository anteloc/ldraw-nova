# Annotate reference models

`ldraw-annotator-nova` installs the executable `bin/ldraw-annotator`. It turns
plain LDraw sources into a semantic submodel hierarchy with descriptions and
part comments while preserving physical part occurrences, world placements and
colours. Use it when a source lacks useful structure for inspection and reuse;
annotation does not admit a source into this project's curated knowledge base.

This guide adapts the upstream [agent instructions](https://github.com/anteloc/ldraw-annotator-nova/blob/v0.5.0/AGENTS.md),
[README](https://github.com/anteloc/ldraw-annotator-nova/blob/v0.5.0/README.md) and
[output contract](https://github.com/anteloc/ldraw-annotator-nova/blob/v0.5.0/docs/output-contract.md).
Consult those for detailed format requirements; no sibling checkout is needed.

## Prepare and annotate

Set `LDRAW_ANNOTATOR_DB` to this checkout's `data/ldraw-info.db`, or pass `--db`.
Commands that read models need the database; `status` and `prompt` do not. Keep original sources untouched
and all task work under `output/<task>/`.

When annotating yourself, use the deterministic workflow:

```sh
mkdir -p output/task
bin/ldraw-annotator prep source.mpd --db data/ldraw-info.db \
  --mpd output/task/model.annotated.mpd
bin/ldraw-annotator prompt > output/task/annotation-instructions.md
# Read the prompt, then edit only the prepared MPD following its rules.
bin/ldraw-annotator check source.mpd output/task/model.annotated.mpd \
  --db data/ldraw-info.db > output/task/annotation-check.json
```

Read the prep result's naming prefix. Preserve attribution, licences, metadata,
embedded parts, transforms and effective colours. New semantic sections use
identity references in the parent frame; do not recenter parts. Follow the
prompt's description, part-comment, step, naming and flexible-section rules.
Repeat `check` until `ok: true`; then inspect the resulting sections in isolation
and in their parents with [xray](xray.md).

For the tool's automated LLM workflow:

```sh
bin/ldraw-annotator run source.mpd --db data/ldraw-info.db \
  --out output/task/annotated --work output/task/annotation-work -j 2
bin/ldraw-annotator status --work output/task/annotation-work
```

`run` makes provider calls. Select split/refine agents via `--split-agent` and
`--refine-agent`, or `LDRAW_ANNOTATOR_SPLIT_AGENT` and
`LDRAW_ANNOTATOR_REFINE_AGENT`. Values use `provider:agent`. The split agent
chooses hierarchy; the refine agent rewrites parent descriptions. Defaults in
0.5.0 use z.ai; configure `ZAI_API_KEY` (optional `ZAI_BASE_URL`). Other providers
use their own variables, e.g. `OPENROUTER_API_KEY`, `OPENAI_API_KEY`,
`ANTHROPIC_API_KEY`, or `OLLAMA_HOST` for local Ollama. Never locate, copy, print
or commit credentials. If required credentials are missing, request configuration
or use the deterministic workflow when appropriate to the task.

## Resume, diagnose and verify

Rerun the same command and work directory after interruption: accepted calls and
completed models are reused. Existing outputs are skipped; `--force` intentionally
redos them. Never hand-edit automated `run` outputs: correct the tool/prompts or
rerun configuration instead. Editing `prep --mpd` output is the manual workflow.

`status` reports progress, calls, tokens and failures. Inspect
`annotation-work/<model>/check.json`, `log.jsonl`, and `units/*.failed.json` for
failures. `digest FILE` shows the model input; `digest NAME --tree --work DIR`
shows the working hierarchy. Low concurrency suits local Ollama. Repeated failed
units can indicate an agent unable to follow the schema; an output's existence
alone does not mean the job passed. `run` exit 0 means all outputs are verified,
1 means a model failed verification, and 2 means bad input.

Do not run `db-sync` from the agent: upstream reserves database writes for the
user. Use the supplied database read-only. Keep check reports and visual evidence
with annotated outputs, and retain the original source for comparison. Lossless
annotation proves preservation, not construction validity, physical connectivity
or knowledge-base admission. Regenerate section-based inspection evidence after
hierarchy changes because names, selections and source hashes change.
