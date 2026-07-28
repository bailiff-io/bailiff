#!/usr/bin/env python3
"""Bootstrap beads in the destination repository.

    bd_init.py [--prefix P] [--skip-hooks] [--dolt-sync git-origin|local-only]
               [--auto-export] [--github-owner O --github-repo R]
               [--setup HARNESS ...]

Wraps `bd init --init-if-missing --non-interactive`, which exits 0 on a second run
instead of aborting. Copier runs this in the destination directory.

Always passes --skip-agents. Without it `bd init` installs the claude and codex
integrations whether or not they were asked for, which makes --setup unable to
express a selection that excludes either one.

`bd init` derives the Dolt remote from the repo's git origin on its own, so
--dolt-sync=local-only removes it afterwards rather than suppressing it.
"""

from __future__ import annotations

import argparse
import subprocess
import sys


def run(command: list[str], *, required: bool = True) -> int:
    print(f"beads: {' '.join(command)}")
    code = subprocess.run(command).returncode
    if code != 0 and required:
        print(f"beads: {' '.join(command)} failed with exit {code}", file=sys.stderr)
    return code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", default="")
    parser.add_argument("--skip-hooks", action="store_true")
    parser.add_argument("--dolt-sync", default="git-origin", choices=["git-origin", "local-only"])
    parser.add_argument("--auto-export", action="store_true")
    parser.add_argument("--github-owner", default="")
    parser.add_argument("--github-repo", default="")
    parser.add_argument("--setup", action="append", default=[], metavar="HARNESS")
    args = parser.parse_args(argv)

    command = ["bd", "init", "--init-if-missing", "--non-interactive", "--skip-agents"]
    if args.prefix:
        command += ["--prefix", args.prefix]
    if args.skip_hooks:
        command.append("--skip-hooks")
    if (code := run(command)) != 0:
        return code

    if args.dolt_sync == "local-only":
        # A missing remote is the desired end state, so a failure here is not one.
        run(["bd", "dolt", "remote", "remove", "origin"], required=False)

    if args.auto_export and (code := run(["bd", "config", "set", "export.auto", "true"])) != 0:
        return code

    for key, value in (("github.owner", args.github_owner), ("github.repo", args.github_repo)):
        if value and (code := run(["bd", "config", "set", key, value])) != 0:
            return code

    for harness in args.setup:
        if (code := run(["bd", "setup", harness])) != 0:
            return code
    return 0


if __name__ == "__main__":
    sys.exit(main())
