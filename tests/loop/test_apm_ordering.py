"""spec 014 FR-019/R7 + spec 007 SC-005, Q5: [bailiff-mod-base, bailiff-mod-apm] ordering.

Under spec 014 the only ordering edge is ``depends_on``.  apm declares
``depends_on: [bailiff-mod-base]`` in its copier.yml, so the engine orders base
before apm regardless of the selection order passed to init_many.

SC-005: project_name is read from base via ``_external_data.base.project_name``
and rendered into apm.yml.

reproduce_many recomputes the same order from committed edges (spec-003 engine).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from bailiff import discovery, ordering, runner, trust
from bailiff.catalog import TemplateRecord
from tests.conftest import TemplateRepo

_PKGS = ["srobroek/agentic-packages/packages/speckit#>=5.0.0 <6.0.0"]


@pytest.fixture(autouse=True)
def _isolated_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COPIER_SETTINGS_PATH", str(tmp_path / "settings.yml"))


def _record(full_id: str, repo: TemplateRepo, questions: list[str]) -> TemplateRecord:
    return TemplateRecord(
        full_id=full_id,
        source=repo.url,
        ref=repo.tag,
        versions=[repo.tag],
        reproducible=True,
        has_tasks=True,
        questions=questions,
    )


def _selection(
    bailiff_mod_base: TemplateRepo, bailiff_mod_apm: TemplateRepo
) -> list[tuple[TemplateRecord, dict[str, Any]]]:
    # Mis-order the selection (apm first) — apm's depends_on: [bailiff-mod-base]
    # edge drives base before apm (spec 014 FR-019).
    return [
        (
            _record("demo/bailiff-mod-apm", bailiff_mod_apm, ["project_name", "apm_packages"]),
            {"apm_packages": _PKGS},
        ),
        (
            _record("demo/bailiff-mod-base", bailiff_mod_base, ["project_name"]),
            {"project_name": "myapp"},
        ),
    ]


def test_base_orders_before_apm_via_depends_on(
    bailiff_mod_base: TemplateRepo, bailiff_mod_apm: TemplateRepo, tmp_path: Path
) -> None:
    """SC-005/FR-019: apm depends_on forces base first; project_name resolves via _external_data."""
    trust.add_trust(bailiff_mod_base.url)
    trust.add_trust(bailiff_mod_apm.url)
    dest = tmp_path / "proj"
    runner.init_many(_selection(bailiff_mod_base, bailiff_mod_apm), str(dest), today="2026-07-13")

    # apm rendered with the base-produced project_name (via _external_data).
    assert yaml.safe_load((dest / "apm.yml").read_text())["name"] == "myapp", (
        "project_name not resolved base → apm via _external_data"
    )

    # Each layer committed its own answers file; NO bailiff-specific recipe file exists.
    assert (dest / ".copier-answers.bailiff-mod-base.yml").is_file()
    assert (dest / ".copier-answers.bailiff-mod-apm.yml").is_file()
    # spec-010 invariant: no bailiff-authored order/recipe file in the project.
    recipe_like = [
        p.name
        for p in dest.iterdir()
        if p.name.startswith(".bailiff") and p.name.endswith((".yml", ".yaml", ".json"))
    ]
    assert recipe_like == [], f"unexpected bailiff recipe file committed: {recipe_like}"


def test_reproduce_recomputes_same_order(
    bailiff_mod_base: TemplateRepo, bailiff_mod_apm: TemplateRepo, tmp_path: Path
) -> None:
    """SC-005 / FR-019: reproduce recomputes base-before-apm from committed depends_on edge."""
    trust.add_trust(bailiff_mod_base.url)
    trust.add_trust(bailiff_mod_apm.url)
    dest = tmp_path / "proj"
    runner.init_many(_selection(bailiff_mod_base, bailiff_mod_apm), str(dest), today="2026-07-13")

    # Recompute the order from committed answers + pinned edges (as reproduce does).
    edges_by_basename: dict[str, dict[str, Any]] = {}
    recs: list[TemplateRecord] = []
    for af in ("bailiff-mod-base", "bailiff-mod-apm"):
        raw = yaml.safe_load((dest / f".copier-answers.{af}.yml").read_text())
        disc = discovery.discover(str(raw["_src_path"]), str(raw["_commit"]))
        edges_by_basename[af] = disc.dependency_edges
        recs.append(
            TemplateRecord(
                full_id=f"_recorded/{af}",
                source=str(raw["_src_path"]),
                ref=str(raw["_commit"]),
                versions=disc.versions,
                reproducible=disc.reproducible,
                has_tasks=disc.has_tasks,
                questions=[q.key for q in disc.questions],
            )
        )
    plan = ordering.layer_plan_from_edges(recs, edges_by_basename)
    order = [r.full_id.rsplit("/", 1)[-1] for r, _ in plan]
    assert order == ["bailiff-mod-base", "bailiff-mod-apm"], f"recomputed order wrong: {order}"

    # And reproduce actually runs clean.
    runner.reproduce_many(str(dest))
    assert (dest / "apm.yml").is_file()
