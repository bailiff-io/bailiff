#!/usr/bin/env python3
"""Check that the chosen Python package manager is on PATH.

`requires_bin` cannot express "one of uv, pdm", so the choice is checked here
against the python_pkg_manager answer that render.py exports as
BAILIFF_PYTHON_PKG_MANAGER.
"""

from __future__ import annotations

import os
import shutil
import sys

INSTALL_URL = {
    "uv": "https://docs.astral.sh/uv/getting-started/installation/",
    "pdm": "https://pdm-project.org/latest/#installation",
}


def main() -> int:
    manager = os.environ.get("BAILIFF_PYTHON_PKG_MANAGER", "uv")
    if manager not in INSTALL_URL:
        print(f"python: unknown python_pkg_manager '{manager}'", file=sys.stderr)
        return 1
    if shutil.which(manager) is None:
        print(
            f"python: '{manager}' is not on PATH; it writes pyproject.toml.\n"
            f"  install it from {INSTALL_URL[manager]}, "
            f"or answer python_pkg_manager with the other option",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
