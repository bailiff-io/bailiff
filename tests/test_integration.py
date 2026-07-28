"""Render real tool packages into temp directories and check what lands.

These run the shipped copier templates and their `_tasks`, so they need the
binaries the packages declare in `requires_bin` plus a network for the package
managers the tasks invoke. Marked `integration`; deselect with `-m "not
integration"`.

Answers here are written as a real agent would write them, so an invalid enum
value fails the test rather than being silently coerced.
"""

from __future__ import annotations

import subprocess
import sys

import pytest
import yaml

from conftest import REPO, PACKAGES, render

pytestmark = pytest.mark.integration

SKILL = PACKAGES.parent


def have(binary: str) -> bool:
    import shutil

    return shutil.which(binary) is not None


def do_render(dest, package_id: str, answers: dict, **kw) -> dict:
    """Render in-process. copier chdir's, so the cwd is restored after."""
    import os

    cwd = os.getcwd()
    try:
        return render.render(SKILL, package_id, dest, answers, quiet=True, **kw)
    finally:
        os.chdir(cwd)


def files_in(dest) -> set[str]:
    return {
        str(p.relative_to(dest))
        for p in dest.rglob("*")
        if p.is_file() and ".git/" not in str(p.relative_to(dest))
    }


BASE = dict(
    project_name="Widget",
    org="acme",
    description="A widget",
    layout="single",
    default_branch="main",
    license="mit",
    copyright_name="Acme",
    branch_strategy="trunk-based",
    docs_subdirs=False,
    extra_dirs=[],
    run_git_init=True,
)

PYTHON_CI = dict(
    python_version="3.13",
    python_pkg_manager="uv",
    python_test_command="pytest",
    python_type_checker="mypy",
    ci_cache=True,
    ci_os_matrix=["ubuntu-latest"],
    ci_version_matrix=[],
)

CI_HOST = dict(
    default_branch="main",
    merge_queue=False,
    job_timeout_minutes=15,
)

PYTHON = dict(
    project_name="Widget",
    description="A widget",
    python_pkg_manager="uv",
    python_version="3.13",
    python_layout="src",
    python_framework="none",
    ruff_line_length=100,
    ruff_quote_style="double",
    ruff_rule_profile="standard",
    add_tests=True,
)


# ------------------------------------------------------------------ foundation


def test_base_renders_identity_and_initialises_git(tmp_path):
    dest = tmp_path / "proj"
    result = do_render(dest, "foundation/base", BASE)

    assert result["answers_file"] == ".copier-answers.base.yml"
    assert files_in(dest) >= {
        ".copier-answers.base.yml",
        ".gitignore",
        "AGENTS.md",
        "LICENSE",
        "docs/.gitkeep",
        "scripts/.gitkeep",
        "tests/.gitkeep",
    }

    # The license task picks the file by the enum value, so a wrong branch here
    # would ship the wrong licence text with no other symptom.
    assert "MIT License" in (dest / "LICENSE").read_text()
    assert "Acme" in (dest / "LICENSE").read_text()

    # run_git_init is true, so the repo exists on the branch that was asked for.
    branch = subprocess.run(
        ["git", "-C", str(dest), "branch", "--show-current"],
        capture_output=True,
        text=True,
    )
    assert branch.stdout.strip() == "main"


def test_base_docs_subdirs_false_renders_no_subdirs(tmp_path):
    """The conditional-filename idiom: a false answer must render no file at
    all, not an empty directory named for the jinja expression."""
    dest = tmp_path / "proj"
    do_render(dest, "foundation/base", BASE)
    rendered = files_in(dest)
    assert not any("architecture" in f or "runbooks" in f for f in rendered)
    assert not any("{%" in f or "{{" in f for f in rendered)


def test_base_docs_subdirs_true_renders_all_three(tmp_path):
    dest = tmp_path / "proj"
    do_render(dest, "foundation/base", BASE | {"docs_subdirs": True})
    assert files_in(dest) >= {
        "docs/architecture/.gitkeep",
        "docs/decisions/.gitkeep",
        "docs/runbooks/.gitkeep",
    }


def test_answers_file_records_every_answer(tmp_path):
    """The answers file is what makes a later `copier update` possible, so every
    question must round-trip into it."""
    dest = tmp_path / "proj"
    do_render(dest, "foundation/base", BASE)
    recorded = yaml.safe_load((dest / ".copier-answers.base.yml").read_text())
    for key, value in BASE.items():
        if key == "run_git_init":
            continue  # a task switch, not project state
        assert recorded[key] == value, key


# -------------------------------------------------------------------- language


@pytest.mark.skipif(not have("mise"), reason="languages/python requires mise")
def test_python_renders_and_uv_init_runs(tmp_path):
    dest = tmp_path / "proj"
    do_render(dest, "foundation/base", BASE)
    do_render(dest, "languages/python", PYTHON)

    assert files_in(dest) >= {
        "ruff.toml",
        "pytest.ini",
        "tests/test_example.py",
        ".mise/conf.d/python.toml",
        ".pre-commit.d/python.yaml",
        ".hooks.d/python.yaml",
        ".gitignore.d/python",
    }
    # The uv init task ran, and named the package after project_name rather than
    # after the temp directory.
    assert (dest / "pyproject.toml").is_file()
    assert 'name = "widget"' in (dest / "pyproject.toml").read_text()
    assert (dest / "src/widget/__init__.py").is_file()

    # The version enum reaches both the mise config and ruff's target.
    assert "3.13" in (dest / ".mise/conf.d/python.toml").read_text()


@pytest.mark.skipif(not have("mise"), reason="languages/python requires mise")
def test_python_answers_are_namespaced_not_shared(tmp_path):
    """Two packages that ask the same question must keep separate answers files,
    or a later update to one would overwrite the other's answers."""
    dest = tmp_path / "proj"
    do_render(dest, "foundation/base", BASE)
    do_render(dest, "languages/python", PYTHON)
    assert (dest / ".copier-answers.base.yml").is_file()
    assert (dest / ".copier-answers.python.yml").is_file()
    base = yaml.safe_load((dest / ".copier-answers.base.yml").read_text())
    python = yaml.safe_load((dest / ".copier-answers.python.yml").read_text())
    assert "python_version" not in base
    assert python["python_version"] == "3.13"


@pytest.mark.skipif(not have("go"), reason="languages/go requires go")
def test_go_renders_and_go_mod_init_runs(tmp_path):
    dest = tmp_path / "proj"
    do_render(dest, "foundation/base", BASE)
    do_render(
        dest,
        "languages/go",
        dict(
            project_name="Widget",
            description="A widget",
            go_version="1.25",
            app_kind="cli",
            test_runner="go-test",
            use_vendor_mode=False,
            golangci_hook_rev="v2.5.0",
        ),
    )
    assert (dest / "go.mod").is_file()
    assert "module widget" in (dest / "go.mod").read_text()
    assert (dest / "cmd/widget/main.go").is_file()
    assert (dest / ".golangci.yml").is_file()


# -------------------------------------------------------------- CI composition


def test_ci_host_and_one_language_compose(tmp_path):
    dest = tmp_path / "proj"
    do_render(dest, "foundation/base", BASE)
    do_render(dest, "ci/github", CI_HOST)
    do_render(
        dest,
        "ci/github-python",
        dict(
            python_version="3.13",
            python_pkg_manager="uv",
            python_test_command="pytest",
            python_type_checker="mypy",
            ci_cache=True,
            ci_os_matrix=["ubuntu-latest"],
            ci_version_matrix=[],
        ),
    )
    rendered = files_in(dest)
    assert rendered >= {
        ".github/actions/ci-gate/action.yml",
        ".github/workflows/wc-gate.yml",
        ".github/actions/setup-python/action.yml",
        ".github/workflows/wc-lint-python.yml",
        ".github/workflows/wc-test-python.yml",
    }
    # No package may render the caller workflow; the agent authors ci.yml.
    assert ".github/workflows/ci.yml" not in rendered


def test_every_reusable_workflow_is_callable_and_takes_working_directory(tmp_path):
    """One render of a language CI package serves every package in a monorepo,
    which only holds if each workflow is callable and accepts the directory."""
    dest = tmp_path / "proj"
    do_render(dest, "ci/github", CI_HOST)
    do_render(
        dest,
        "ci/github-python",
        dict(
            python_version="3.13",
            python_pkg_manager="uv",
            python_test_command="pytest",
            python_type_checker="mypy",
            ci_cache=True,
            ci_os_matrix=["ubuntu-latest"],
            ci_version_matrix=[],
        ),
    )
    for path in sorted((dest / ".github/workflows").glob("wc-*.yml")):
        spec = yaml.safe_load(path.read_text())
        trigger = spec.get("on") or spec.get(True)  # YAML 1.1 reads `on:` as True
        assert "workflow_call" in trigger, path.name
        inputs = trigger["workflow_call"].get("inputs") or {}
        if path.name == "wc-gate.yml":
            # The gate aggregates the other jobs' results and runs no build step
            # of its own, so it takes the caller's needs context instead.
            assert "needs" in inputs
            continue
        if path.name == "wc-changes.yml":
            # Path filtering is repo-wide by definition: it decides which areas
            # changed, so it takes a filter spec rather than one directory.
            assert "filters" in inputs
            continue
        assert "working-directory" in inputs, path.name
        assert inputs["working-directory"]["default"] == "."


def test_every_rendered_job_is_bounded_and_leaks_no_credentials(tmp_path):
    """Two defaults GitHub gets wrong. A job with no timeout-minutes inherits
    360, so a hung job burns six runner hours. A checkout with the default
    persist-credentials leaves GITHUB_TOKEN in .git/config for any later step to
    read, which is what zizmor's artipacked audit reports -- and hooks/baseline
    runs zizmor, so our own templates have to pass it."""
    dest = tmp_path / "proj"
    do_render(dest, "ci/github", CI_HOST)
    do_render(dest, "ci/github-python", PYTHON_CI | {"ci_job_timeout_minutes": 25})

    for path in sorted((dest / ".github/workflows").glob("wc-*.yml")):
        spec = yaml.safe_load(path.read_text())
        for name, job in spec["jobs"].items():
            assert "timeout-minutes" in job, f"{path.name}:{name}"
            for step in job.get("steps", []):
                if str(step.get("uses", "")).startswith("actions/checkout"):
                    assert step["with"]["persist-credentials"] is False, path.name

    # The answer reaches the file rather than falling back to the jinja default.
    test_wf = yaml.safe_load(
        (dest / ".github/workflows/wc-test-python.yml").read_text()
    )
    assert test_wf["jobs"]["test"]["timeout-minutes"] == 25


def test_every_action_reference_is_pinned_to_a_sha(tmp_path):
    """zizmor's unpinned-uses audit rejects a tag on any action under its blanket
    policy, including actions/*. A 40-char SHA is the only form that passes."""
    import re

    dest = tmp_path / "proj"
    do_render(dest, "ci/github", CI_HOST)
    do_render(dest, "ci/github-python", PYTHON_CI)

    unpinned = []
    for path in sorted((dest / ".github").rglob("*.yml")):
        for line in path.read_text().splitlines():
            m = re.search(r"uses:\s*([^\s]+)", line)
            if not m:
                continue
            ref = m.group(1)
            if ref.startswith("./"):
                continue  # a local composite action has nothing to pin
            if not re.search(r"@[0-9a-f]{40}$", ref):
                unpinned.append(f"{path.name}: {ref}")
    assert not unpinned, unpinned


def test_security_workflows_follow_the_selection(tmp_path):
    dest = tmp_path / "proj"
    do_render(dest, "ci/github", CI_HOST)
    do_render(
        dest,
        "ci/github-security",
        dict(
            sec_codeql=True,
            sec_codeql_languages=["python"],
            sec_trivy=False,
            sec_gitleaks=False,
        ),
    )
    rendered = files_in(dest)
    assert ".github/workflows/wc-security-codeql.yml" in rendered
    assert not any("trivy" in f for f in rendered)
    assert not any("gitleaks" in f for f in rendered)

    codeql = (dest / ".github/workflows/wc-security-codeql.yml").read_text()
    assert "language: [python]" in codeql
    # GitHub rejects an empty matrix, so the fallback must never render one.
    assert "language: []" not in codeql


def test_deselecting_every_codeql_language_still_renders_a_matrix(tmp_path):
    dest = tmp_path / "proj"
    do_render(dest, "ci/github", CI_HOST)
    do_render(
        dest,
        "ci/github-security",
        dict(
            sec_codeql=True,
            sec_codeql_languages=[],
            sec_trivy=False,
            sec_gitleaks=False,
        ),
    )
    codeql = (dest / ".github/workflows/wc-security-codeql.yml").read_text()
    assert "language: [actions]" in codeql


def test_deselecting_every_runner_still_renders_a_runs_on(tmp_path):
    """ci_os_matrix is the full runner list, so an empty selection is reachable
    and must fall back rather than index an empty list."""
    dest = tmp_path / "proj"
    do_render(dest, "ci/github", CI_HOST)
    do_render(
        dest,
        "ci/github-python",
        dict(
            python_version="3.13",
            python_pkg_manager="uv",
            python_test_command="pytest",
            python_type_checker="mypy",
            ci_cache=True,
            ci_os_matrix=[],
            ci_version_matrix=[],
        ),
    )
    body = (dest / ".github/workflows/wc-test-python.yml").read_text()
    assert "runs-on: ubuntu-latest" in body
    spec = yaml.safe_load(body)
    assert "matrix" not in yaml.safe_dump(spec.get("jobs", {}))


def test_full_matrix_renders_valid_yaml(tmp_path):
    dest = tmp_path / "proj"
    do_render(dest, "ci/github", CI_HOST)
    do_render(
        dest,
        "ci/github-python",
        dict(
            python_version="3.13",
            python_pkg_manager="uv",
            python_test_command="pytest",
            python_type_checker="mypy",
            ci_cache=True,
            ci_os_matrix=["ubuntu-latest", "macos-latest", "windows-latest"],
            ci_version_matrix=["3.12", "3.13"],
        ),
    )
    spec = yaml.safe_load((dest / ".github/workflows/wc-test-python.yml").read_text())
    matrix = spec["jobs"]["test"]["strategy"]["matrix"]
    assert matrix["os"] == ["ubuntu-latest", "macos-latest", "windows-latest"]
    # copier's multiselect returns the values in the order `choices:` declares
    # them, not the order the caller listed, so the assertion follows choices.
    assert matrix["python-version"] == ["3.13", "3.12"]
    # A matrixed version must reach the setup action, not the scalar input.
    step = next(
        s for s in spec["jobs"]["test"]["steps"] if "setup-python" in str(s.get("uses"))
    )
    assert step["with"]["python-version"] == "${{ matrix.python-version }}"


@pytest.mark.skipif(
    not have("actionlint"), reason="workflow linting requires actionlint"
)
def test_rendered_workflows_pass_actionlint(tmp_path):
    dest = tmp_path / "proj"
    do_render(dest, "ci/github", CI_HOST)
    do_render(
        dest,
        "ci/github-python",
        dict(
            python_version="3.13",
            python_pkg_manager="uv",
            python_test_command="pytest",
            python_type_checker="mypy",
            ci_cache=True,
            ci_os_matrix=["ubuntu-latest", "macos-latest"],
            ci_version_matrix=["3.13"],
        ),
    )
    do_render(
        dest,
        "ci/github-security",
        dict(
            sec_codeql=True,
            sec_codeql_languages=["python", "actions"],
            sec_trivy=True,
            sec_gitleaks=True,
        ),
    )
    subprocess.run(["git", "-C", str(dest), "init", "--quiet"], check=True)
    proc = subprocess.run(
        ["actionlint", "-no-color", "-oneline"],
        cwd=str(dest),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


# ------------------------------------------------------------- exclusive axes


def test_hooks_group_splits_checks_from_the_manager(tmp_path):
    """The checks and the manager are separate decisions, so they are separate
    packages. The manager choice itself is a copier answer rather than a package
    per manager, because each writes .git/hooks/ and whichever installs last
    wins: an enum makes that exclusive at render time."""
    from conftest import scan

    catalog = scan.build_catalog(SKILL)
    hooks = next(g for g in catalog["groups"] if g["name"] == "hooks")
    assert hooks["axes"] == {"hooks": ["baseline", "manager"]}

    manager = next(p for p in hooks["packages"] if p["name"] == "manager")
    choice = next(q for q in manager["questions"] if q["key"] == "hook_manager")
    assert choice["choices"] == ["prek", "lefthook", "pre-commit"]
    assert choice["default"] == "prek"


def test_repo_host_axis_has_two_members(tmp_path):
    from conftest import scan

    catalog = scan.build_catalog(SKILL)
    repo = next(g for g in catalog["groups"] if g["name"] == "repo")
    assert repo["axes"]["repo"] == ["github-repo", "gitlab-repo"]


def test_monorepo_packages_live_in_the_repo_group(tmp_path):
    """moon and package-add are monorepo structure, so they sit with the other
    repo-shape packages rather than with the local-ergonomics ones. Their axis
    namespace is 'monorepo', not 'repo', because scan.py keys an axis on the
    namespace alone and 'repo' already names the forge-host axis."""
    from conftest import scan

    catalog = scan.build_catalog(SKILL)
    repo = next(g for g in catalog["groups"] if g["name"] == "repo")
    assert repo["axes"]["monorepo"] == ["moon", "package-add"]

    workspace = next(g for g in catalog["groups"] if g["name"] == "workspace")
    assert "moon" not in [p["name"] for p in workspace["packages"]]


# -------------------------------------------------------------- fragment dirs


BASELINE = dict(
    check_secrets=False,
    check_secrets_verified=False,
    check_typos=False,
    check_shell=False,
    check_hygiene=True,
    max_file_kb=500,
    check_workflows=False,
    check_toml=False,
    check_links=False,
    check_complexity=False,
    show_repo_stats=False,
    enforce_conventional_commits=True,
    hook_exclude_patterns=[],
)


@pytest.mark.skipif(not have("mise"), reason="languages/python requires mise")
@pytest.mark.parametrize("manager", ["prek", "pre-commit"])
def test_the_fragment_directory_is_merged_for_either_config_reader(
    tmp_path, manager
):
    """prek and pre-commit read the same single config file and neither has an
    include directive, so both need the merge. A language fragment must reach
    the merged config whichever of the two the user picked."""
    dest = tmp_path / "proj"
    do_render(dest, "foundation/base", BASE)
    do_render(dest, "languages/python", PYTHON)
    do_render(dest, "hooks/baseline", BASELINE)
    do_render(
        dest, "hooks/manager", dict(hook_manager=manager, install_hooks=False)
    )
    config = dest / ".pre-commit-config.yaml"
    assert config.is_file(), "the merge task did not produce a config"
    merged = yaml.safe_load(config.read_text())
    repos = yaml.safe_dump(merged["repos"])
    assert "ruff" in repos, "the python fragment did not reach the merged config"
    # lefthook.yml belongs to the other answer and must not appear.
    assert not (dest / "lefthook.yml").exists()


@pytest.mark.skipif(not have("mise"), reason="languages/python requires mise")
def test_lefthook_gets_its_entry_point_and_no_merged_config(tmp_path):
    """lefthook expands .hooks.d/*.yaml itself, so it needs the extends glob and
    no merged file. Rendering the merged config for it would leave a derived
    file nothing reads."""
    dest = tmp_path / "proj"
    do_render(dest, "foundation/base", BASE)
    do_render(dest, "languages/python", PYTHON)
    do_render(dest, "hooks/baseline", BASELINE)
    do_render(
        dest, "hooks/manager", dict(hook_manager="lefthook", install_hooks=False)
    )
    assert (dest / "lefthook.yml").is_file()
    assert not (dest / ".pre-commit-config.yaml").exists()


@pytest.mark.skipif(not have("mise"), reason="languages/python requires mise")
def test_baseline_writes_the_same_checks_into_both_schemas(tmp_path):
    """The parity guarantee: picking a different manager must not weaken the
    checks. Both fragments come from one answer set, so a check enabled once
    appears in each schema."""
    dest = tmp_path / "proj"
    do_render(dest, "foundation/base", BASE)
    answers = dict(BASELINE, check_secrets=True, secret_scanner="betterleaks")
    do_render(dest, "hooks/baseline", answers)

    lefthook = yaml.safe_load((dest / ".hooks.d" / "baseline.yaml").read_text())
    precommit = yaml.safe_load(
        (dest / ".pre-commit.d" / "baseline.yaml").read_text()
    )

    assert "betterleaks" in lefthook["pre-commit"]["commands"]
    assert "betterleaks" in yaml.safe_dump(precommit["repos"])
    # The commit-msg hook is in both, and the script both call is rendered once.
    assert "commit-msg" in lefthook
    assert "conventional-commit-msg" in yaml.safe_dump(precommit["repos"])
    assert (dest / ".hooks-bin" / "check-commit-msg.py").is_file()


@pytest.mark.skipif(not have("mise"), reason="languages/python requires mise")
def test_gitignore_fragments_are_folded_into_gitignore(tmp_path):
    """git has no include directive, so a fragment is inert until it is folded
    into .gitignore. Every line the fragment contributes must end up there."""
    dest = tmp_path / "proj"
    do_render(dest, "foundation/base", BASE)
    do_render(dest, "languages/python", PYTHON)
    assert (dest / ".gitignore.d/python").is_file()
    ignored = (dest / ".gitignore").read_text()
    fragment = (dest / ".gitignore.d/python").read_text()
    missing = [
        line
        for line in fragment.splitlines()
        if line.strip() and not line.startswith("#") and line not in ignored
    ]
    assert not missing, f".gitignore.d/python not folded into .gitignore: {missing}"


@pytest.mark.skipif(
    not (have("mise") and have("go")), reason="needs mise and go"
)
def test_two_packages_fold_without_clobbering_each_other(tmp_path):
    """The fold runs once per contributing package, so it has to be additive.
    Whichever renders second must not drop the first one's block."""
    dest = tmp_path / "proj"
    do_render(dest, "foundation/base", BASE)
    do_render(dest, "languages/python", PYTHON)
    do_render(
        dest,
        "languages/go",
        dict(
            project_name="Widget",
            description="A widget",
            go_version="1.25",
            app_kind="cli",
            test_runner="go-test",
            use_vendor_mode=False,
            golangci_hook_rev="v2.5.0",
        ),
    )
    ignored = (dest / ".gitignore").read_text()
    for name in ("python", "go"):
        assert f"# >>> bailiff:{name}" in ignored
        assert f"# <<< bailiff:{name}" in ignored
    # base's own gitnr-seeded content survives both folds.
    assert ".DS_Store" in ignored or "Thumbs.db" in ignored


@pytest.mark.skipif(not have("mise"), reason="languages/python requires mise")
def test_folding_twice_converges(tmp_path):
    """A re-render must rewrite the block in place, not append a second copy."""
    dest = tmp_path / "proj"
    do_render(dest, "foundation/base", BASE)
    do_render(dest, "languages/python", PYTHON)
    once = (dest / ".gitignore").read_text()
    do_render(dest, "languages/python", PYTHON)
    assert (dest / ".gitignore").read_text() == once
    assert once.count("# >>> bailiff:python") == 1


LEFTHOOK_STAGES = {"pre-commit", "pre-push", "commit-msg", "prepare-commit-msg", "post-merge"}

HOOK_FRAGMENT_CASES = [
    (
        "languages/python",
        dict(
            project_name="W",
            description="d",
            python_pkg_manager="uv",
            python_version="3.13",
            python_layout="src",
            python_framework="none",
            ruff_line_length=100,
            ruff_quote_style="double",
            ruff_rule_profile="standard",
            add_tests=True,
        ),
    ),
    (
        "languages/ts",
        dict(
            project_name="W",
            description="d",
            js_pkg_manager="bun",
            ts_linter="biome",
            test_runner="none",
            node_version="24",
            ts_framework="plain",
            ui_kit="none",
        ),
    ),
    (
        "languages/go",
        dict(
            project_name="W",
            description="d",
            go_version="1.25",
            app_kind="cli",
            test_runner="go-test",
            use_vendor_mode=False,
            golangci_hook_rev="v2.5.0",
        ),
    ),
    (
        "languages/rust",
        dict(
            project_name="W",
            description="d",
            rust_channel="stable",
            rust_edition="2024",
            crate_kind="bin",
            test_runner="cargo-test",
            rustfmt_heuristics="Max",
            clippy_stage="pre-push",
        ),
    ),
]


@pytest.mark.parametrize("package_id,answers", HOOK_FRAGMENT_CASES, ids=lambda v: v if isinstance(v, str) else "")
def test_hooks_fragment_is_in_lefthook_schema(tmp_path, package_id, answers):
    """A `.hooks.d/` fragment is lefthook config, keyed by stage name.

    A pre-commit-shaped fragment is valid YAML, so nothing rejects it at render
    time; lefthook reports `hooks: Value is array but should be object` and then
    silently runs nothing. That is the failure this pins.
    """
    binary = {"languages/go": "go", "languages/rust": "cargo"}.get(package_id, "mise")
    if not have(binary):
        pytest.skip(f"{package_id} requires {binary}")

    dest = tmp_path / "proj"
    dest.mkdir()
    subprocess.run(["git", "-C", str(dest), "init", "--quiet"], check=True)
    do_render(dest, package_id, answers)

    fragments = sorted((dest / ".hooks.d").glob("*.yaml"))
    assert fragments, f"{package_id} ships no .hooks.d fragment"
    for fragment in fragments:
        spec = yaml.safe_load(fragment.read_text())
        assert "hooks" not in spec, f"{fragment.name} uses the pre-commit schema"
        assert set(spec) <= LEFTHOOK_STAGES, f"{fragment.name} keys: {sorted(spec)}"
        for stage, body in spec.items():
            assert "commands" in body, f"{fragment.name}:{stage} has no commands"


@pytest.mark.parametrize("package_id,answers", HOOK_FRAGMENT_CASES, ids=lambda v: v if isinstance(v, str) else "")
@pytest.mark.skipif(not have("lefthook"), reason="needs lefthook")
def test_lefthook_validates_and_merges_each_fragment(tmp_path, package_id, answers):
    """The end-to-end check: lefthook itself accepts the merged config and the
    fragment's commands appear in what it will run."""
    binary = {"languages/go": "go", "languages/rust": "cargo"}.get(package_id, "mise")
    if not have(binary):
        pytest.skip(f"{package_id} requires {binary}")

    dest = tmp_path / "proj"
    dest.mkdir()
    subprocess.run(["git", "-C", str(dest), "init", "--quiet"], check=True)
    do_render(dest, package_id, answers)
    do_render(
        dest, "hooks/manager", dict(hook_manager="lefthook", install_hooks=False)
    )

    validate = subprocess.run(
        ["lefthook", "validate"], cwd=str(dest), capture_output=True, text=True
    )
    assert validate.returncode == 0, validate.stdout + validate.stderr
    assert "All good" in validate.stdout

    dump = subprocess.run(
        ["lefthook", "dump"], cwd=str(dest), capture_output=True, text=True
    )
    merged = yaml.safe_load(dump.stdout)
    assert any(
        stage in merged and merged[stage].get("commands")
        for stage in LEFTHOOK_STAGES
    ), f"lefthook merged no commands: {dump.stdout}"


@pytest.mark.skipif(not have("cargo") or not have("lefthook"), reason="needs cargo and lefthook")
def test_clippy_stage_answer_selects_the_lefthook_stage(tmp_path):
    """clippy_stage is an enum, and the answer has to reach the stage key rather
    than just a comment."""
    rust = dict(
        project_name="W",
        description="d",
        rust_channel="stable",
        rust_edition="2024",
        crate_kind="bin",
        test_runner="cargo-test",
        rustfmt_heuristics="Max",
    )
    for stage in ("pre-push", "pre-commit"):
        dest = tmp_path / stage
        dest.mkdir()
        subprocess.run(["git", "-C", str(dest), "init", "--quiet"], check=True)
        do_render(dest, "languages/rust", rust | {"clippy_stage": stage})
        spec = yaml.safe_load((dest / ".hooks.d/rust.yaml").read_text())
        assert "clippy" in spec[stage]["commands"], f"clippy not at {stage}: {spec}"
        # cargo fmt always runs at pre-commit, whichever stage clippy takes.
        assert "cargo-fmt" in spec["pre-commit"]["commands"]


# ------------------------------------------------------------------ idempotence


def test_re_rendering_a_package_is_idempotent(tmp_path):
    """The agent may re-run a package after a failed sibling, so a second render
    must converge rather than duplicate."""
    dest = tmp_path / "proj"
    do_render(dest, "foundation/base", BASE)
    first = files_in(dest)
    licence = (dest / "LICENSE").read_text()

    do_render(dest, "foundation/base", BASE)
    assert files_in(dest) == first
    assert (dest / "LICENSE").read_text() == licence


@pytest.mark.skipif(not have("mise"), reason="languages/python requires mise")
def test_language_render_does_not_clobber_base(tmp_path):
    dest = tmp_path / "proj"
    do_render(dest, "foundation/base", BASE)
    agents = (dest / "AGENTS.md").read_text()
    do_render(dest, "languages/python", PYTHON)
    assert (dest / "AGENTS.md").read_text() == agents
    assert (dest / "LICENSE").is_file()


# --------------------------------------------------------------- the contract


def test_precheck_failure_leaves_no_partial_render(tmp_path):
    """A failing precheck must render nothing, so the agent can retry after
    fixing the cause without cleaning up first.

    cdk's precheck rejects an unknown cdk_language, which is the one failure
    branch reachable on a machine that has every CDK runtime installed."""
    dest = tmp_path / "proj"
    with pytest.raises(render.RenderError) as caught:
        do_render(
            dest,
            "iac/cdk",
            dict(project_name="W", cdk_language="fortran", placement_dir="infra"),
        )
    assert caught.value.code == render.EXIT_PRECHECK
    assert not (dest / "infra").exists()
    assert not (dest / ".copier-answers.cdk.yml").exists()


def test_missing_required_binary_stops_before_rendering(tmp_path, monkeypatch):
    """requires_bin is checked before anything is written. Simulated by emptying
    PATH, because every binary the shipped packages require is installed here."""
    monkeypatch.setenv("PATH", str(tmp_path / "empty"))
    dest = tmp_path / "proj"
    with pytest.raises(render.RenderError) as caught:
        do_render(dest, "languages/rust", dict(project_name="W", description="d"))
    assert caught.value.code == render.EXIT_PRECHECK
    assert "cargo" in str(caught.value)
    assert not (dest / "Cargo.toml").exists()


@pytest.mark.skipif(not have("mise") or not have("bun"), reason="needs mise and bun")
def test_vite_template_rejects_a_name_create_vite_does_not_have(tmp_path):
    """create-vite 9 scaffolds vanilla for an unknown --template instead of
    failing, so the enum is the only thing standing between a typo and the wrong
    project. The valid answer has to still render, or the enum is just a wall."""
    ts = dict(
        project_name="W",
        description="d",
        js_pkg_manager="bun",
        ts_linter="biome",
        test_runner="none",
        node_version="24",
        ts_framework="vite",
        ui_kit="none",
    )

    with pytest.raises(render.RenderError) as caught:
        do_render(tmp_path / "bad", "languages/ts", ts | {"vite_template": "reactts"})
    assert caught.value.code == render.EXIT_RENDER

    do_render(tmp_path / "ok", "languages/ts", ts | {"vite_template": "react-ts"})
    answers = yaml.safe_load((tmp_path / "ok" / ".copier-answers.ts.yml").read_text())
    assert answers["vite_template"] == "react-ts"


def test_pretend_touches_nothing(tmp_path):
    dest = tmp_path / "proj"
    do_render(dest, "foundation/base", BASE, pretend=True)
    assert files_in(dest) == set()


def test_catalog_lints_clean(tmp_path):
    """The lint gate is the contract every package is held to; it has to pass on
    the shipped tree, not just on the fixtures."""
    proc = subprocess.run(
        [sys.executable, str(SKILL / "scripts/scan.py"), "--lint-only",
         "--skill-dir", str(SKILL)],
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )
    assert proc.returncode == 0, proc.stderr
