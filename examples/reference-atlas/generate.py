"""Rebuild the visual reference library from its stable, attributed manifest."""
from pathlib import Path
import argparse
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from ldraw_tools.common import ROOT, dumps, get_parts
from ldraw_tools.discovery import DiscoveryIndex
from ldraw_tools.reference_catalog import build_catalog
import json

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,default=Path(__file__).with_name('library.manifest.json'))
    parser.add_argument('--outdir',type=Path,default=ROOT/'output/reference-library')
    parser.add_argument('--jobs',type=int,choices=[1,2,3,4],default=2)
    parser.add_argument('--views',nargs='+',default=['home','front','right','top'])
    parser.add_argument('--refresh',action='store_true')
    args=parser.parse_args()
    report=build_catalog(DiscoveryIndex(get_parts()),json.loads(args.manifest.read_text()),args.outdir,views=args.views,
                         jobs=args.jobs,refresh=args.refresh,progress=lambda row:print(json.dumps(row),file=sys.stderr,flush=True))
    print(dumps(report))
    return 1 if report['failures'] else 0

if __name__=='__main__':
    raise SystemExit(main())
