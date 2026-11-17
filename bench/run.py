"""Run frozen briefs with headless agents against a frozen toolkit snapshot.

Run this from a terminal (an interactive agent session cannot launch headless
workers). Each run gets a fresh agent, the same harness prompt, a budget and a
private output folder inside an isolated workspace. The workspace is a git
worktree of the selected revision, so earlier models under ``output/`` are not
visible. Ignored runtime resources (.venv, bin tools, the parts library and the
shared cache) are linked from this checkout.

    .venv/bin/python bench/run.py --suite baseline --ref HEAD --model haiku --model opus --repeats 2
    .venv/bin/python bench/run.py --suite candidate --model haiku --model opus --repeats 2
    .venv/bin/python bench/score.py table output/bench/baseline output/bench/candidate

Without --ref the workspace is HEAD plus this checkout's uncommitted and
untracked (non-ignored) files, i.e. the toolkit exactly as it is on disk.
Results, transcripts and scores are copied to output/bench/SUITE/.
"""
from __future__ import annotations

import argparse
import concurrent.futures as futures
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BRIEFS = Path(__file__).with_name('briefs.json')
LINKED = ('.venv', 'data/ldraw', 'data/parts-descriptions-full.tsv', '.cache')
TOOLS = 'Bash,Read,Write,Edit'


def git(*args, cwd=REPO, check=True):
    return subprocess.run(['git', *args], cwd=cwd, check=check, capture_output=True, text=True).stdout


def prepare_workspace(root, ref):
    """Detached worktree at ref; optionally overlay the uncommitted working tree."""
    repo = root / 'repo'
    if repo.exists():
        return repo
    root.mkdir(parents=True, exist_ok=True)
    git('worktree', 'add', '--detach', str(repo), ref or 'HEAD')
    if ref is None:
        changed = git('ls-files', '-m', '-o', '--exclude-standard', '-z').split('\0')
        for name in filter(None, changed):
            source = REPO / name
            target = repo / name
            if source.is_file():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
        for name in filter(None, git('ls-files', '-d', '-z').split('\0')):
            (repo / name).unlink(missing_ok=True)
    for name in LINKED:
        source, target = REPO / name, repo / name
        if source.exists() and not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(source, target_is_directory=source.is_dir())
    (repo / 'bin').mkdir(exist_ok=True)
    for entry in (REPO / 'bin').iterdir():
        target = repo / 'bin' / entry.name
        if not target.exists():
            target.symlink_to(entry, target_is_directory=entry.is_dir())
    revision = dict(ref=ref or 'HEAD+working-tree', commit=git('rev-parse', 'HEAD', cwd=repo).strip(),
                    overlay=ref is None)
    (root / 'revision.json').write_text(json.dumps(revision, indent=2) + '\n')
    return repo


def clean_workspace(root):
    """Remove a suite's worktree: unlink the shared resources first, never their targets."""
    repo = root / 'repo'
    if repo.exists():
        for link in [repo / name for name in LINKED] + list((repo / 'bin').glob('*')):
            if link.is_symlink():
                link.unlink()
        git('worktree', 'remove', '--force', str(repo))
    git('worktree', 'prune')
    (root / 'revision.json').unlink(missing_ok=True)
    if root.exists() and not any(root.iterdir()):
        root.rmdir()


def command(prompt, model, *, effort, budget, max_turns, workspace):
    cmd = ['claude', '-p', prompt, '--model', model, '--output-format', 'stream-json', '--verbose',
           '--strict-mcp-config', '--disable-slash-commands', '--no-session-persistence',
           '--tools', TOOLS, '--allowedTools', TOOLS, '--permission-mode', 'dontAsk',
           '--setting-sources', 'project', '--add-dir', str(workspace)]
    if effort:
        cmd += ['--effort', effort]
    if budget:
        cmd += ['--max-budget-usd', str(budget)]
    if max_turns:
        cmd += ['--max-turns', str(max_turns)]
    return cmd


def run_one(brief, model, repeat, *, harness, workspace, results, effort, max_turns, dry_run):
    run_id = f"{brief['id']}-{model}-r{repeat}"
    relative = f'output/bench/{run_id}'
    work = workspace / relative
    folder = results / run_id
    if (folder / 'run.json').exists():
        return json.loads((folder / 'run.json').read_text())
    prompt = harness.format(outdir=relative) + '\n\n' + brief['prompt']
    cmd = command(prompt, model, effort=effort, budget=brief['budget'].get('usd'),
                  max_turns=max_turns, workspace=workspace)
    if dry_run:
        print(' '.join(repr(c) if ' ' in c else c for c in cmd))
        return dict(run=run_id, dry_run=True)
    work.mkdir(parents=True, exist_ok=True)
    folder.mkdir(parents=True, exist_ok=True)
    # The venv's editable install maps ldraw_tools to this checkout; PYTHONPATH
    # precedes that finder, so commands and generators use the workspace copy.
    environment = dict(os.environ, LDRAW_AGENT_TRACE=str(work / 'trace.jsonl'), PYTHONPATH=str(workspace))
    started = time.time()
    timeout = 60 * brief['budget'].get('minutes', 60)
    try:
        process = subprocess.run(cmd, cwd=workspace, env=environment, capture_output=True, text=True, timeout=timeout)
        stdout, stderr, status = process.stdout, process.stderr, process.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or '')
        stderr, status = 'TIMEOUT', 'timeout'
    (folder / 'transcript.jsonl').write_text(stdout)
    if stderr:
        (folder / 'stderr.txt').write_text(stderr)
    if work.exists():
        shutil.copytree(work, folder / 'delivered', dirs_exist_ok=True)
    record = dict(run=run_id, brief=brief['id'], model=model, repeat=repeat, status=status,
                  seconds=round(time.time() - started, 1), prompt=prompt, command=cmd[3:])
    (folder / 'run.json').write_text(json.dumps(record, indent=2) + '\n')
    from score import score_run  # noqa: E402  (bench/ is on sys.path)
    scored = score_run(folder, brief)
    (folder / 'score.json').write_text(json.dumps(scored, indent=2) + '\n')
    with open(results / 'scores.jsonl', 'a', encoding='utf-8') as f:
        f.write(json.dumps(scored) + '\n')
    print(json.dumps(dict(run=run_id, status=status, minutes=round(record['seconds'] / 60, 1),
                          build=scored['model'].get('checks_passed'), cost=scored['cost'].get('usd'))), flush=True)
    return record


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--suite', required=True, help='Result folder name under output/bench/')
    p.add_argument('--ref', help='Git revision to benchmark (default: HEAD plus the uncommitted working tree)')
    p.add_argument('--model', action='append', help='Repeatable, e.g. haiku, sonnet, opus (required unless --clean)')
    p.add_argument('--brief', action='append', help='Brief ID (default: every brief in --round)')
    p.add_argument('--round', type=int, default=1, help='Brief round; round 2 adds Technic and flex, round 3 the Technic suite')
    p.add_argument('--family', action='append', help='Only briefs of this family (repeatable), e.g. technic')
    p.add_argument('--repeats', type=int, default=2)
    p.add_argument('--jobs', type=int, default=1, help='Concurrent agents; parallel heavy runs exhaust usage quotas')
    p.add_argument('--effort', default='medium')
    p.add_argument('--max-turns', type=int)
    p.add_argument('--workspace', help='Isolated workspace root (default: system temp)')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--clean', action='store_true', help="Remove the suite's isolated workspace and exit; results stay")
    args = p.parse_args(argv)
    if args.clean:
        clean_workspace(Path(args.workspace or Path(tempfile.gettempdir()) / 'ldraw-nova-bench') / args.suite)
        print(json.dumps(dict(cleaned=args.suite)))
        return
    if not args.model:
        p.error('--model is required')
    data = json.loads(BRIEFS.read_text())
    briefs = [b for b in data['briefs'] if (args.brief and b['id'] in args.brief) or
              (not args.brief and b['round'] <= args.round and (not args.family or b['family'] in args.family))]
    if args.brief and len(briefs) != len(set(args.brief)):
        p.error('Unknown brief ID; see bench/briefs.json')
    results = REPO / 'output/bench' / args.suite
    root = Path(args.workspace or Path(tempfile.gettempdir()) / 'ldraw-nova-bench') / args.suite
    workspace = root / 'repo'
    if not args.dry_run:
        results.mkdir(parents=True, exist_ok=True)
        workspace = prepare_workspace(root, args.ref)
        shutil.copy2(root / 'revision.json', results / 'revision.json')
    sys.path.insert(0, str(Path(__file__).parent))
    jobs = [(b, m, r) for b in briefs for m in args.model for r in range(1, args.repeats + 1)]
    with futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        done = list(pool.map(lambda job: run_one(*job, harness=data['harness'], workspace=workspace, results=results,
                                                   effort=args.effort, max_turns=args.max_turns,
                                                   dry_run=args.dry_run), jobs))
    print(json.dumps(dict(suite=args.suite, runs=len(done), results=str(results))))


if __name__ == '__main__':
    main()
