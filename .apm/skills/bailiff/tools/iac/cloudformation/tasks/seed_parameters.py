#!/usr/bin/env python3
"""Write one parameters/<env>.json per environment name.

    seed_parameters.py <placement_dir> <env> [<env> ...]

Copier renders a fixed path set from the template tree, so a file count driven by
an answer needs a task. Copier runs it in the destination directory. Existing
files are left alone: they hold the project's real parameter values.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    if len(argv) < 1:
        print("usage: seed_parameters.py <placement_dir> [<env> ...]", file=sys.stderr)
        return 2

    placement, names = Path(argv[0]), argv[1:]
    if not names:
        print("cloudformation: environment_names is empty; no parameter files written")
        return 0

    target = placement / "parameters"
    target.mkdir(parents=True, exist_ok=True)
    for name in names:
        path = target / f"{name}.json"
        if path.exists():
            continue
        body = [{"ParameterKey": "Environment", "ParameterValue": name}]
        path.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
        print(f"cloudformation: seeded {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
