#!/usr/bin/env python3
"""Summarise connection groups from an `inspect --contacts all --detail full` report (review aid).

Each group outside the largest one is listed with its section, plan placement id,
reference and world bounds, so floating parts can be traced back to the generator.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


def plan_ids(mpd):
    """Map (section, line number) to the plan placement id comment preceding it."""
    ids, section, previous = {}, None, None
    for number, line in enumerate(Path(mpd).read_text().splitlines(), 1):
        if line.startswith('0 FILE '):
            section = line[7:].strip()
        match = re.match(r'0 // ([^:]+):', line)
        if match:
            previous = match.group(1)
        elif line.startswith('1 '):
            ids[(section, number)] = previous
            previous = None
    return ids


def main(report, mpd, key='optimistic_components'):
    g = json.loads(Path(report).read_text())['geometry']
    inst = {i['index']: i for i in g['instances']}
    ids = plan_ids(mpd)
    groups = sorted(g[key], key=len, reverse=True)
    print(f'{key}: {len(groups)} groups, sizes {[len(c) for c in groups][:30]}')
    print('largest group sections:', dict(Counter(inst[i]['section'] for i in groups[0])))
    for n, group in enumerate(groups[1:], 1):
        by = defaultdict(list)
        for i in group:
            it = inst[i]
            by[it['section']].append(f"{ids.get((it['section'], it['line_number']), '?')}:{it['part']}"
                                     f"@{[round(v) for v in it['position']]}")
        print(f'group {n} ({len(group)}):')
        for section, members in by.items():
            print('   ', section, members[:8], '...' if len(members) > 8 else '')


if __name__ == '__main__':
    main(*sys.argv[1:])
