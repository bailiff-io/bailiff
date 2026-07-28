#!/usr/bin/env bash
# Seed .gitignore with editor and OS entries via gitnr.
# Best-effort: gitnr is optional, so a missing binary or a failed run leaves the
# file absent and exits 0. A non-zero exit would trip copier's cleanup_on_error
# and delete everything base rendered.
set -u

if [ -f .gitignore ]; then
  exit 0
fi

if ! command -v gitnr >/dev/null 2>&1; then
  echo "base: gitnr not on PATH; no .gitignore written. Install https://github.com/reemus-dev/gitnr or write one by hand." >&2
  exit 0
fi

gitnr create --save ghg:macOS ghg:Linux ghg:Windows ghg:JetBrains ghg:VisualStudioCode ghg:Vim ||
  echo "base: gitnr failed; no .gitignore written." >&2

exit 0
