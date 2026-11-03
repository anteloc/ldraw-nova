"""Rebuild the owned editable plan into a separate checked model."""
from pathlib import Path
import argparse
import sys
HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'ldraw_tools').is_dir())
sys.path.insert(0, str(ROOT))
from ldraw_tools.builder import load_plan
from ldraw_tools.common import atomic_write, get_parts
from ldraw_tools.workflow import build_checked
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    if args.output.exists() and not args.force: parser.error('Output exists; use --force')
    text, _, report = build_checked(load_plan(HERE/'scene.plan.json'), get_parts())
    if not report['checks_passed']: raise SystemExit(str(report['diagnostics']))
    atomic_write(args.output, text)
