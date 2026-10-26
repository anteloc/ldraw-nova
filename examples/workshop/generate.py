"""Export the bounded workshop recipes as editable JSON plans."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ldraw_tools.workshop import chain_drive, named_structure, workshop_plan  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name', choices=['chain-drive', 'mounted-frame', 'workshop'])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--colour', type=int, default=71)
    parser.add_argument('--accent', type=int, default=14)
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    if args.output.exists() and not args.force:
        parser.error('Output exists; use --force to replace a generated plan')
    options = dict(colour=args.colour, accent=args.accent)
    plan = (named_structure('service-platform', **options) if args.name == 'mounted-frame' else
            chain_drive(**options) if args.name == 'chain-drive' else workshop_plan(**options))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, indent=2) + '\n')
    print(args.output)


if __name__ == '__main__':
    main()
