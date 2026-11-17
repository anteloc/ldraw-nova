"""Delivery metadata for a built model (docs/agent/cards/review.md#deliver).

The plan writes the author, `0 !LICENSE CC-BY-NC` and the `[AI-GENERATED] `
title; it has no field for the licence explanation or the keywords. `finalize`
adds both to every section the plan generated (the sections carrying that
licence line), keeps the file's line endings, and checks the rest. It is
repeatable: lines already present are not added twice.
"""
from __future__ import annotations

from pathlib import Path

LICENCE = '0 !LICENSE CC-BY-NC'
COMMENT = ('0 Allows sharing and adapting for noncommercial purposes only, with attribution to the AI '
           'that authored the current model.')
KEYWORDS = '0 !KEYWORDS AI, AI-generated'
MARKER = '[AI-GENERATED]'


def finalize_text(text):
    """(finalized text, problems)."""
    newline = '\r\n' if '\r\n' in text else '\n'
    out = []
    for line in text.splitlines():
        if line.rstrip() in (COMMENT, KEYWORDS):
            continue
        out.append(line)
        if line.rstrip() == LICENCE:
            out += [COMMENT, KEYWORDS]
    problems = []
    starts = [i for i, line in enumerate(out) if line.startswith('0 FILE ')] or [0]
    sections = [out[a:b] for a, b in zip(starts, [*starts[1:], len(out)])]
    generated = [s for s in sections if any(line.rstrip() == LICENCE for line in s)]
    if not generated:
        problems.append(f"No section has '{LICENCE}': set \"license\": \"CC-BY-NC\" in the plan and rebuild.")
    title = next((line for line in sections[0] if line.startswith('0 ') and not line.startswith('0 FILE ')), '')
    if not title.startswith(f'0 {MARKER} '):
        problems.append(f"The main model's title must start with '{MARKER} ': prefix the root section's description.")
    if sum(line.count(MARKER) for line in out) != 1:
        problems.append(f"'{MARKER}' must appear exactly once in the file, on the main model's title.")
    for section in generated:
        name = section[0].removeprefix('0 FILE ').strip() if section[0].startswith('0 FILE ') else 'main model'
        if not any(line.startswith('0 Author:') and line[9:].strip() for line in section):
            problems.append(f"Section {name} has no '0 Author:' line naming the agent and model.")
    return newline.join(out) + newline, problems


def finalize(path, output=None):
    """Finalize an MPD (in place unless ``output`` is given); the file is written only without problems."""
    source = Path(path)
    text, problems = finalize_text(source.read_bytes().decode())
    target = Path(output) if output else source
    if not problems:
        target.write_bytes(text.encode())
    sections = text.count('0 FILE ') or 1
    return dict(checks_passed=not problems, output=str(target), written=not problems, sections=sections,
                generated_sections=text.count(LICENCE), problems=problems,
                next='Review the finalized file: review MPD --outdir DIR' if not problems else 'Fix the plan, rebuild, finalize again')
