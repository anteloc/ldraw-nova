"""Measure what an agent must read before placing its first part.

    .venv/bin/python bench/reading_cost.py            # entry document and its required reading
    .venv/bin/python bench/reading_cost.py --json

Required reading is every local Markdown link in a sentence of the entry
document that tells the agent to read something ("read", "start with",
"before using"). Tokens are estimated as characters / 4; the estimate is for
comparing revisions, not billing.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INSTRUCTION = re.compile(r'\b(read|start with|before using|open)\b', re.I)
LINK = re.compile(r'\[[^\]]*\]\(([^)#\s]+\.md)(?:#[^)]*)?\)')


def sentences(text):
    text = re.sub(r'```.*?```', ' ', text, flags=re.S)
    return re.split(r'(?<=[.!?])\s+|\n\s*\n|\n[-*|] ', text)


def required(entry):
    found = []
    for sentence in sentences(entry.read_text(encoding='utf-8')):
        if INSTRUCTION.search(sentence):
            for target in LINK.findall(sentence):
                path = (entry.parent / target).resolve()
                if path.is_file() and path not in found:
                    found.append(path)
    return found


def tokens(path):
    return round(len(path.read_text(encoding='utf-8')) / 4)


def report(entry):
    entry = Path(entry).resolve()
    root = entry.parent  # the entry document sits at its checkout's root
    files = [entry, *required(entry)]
    rows = [dict(file=os.path.relpath(p, root), bytes=p.stat().st_size, tokens=tokens(p)) for p in files]
    corpus = sorted((root / 'docs/agent').rglob('*.md'))
    return dict(entry=os.path.relpath(entry, root), required=rows,
                required_tokens=sum(r['tokens'] for r in rows),
                docs_agent_files=len(corpus), docs_agent_tokens=sum(tokens(p) for p in corpus),
                note='tokens are characters / 4')


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--entry', default=str(REPO / 'AGENTS.md'))
    p.add_argument('--json', action='store_true')
    args = p.parse_args(argv)
    result = report(args.entry)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    for r in result['required']:
        print(f"{r['tokens']:>7}  {r['file']}")
    print(f"{result['required_tokens']:>7}  required before the first part")
    print(f"{result['docs_agent_tokens']:>7}  all of docs/agent ({result['docs_agent_files']} files)")


if __name__ == '__main__':
    main()
