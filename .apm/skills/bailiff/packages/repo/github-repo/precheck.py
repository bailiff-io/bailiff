#!/usr/bin/env python3
"""Abort before rendering when a public GitHub repo lacks typed confirmation.

`gh repo create --public` publishes the repository immediately and no later
step undoes it, so the confirmation is a typed answer rather than a boolean:
public_confirm must repeat project_name exactly.
"""

from __future__ import annotations

import os
import sys


def truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def main() -> int:
    if not truthy(os.environ.get("BAILIFF_CREATE_REMOTE", "")):
        return 0
    if os.environ.get("BAILIFF_VISIBILITY", "").strip().lower() != "public":
        return 0

    project_name = os.environ.get("BAILIFF_PROJECT_NAME", "").strip()
    confirm = os.environ.get("BAILIFF_PUBLIC_CONFIRM", "").strip()

    if not project_name:
        print(
            "github-repo: visibility=public needs project_name set so the "
            "confirmation can be checked. Nothing rendered.",
            file=sys.stderr,
        )
        return 1
    if confirm != project_name:
        print(
            "github-repo: ABORTED. visibility=public with create_remote=true "
            f"requires public_confirm to equal the project name '{project_name}'. "
            f"Got '{confirm}'. Read the visibility answer back to the user, then "
            "set public_confirm or switch visibility to private. Nothing rendered.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
