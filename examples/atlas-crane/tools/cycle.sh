#!/bin/sh
# Regenerate, build, render and sheet.  Usage: tools/cycle.sh NAME [views...]
set -e
cd "$(dirname "$0")/../../.."
N=$1; shift
V=${*:-home front right top}
W=output/atlas-crane/work
mkdir -p $W
.venv/bin/python output/atlas-crane/generate.py $GEN_ARGS
./ldraw-agent build output/atlas-crane/atlas-crane.plan.json --output output/atlas-crane/atlas-crane.mpd \
  --detail summary --contacts none --force --report $W/$N.build.json > $W/$N.build.out 2>&1 || { echo BUILD FAILED; .venv/bin/python -c "
import json;d=json.load(open('$W/$N.build.json'))
for x in (d.get('diagnostics') or [])[:15]:
    print(x['severity'],x['code'],x['message'][:250])"; exit 1; }
.venv/bin/python -c "
import json,collections;d=json.load(open('$W/$N.build.json'))
print('build ok', collections.Counter((x['severity'],x['code']) for x in d.get('diagnostics',[])))"
./ldraw-agent render output/atlas-crane/atlas-crane.mpd --outdir $W/$N --views $V > $W/$N.render.out 2>&1
SP=/private/tmp/claude-501/-Users-captain-workspaces-workspace-ai-ldraw-nova/41eb1e67-4bb7-4eb6-8e52-05f31fd87c92/scratchpad
args=""
for v in $V; do args="$args $W/$N/$v.png::$v"; done
.venv/bin/python $SP/sheet2.py $W/$N-sheet.png 2 620 $args
echo "sheet: $W/$N-sheet.png"
