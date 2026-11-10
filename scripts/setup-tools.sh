#!/bin/sh
# Project-local tool installation, matching ldraw-mecha's uv layout.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"
UV_VERSION=0.9.3
LDRAW_XRAY_VERSION=0.5.0
JEV_RERANK_VERSION=0.5.0
LDRAW_ANNOTATOR_VERSION=0.5.0
LSYNTH_NOVA_VERSION=0.5.0
export UV_CACHE_DIR="$root/.cache/uv"
export UV_PYTHON_INSTALL_DIR="$root/bin/python"
export UV_TOOL_DIR="$root/bin/uv-tools"
export UV_TOOL_BIN_DIR="$root/bin"
for tool in curl tar unzip; do
  command -v "$tool" >/dev/null 2>&1 || { echo "Install $tool, then rerun ./setup.sh" >&2; exit 2; }
done
case "$(uname -s)-$(uname -m)" in
  Darwin-arm64) platform=aarch64-apple-darwin ;;
  Darwin-x86_64) platform=x86_64-apple-darwin ;;
  Linux-x86_64) platform=x86_64-unknown-linux-gnu ;;
  Linux-aarch64) platform=aarch64-unknown-linux-gnu ;;
  *) echo 'Supported systems: macOS or Linux (including WSL), arm64 or x86_64.' >&2; exit 2 ;;
esac
printf 'Installing uv %s and xray/jev-rerank/annotator/lsynth %s/%s/%s/%s under %s/bin\n' "$UV_VERSION" "$LDRAW_XRAY_VERSION" "$JEV_RERANK_VERSION" "$LDRAW_ANNOTATOR_VERSION" "$LSYNTH_NOVA_VERSION" "$root"
printf 'Official LDraw library: %s/data/ldraw (existing complete library is reused)\n' "$root"
mkdir -p bin .cache data
tmp=$(mktemp -d "$root/.cache/setup.XXXXXX")
trap 'rm -rf "$tmp"' EXIT HUP INT TERM
fetch() { curl --fail --location --retry 3 --output "$2" "$1"; }
case "$(bin/uv --version 2>/dev/null || true)" in
  "uv $UV_VERSION "* | "uv $UV_VERSION") ;;
  *)
    fetch "https://github.com/astral-sh/uv/releases/download/$UV_VERSION/uv-$platform.tar.gz" "$tmp/uv.tar.gz"
    tar -xzf "$tmp/uv.tar.gz" --strip-components=1 -C bin
    ;;
esac
bin/uv tool install --python 3.12 --reinstall "https://github.com/anteloc/ldraw-xray/releases/download/v$LDRAW_XRAY_VERSION/ldraw_xray-$LDRAW_XRAY_VERSION-py3-none-any.whl"
bin/uv tool install --python 3.12 --reinstall "https://github.com/anteloc/jev-rerank/releases/download/v$JEV_RERANK_VERSION/jev_rerank-$JEV_RERANK_VERSION-py3-none-any.whl"
bin/uv tool install --python 3.12 --reinstall "https://github.com/anteloc/ldraw-annotator-nova/releases/download/v$LDRAW_ANNOTATOR_VERSION/ldraw_annotator_nova-$LDRAW_ANNOTATOR_VERSION-py3-none-any.whl"
bin/uv tool install --python 3.12 --reinstall "https://github.com/anteloc/lsynth-nova/releases/download/v$LSYNTH_NOVA_VERSION/lsynth_nova-$LSYNTH_NOVA_VERSION-py3-none-any.whl"
if [ ! -f data/ldraw/LDConfig.ldr ] || [ ! -d data/ldraw/parts ] || [ ! -d data/ldraw/p ]; then
  if [ -e data/ldraw ]; then
    echo 'data/ldraw is incomplete; move it aside and rerun setup.' >&2
    exit 2
  fi
  fetch https://library.ldraw.org/library/updates/complete.zip "$tmp/complete.zip"
  unzip -q "$tmp/complete.zip" -d "$tmp/library"
  test -f "$tmp/library/ldraw/LDConfig.ldr"
  test -d "$tmp/library/ldraw/parts"
  test -d "$tmp/library/ldraw/p"
  mv "$tmp/library/ldraw" data/ldraw
fi
