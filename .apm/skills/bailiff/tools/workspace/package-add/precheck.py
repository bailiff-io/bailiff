#!/usr/bin/env python3
"""Validate the answers package-add interpolates into shell commands.

`name` reaches `uv init --name`, `go mod init`, and the manifests, so a value
carrying a path separator or a shell metacharacter is rejected before copier
runs any task. Also checks the one binary the chosen language needs, which
requires_bin cannot express because it varies per answer.

render.py exports each scalar answer as BAILIFF_<KEY>.
"""

from __future__ import annotations

import os
import re
import shutil
import sys

NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

TOOLS = {
    ("ts", "bun"): ("bun", "https://bun.sh/docs/installation"),
    ("ts", "pnpm"): ("pnpm", "https://pnpm.io/installation"),
    ("ts", "npm"): ("npm", "https://nodejs.org"),
    ("python", "uv"): ("uv", "https://docs.astral.sh/uv/getting-started/installation/"),
    ("python", "pdm"): ("pdm", "https://pdm-project.org/en/latest/#installation"),
    ("go", ""): ("go", "https://go.dev/doc/install"),
    ("rust", ""): ("cargo", "https://rustup.rs/"),
}


def main() -> int:
    name = os.environ.get("BAILIFF_NAME", "")
    lang = os.environ.get("BAILIFF_LANG", "")

    if not NAME_RE.match(name):
        print(
            f"package-add: name {name!r} must start alphanumeric and hold only"
            " letters, digits, dot, dash, or underscore.",
            file=sys.stderr,
        )
        return 1

    if lang == "ts":
        variant = os.environ.get("BAILIFF_JS_PKG_MANAGER", "")
    elif lang == "python":
        variant = os.environ.get("BAILIFF_PYTHON_PKG_MANAGER", "")
    else:
        variant = ""

    tool = TOOLS.get((lang, variant))
    if tool is None:
        print(
            f"package-add: no tool known for lang={lang!r} manager={variant!r}.",
            file=sys.stderr,
        )
        return 1

    binary, url = tool
    if shutil.which(binary) is None:
        print(f"package-add: {binary!r} not found on PATH. See {url}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
