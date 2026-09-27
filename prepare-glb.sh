#!/bin/sh
set -eu
task_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
task_library=${LDRAW_DIR:-${LDRAWDIR:-}}
task_models="$task_dir/data/models-annotated"
if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  echo 'Usage: ./prepare-glb.sh --file local.mpd [output.glb] | --model name.mpd | --part 3001.dat' >&2
  exit 2
fi
if [ -z "$task_library" ]; then
  echo 'Set LDRAW_DIR (or LDRAWDIR) to the parts library.' >&2
  exit 2
fi
case "$1" in
  --file) task_source=$2; task_dest_dir="$task_dir/models-glb" ;;
  --model) task_source="$task_models/$2"; task_dest_dir="$task_dir/models-glb" ;;
  --part) task_source="$task_library/parts/$2"; task_dest_dir="$task_dir/parts-glb" ;;
  *) echo 'Expected --file, --model or --part.' >&2; exit 2 ;;
esac
task_basename=$(basename -- "$2")
task_output=${3:-"$task_dest_dir/${task_basename%.*}.glb"}
exec "$task_dir/ldraw-agent" --library "$task_library" glb "$task_source" --output "$task_output"
