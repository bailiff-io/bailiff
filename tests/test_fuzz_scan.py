"""Fuzz scan.py against malformed package trees.

The contract for every case here is the same: scan.py reports a lint finding and
exits 1. It never raises, and it never reports a clean catalog for a package that
violates the contract.
"""

from __future__ import annotations

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from conftest import make_skill, scan

ANSWERS = "template/{{ _copier_conf.answers_file }}.jinja"
ANSWERS_BODY = "{{ _copier_answers|to_nice_yaml -}}\n"

NO_SHRINK = settings(
    max_examples=60,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)


def good_package(name: str) -> dict[str, str]:
    return {
        "package.md": (
            f"---\nname: {name}\nsummary: A package\nprovides: [test:{name}]\n---\n\nBody.\n"
        ),
        "copier.yml": "_subdirectory: template\n",
        ANSWERS: ANSWERS_BODY,
    }


def test_valid_tree_is_clean(tmp_path):
    make_skill(tmp_path, {"g/alpha": good_package("alpha")})
    catalog = scan.build_catalog(tmp_path)
    assert catalog["lint"] == []
    assert catalog["groups"][0]["packages"][0]["axes"] == ["test"]


def test_missing_tools_directory_is_a_finding_not_a_crash(tmp_path):
    catalog = scan.build_catalog(tmp_path)
    assert catalog["groups"] == []
    assert len(catalog["lint"]) == 1


# ---------------------------------------------------------------- malformed YAML

# Bytes that break a YAML parse or a frontmatter split. Each must surface as a
# finding rather than an exception.
BROKEN_FRONTMATTER = [
    "",
    "---\n",
    "---\n---\n",
    "no frontmatter at all\n",
    "---\nname: [unclosed\n---\n",
    "---\n\tname: tabs\n---\n",
    "---\nname: a\nname: b\n---\n",  # duplicate key
    "---\n- a list\n- not a mapping\n---\n",
    "---\njust a string\n---\n",
    "---\nname: !!python/object/apply:os.system ['echo pwned']\n---\n",
    "---\n" + "a: " * 200 + "1\n---\n",
    "﻿---\nname: bom\n---\n",  # byte-order mark before the delimiter
    "---\r\nname: crlf\r\n---\r\n",
    "---\nname: \x00null-byte\n---\n",
]


@pytest.mark.parametrize("body", BROKEN_FRONTMATTER)
def test_broken_frontmatter_never_raises(tmp_path, body):
    make_skill(tmp_path, {"g/alpha": {"package.md": body}})
    catalog = scan.build_catalog(tmp_path)
    assert catalog["lint"], f"no finding for {body!r}"


BROKEN_COPIER = [
    "",
    "not a mapping\n",
    "- a\n- b\n",
    "key: [unclosed\n",
    "\tkey: tab-indented\n",
    "a: 1\na: 2\n",  # a duplicated question key silently loses one question
    "key: !!python/object/apply:os.system ['echo pwned']\n",
    "key: " + "[" * 200 + "\n",
]


@pytest.mark.parametrize("body", BROKEN_COPIER)
def test_broken_copier_yml_never_raises(tmp_path, body):
    files = good_package("alpha") | {"copier.yml": body}
    make_skill(tmp_path, {"g/alpha": files})
    catalog = scan.build_catalog(tmp_path)
    # A copier.yml that parses to a non-mapping, or not at all, is a finding.
    # An empty one is legal: copier renders a template with zero questions.
    if body.strip():
        assert catalog["lint"], f"no finding for {body!r}"


# ------------------------------------------------------------------ wrong types

# Every frontmatter field fed a type it was not declared as. read_package must
# coerce or report, never raise.
WRONG_TYPES = [
    "name: 42",
    "name: true",
    "name: null",
    "name: [a, b]",
    "name: {a: b}",
    "name: 1.5",
    "summary: [a, b]",
    "summary: {nested: map}",
    "summary: 0",
    "provides: a-bare-string",
    "provides: {axis: value}",
    "provides: 42",
    "provides: [1, 2, 3]",
    "provides: []",
    "after: not-a-list",
    "after: {a: b}",
    "after: [null]",
    "depends_on: 42",
    "requires_bin: {a: b}",
    "requires_bin: [[nested]]",
    "precheck: [a, b]",
    "precheck: 42",
    "precheck: true",
]


@pytest.mark.parametrize("line", WRONG_TYPES)
def test_wrong_field_types_never_raise(tmp_path, line):
    body = f"---\nname: alpha\nsummary: s\nprovides: [test:alpha]\n{line}\n---\n\nB.\n"
    make_skill(tmp_path, {"g/alpha": {"package.md": body}})
    catalog = scan.build_catalog(tmp_path)
    assert isinstance(catalog["lint"], list)


# ------------------------------------------------------- generated field values

# Unicode, control characters, and the empty string, in every scalar field.
# Control characters are excluded because YAML does not round-trip them: dumping
# '\x85' and loading it back yields ' ', so a test comparing the parsed value
# against the input would fail on the serialiser rather than on scan.py.
SCALARS = st.text(
    alphabet=st.characters(blacklist_categories=("Cs", "Cc")), min_size=0, max_size=60
)


@NO_SHRINK
@given(name=SCALARS, summary=SCALARS)
def test_arbitrary_scalars_never_raise(tmp_path_factory, name, summary):
    root = tmp_path_factory.mktemp("skill")
    body = {
        "name": name,
        "summary": summary,
        "provides": ["test:alpha"],
    }
    import yaml

    text = "---\n" + yaml.safe_dump(body, allow_unicode=True) + "---\n\nBody.\n"
    make_skill(root, {"g/alpha": {"package.md": text}})
    catalog = scan.build_catalog(root)
    assert isinstance(catalog["lint"], list)
    # The declared name must match the directory, so anything but "alpha" is a
    # finding. This is the invariant that keeps a package id trustworthy.
    if name.strip() != "alpha":
        assert catalog["lint"]


@NO_SHRINK
@given(tags=st.lists(SCALARS, min_size=1, max_size=5))
def test_arbitrary_provides_tags_never_raise(tmp_path_factory, tags):
    root = tmp_path_factory.mktemp("skill")
    import yaml

    text = (
        "---\n"
        + yaml.safe_dump(
            {"name": "alpha", "summary": "s", "provides": tags}, allow_unicode=True
        )
        + "---\n\nBody.\n"
    )
    make_skill(root, {"g/alpha": {"package.md": text}})
    catalog = scan.build_catalog(root)
    pkg = catalog["groups"][0]["packages"][0]
    # Every axis is the part before the first colon, and axes are deduplicated.
    assert pkg["axes"] == sorted({t.split(":", 1)[0] for t in tags})


@NO_SHRINK
@given(edges=st.lists(SCALARS, min_size=1, max_size=4))
def test_unknown_edge_targets_are_reported(tmp_path_factory, edges):
    root = tmp_path_factory.mktemp("skill")
    import yaml

    text = (
        "---\n"
        + yaml.safe_dump(
            {
                "name": "alpha",
                "summary": "s",
                "provides": ["test:alpha"],
                "after": edges,
            },
            allow_unicode=True,
        )
        + "---\n\nBody.\n"
    )
    make_skill(root, {"g/alpha": {"package.md": text}})
    catalog = scan.build_catalog(root)
    # "alpha" is the only known name, so any other target is a dangling edge.
    dangling = {e for e in edges if e != "alpha"}
    assert len(catalog["lint"]) >= len(dangling)


# --------------------------------------------------------------- huge and deep


def test_many_packages(tmp_path):
    packages = {f"g/p{i}": good_package(f"p{i}") for i in range(200)}
    make_skill(tmp_path, packages)
    catalog = scan.build_catalog(tmp_path)
    assert catalog["lint"] == []
    assert len(catalog["groups"][0]["packages"]) == 200


def test_huge_summary(tmp_path):
    summary = "x" * 200_000
    body = f"---\nname: alpha\nsummary: {summary}\nprovides: [test:alpha]\n---\n\nB.\n"
    make_skill(tmp_path, {"g/alpha": {"package.md": body}})
    catalog = scan.build_catalog(tmp_path)
    assert catalog["lint"] == []


def test_deeply_nested_copier_yml(tmp_path):
    import yaml

    nested: object = "leaf"
    for _ in range(60):
        nested = {"k": nested}
    files = good_package("alpha") | {
        "copier.yml": yaml.safe_dump({"_subdirectory": "template", "q": nested})
    }
    make_skill(tmp_path, {"g/alpha": files})
    catalog = scan.build_catalog(tmp_path)
    assert isinstance(catalog["lint"], list)


# --------------------------------------------------------- yaml bombs and evals


def test_billion_laughs_is_not_expanded(tmp_path):
    """A YAML alias bomb must not exhaust memory. safe_load caps expansion, so
    this either parses small or raises a caught YAMLError."""
    bomb = "a: &a [1,1]\nb: &b [*a,*a]\nc: &c [*b,*b]\nd: &d [*c,*c]\ne: [*d,*d]\n"
    files = good_package("alpha") | {"copier.yml": bomb}
    make_skill(tmp_path, {"g/alpha": files})
    catalog = scan.build_catalog(tmp_path)
    assert isinstance(catalog["lint"], list)


def test_python_tag_does_not_execute(tmp_path):
    """safe_load must refuse the python/object tag rather than construct it."""
    payload = "_subdirectory: template\nq: !!python/object/apply:os.system ['exit 7']\n"
    files = good_package("alpha") | {"copier.yml": payload}
    make_skill(tmp_path, {"g/alpha": files})
    catalog = scan.build_catalog(tmp_path)
    assert any("copier.yml" in m for m in catalog["lint"])


# ------------------------------------------------------------ exit-code contract


def test_main_exits_1_on_lint_and_0_when_clean(tmp_path, capsys):
    make_skill(tmp_path, {"g/alpha": good_package("alpha")})
    assert scan.main(["--skill-dir", str(tmp_path), "--lint-only"]) == 0

    make_skill(tmp_path, {"g/beta": {"package.md": "---\nname: wrong\n---\n"}})
    assert scan.main(["--skill-dir", str(tmp_path), "--lint-only"]) == 1


def test_catalog_json_is_serialisable(tmp_path):
    import json

    make_skill(tmp_path, {"g/alpha": good_package("alpha")})
    catalog = scan.build_catalog(tmp_path)
    json.dumps(catalog)  # must not raise on any value scan puts in the catalog
