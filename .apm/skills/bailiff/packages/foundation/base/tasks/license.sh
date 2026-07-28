#!/usr/bin/env bash
# Fetch a LICENSE body from the GitHub Licenses API.
#   license.sh <spdx-id> <copyright-holder>
# Best-effort: the network, gh's absence, or an unauthenticated gh leaves no
# LICENSE and exits 0. A non-zero exit would trip copier's cleanup_on_error and
# delete everything base rendered.
set -u

spdx="${1:-none}"
holder="${2:-}"

if [ "$spdx" = "none" ] || [ -z "$spdx" ] || [ -f LICENSE ]; then
  exit 0
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "base: gh not on PATH; no LICENSE written for $spdx." >&2
  exit 0
fi

body="$(gh api "/licenses/$(printf '%s' "$spdx" | tr '[:upper:]' '[:lower:]')" --jq '.body' 2>&1)" || {
  echo "base: LICENSE fetch failed for $spdx: $body" >&2
  exit 0
}

year="$(date +%Y)"
printf '%s\n' "$body" |
  sed -e "s/\[year\]/$year/g" \
    -e "s/\[yyyy\]/$year/g" \
    -e "s|\[fullname\]|$holder|g" \
    -e "s|\[name of copyright owner\]|$holder|g" > LICENSE

exit 0
