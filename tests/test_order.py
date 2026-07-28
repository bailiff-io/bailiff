"""The render order is derived from `after:`, so these pin the derivation.

The runbooks used to carry the order as a hand-maintained list. That list is now
scan.py's output, which means a wrong sort is a wrong render rather than a
documentation defect, and it needs the same coverage as render.py.
"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from conftest import PACKAGES, make_skill, scan

SKILL = PACKAGES.parent


def catalog_of(names: dict[str, list[str]]) -> dict:
    """Build a throwaway catalog where each name maps to its `after:` list."""
    packages = {
        f"g/{name}": {
            "package.md": (
                f"---\nname: {name}\nsummary: s\nprovides: [x:{name}]\n"
                f"after: {json.dumps(after)}\n---\n"
            )
        }
        for name, after in names.items()
    }
    return packages


@pytest.fixture
def tiny(tmp_path):
    def build(names: dict[str, list[str]]):
        root = tmp_path / "skill"
        make_skill(root, catalog_of(names))
        return scan.build_catalog(root)

    return build


def ids(result: list[str]) -> list[str]:
    return [i.split("/", 1)[1] for i in result]


# ------------------------------------------------------------------- ordering


def test_after_decides_the_order(tiny):
    catalog = tiny({"a": [], "b": ["a"], "c": ["b"]})
    ordered, notes = scan.order(catalog, ["c", "a", "b"])
    assert ids(ordered) == ["a", "b", "c"]
    assert notes == []


def test_order_is_independent_of_the_input_order(tiny):
    catalog = tiny({"a": [], "b": ["a"], "c": ["b"]})
    first, _ = scan.order(catalog, ["c", "b", "a"])
    second, _ = scan.order(catalog, ["a", "b", "c"])
    assert first == second


def test_an_after_edge_to_an_unselected_package_is_dropped(tiny):
    """`after:` is soft: it orders what is selected and never pulls in more.
    Rendering an unrequested package would write files the user never asked
    for."""
    catalog = tiny({"a": [], "b": ["a"]})
    ordered, notes = scan.order(catalog, ["b"])
    assert ids(ordered) == ["b"]
    assert notes == []


def test_depends_on_unselected_is_reported_but_still_orders(tmp_path):
    """A hard requirement the user did not pick is the agent's call to make, so
    it is a note rather than a refusal."""
    packages = catalog_of({"a": [], "b": ["a"]})
    packages["g/b"]["package.md"] = (
        '---\nname: b\nsummary: s\nprovides: [x:b]\nafter: ["a"]\n'
        'depends_on: ["a"]\n---\n'
    )
    root = tmp_path / "skill"
    make_skill(root, packages)
    ordered, notes = scan.order(scan.build_catalog(root), ["b"])
    assert ids(ordered) == ["b"]
    assert any("depends_on" in n for n in notes)


def test_ties_break_deterministically(tiny):
    """Two packages with no edge between them must still come out in a fixed
    order, or two runs of the same interview render in different sequences."""
    catalog = tiny({"a": [], "b": [], "c": []})
    for _ in range(5):
        ordered, _ = scan.order(catalog, ["c", "a", "b"])
        assert ids(ordered) == ["a", "b", "c"]


def test_duplicate_selection_renders_once(tiny):
    catalog = tiny({"a": [], "b": ["a"]})
    ordered, _ = scan.order(catalog, ["a", "b", "a"])
    assert ids(ordered) == ["a", "b"]


def test_unknown_package_is_a_note_not_a_crash(tiny):
    catalog = tiny({"a": []})
    ordered, notes = scan.order(catalog, ["a", "ghost"])
    assert ids(ordered) == ["a"]
    assert any("ghost" in n for n in notes)


def test_ids_and_bare_names_are_both_accepted(tiny):
    catalog = tiny({"a": [], "b": ["a"]})
    ordered, notes = scan.order(catalog, ["g/b", "a"])
    assert ids(ordered) == ["a", "b"]
    assert notes == []


def test_empty_selection_is_empty(tiny):
    assert scan.order(tiny({"a": []}), []) == ([], [])


# --------------------------------------------------------------------- cycles


def test_a_cycle_is_a_lint_finding(tmp_path):
    """A cycle makes the order undefined. The agent derives the order from this
    metadata, so the catalog must refuse to lint clean."""
    root = tmp_path / "skill"
    make_skill(root, catalog_of({"a": ["b"], "b": ["a"]}))
    catalog = scan.build_catalog(root)
    assert any("cycle" in m for m in catalog["lint"])


def test_a_self_edge_is_a_cycle(tmp_path):
    root = tmp_path / "skill"
    make_skill(root, catalog_of({"a": ["a"]}))
    assert any("cycle" in m for m in scan.build_catalog(root)["lint"])


def test_order_refuses_a_cycle_rather_than_dropping_packages(tiny):
    catalog = tiny({"a": ["b"], "b": ["a"]})
    with pytest.raises(ValueError, match="cycle"):
        scan.order(catalog, ["a", "b"])


# ------------------------------------------------------------- the real catalog


def test_the_shipped_catalog_is_acyclic():
    catalog = scan.build_catalog(SKILL)
    assert scan.find_cycles(scan.index_by_name(catalog)) == []


def test_every_shipped_package_orders_together():
    """Selecting the whole catalog has to produce an order. This is the case a
    hand-maintained list could never cover."""
    catalog = scan.build_catalog(SKILL)
    every = [p["name"] for g in catalog["groups"] for p in g["packages"]]
    ordered, _ = scan.order(catalog, every)
    assert len(ordered) == len(every)


def test_base_comes_first_for_any_selection_containing_it():
    """The invariant the runbooks stated four separate times in prose."""
    catalog = scan.build_catalog(SKILL)
    every = [p["name"] for g in catalog["groups"] for p in g["packages"]]
    ordered, _ = scan.order(catalog, every)
    assert ordered[0] == "foundation/base"


def test_languages_precede_the_hook_manager_and_ci_jobs():
    """Both read what the language packages wrote, which is why the ordering
    exists at all."""
    catalog = scan.build_catalog(SKILL)
    ordered, _ = scan.order(
        catalog, ["base", "python", "ts", "lefthook", "github", "github-python"]
    )
    assert ordered.index("languages/python") < ordered.index("hooks/lefthook")
    assert ordered.index("languages/python") < ordered.index("ci/github-python")
    assert ordered.index("ci/github") < ordered.index("ci/github-python")


def test_beads_follows_agentic_because_both_write_agents_md():
    catalog = scan.build_catalog(SKILL)
    ordered, _ = scan.order(catalog, ["base", "agentic", "beads"])
    assert ordered.index("agentic/agentic") < ordered.index("agentic/beads")


def test_cli_order_matches_the_library(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(SKILL / "scripts/scan.py"), "--skill-dir", str(SKILL),
         "--order", "base", "python", "lefthook"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["order"][0] == "foundation/base"
    assert payload["order"][-1] == "hooks/lefthook"
