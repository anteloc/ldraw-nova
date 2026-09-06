#!/bin/sh
set -eu
task_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$task_dir"
if command -v uv >/dev/null 2>&1; then
  uv sync --locked --extra test
else
  python3 -m venv .venv
  .venv/bin/python -m pip install -e '.[test]'
fi
./ldraw-agent doctor
./ldraw-agent index
./ldraw-agent spec --page 63 > /dev/null
