#!/bin/sh
set -eu
task_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$task_dir"
if [ "$#" -ne 0 ]; then
  echo "Usage: ./setup.sh" >&2
  exit 2
fi
./scripts/setup-tools.sh
./scripts/setup-viewer.sh
export UV_CACHE_DIR="$task_dir/.cache/uv"
export UV_PYTHON_INSTALL_DIR="$task_dir/bin/python"
# Nova imports LSynth configuration and runs synthesis through its own Python.
bin/uv sync --locked --python 3.12 --extra test
# Print checkout-specific configuration without changing the user's shell profile.
cat <<EOF_ENV
Tools installed under $task_dir/bin; official library under $task_dir/data/ldraw.
For this project, set these in your shell and restart agents from that shell:
export LDRAW_DIR="$task_dir/data/ldraw"
export LDRAWDIR="\$LDRAW_DIR"
export LDRAW_XRAY_CACHE="$task_dir/.cache/ldraw-xray"
export LDRAW_ANNOTATOR_DB="$task_dir/data/ldraw-info.db"
# export LEOCAD=/absolute/path/to/leocad
# export TYPESAFE_API_KEY=...   # optional semantic search
Use bin/ldraw-xray, bin/ldraw-annotator and bin/lsynth directly; bin/ need not be on PATH.
Launch the model selector with ./model-selector.sh (http://127.0.0.1:8770/).
See docs/setup.md for renderer prerequisites and annotator credentials.
EOF_ENV
export LDRAW_DIR="$task_dir/data/ldraw"
export LDRAWDIR="$LDRAW_DIR"
export LDRAW_XRAY_CACHE="$task_dir/.cache/ldraw-xray"
export LDRAW_ANNOTATOR_DB="$task_dir/data/ldraw-info.db"
./ldraw-agent doctor
./ldraw-agent index
./ldraw-agent spec --page 63 > /dev/null
bin/ldraw-xray doctor
./model-selector.sh --index-only
