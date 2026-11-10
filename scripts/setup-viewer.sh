#!/bin/sh
# Same browser viewer and revision as ldraw-mecha; all assets stay project-local.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
LDRAWORG_REF=a38efc7aca5b1171e888687939d77b6c0b228c7f
vendor="$root/bin/ldbi-viewer"
if [ "$(cat "$vendor/.revision" 2>/dev/null || true)" = "$LDRAWORG_REF" ] &&
   [ -f "$vendor/js/ldraworgscene.js" ] && [ -f "$vendor/js/WebGL.js" ] &&
   [ -f "$vendor/ldbi/js/three.min.js" ] && [ -f "$vendor/ldbi/js/LDRLoader.js" ]; then
  echo "Model selector viewer already installed ($LDRAWORG_REF)"
  exit 0
fi
mkdir -p "$root/bin" "$root/.cache"
tmp=$(mktemp -d "$root/.cache/viewer-setup.XXXXXX")
trap 'rm -rf "$tmp"' EXIT HUP INT TERM
echo "Installing model selector viewer ($LDRAWORG_REF) in $vendor"
curl --fail --location --retry 3 --output "$tmp/library.tar.gz" \
  "https://codeload.github.com/ldraw-org/ldraworg-library/tar.gz/$LDRAWORG_REF"
mkdir -p "$tmp/source" "$tmp/viewer/js"
# Wildcard archive extraction differs across BSD and GNU tar; extract the pinned archive.
tar -xzf "$tmp/library.tar.gz" --strip-components=1 -C "$tmp/source"
cp -R "$tmp/source/public/assets/ldbi" "$tmp/viewer/ldbi"
cp "$tmp/source/public/assets/js/ldraworgscene.js" "$tmp/source/public/assets/js/WebGL.js" "$tmp/viewer/js/"
cp "$tmp/source/LICENSE" "$tmp/viewer/LICENSE-ldraworg-library.txt"
test -f "$tmp/viewer/ldbi/js/three.min.js"
test -f "$tmp/viewer/ldbi/js/LDRLoader.js"
printf '%s\n' "$LDRAWORG_REF" > "$tmp/viewer/.revision"
# Publish only after a successful download and validation.
rm -rf "$vendor"
mv "$tmp/viewer" "$vendor"
