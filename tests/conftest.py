"""Shared fixtures. The scripts live outside an importable package, so they are
loaded by path rather than imported by name."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / ".apm/skills/bailiff/scripts"
PACKAGES = REPO / ".apm/skills/bailiff/packages"


def _load(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


scan = _load("scan")
render = _load("render")


def make_skill(root: Path, packages: dict[str, dict[str, str]]) -> Path:
    """Build a throwaway skill tree.

    `packages` maps "<group>/<package>" to a file map, where each key is a path
    relative to the package directory. A group gets an index.md automatically,
    because a missing one is a lint finding of its own and would mask the
    finding under test.
    """
    catalog = root / "packages"
    for pkg_id, files in packages.items():
        group, _, name = pkg_id.partition("/")
        pkg_dir = catalog / group / name
        pkg_dir.mkdir(parents=True, exist_ok=True)
        (catalog / group / "index.md").write_text(f"# {group}\n", encoding="utf-8")
        for rel, content in files.items():
            target = pkg_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
    return root
