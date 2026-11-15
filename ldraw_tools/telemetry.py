"""Opt-in trace of CLI invocations for benchmarks and cost diagnosis.

Set ``LDRAW_AGENT_TRACE=/path/trace.jsonl`` to append one JSON line per
command: arguments, wall time, stdout bytes and exit status. Nothing is
recorded when the variable is unset, and tracing never changes a command's
result: write failures are ignored.
"""
from __future__ import annotations

import json
import os
import time

ENVIRONMENT = 'LDRAW_AGENT_TRACE'


def started():
    return time.perf_counter()


def record(argv, start, *, stdout_bytes, status, error_type=None):
    path = os.environ.get(ENVIRONMENT)
    if not path:
        return
    row = dict(time=time.strftime('%Y-%m-%dT%H:%M:%S'), argv=list(argv),
               seconds=round(time.perf_counter() - start, 3), stdout_bytes=stdout_bytes, exit=status)
    if error_type:
        row['error_type'] = error_type
    try:
        with open(path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(row) + '\n')
    except OSError:
        pass
