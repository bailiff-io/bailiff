#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Report what a destination directory already is, as JSON.

Every fact the agent needs to pick a scenario and to answer language questions
from the repo rather than from the user is readable from the filesystem. The
runbooks used to spell this out as shell for the agent to run and interpret by
eye, which made the read non-reproducible and the interpretation a judgment call
per session. This does the read; the agent decides.

Reports what is present, never what to do about it. `scenario` is a suggestion
derived from markers alone: a directory with no marker cannot distinguish "new
single project" from "new monorepo", so the agent still has to ask intent.

Usage:
    probe.py <dest>

Exit codes: 0 probed, 2 usage.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Marker -> workspace mechanism. A file listed with a needle matches only when
# the needle appears in it, because pyproject.toml and Cargo.toml exist in
# single-package repos too.
WORKSPACE_MARKERS: list[tuple[str, str, str | None]] = [
    ("moon.yml", "moon", None),
    ("pnpm-workspace.yaml", "pnpm", None),
    ("go.work", "go", None),
    ("pyproject.toml", "uv", "[tool.uv.workspace]"),
    ("Cargo.toml", "cargo", "[workspace]"),
]

MANIFESTS = {
    "pyproject.toml": "python",
    "setup.py": "python",
    "package.json": "ts",
    "go.mod": "go",
    "Cargo.toml": "rust",
}

LOCKFILES = {
    "uv.lock": "uv",
    "poetry.lock": "poetry",
    "pdm.lock": "pdm",
    "pnpm-lock.yaml": "pnpm",
    "package-lock.json": "npm",
    "yarn.lock": "yarn",
    "bun.lock": "bun",
    "bun.lockb": "bun",
    "go.sum": "go",
    "Cargo.lock": "cargo",
}

HOOK_MANAGERS = {
    ".pre-commit-config.yaml": "precommit",
    "lefthook.yml": "lefthook",
    "lefthook.yaml": "lefthook",
}

CI_HOSTS = {
    ".github/workflows": "github",
    ".gitlab-ci.yml": "gitlab",
}

VERSION_FILES = (
    ".python-version",
    ".node-version",
    ".nvmrc",
    "rust-toolchain.toml",
    ".tool-versions",
    ".mise.toml",
)


def _git(dest: Path, *args: str) -> str | None:
    """Run git in dest. None when git fails, which includes "not a repo"."""
    try:
        done = subprocess.run(
            ["git", "-C", str(dest), *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    return done.stdout.strip() if done.returncode == 0 else None


def _contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False


def probe(dest: Path) -> dict:
    exists = dest.is_dir()
    entries = sorted(p.name for p in dest.iterdir()) if exists else []
    visible = [name for name in entries if not name.startswith(".")]

    report: dict = {
        "dest": str(dest),
        "exists": exists,
        "empty": not entries,
        "entries": len(entries),
        "visible_entries": visible[:50],
    }

    report["git"] = {
        "repo": (dest / ".git").exists(),
        "default_branch": _git(dest, "symbolic-ref", "--short", "refs/remotes/origin/HEAD"),
        "current_branch": _git(dest, "branch", "--show-current"),
        "remote": _git(dest, "remote", "get-url", "origin"),
        "commits": _git(dest, "rev-list", "--count", "HEAD"),
    }
    # A dirty tree has to block rendering: copier passes overwrite=True, so
    # rendering over uncommitted work leaves no diff to review.
    dirty = _git(dest, "status", "--porcelain")
    report["git"]["dirty"] = bool(dirty) if dirty is not None else None
    report["git"]["dirty_paths"] = dirty.splitlines()[:20] if dirty else []

    workspace = []
    for name, mechanism, needle in WORKSPACE_MARKERS:
        path = dest / name
        if path.is_file() and (needle is None or _contains(path, needle)):
            workspace.append({"marker": name, "mechanism": mechanism})
    report["workspace"] = workspace

    report["languages"] = sorted(
        {lang for name, lang in MANIFESTS.items() if (dest / name).is_file()}
    )
    report["package_managers"] = sorted(
        {tool for name, tool in LOCKFILES.items() if (dest / name).is_file()}
    )
    report["hook_managers"] = sorted(
        {tool for name, tool in HOOK_MANAGERS.items() if (dest / name).exists()}
    )
    report["ci_hosts"] = sorted(
        {host for name, host in CI_HOSTS.items() if (dest / name).exists()}
    )
    report["version_files"] = [name for name in VERSION_FILES if (dest / name).is_file()]

    # An existing answers file is the identity the agent must reuse rather than
    # ask for again, and it names which packages already rendered here.
    answers = sorted(p.name for p in dest.glob(".copier-answers.*.yml")) if exists else []
    report["copier_answers"] = answers
    report["rendered_packages"] = [
        name[len(".copier-answers.") : -len(".yml")] for name in answers
    ]

    # Package directories, for a monorepo. Reported as candidates only: a
    # directory holding a manifest is what makes it a package, not its name.
    candidates = []
    if exists:
        for parent in ("packages", "apps", "libs", "services", "crates"):
            base = dest / parent
            if not base.is_dir():
                continue
            for child in sorted(p for p in base.iterdir() if p.is_dir()):
                if any((child / m).is_file() for m in MANIFESTS):
                    candidates.append(str(child.relative_to(dest)))
    report["package_dirs"] = candidates

    report["scenario"] = suggest(report)
    return report


def suggest(report: dict) -> dict:
    """Suggest a scenario from markers, and say what the markers cannot settle.

    Marker detection cannot tell a fresh single project from a fresh monorepo,
    because neither has a marker yet. `ask_intent` says when the agent has to
    put that to the user instead of taking the suggestion.
    """
    if report["workspace"] or report["package_dirs"]:
        which = "monorepo/add-package" if report["package_dirs"] else "monorepo/setup"
        return {"suggested": "monorepo", "runbook": f"runbooks/{which}/index.md",
                "ask_intent": True,
                "why": "a workspace marker or a populated package directory is present"}
    if report["git"]["repo"] and report["visible_entries"]:
        return {"suggested": "existing-repo", "runbook": "runbooks/existing-repo/index.md",
                "ask_intent": False,
                "why": "git history and source are both present"}
    return {
        "suggested": "new-project",
        "runbook": "runbooks/new-project/index.md",
        "ask_intent": True,
        "why": "no marker and no source; a fresh monorepo looks identical here, "
        "so ask whether this is one project, a monorepo, or several repos",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dest", type=Path, help="the destination directory")
    args = parser.parse_args(argv)

    json.dump(probe(args.dest.expanduser().resolve()), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
