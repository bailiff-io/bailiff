#!/usr/bin/env python3
"""Verify the toolchain `cdk init --language=<lang>` needs.

`cdk` itself is declared in requires_bin. This checks the per-language runtime,
which depends on an answer and so cannot be a static requires_bin entry.
Answers arrive as BAILIFF_<KEY> environment variables from render.py.
"""

from __future__ import annotations

import os
import shutil
import sys

RUNTIME = {
    "typescript": ("node", "mise use node@lts"),
    "python": ("python3", "mise use python@latest"),
    "go": ("go", "mise use go@latest"),
    "java": ("java", "mise use java@latest"),
    "csharp": ("dotnet", "mise use dotnet@latest"),
}


def main() -> int:
    language = os.environ.get("BAILIFF_CDK_LANGUAGE", "typescript")
    entry = RUNTIME.get(language)
    if entry is None:
        print(f"cdk: unknown cdk_language '{language}'", file=sys.stderr)
        return 1
    binary, install = entry
    if shutil.which(binary) is None:
        print(
            f"cdk: cdk_language={language} needs '{binary}' on PATH. Install it: {install}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
