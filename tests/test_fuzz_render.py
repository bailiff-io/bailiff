"""Fuzz render.py against hostile package ids, answers files, and destinations.

The invariants: a bad input produces a RenderError with a documented exit code,
never a traceback; and no input reaches a directory outside the packages tree.
"""

from __future__ import annotations

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from conftest import make_skill, render

ANSWERS_TPL = "template/{{ _copier_conf.answers_file }}.jinja"
ANSWERS_BODY = "{{ _copier_answers|to_nice_yaml -}}\n"

NO_SHRINK = settings(
    max_examples=60,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)


def good_package(name: str = "alpha") -> dict[str, str]:
    return {
        "package.md": (
            f"---\nname: {name}\nsummary: A package\nprovides: [test:{name}]\n---\n\nBody.\n"
        ),
        "copier.yml": "_subdirectory: template\n",
        ANSWERS_TPL: ANSWERS_BODY,
        "template/hello.txt": "hello\n",
    }


@pytest.fixture
def skill(tmp_path):
    root = tmp_path / "skill"
    make_skill(root, {"g/alpha": good_package()})
    return root


# --------------------------------------------------------- path traversal

# Every one of these must be rejected. A package id is a positional argument the
# agent builds from the catalog, but the catalog is a file on disk and the id
# reaches the filesystem as a path, so it is untrusted input.
TRAVERSAL = [
    "../../../../etc",
    "g/../../..",
    "g/alpha/../../../..",
    "/etc/passwd",
    "//etc/passwd",
    "g/alpha/..%2f..",
    "....//....//etc",
    "g/./alpha/./..",
    "~/",
    "~root/",
    "g\\alpha",
    "g/alpha\x00.txt",
    "",
    ".",
    "..",
    "./",
    "g//alpha",
    " g/alpha",
    "g/alpha ",
    "G/ALPHA",
]


@pytest.mark.parametrize("package_id", TRAVERSAL)
def test_traversal_package_ids_are_rejected(skill, tmp_path, package_id):
    dest = tmp_path / "dest"
    with pytest.raises(render.RenderError) as caught:
        render.render(skill, package_id, dest, {})
    assert caught.value.code == render.EXIT_USAGE


def test_absolute_path_outside_tools_is_rejected(skill, tmp_path):
    """An absolute id must not escape, even when it names a real directory that
    happens to hold a valid package."""
    outside = tmp_path / "outside"
    make_skill(outside, {"g/alpha": good_package()})
    with pytest.raises(render.RenderError) as caught:
        render.render(skill, str(outside / "packages/g/alpha"), tmp_path / "d", {})
    assert caught.value.code == render.EXIT_USAGE


def test_symlink_out_of_tools_is_rejected(skill, tmp_path):
    """A symlink inside packages/ pointing out of it must not be followed."""
    outside = tmp_path / "outside"
    make_skill(outside, {"g/evil": good_package("evil")})
    link = skill / "packages/g/link"
    link.symlink_to(outside / "packages/g/evil")
    with pytest.raises(render.RenderError) as caught:
        render.render(skill, "g/link", tmp_path / "d", {})
    assert caught.value.code == render.EXIT_USAGE


@NO_SHRINK
@given(
    package_id=st.text(
        alphabet=st.characters(blacklist_categories=("Cs",)), min_size=0, max_size=40
    )
)
def test_arbitrary_package_ids_never_traceback(tmp_path_factory, package_id):
    root = tmp_path_factory.mktemp("skill")
    make_skill(root, {"g/alpha": good_package()})
    dest = tmp_path_factory.mktemp("dest")
    try:
        render.render(root, package_id, dest, {})
    except render.RenderError as exc:
        assert exc.code in (render.EXIT_USAGE, render.EXIT_PRECHECK, render.EXIT_RENDER)
    else:
        # The only id that may succeed is the real one.
        assert package_id == "g/alpha"


# ------------------------------------------------------------- answers files

MALFORMED_ANSWERS = [
    ("- a\n- b\n", render.EXIT_USAGE),
    ("just a string\n", render.EXIT_USAGE),
    ("42\n", render.EXIT_USAGE),
    ("key: [unclosed\n", render.EXIT_USAGE),
    ("\tkey: tab\n", render.EXIT_USAGE),
    ("!!python/object/apply:os.system ['exit 7']\n", render.EXIT_USAGE),
    ("a: &a [1,1]\nb: &b [*a,*a]\nc: [*b,*b]\n", None),
    ("", None),
    ("   \n", None),
    ("{}\n", None),
    ("null\n", None),
]


@pytest.mark.parametrize("body,expected", MALFORMED_ANSWERS)
def test_malformed_answers_files(tmp_path, body, expected):
    path = tmp_path / "answers.yml"
    path.write_text(body, encoding="utf-8")
    if expected is None:
        assert isinstance(render.load_answers(path), dict)
    else:
        with pytest.raises(render.RenderError) as caught:
            render.load_answers(path)
        assert caught.value.code == expected


def test_answers_file_that_does_not_exist(tmp_path):
    with pytest.raises((render.RenderError, OSError)):
        render.load_answers(tmp_path / "nope.yml")


def test_answers_file_is_a_directory(tmp_path):
    with pytest.raises((render.RenderError, OSError)):
        render.load_answers(tmp_path)


@NO_SHRINK
@given(
    answers=st.dictionaries(
        st.text(
            alphabet=st.characters(blacklist_categories=("Cs", "Cc")),
            min_size=1,
            max_size=20,
        ),
        st.one_of(
            st.text(max_size=30),
            st.integers(),
            st.booleans(),
            st.none(),
            st.lists(st.text(max_size=10), max_size=3),
        ),
        max_size=6,
    )
)
def test_arbitrary_answers_render_or_error_cleanly(tmp_path_factory, answers):
    """Answers a user could plausibly hand-write must not crash the renderer.

    A zero-question template ignores unknown keys, so the render succeeds; the
    point is that no key or value shape produces a traceback."""
    root = tmp_path_factory.mktemp("skill")
    make_skill(root, {"g/alpha": good_package()})
    dest = tmp_path_factory.mktemp("dest")
    try:
        result = render.render(root, "g/alpha", dest, answers, quiet=True)
    except render.RenderError as exc:
        assert exc.code in (render.EXIT_USAGE, render.EXIT_PRECHECK, render.EXIT_RENDER)
    else:
        assert result["answers_file"] == ".copier-answers.alpha.yml"


# ------------------------------------------------------------------- metadata


def test_missing_package_md_is_usage_error(skill, tmp_path):
    (skill / "packages/g/bare").mkdir(parents=True)
    with pytest.raises(render.RenderError) as caught:
        render.render(skill, "g/bare", tmp_path / "d", {})
    assert caught.value.code == render.EXIT_USAGE


def test_requires_bin_missing_stops_before_rendering(skill, tmp_path):
    pkg = skill / "packages/g/alpha/package.md"
    pkg.write_text(
        "---\nname: alpha\nsummary: s\nprovides: [test:alpha]\n"
        "requires_bin: [definitely-not-a-real-binary-xyz]\n---\n\nB.\n",
        encoding="utf-8",
    )
    dest = tmp_path / "dest"
    with pytest.raises(render.RenderError) as caught:
        render.render(skill, "g/alpha", dest, {})
    assert caught.value.code == render.EXIT_PRECHECK
    # Nothing may be written when a required binary is absent.
    assert not dest.exists() or not list(dest.iterdir())


def test_precheck_nonzero_renders_nothing(skill, tmp_path):
    (skill / "packages/g/alpha/precheck.py").write_text(
        "import sys\nsys.exit(9)\n", encoding="utf-8"
    )
    (skill / "packages/g/alpha/package.md").write_text(
        "---\nname: alpha\nsummary: s\nprovides: [test:alpha]\n"
        "precheck: precheck.py\n---\n\nB.\n",
        encoding="utf-8",
    )
    dest = tmp_path / "dest"
    with pytest.raises(render.RenderError) as caught:
        render.render(skill, "g/alpha", dest, {})
    assert caught.value.code == render.EXIT_PRECHECK
    assert not (dest / "hello.txt").exists()


def test_precheck_that_does_not_exist_is_usage_error(skill, tmp_path):
    (skill / "packages/g/alpha/package.md").write_text(
        "---\nname: alpha\nsummary: s\nprovides: [test:alpha]\n"
        "precheck: nope.py\n---\n\nB.\n",
        encoding="utf-8",
    )
    with pytest.raises(render.RenderError) as caught:
        render.render(skill, "g/alpha", tmp_path / "d", {})
    assert caught.value.code == render.EXIT_USAGE


def test_precheck_receives_only_scalar_answers(skill, tmp_path):
    """Env vars are strings, so a dict or list answer has no faithful encoding.
    render.py drops them; this pins that so a precheck cannot read a stale one."""
    (skill / "packages/g/alpha/precheck.py").write_text(
        "import os, sys\n"
        "assert os.environ['BAILIFF_FLAT'] == 'x', os.environ.get('BAILIFF_FLAT')\n"
        "assert 'BAILIFF_NESTED' not in os.environ\n"
        "assert os.environ['BAILIFF_DEST']\n",
        encoding="utf-8",
    )
    (skill / "packages/g/alpha/package.md").write_text(
        "---\nname: alpha\nsummary: s\nprovides: [test:alpha]\n"
        "precheck: precheck.py\n---\n\nB.\n",
        encoding="utf-8",
    )
    render.render(
        skill,
        "g/alpha",
        tmp_path / "dest",
        {"flat": "x", "nested": {"a": 1}},
        quiet=True,
    )


def test_steering_only_package_renders_nothing(skill, tmp_path):
    (skill / "packages/g/alpha/copier.yml").unlink()
    result = render.render(skill, "g/alpha", tmp_path / "dest", {}, quiet=True)
    assert result["renders"] is False


# --------------------------------------------------------------- destinations


def test_dest_is_an_existing_file(skill, tmp_path):
    dest = tmp_path / "afile"
    dest.write_text("content\n", encoding="utf-8")
    with pytest.raises((render.RenderError, OSError)):
        render.render(skill, "g/alpha", dest, {}, quiet=True)


def test_pretend_writes_nothing(skill, tmp_path):
    dest = tmp_path / "dest"
    render.render(skill, "g/alpha", dest, {}, pretend=True, quiet=True)
    assert not (dest / "hello.txt").exists()


def test_render_is_idempotent(skill, tmp_path):
    dest = tmp_path / "dest"
    for _ in range(3):
        render.render(skill, "g/alpha", dest, {}, quiet=True)
    assert (dest / "hello.txt").read_text() == "hello\n"


# ---------------------------------------------------------- exit-code contract


def test_main_returns_documented_codes(skill, tmp_path, capsys):
    assert (
        render.main(
            ["g/alpha", str(tmp_path / "d1"), "--skill-dir", str(skill), "--quiet"]
        )
        == render.EXIT_OK
    )
    assert (
        render.main(
            ["g/nope", str(tmp_path / "d2"), "--skill-dir", str(skill), "--quiet"]
        )
        == render.EXIT_USAGE
    )
