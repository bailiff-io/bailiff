#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["python-frontmatter>=1.1,<2", "pyyaml>=6,<7"]
# ///
"""Emit the bailiff tool catalog as JSON.

Reads every tools/<group>/<package>/package.md frontmatter and the sibling
copier.yml, groups packages by choice axis, and reports contract violations
under "lint". Exits 1 when any violation is found.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import frontmatter
import yaml

LIST_FIELDS = ("provides", "after", "depends_on", "requires_bin")
SCALAR_FIELDS = ("name", "summary", "precheck")
KNOWN_FIELDS = set(LIST_FIELDS) | set(SCALAR_FIELDS)

# copier reserved keys are configuration, not questions
COPIER_RESERVED_PREFIX = "_"


def tools_root(skill_dir: Path) -> Path:
    return skill_dir / "tools"


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(v) for v in value]
    return []


def read_questions(copier_yml: Path) -> tuple[list[dict[str, Any]], str | None]:
    """Extract question definitions from a copier.yml.

    Returns (questions, error). Reserved keys (leading underscore) are skipped.
    """
    try:
        raw = yaml.safe_load(copier_yml.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        return [], f"unparseable copier.yml: {exc}"
    if not isinstance(raw, dict):
        return [], "copier.yml is not a mapping"

    questions: list[dict[str, Any]] = []
    for key, spec in raw.items():
        if str(key).startswith(COPIER_RESERVED_PREFIX):
            continue
        entry: dict[str, Any] = {"key": str(key)}
        if isinstance(spec, dict):
            if spec.get("when") is False:
                entry["hidden"] = True
            for field in ("type", "help", "choices", "default", "validator", "secret"):
                if field in spec:
                    entry[field] = spec[field]
        else:
            entry["type"] = "str"
            entry["default"] = spec
        questions.append(entry)
    return questions, None


def axis_of(tag: str) -> str:
    """The choice axis is the tag's namespace: 'language:python' -> 'language'."""
    return tag.split(":", 1)[0] if ":" in tag else tag


def read_package(pkg_dir: Path, group: str) -> tuple[dict[str, Any] | None, list[str]]:
    """Parse one package directory. Returns (package, lint_messages)."""
    lint: list[str] = []
    rel = f"{group}/{pkg_dir.name}"
    package_md = pkg_dir / "package.md"

    if not package_md.is_file():
        return None, [f"{rel}: no package.md"]

    try:
        post = frontmatter.load(package_md)
    except Exception as exc:  # frontmatter raises assorted parser errors
        return None, [f"{rel}: unparseable package.md frontmatter: {exc}"]

    meta = dict(post.metadata or {})
    name = str(meta.get("name") or "")

    if not name:
        lint.append(f"{rel}: package.md declares no name")
        name = pkg_dir.name
    elif name != pkg_dir.name:
        lint.append(f"{rel}: name '{name}' differs from directory name '{pkg_dir.name}'")

    summary = str(meta.get("summary") or "")
    if not summary:
        lint.append(f"{rel}: package.md declares no summary")

    for key in meta:
        if key not in KNOWN_FIELDS:
            lint.append(f"{rel}: unknown frontmatter field '{key}'")

    copier_yml = pkg_dir / "copier.yml"
    renders = copier_yml.is_file()
    questions: list[dict[str, Any]] = []
    if renders:
        questions, err = read_questions(copier_yml)
        if err:
            lint.append(f"{rel}: {err}")
        if not any(pkg_dir.rglob("*_copier_conf.answers_file*")):
            lint.append(f"{rel}: template ships no answers-file template")

    precheck = meta.get("precheck")
    if precheck:
        precheck_path = pkg_dir / str(precheck)
        if not precheck_path.is_file():
            lint.append(f"{rel}: precheck '{precheck}' does not exist")

    provides = _as_list(meta.get("provides"))
    if not provides:
        lint.append(f"{rel}: package.md declares no provides tag")

    package: dict[str, Any] = {
        "name": name,
        "group": group,
        "id": rel,
        "summary": summary,
        "provides": provides,
        "axes": sorted({axis_of(t) for t in provides}),
        "after": _as_list(meta.get("after")),
        "depends_on": _as_list(meta.get("depends_on")),
        "requires_bin": _as_list(meta.get("requires_bin")),
        "renders": renders,
        "precheck": str(precheck) if precheck else None,
        "steering": f"tools/{rel}/package.md",
    }
    if questions:
        package["questions"] = questions
    return package, lint


def build_catalog(skill_dir: Path) -> dict[str, Any]:
    root = tools_root(skill_dir)
    lint: list[str] = []
    groups: list[dict[str, Any]] = []
    all_names: set[str] = set()

    if not root.is_dir():
        return {"groups": [], "lint": [f"no tools directory at {root}"]}

    for group_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        group = group_dir.name
        index_md = group_dir / "index.md"
        if not index_md.is_file():
            lint.append(f"{group}: no index.md")

        packages: list[dict[str, Any]] = []
        for pkg_dir in sorted(p for p in group_dir.iterdir() if p.is_dir()):
            package, pkg_lint = read_package(pkg_dir, group)
            lint.extend(pkg_lint)
            if package:
                packages.append(package)
                all_names.add(package["name"])

        axes: dict[str, list[str]] = {}
        for package in packages:
            for axis in package["axes"]:
                axes.setdefault(axis, []).append(package["name"])

        groups.append(
            {
                "name": group,
                "index": f"tools/{group}/index.md",
                "axes": {a: sorted(names) for a, names in sorted(axes.items())},
                "packages": packages,
            }
        )

    # edge validation needs the full name set, so it runs after the walk
    for group in groups:
        for package in group["packages"]:
            for field in ("after", "depends_on"):
                for target in package[field]:
                    if target not in all_names:
                        lint.append(
                            f"{package['id']}: {field} names unknown package '{target}'"
                        )

    return {"groups": groups, "lint": sorted(lint)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skill-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="directory containing SKILL.md (default: this script's parent)",
    )
    parser.add_argument(
        "--lint-only",
        action="store_true",
        help="print only contract violations",
    )
    args = parser.parse_args(argv)

    catalog = build_catalog(args.skill_dir.resolve())

    if args.lint_only:
        for message in catalog["lint"]:
            print(message, file=sys.stderr)
    else:
        json.dump(catalog, sys.stdout, indent=2, sort_keys=False)
        sys.stdout.write("\n")
        for message in catalog["lint"]:
            print(message, file=sys.stderr)

    return 1 if catalog["lint"] else 0


if __name__ == "__main__":
    sys.exit(main())
