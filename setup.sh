#!/bin/sh
set -eu
task_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$task_dir"
with_lsynth=false
case "${1:-}" in
  "") ;;
  --with-lsynth) with_lsynth=true ;;
  *) echo "Usage: ./setup.sh [--with-lsynth]" >&2; exit 2 ;;
esac
if [ "$#" -gt 1 ]; then
  echo "Usage: ./setup.sh [--with-lsynth]" >&2
  exit 2
fi
lsynth_source=${LSYNTH_SOURCE:-../lsynth-nova}
if "$with_lsynth" && [ ! -f "$lsynth_source/pyproject.toml" ]; then
  echo "Missing lsynth-nova checkout: $lsynth_source (override with LSYNTH_SOURCE)" >&2
  exit 2
fi
if command -v uv >/dev/null 2>&1; then
  uv sync --locked --extra test
  if "$with_lsynth"; then
    uv pip install --python .venv/bin/python "$lsynth_source"
  fi
else
  python3 -m venv .venv
  .venv/bin/python -m pip install -e '.[test]'
  if "$with_lsynth"; then
    .venv/bin/python -m pip install "$lsynth_source"
  fi
fi
./ldraw-agent doctor
./ldraw-agent index
./ldraw-agent spec --page 63 > /dev/null
