#!/bin/sh
# Same as fetch.ps1 for a shell with curl.
cd "$(dirname "$0")"; while IFS="$(printf '\t')" read -r f u; do [ -n "$u" ] && curl -sS -L -o "$f" "$u" && echo "$f $(wc -c < "$f") bytes"; done < urls.tsv
