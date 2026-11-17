"""Generate ldraw_tools/data/technic-ports.json from the installed LDCad shadow data.

    .venv/bin/python scripts/technic_ports.py            # rewrite the table
    .venv/bin/python scripts/technic_ports.py --check    # fail when it is stale

Reviewed parts (data/technic-parts.json) are not regenerated; they stay
authoritative. Run scripts/technic_corpus.py afterwards: it measures how the
derived ports seat in the official sets and records which ports to withhold.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ldraw_tools.common import DATA, RESOURCE_DATA, atomic_write, get_parts, shadow_paths  # noqa: E402
from ldraw_tools import technic_ports  # noqa: E402

TABLE = DATA / 'technic-ports.json'


def descriptions(parts):
    """Titles from the installed library index, which also lists moved parts."""
    rows = {}
    for line in Path(parts.path).read_text(errors='replace').splitlines():
        match = re.match(r'(\S+)\.dat\s+(.*)', line.strip(), re.I)
        if match:
            rows[match.group(1).casefold()] = match.group(2)
    return rows


def render(table):
    """One part per line: readable diffs for a generated file."""
    head = {k: v for k, v in table.items() if k not in ('parts', 'aliases')}
    lines = ['{'] + [f' {json.dumps(k)}: {json.dumps(v)},' for k, v in head.items()]
    lines.append(' "aliases": ' + json.dumps(table['aliases'], sort_keys=True) + ',')
    lines.append(' "parts": {')
    rows = [f'  {json.dumps(code)}: {json.dumps(entry, separators=(",", ":"))}' for code, entry in sorted(table['parts'].items())]
    lines.append(',\n'.join(rows))
    lines += [' }', '}']
    return '\n'.join(lines) + '\n'


def build(withheld=None):
    parts = get_parts(shadows=shadow_paths())
    listed = descriptions(parts)
    reviewed = json.loads((DATA / 'technic-parts.json').read_text())
    known = set(reviewed['parts']) | set(reviewed['aliases'])
    entries = technic_ports.generate(parts, listed, reviewed=known,
                                     progress=lambda i, n: print(f'  {i}/{n}', file=sys.stderr, flush=True))
    corpus = DATA / 'technic-corpus.json'
    if withheld is None:
        # Ports that almost never seat in the official sets (scripts/technic_corpus.py ports --apply).
        withheld = json.loads(corpus.read_text())['withheld'] if corpus.exists() else {}
    for code, ports in withheld.items():
        if code in entries:
            # Kept, out of the way of the tools, so the next corpus run can measure them again.
            entries[code]['withheld'] = [p for p in entries[code]['ports'] if p['id'] in ports]
            entries[code]['ports'] = [p for p in entries[code]['ports'] if p['id'] not in ports]
            if not entries[code]['ports'] and not entries[code].get('nozzles'):
                entries[code]['role'] = 'withheld'
    aliases = technic_ports.moved_aliases(listed, set(entries) | known)
    aliases = {k: v for k, v in aliases.items() if k not in reviewed['aliases']}
    return dict(version=1, units='LDU', generator='scripts/technic_ports.py',
                note='Derived from LDCad shadow SNAP_CYL metadata; data/technic-parts.json overrides it.',
                withheld=withheld, aliases=aliases, parts=entries)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--check', action='store_true', help='Compare with the saved table instead of writing it')
    args = parser.parse_args(argv)
    text = render(build())
    if args.check:
        if not TABLE.exists() or TABLE.read_text() != text:
            print('technic-ports.json is stale; run scripts/technic_ports.py', file=sys.stderr)
            return 1
        return 0
    atomic_write(TABLE, text)
    table = json.loads(text)
    print(f"{len(table['parts'])} parts, {sum(len(e['ports']) for e in table['parts'].values())} ports, "
          f"{len(table['aliases'])} aliases -> {TABLE.relative_to(ROOT)}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
