"""Measure agent sessions: where time, tool calls and context go.

Reads Claude Code transcripts (``~/.claude/projects/<project>/*.jsonl``) and
ldraw-nova web-app chats (``data/chats/<id>/messages.jsonl``). Read-only.

    .venv/bin/python scripts/session_stats.py ~/.claude/projects/-Users-me-ldraw-nova
    .venv/bin/python scripts/session_stats.py SESSION.jsonl ../ldraw-nova-docker/data/chats --json

Categories are heuristics over tool inputs; they compare runs, they do not audit them.
"""
from __future__ import annotations

import argparse
import collections
import datetime
import json
import re
import sys
from pathlib import Path

CATEGORIES = [  # first match wins
    ('render', r'ldraw-agent\s+(render|look|part-board)\b|leocad|closeup|ldraw-render-steps|sheet\.py'),
    ('build', r'ldraw-agent\s+build\b|generate\.py|cycle\.sh'),
    ('check', r'ldraw-agent\s+(check|validate|inspect|bom|compare-bom|cad-check|snap|connectors|deliver|technic\s+check|vehicle\s+check)\b|check-model|mesh_clearance|overlaps\.py|components\.py'),
    ('research', r'ldraw-agent\s+\S+|jev-rerank|probe\.py|partinfo'),
    ('adhoc-python', r'python'),
]
WEB_TOOL_CATEGORY = {'view_image': 'view-image', 'read_file': 'read-file', 'write_file': 'write-file',
                     'publish_model': 'deliver', 'report_progress': 'progress', 'list_files': 'shell-read'}


def timestamp(value):
    if isinstance(value, (int, float)):
        return datetime.datetime.fromtimestamp(value, datetime.timezone.utc)
    try:
        return datetime.datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except ValueError:
        return None


def command_category(command):
    for name, pattern in CATEGORIES:
        if re.search(pattern, command):
            return name
    return 'shell-read' if re.match(r'\s*(ls|cat|head|tail|grep|find|wc|sed)\b', command) else 'other-shell'


def tool_category(name, arguments):
    if name in ('Bash', 'run_shell', 'run_python', 'run_toolkit'):
        command = arguments.get('command') or arguments.get('code') or ' '.join(map(str, arguments.get('args', [])))
        if name == 'run_toolkit':
            command = 'ldraw-agent ' + command
        if name == 'run_python' and not re.search(r'python', command):
            command = 'python ' + command
        return command_category(str(command))
    if name in ('Read', 'read_file'):
        path = str(arguments.get('file_path') or arguments.get('path') or '')
        if re.search(r'\.(png|jpe?g)$', path, re.I):
            return 'view-image'
        return 'read-docs' if path.endswith('.md') else 'read-file'
    if name in ('Write', 'Edit', 'write_file'):
        path = str(arguments.get('file_path') or arguments.get('path') or '')
        return 'write-helper' if path.endswith(('.py', '.sh')) else 'write-file'
    return WEB_TOOL_CATEGORY.get(name, name)


def text_of(content):
    if isinstance(content, list):
        return ' '.join(str(c.get('text', '')) for c in content if isinstance(c, dict))
    return str(content or '')


class Session:
    def __init__(self, source):
        self.source, self.prompt, self.models = source, None, collections.Counter()
        self.first = self.last = None
        self.turns, self.cost, self.api_ms = 0, None, None
        self.calls = collections.defaultdict(lambda: dict(calls=0, seconds=0.0, result_chars=0, errors=0))
        self.helpers, self.pending = set(), {}

    def seen(self, when):
        if when:
            self.first = min(self.first or when, when)
            self.last = max(self.last or when, when)

    def start(self, call_id, name, arguments, when):
        category = tool_category(name, arguments)
        if category == 'write-helper':
            self.helpers.add(str(arguments.get('file_path') or arguments.get('path')))
        self.pending[call_id] = (category, when)

    def finish(self, call_id, result, error, when):
        if call_id not in self.pending:
            return
        category, started = self.pending.pop(call_id)
        row = self.calls[category]
        row['calls'] += 1
        row['errors'] += bool(error)
        row['result_chars'] += len(text_of(result))
        if started and when:
            row['seconds'] += max(0.0, (when - started).total_seconds())

    def summary(self):
        tool_seconds = sum(r['seconds'] for r in self.calls.values())
        return dict(source=self.source, prompt=(self.prompt or '')[:120], models=dict(self.models.most_common(2)),
                    wall_hours=round((self.last - self.first).total_seconds() / 3600, 2) if self.first else None,
                    api_hours=round(self.api_ms / 3.6e6, 2) if self.api_ms else None,
                    cost_usd=round(self.cost, 2) if self.cost is not None else None, assistant_turns=self.turns,
                    tool_calls=sum(r['calls'] for r in self.calls.values()), tool_minutes=round(tool_seconds / 60, 1),
                    docs_kchars=round(self.calls['read-docs']['result_chars'] / 1000, 1) if 'read-docs' in self.calls else 0,
                    images_viewed=self.calls['view-image']['calls'] if 'view-image' in self.calls else 0,
                    helpers_written=len(self.helpers),
                    categories={k: dict(v, minutes=round(v['seconds'] / 60, 1)) for k, v in
                                sorted(self.calls.items(), key=lambda kv: -kv[1]['seconds'])})


def claude_session(path):
    s = Session(str(path))
    for line in path.open(errors='replace'):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        when = timestamp(record['timestamp']) if record.get('timestamp') else None
        s.seen(when)
        if record.get('type') == 'cost-state':
            s.cost, s.api_ms = record.get('totalCostUSD'), record.get('totalAPIDuration')
        message = record.get('message') or {}
        if record.get('type') == 'assistant':
            s.turns += 1
            if message.get('model'):
                s.models[message['model']] += 1
            for c in message.get('content') or []:
                if isinstance(c, dict) and c.get('type') == 'tool_use':
                    s.start(c['id'], c['name'], c.get('input') or {}, when)
        elif record.get('type') == 'user':
            content = message.get('content')
            human = (record.get('origin') or {}).get('kind') == 'human'
            for c in content if isinstance(content, list) else [dict(type='text', text=content)]:
                if not isinstance(c, dict):
                    continue
                if c.get('type') == 'tool_result':
                    s.finish(c.get('tool_use_id'), c.get('content'), c.get('is_error'), when)
                elif human and s.prompt is None and c.get('type') == 'text' and not str(c.get('text', '')).startswith('<'):
                    s.prompt = str(c.get('text', ''))
    return s


def web_chat(directory):
    s = Session(str(directory))
    for line in (directory / 'messages.jsonl').open(errors='replace'):
        if not line.strip():
            continue
        message = json.loads(line)
        when = timestamp(message.get('created_at'))
        s.seen(when)
        role = message.get('role')
        if role == 'user' and s.prompt is None:
            s.prompt = text_of(message.get('content')) if not isinstance(message.get('content'), str) else message['content']
        if role == 'assistant':
            s.turns += 1
            if message.get('_llm_model'):
                s.models[str(message['_llm_model'])] += 1
            for call in message.get('tool_calls') or []:
                function = call.get('function') or {}
                try:
                    arguments = json.loads(function.get('arguments') or '{}')
                except (TypeError, json.JSONDecodeError):
                    arguments = {}
                s.start(call.get('id'), function.get('name') or call.get('name'), arguments if isinstance(arguments, dict) else {}, when)
        if role == 'tool':
            s.finish(message.get('tool_call_id'), message.get('content'), bool(message.get('_error')), when)
    return s


def sessions(paths):
    for path in map(Path, paths):
        path = path.expanduser()
        if path.is_file() and path.suffix == '.jsonl':
            yield claude_session(path)
        elif (path / 'messages.jsonl').is_file():
            yield web_chat(path)
        elif path.is_dir():
            for child in sorted(path.iterdir()):
                if child.suffix == '.jsonl' or (child / 'messages.jsonl').is_file():
                    yield from sessions([child])


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('paths', nargs='+', help='Transcript .jsonl files, chat directories or folders of them')
    parser.add_argument('--min-calls', type=int, default=10, help='Skip sessions with fewer tool calls')
    parser.add_argument('--json', action='store_true', help='Print one JSON object per session')
    args = parser.parse_args()
    for session in sessions(args.paths):
        row = session.summary()
        if row['tool_calls'] < args.min_calls:
            continue
        if args.json:
            print(json.dumps(row))
            continue
        top = ', '.join(f"{k} {v['calls']}×/{v['minutes']}m" for k, v in list(row['categories'].items())[:5])
        print(f"{Path(row['source']).stem[:12]:12} {','.join(row['models'])[:28]:28} wall {row['wall_hours']}h "
              f"cost ${row['cost_usd']} turns {row['assistant_turns']} calls {row['tool_calls']} "
              f"tool {row['tool_minutes']}m docs {row['docs_kchars']}k imgs {row['images_viewed']} "
              f"helpers {row['helpers_written']}\n    {row['prompt'][:100]!r}\n    {top}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
