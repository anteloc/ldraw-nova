#!/bin/bash
ldraw_errors() {
  local error="" file="" line content line_no

  while IFS= read -r line; do
    case "$line" in
      "Error: "*)
        error="${line#Error: }"
        file=""
        ;;

      "File: "*)
        [[ -n "$error" ]] && file="${line#File: }"
        ;;

      "Line #"*)
        [[ -n "$error" && -n "$file" ]] || continue

        if [[ "$line" =~ ^Line\ \#([0-9]+):\ (.*)$ ]]; then
          line_no="${BASH_REMATCH[1]}"
          content="${BASH_REMATCH[2]}"

          jq -nc \
            --arg error "$error" \
            --arg file "$file" \
            --arg line "$line_no" \
            --arg content "$content" \
            '{
              error: $error,
              file: $file,
              line: ($line | tonumber),
              content: $content
            }'
        fi

        error=""
        file=""
        ;;
    esac
  done
}

model="$1"

if [ -z "$model" ]; then
  echo "Usage: $0 <model-file>"
  echo "Checks an LDraw .mpd, .ldr, or .dat model file for errors, reporting them in JSON format."
  echo '
Example outputs:
{"error":"Error parsing line.","file":"42000-1-corrupted.mpd","line":46,"content":"19 0 20 0 -20 0 -1 0 1 0 0 0 0 1 32524.dat"}
{"error":"Singular matrix.","file":"2210-1-broken.mpd","line":57,"content":"1 0 20 0 -20 0 -1 0 0 0 0 0 0 1 12624.dat"}
  '
  exit 1
fi

# Check if the model file exists
if [ ! -f "$model" ]; then
  echo "Error: File '$model' not found."
  exit 1
fi

# This is a workaround to check the model, we discard the image output in any case, 
# so ldview does the heavy work of syntax and error checking validations
ldview "$model" -SaveSnapshot=/tmp/dummy.jpg -SaveSteps=1 | ldraw_errors
