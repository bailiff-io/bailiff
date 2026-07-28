#!/usr/bin/env python3
"""Check that the chosen JavaScript package manager is on PATH.

`requires_bin` cannot express "one of bun, pnpm, npm", so the choice is checked
here against the js_pkg_manager answer that render.py exports as
BAILIFF_JS_PKG_MANAGER.
"""

from __future__ import annotations

import os
import shutil
import sys

INSTALL_URL = {
    "bun": "https://bun.sh/docs/installation",
    "pnpm": "https://pnpm.io/installation",
    "npm": "https://nodejs.org/en/download",
}


def main() -> int:
    manager = os.environ.get("BAILIFF_JS_PKG_MANAGER", "bun")
    if manager not in INSTALL_URL:
        print(f"ts: unknown js_pkg_manager '{manager}'", file=sys.stderr)
        return 1
    if shutil.which(manager) is None:
        print(
            f"ts: '{manager}' is not on PATH; it writes package.json.\n"
            f"  install it from {INSTALL_URL[manager]}, "
            f"or answer js_pkg_manager with another option",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
