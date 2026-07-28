#!/usr/bin/env python3
"""Fold .gitignore.d/* fragments into .gitignore.

git reads exactly one .gitignore per directory and has no include directive, so
a rendered fragment is inert until it is folded in. Every package that ships a
fragment carries a copy of this script and runs it as a copier task; the fold is
generic and idempotent, so the order the packages render in does not matter.

Each fragment gets a delimited block. A fragment already present is rewritten in
place rather than appended again, so re-rendering a package converges and an
edited fragment propagates.

Exits 0 when there is nothing to do, including when .gitignore.d is absent: a
non-zero exit would trip copier's cleanup_on_error and delete the whole render.
"""

from __future__ import annotations

import sys
from pathlib import Path

BEGIN = "# >>> bailiff:{name}"
END = "# <<< bailiff:{name}"


def block(name: str, body: str) -> list[str]:
    lines = [BEGIN.format(name=name)]
    lines += body.splitlines()
    lines.append(END.format(name=name))
    return lines


def replace_or_append(lines: list[str], name: str, body: str) -> list[str]:
    begin, end = BEGIN.format(name=name), END.format(name=name)
    try:
        start = lines.index(begin)
    except ValueError:
        prefix = lines + ([""] if lines and lines[-1].strip() else [])
        return prefix + block(name, body)
    try:
        stop = lines.index(end, start)
    except ValueError:  # truncated block; replace to the end of the file
        stop = len(lines) - 1
    return lines[:start] + block(name, body) + lines[stop + 1 :]


def main() -> int:
    fragments = Path(".gitignore.d")
    if not fragments.is_dir():
        return 0

    target = Path(".gitignore")
    try:
        lines = target.read_text(encoding="utf-8").splitlines() if target.is_file() else []
    except (OSError, UnicodeDecodeError) as exc:
        print(f"gitignore: cannot read .gitignore, leaving it alone: {exc}", file=sys.stderr)
        return 0

    for fragment in sorted(p for p in fragments.iterdir() if p.is_file()):
        try:
            body = fragment.read_text(encoding="utf-8").rstrip("\n")
        except (OSError, UnicodeDecodeError) as exc:
            # Skipping beats failing: a non-zero exit here trips copier's
            # cleanup_on_error and deletes every file the render produced.
            print(f"gitignore: skipping {fragment.name}: {exc}", file=sys.stderr)
            continue
        if not body.strip():
            continue
        lines = replace_or_append(lines, fragment.name, body)

    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"gitignore: folded {len(list(fragments.iterdir()))} fragment(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
