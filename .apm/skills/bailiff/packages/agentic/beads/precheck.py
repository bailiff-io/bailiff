#!/usr/bin/env python3
"""Verify the destination is a git repository.

`bd init` stores issues in an embedded Dolt database under `.beads/` and reads the
repo's git config, so it aborts outside a work tree. Failing here keeps the
render from writing anything.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    dest = Path(os.environ.get("BAILIFF_DEST", "."))
    proc = subprocess.run(
        ["git", "-C", str(dest), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0 or proc.stdout.strip() != "true":
        print(
            f"beads: {dest} is not a git repository. Run 'git init' there first.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
