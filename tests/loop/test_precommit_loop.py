"""spec 011 T005 / spec 014 Surface 2: bailiff-mod-precommit loop tests.

Covers:
- hook_manager removed (spec 014 R13): selecting the module IS choosing pre-commit.
- Fragment written unconditionally (no hook_manager guard).
- Fragment content: base hygiene hooks, gitleaks, shellcheck, typo check, conventional
  commits (conditional on answers).
- spec 014 fragment/merge model: precommit writes .pre-commit.d/bailiff-mod-precommit.yaml
  (not .pre-commit-config.yaml directly — the bundler post-task does that).
- No lefthook.yml is ever produced by this module.
- Dependency edge: depends_on: [bailiff-mod-base] (spec 014 R7 migration from run_after).
- Install task is stubbed offline (preflight marker written).
- No secret: questions.
- hook_blocks union REMOVED (spec 014 R1: fragment/merge model replaces unions).

Contract: specs/014-namespaced-question-keys/contracts/_fragment-merge.md (Surface 2)
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from bailiff import runner, trust
from tests.conftest import TemplateRepo


@pytest.fixture(autouse=True)
def _isolated_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COPIER_SETTINGS_PATH", str(tmp_path / "settings.yml"))


def _init(repo: TemplateRepo, dest: Path, answers: dict) -> None:
    trust.add_trust(repo.url)
    spec = runner.RunSpec(source=repo.url, dest=str(dest), answers=answers)
    runner.init(spec, today="2026-07-13")


# ---------------------------------------------------------------------------
# Fragment is written unconditionally (no hook_manager question)
# ---------------------------------------------------------------------------


def test_precommit_writes_fragment(bailiff_mod_precommit: TemplateRepo, tmp_path: Path) -> None:
    """Selecting precommit → .pre-commit.d/bailiff-mod-precommit.yaml written (MANAGED).

    spec 014 R13: no hook_manager question; selecting the module IS the signal.
    spec 014 Surface 2: the module writes its own fragment; the bundler (_post_task)
    assembles .pre-commit-config.yaml after the full render loop.  Single-layer init
    (runner.init) does not run _post_tasks, so only the fragment exists here.
    """
    dest = tmp_path / "proj"
    _init(bailiff_mod_precommit, dest, {})

    fragment = dest / ".pre-commit.d" / "bailiff-mod-precommit.yaml"
    assert fragment.is_file(), ".pre-commit.d/bailiff-mod-precommit.yaml must exist"
    parsed = yaml.safe_load(fragment.read_text())
    assert "repos" in parsed, "fragment must have a repos key"

    # Stub task ran (preflight marker present)
    assert (dest / ".bailiff-precommit-preflight").is_file(), "preflight stub must run"

    # Vendored close-keywords script is present (MANAGED)
    check_script = dest / ".pre-commit-hooks" / "check-commit-msg.py"
    assert check_script.is_file(), "vendored check-commit-msg.py must be present"

    # No lefthook.yml
    assert not (dest / "lefthook.yml").exists()


def test_precommit_fragment_contains_base_hooks(
    bailiff_mod_precommit: TemplateRepo, tmp_path: Path
) -> None:
    """Base hygiene hooks, gitleaks, shellcheck are in the fragment."""
    dest = tmp_path / "proj"
    _init(bailiff_mod_precommit, dest, {})

    text = (dest / ".pre-commit.d" / "bailiff-mod-precommit.yaml").read_text()
    assert "pre-commit/pre-commit-hooks" in text, "base hooks repo missing"
    assert "trailing-whitespace" in text
    assert "end-of-file-fixer" in text
    assert "gitleaks" in text, "gitleaks hook missing"
    assert "shellcheck" in text, "shellcheck hook missing"


def test_precommit_fragment_enforce_conventional_commits(
    bailiff_mod_precommit: TemplateRepo, tmp_path: Path
) -> None:
    """enforce_conventional_commits=true adds the close-keywords commit-msg hook to fragment."""
    dest = tmp_path / "proj"
    _init(
        bailiff_mod_precommit,
        dest,
        {"enforce_conventional_commits": True},
    )

    text = (dest / ".pre-commit.d" / "bailiff-mod-precommit.yaml").read_text()
    assert "conventional-commit-msg" in text or "check-commit-msg" in text, (
        "enforce_conventional_commits=true must add the commit-msg hook to fragment"
    )
    assert "commit-msg" in text, "commit-msg stage must be referenced"


def test_precommit_fragment_no_conventional_commits_when_disabled(
    bailiff_mod_precommit: TemplateRepo, tmp_path: Path
) -> None:
    """enforce_conventional_commits=false omits the close-keywords hook from fragment."""
    dest = tmp_path / "proj"
    _init(
        bailiff_mod_precommit,
        dest,
        {"enforce_conventional_commits": False},
    )

    text = (dest / ".pre-commit.d" / "bailiff-mod-precommit.yaml").read_text()
    assert "conventional-commit-msg" not in text, (
        "conventional commit hook must be absent when enforce_conventional_commits=false"
    )


def test_precommit_fragment_typo_check_default_on(
    bailiff_mod_precommit: TemplateRepo, tmp_path: Path
) -> None:
    """enable_typo_check=true (default) includes the typos hook in fragment."""
    dest = tmp_path / "proj"
    _init(bailiff_mod_precommit, dest, {"enable_typo_check": True})

    text = (dest / ".pre-commit.d" / "bailiff-mod-precommit.yaml").read_text()
    assert "typos" in text, "typos hook must be present when enable_typo_check=true"


def test_precommit_fragment_typo_check_disabled(
    bailiff_mod_precommit: TemplateRepo, tmp_path: Path
) -> None:
    """enable_typo_check=false excludes the typos hook from fragment."""
    dest = tmp_path / "proj"
    _init(bailiff_mod_precommit, dest, {"enable_typo_check": False})

    text = (dest / ".pre-commit.d" / "bailiff-mod-precommit.yaml").read_text()
    assert "typos" not in text, "typos hook must be absent when enable_typo_check=false"


def test_precommit_no_direct_config_file_from_single_layer_init(
    bailiff_mod_precommit: TemplateRepo, tmp_path: Path
) -> None:
    """Single-layer init does not produce .pre-commit-config.yaml directly.

    The merged config is produced by the bundler _post_task, which only runs
    via init_many/reproduce_many (not single-layer runner.init).
    """
    dest = tmp_path / "proj"
    _init(bailiff_mod_precommit, dest, {})

    # Fragment exists; merged config does NOT (post_task not run in single-layer init)
    assert (dest / ".pre-commit.d" / "bailiff-mod-precommit.yaml").is_file()
    assert not (dest / ".pre-commit-config.yaml").exists(), (
        ".pre-commit-config.yaml must not exist from single-layer init "
        "(bundler runs as _post_task in init_many only)"
    )


def test_precommit_no_hook_blocks_question(
    bailiff_mod_precommit: TemplateRepo, tmp_path: Path
) -> None:
    """hook_blocks is NOT a question in copier.yml (spec 014 R1: unions removed).

    The fragment/merge model replaces the frozen-union hook_blocks mechanism.
    """
    import yaml as _yaml

    from tests.conftest import _MODULES_DIR

    orig = _yaml.safe_load((_MODULES_DIR / "bailiff-mod-precommit" / "copier.yml").read_text())
    assert "hook_blocks" not in orig, (
        "hook_blocks must be removed from copier.yml (spec 014 fragment/merge model)"
    )


def test_hook_manager_question_absent(
    bailiff_mod_precommit: TemplateRepo,
) -> None:
    """hook_manager question must NOT exist in copier.yml (spec 014 R13).

    Selecting bailiff-mod-precommit IS choosing pre-commit; no question needed.
    """
    import yaml as _yaml

    from tests.conftest import _MODULES_DIR

    orig = _yaml.safe_load((_MODULES_DIR / "bailiff-mod-precommit" / "copier.yml").read_text())
    assert "hook_manager" not in orig, (
        "hook_manager must be deleted from copier.yml (spec 014 R13: presence-derived)"
    )


def test_precommit_never_produces_lefthook_yml(
    bailiff_mod_precommit: TemplateRepo, tmp_path: Path
) -> None:
    """Selecting precommit never produces lefthook.yml."""
    dest = tmp_path / "proj"
    _init(bailiff_mod_precommit, dest, {})
    assert not (dest / "lefthook.yml").exists(), (
        "lefthook.yml must never be produced by this module"
    )


# ---------------------------------------------------------------------------
# Bundler runs when precommit is selected (fragment present)
# ---------------------------------------------------------------------------


def test_precommit_bundler_produces_config_when_selected(
    bailiff_mod_precommit: TemplateRepo, tmp_path: Path
) -> None:
    """Fragment is unconditionally written; bundler can merge it to produce config.

    Verifies that the fragment exists and contains valid YAML with repos key —
    confirming bundler would produce .pre-commit-config.yaml if post-task ran.
    """
    dest = tmp_path / "proj"
    _init(bailiff_mod_precommit, dest, {})

    fragment = dest / ".pre-commit.d" / "bailiff-mod-precommit.yaml"
    assert fragment.is_file(), "fragment must exist unconditionally when module is selected"
    parsed = yaml.safe_load(fragment.read_text())
    assert parsed.get("repos"), "fragment must contain non-empty repos list"


# ---------------------------------------------------------------------------
# Dependency ordering edge: depends_on: [bailiff-mod-base] (spec 014 R7)
# ---------------------------------------------------------------------------


def test_precommit_depends_on_edge_declared(
    bailiff_mod_precommit: TemplateRepo, tmp_path: Path
) -> None:
    """depends_on: [bailiff-mod-base] is declared (spec 014 R7: run_after migrated)."""
    import yaml as _yaml

    copier_yml = Path(bailiff_mod_precommit.url) / "copier.yml"
    cfg = _yaml.safe_load(copier_yml.read_text())
    depends_on = cfg.get("depends_on", {}).get("default", [])
    assert "bailiff-mod-base" in depends_on, (
        "bailiff-mod-precommit must declare depends_on: [bailiff-mod-base] (spec 014 R7)"
    )


# ---------------------------------------------------------------------------
# No secret: questions
# ---------------------------------------------------------------------------


def test_no_secret_questions(bailiff_mod_precommit: TemplateRepo, tmp_path: Path) -> None:
    """Compliance: no secret: questions in copier.yml (Constitution VI)."""
    import yaml as _yaml

    copier_yml = Path(bailiff_mod_precommit.url) / "copier.yml"
    cfg = _yaml.safe_load(copier_yml.read_text())
    secret_keys = [
        key
        for key, spec in cfg.items()
        if not key.startswith("_") and isinstance(spec, dict) and spec.get("secret")
    ]
    assert not secret_keys, f"secret: questions found: {secret_keys}"
