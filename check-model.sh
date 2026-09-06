#!/bin/sh
# Structured Python diagnostics plus a LeoCAD snapshot/BOM import smoke test.
set -eu
task_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ "$#" -ne 1 ]; then
  echo 'Usage: ./check-model.sh model.mpd' >&2
  exit 2
fi
exec "$task_dir/ldraw-agent" cad-check "$1"
