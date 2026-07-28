#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["copier>=9.16,<10", "python-frontmatter>=1.1,<2", "pyyaml>=6,<7"]
# ///
"""Render one bailiff tool package into a destination.

    render.py <group>/<package> <dest> --answers <file>

Runs the package's precheck (when it declares one), verifies the binaries it
requires, then calls copier.run_copy with a namespaced answers file.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import frontmatter
import yaml

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_PRECHECK = 3
EXIT_RENDER = 4

# A package id is exactly one group slug and one package slug. It reaches the
# filesystem as a path, so anything outside this shape is rejected before it is
# joined: '..', a leading '/', a NUL byte, and a case variant that a
# case-insensitive filesystem would otherwise resolve to a real directory.
PACKAGE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]*/[a-z0-9][a-z0-9._-]*$")


class RenderError(Exception):
    """Aborts the run with a message and an exit code."""

    def __init__(self, message: str, code: int = EXIT_RENDER) -> None:
        super().__init__(message)
        self.code = code


def load_answers(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(text) if text.strip() else {}
    except yaml.YAMLError as exc:
        raise RenderError(f"unparseable answers file {path}: {exc}", EXIT_USAGE) from exc
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise RenderError(f"answers file {path} is not a mapping", EXIT_USAGE)
    return data


def load_metadata(pkg_dir: Path) -> dict[str, Any]:
    package_md = pkg_dir / "package.md"
    if not package_md.is_file():
        raise RenderError(f"no package.md in {pkg_dir}", EXIT_USAGE)
    return dict(frontmatter.load(package_md).metadata or {})


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [str(v) for v in value] if isinstance(value, list) else []


def check_binaries(required: list[str]) -> list[str]:
    return [binary for binary in required if shutil.which(binary) is None]


def run_precheck(pkg_dir: Path, script: str, dest: Path, answers: dict[str, Any]) -> None:
    path = pkg_dir / script
    if not path.is_file():
        raise RenderError(f"precheck '{script}' does not exist in {pkg_dir}", EXIT_USAGE)
    env_answers = {f"BAILIFF_{k.upper()}": str(v) for k, v in answers.items() if not isinstance(v, (dict, list))}
    proc = subprocess.run(
        [sys.executable, str(path)] if path.suffix == ".py" else [str(path)],
        cwd=str(dest) if dest.is_dir() else None,
        env={**_environ(), **env_answers, "BAILIFF_DEST": str(dest)},
        capture_output=True,
        text=True,
    )
    if proc.stdout:
        sys.stderr.write(proc.stdout)
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    if proc.returncode != 0:
        raise RenderError(
            f"precheck '{script}' failed with exit {proc.returncode}; nothing rendered",
            EXIT_PRECHECK,
        )


def _environ() -> dict[str, str]:
    import os

    return dict(os.environ)


def render(
    skill_dir: Path,
    package_id: str,
    dest: Path,
    answers: dict[str, Any],
    *,
    pretend: bool = False,
    quiet: bool = False,
) -> dict[str, Any]:
    if not PACKAGE_ID.match(package_id):
        raise RenderError(
            f"malformed package id '{package_id}'; expected <group>/<package>", EXIT_USAGE
        )

    root = (skill_dir / "packages").resolve()
    pkg_dir = (root / package_id).resolve()
    # The id is well-formed, but a symlink inside packages/ can still point out of
    # it, so containment is checked after resolution rather than inferred.
    if not pkg_dir.is_relative_to(root):
        raise RenderError(f"package '{package_id}' resolves outside {root}", EXIT_USAGE)
    if not pkg_dir.is_dir():
        raise RenderError(f"unknown package '{package_id}'", EXIT_USAGE)

    meta = load_metadata(pkg_dir)
    name = str(meta.get("name") or pkg_dir.name)

    missing = check_binaries(_as_list(meta.get("requires_bin")))
    if missing:
        raise RenderError(
            f"{package_id} requires these executables on PATH: {', '.join(missing)}",
            EXIT_PRECHECK,
        )

    dest.mkdir(parents=True, exist_ok=True)

    precheck = meta.get("precheck")
    if precheck:
        run_precheck(pkg_dir, str(precheck), dest, answers)

    copier_yml = pkg_dir / "copier.yml"
    if not copier_yml.is_file():
        return {
            "package": package_id,
            "renders": False,
            "note": "steering-only package; the agent authors its output",
        }

    import copier

    try:
        copier.run_copy(
            str(pkg_dir),
            str(dest),
            data=answers,
            answers_file=f".copier-answers.{name}.yml",
            unsafe=True,
            defaults=True,
            overwrite=True,
            pretend=pretend,
            quiet=quiet,
            cleanup_on_error=True,
            vcs_ref=None,
        )
    except Exception as exc:
        raise RenderError(f"{package_id}: render failed: {exc}", EXIT_RENDER) from exc

    return {
        "package": package_id,
        "renders": True,
        "answers_file": f".copier-answers.{name}.yml",
        "dest": str(dest),
        "pretend": pretend,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", help="<group>/<package>")
    parser.add_argument("dest", type=Path, help="destination directory")
    parser.add_argument(
        "--answers", type=Path, help="YAML or JSON file of answers for this package"
    )
    parser.add_argument(
        "--skill-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="directory containing SKILL.md (default: this script's parent)",
    )
    parser.add_argument("--pretend", action="store_true", help="render nothing; validate only")
    parser.add_argument("--quiet", action="store_true", help="suppress copier output")
    args = parser.parse_args(argv)

    try:
        answers = load_answers(args.answers) if args.answers else {}
        result = render(
            args.skill_dir.resolve(),
            args.package,
            args.dest,
            answers,
            pretend=args.pretend,
            quiet=args.quiet,
        )
    except RenderError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.code

    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
