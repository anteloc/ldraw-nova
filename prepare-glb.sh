#!/bin/bash

script_dir=$(dirname "$0")
script_dir=$(realpath "$script_dir")

export LDRAW_LIB_DIR="$HOME/workspaces/workspace-ai/ldraw-lib"
export LDRAW_DIR="$LDRAW_LIB_DIR/ldraw"
export PARTS_DIR="$LDRAW_DIR/parts"
export MODELS_DIR="$LDRAW_LIB_DIR/models-annotated"
export PARTS_GLB_DIR="$script_dir/parts-glb"
export MODELS_GLB_DIR="$script_dir/models-glb"

function usage() {
    echo "Usage: $0 <--model|--part> <model or part name>"
    echo "Converts a .mpd, .ldr or .dat LDraw part file into a .glb file, prepared for use in Blender by LLMs via MCP"
    echo "Example: "
    echo "$0 --part 71944.dat"
    echo "Finished: part '71944.dat' rendered to GLB: ./$PARTS_GLB_DIR/71944.glb"
    exit 1
}

src_type="$1"
src_name="$2"

if [ "$src_type" == "--model" ]; then
    src_path="$MODELS_DIR/$src_name"
elif [ "$src_type" == "--part" ]; then
    src_path="$PARTS_DIR/$src_name"
else
    usage
fi

# src_path is already set based on the type (--model or --part), so this line should be removed.

if [ ! -f "$src_path" ]; then
    echo "Error: Requested model or part '$src_name' does not exist." >&2
    exit 1
fi

dest_glb_name="$(basename "$src_name" | sed 's/\.[^.]*$/.glb/')"

if [ "$src_type" == "--model" ]; then
    dest_glb_path="$MODELS_GLB_DIR/$dest_glb_name"
elif [ "$src_type" == "--part" ]; then
    dest_glb_path="$PARTS_GLB_DIR/$dest_glb_name"
fi

[ -d "$PARTS_GLB_DIR" ] || mkdir -p "$PARTS_GLB_DIR"
[ -d "$MODELS_GLB_DIR" ] || mkdir -p "$MODELS_GLB_DIR"

# temporary tsv file, to be deleted on script exit
descriptions_tsv_tmp=$(mktemp)
trap 'rm -f "$descriptions_tsv_tmp"' EXIT

$LDRAW_LIB_DIR/scripts/ldraw-info-db-query-descriptions.sh --parts --format tabs --max-results -1 > "$descriptions_tsv_tmp"

# Set the default 16 color (Main Color) to Pearl Dark Grey (16), to avoid undesired color or transparency issues when rendering parts with color 16 (Pearl Dark Grey) in LDraw.
mpd2glb.sh -l $LDRAW_DIR -c draco --descriptions "$descriptions_tsv_tmp" --map-color 16,Pearl_Dark_Grey -o "$dest_glb_path" "$src_path"

if [ "$src_type" == "--model" ]; then
    echo "Prepared: '$src_name' rendered to GLB: ./models-glb/$dest_glb_name"
elif [ "$src_type" == "--part" ]; then
    echo "Prepared: '$src_name' rendered to GLB: ./parts-glb/$dest_glb_name"
fi

