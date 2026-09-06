#!/bin/bash

# This is actually a proxy, to avoid the agent to move up in the directory tree to find the ldraw-info-db-query-descriptions.sh script.

: "${LDRAW_LIB_DIR:=$HOME/workspaces/workspace-ai/ldraw-lib}"

target="$LDRAW_LIB_DIR/scripts/ldraw-info-db-query-descriptions.sh"

# See ldraw-summary.sh: a missing target must not read as an empty result set.
if [ ! -x "$target" ]; then
    echo "Error: '$target' not found or not executable. Set LDRAW_LIB_DIR to the ldraw-lib checkout." >&2
    exit 127
fi

exec "$target" "$@"
