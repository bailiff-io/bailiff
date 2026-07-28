"""probe.py replaces shell the runbooks asked the agent to run and read by eye.

The scenario suggestion routes the whole session, so a wrong marker reading sends
the agent into the wrong runbook. These build real trees rather than mocking the
filesystem, because the thing under test is what the filesystem says.
"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from conftest import SCRIPTS, _load

probe = _load("probe")


def git_init(path):
    subprocess.run(["git", "-C", str(path), "init", "--quiet"], check=True)


def commit(path, message="init"):
    subprocess.run(["git", "-C", str(path), "add", "-A"], check=True)
    subprocess.run(
        ["git", "-C", str(path), "-c", "user.name=t", "-c", "user.email=t@t",
         "commit", "--quiet", "-m", message],
        check=True,
    )


# -------------------------------------------------------------------- presence


def test_a_missing_directory_is_reported_not_raised(tmp_path):
    report = probe.probe(tmp_path / "nope")
    assert report["exists"] is False
    assert report["empty"] is True
    assert report["scenario"]["suggested"] == "new-project"


def test_an_empty_directory_suggests_new_project_and_asks_intent(tmp_path):
    """A fresh monorepo has no marker either, so the suggestion cannot be
    trusted alone."""
    report = probe.probe(tmp_path)
    assert report["scenario"]["suggested"] == "new-project"
    assert report["scenario"]["ask_intent"] is True


def test_a_dotfile_only_directory_is_not_empty(tmp_path):
    (tmp_path / ".envrc").write_text("x")
    report = probe.probe(tmp_path)
    assert report["empty"] is False
    assert report["visible_entries"] == []


# ----------------------------------------------------------------------- git


def test_git_facts_come_from_git(tmp_path):
    git_init(tmp_path)
    (tmp_path / "a.py").write_text("x = 1\n")
    commit(tmp_path)
    report = probe.probe(tmp_path)
    assert report["git"]["repo"] is True
    assert report["git"]["commits"] == "1"
    assert report["git"]["dirty"] is False


def test_a_dirty_tree_is_flagged_with_its_paths(tmp_path):
    """Rendering over uncommitted work leaves the user no diff to review, so
    this is the fact that gates a render."""
    git_init(tmp_path)
    (tmp_path / "a.py").write_text("x = 1\n")
    commit(tmp_path)
    (tmp_path / "a.py").write_text("x = 2\n")
    report = probe.probe(tmp_path)
    assert report["git"]["dirty"] is True
    assert any("a.py" in line for line in report["git"]["dirty_paths"])


def test_a_non_repo_reports_dirty_as_unknown_not_false(tmp_path):
    """False would read as "clean, safe to render"; there is no answer here."""
    report = probe.probe(tmp_path)
    assert report["git"]["repo"] is False
    assert report["git"]["dirty"] is None


# ----------------------------------------------------------------- workspaces


@pytest.mark.parametrize(
    "name,body,mechanism",
    [
        ("moon.yml", "projects: []\n", "moon"),
        ("pnpm-workspace.yaml", "packages:\n  - 'packages/*'\n", "pnpm"),
        ("go.work", "go 1.25\n", "go"),
        ("pyproject.toml", "[tool.uv.workspace]\nmembers = []\n", "uv"),
        ("Cargo.toml", "[workspace]\nmembers = []\n", "cargo"),
    ],
)
def test_each_workspace_marker_is_detected(tmp_path, name, body, mechanism):
    (tmp_path / name).write_text(body)
    report = probe.probe(tmp_path)
    assert any(w["mechanism"] == mechanism for w in report["workspace"])
    assert report["scenario"]["suggested"] == "monorepo"


def test_a_plain_pyproject_is_not_a_workspace(tmp_path):
    """pyproject.toml and Cargo.toml exist in single-package repos, so the
    marker is the table inside, not the filename."""
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n')
    report = probe.probe(tmp_path)
    assert report["workspace"] == []
    assert report["languages"] == ["python"]


def test_a_plain_cargo_toml_is_not_a_workspace(tmp_path):
    (tmp_path / "Cargo.toml").write_text('[package]\nname = "x"\n')
    assert probe.probe(tmp_path)["workspace"] == []


def test_an_unreadable_marker_does_not_raise(tmp_path):
    (tmp_path / "pyproject.toml").write_bytes(b"\xff\xfe\x00binary")
    report = probe.probe(tmp_path)
    assert report["workspace"] == []


# -------------------------------------------------------------- repo contents


def test_manifests_and_lockfiles_answer_the_language_questions(tmp_path):
    """These are the answers the existing-repo runbook must take from the repo
    rather than from the user."""
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n')
    (tmp_path / "uv.lock").write_text("")
    (tmp_path / "package.json").write_text("{}")
    (tmp_path / "pnpm-lock.yaml").write_text("")
    report = probe.probe(tmp_path)
    assert report["languages"] == ["python", "ts"]
    assert report["package_managers"] == ["pnpm", "uv"]


def test_the_existing_hook_manager_and_ci_host_are_found(tmp_path):
    (tmp_path / ".pre-commit-config.yaml").write_text("repos: []\n")
    (tmp_path / ".github/workflows").mkdir(parents=True)
    report = probe.probe(tmp_path)
    assert report["hook_managers"] == ["precommit"]
    assert report["ci_hosts"] == ["github"]


def test_prior_renders_are_read_from_the_answers_files(tmp_path):
    """These name the packages already rendered here and carry the identity to
    reuse instead of asking again."""
    (tmp_path / ".copier-answers.base.yml").write_text("project_name: x\n")
    (tmp_path / ".copier-answers.python.yml").write_text("python_version: '3.13'\n")
    report = probe.probe(tmp_path)
    assert report["rendered_packages"] == ["base", "python"]


# ------------------------------------------------------------ package dirs


def test_a_manifest_makes_a_directory_a_package(tmp_path):
    (tmp_path / "packages/api").mkdir(parents=True)
    (tmp_path / "packages/api/pyproject.toml").write_text('[project]\nname = "api"\n')
    (tmp_path / "packages/notes").mkdir(parents=True)
    (tmp_path / "packages/notes/README.md").write_text("# notes\n")
    report = probe.probe(tmp_path)
    assert report["package_dirs"] == ["packages/api"]


def test_populated_package_dirs_route_to_add_package(tmp_path):
    (tmp_path / "moon.yml").write_text("projects: []\n")
    (tmp_path / "apps/web").mkdir(parents=True)
    (tmp_path / "apps/web/package.json").write_text("{}")
    report = probe.probe(tmp_path)
    assert report["scenario"]["runbook"].endswith("add-package/index.md")


def test_a_marker_with_no_packages_routes_to_setup(tmp_path):
    (tmp_path / "moon.yml").write_text("projects: []\n")
    report = probe.probe(tmp_path)
    assert report["scenario"]["runbook"].endswith("setup/index.md")


# ------------------------------------------------------------------ scenarios


def test_git_plus_source_suggests_existing_repo_without_asking(tmp_path):
    """The one case markers settle on their own."""
    git_init(tmp_path)
    (tmp_path / "main.go").write_text("package main\n")
    (tmp_path / "go.mod").write_text("module x\n")
    commit(tmp_path)
    report = probe.probe(tmp_path)
    assert report["scenario"]["suggested"] == "existing-repo"
    assert report["scenario"]["ask_intent"] is False


def test_a_workspace_marker_beats_existing_repo(tmp_path):
    git_init(tmp_path)
    (tmp_path / "go.work").write_text("go 1.25\n")
    commit(tmp_path)
    assert probe.probe(tmp_path)["scenario"]["suggested"] == "monorepo"


def test_a_fresh_git_repo_with_no_source_is_a_new_project(tmp_path):
    """`git init` alone is not a repo with conventions to read."""
    git_init(tmp_path)
    assert probe.probe(tmp_path)["scenario"]["suggested"] == "new-project"


def test_every_suggested_runbook_exists():
    """A suggestion naming a file that is not there sends the agent nowhere."""
    from conftest import PACKAGES

    skill = PACKAGES.parent
    for runbook in (
        "runbooks/new-project/index.md",
        "runbooks/existing-repo/index.md",
        "runbooks/monorepo/setup/index.md",
        "runbooks/monorepo/add-package/index.md",
    ):
        assert (skill / runbook).is_file(), runbook


def test_cli_emits_json_and_exits_zero(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "probe.py"), str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout)["exists"] is True
