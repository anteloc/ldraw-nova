"""Cost model for run 3 (orchestrator-owned). Reads costs.jsonl; writes COST.json and prints a summary.

Multi-agent cost = sum of the CLI-reported total_cost_usd of every headless call (+ orchestrator session
overhead passed with --overhead USD). Solo-Opus estimates reprice the SAME measured per-request token
profile at Opus 5.5 rates (input $4, cache write $5, cache read $0.20, output $20 per MTok):
  lower bound : every request repriced as-is, x 0.6 (credits Opus with 40 % fewer requests/output);
                impossible in practice (assumes one agent with per-task fresh contexts).
  realistic   : the tasks run one after another in ONE context: each request also carries the accumulated
                context of the previous tasks (cache read), compacted to 60k whenever it exceeds 200k
                (each compaction = one 200k read + 20k output); then x 0.6.
These are ESTIMATES of a run that was not executed.
"""
import argparse, json
from pathlib import Path
RUN = Path(__file__).resolve().parent
OPUS = dict(input=4.0, cache_write=5.0, cache_read=0.20, output=20.0)


def reprice(r, extra_read=0):
    return ((r['input']) * OPUS['input'] + r['cache_write'] * OPUS['cache_write'] +
            (r['cache_read'] + extra_read) * OPUS['cache_read'] + r['output'] * OPUS['output']) / 1e6


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--overhead', type=float, default=0.0)
    a = ap.parse_args()
    calls = [json.loads(l) for l in (RUN / 'costs.jsonl').read_text().splitlines() if l.strip()]
    by_role = {}
    for c in calls:
        by_role.setdefault(c['role'], dict(calls=0, cost=0.0, turns=0, max_prompt=0))
        b = by_role[c['role']]
        b['calls'] += 1; b['cost'] += c['cost_usd'] or 0; b['turns'] += c['turns'] or 0
        b['max_prompt'] = max(b['max_prompt'], c['max_prompt'] or 0)
    multi = sum(b['cost'] for b in by_role.values()) + a.overhead
    lower = 0.6 * sum(reprice(r) for c in calls for r in c['per_request'])
    real, offset = 0.0, 0
    for c in calls:
        reqs = c['per_request']
        if not reqs:
            continue
        base = reqs[0]['input'] + reqs[0]['cache_write'] + reqs[0]['cache_read']
        for r in reqs:
            real += reprice(r, extra_read=offset)
        final = reqs[-1]['input'] + reqs[-1]['cache_write'] + reqs[-1]['cache_read'] + reqs[-1]['output']
        offset += max(0, final - base)
        while offset + base > 200_000:
            real += (200_000 * OPUS['cache_read'] + 20_000 * OPUS['output']) / 1e6
            offset = 60_000
    real *= 0.6
    out = dict(by_role=by_role, overhead_usd=a.overhead, multi_total_usd=round(multi, 4),
               solo_opus_lower_bound_usd=round(lower, 4), solo_opus_realistic_usd=round(real, 4),
               ratio_vs_lower=round(lower / multi, 1) if multi else None, ratio_vs_realistic=round(real / multi, 1) if multi else None,
               haiku_max_prompt=max((c['max_prompt'] or 0) for c in calls if c['model'] == 'haiku') if calls else None)
    (RUN / 'COST.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
