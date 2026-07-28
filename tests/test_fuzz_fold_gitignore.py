"""Fuzz the .gitignore.d fold.

The script rewrites a file the user owns and edits by hand, so the invariants
are: never lose a line outside a bailiff block, never duplicate a block, and
never exit non-zero (copier's cleanup_on_error would delete the whole render).

Seven packages ship a byte-identical copy; this exercises the one in
languages/python and asserts the copies have not drifted.
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from conftest import TOOLS

SCRIPT = TOOLS / "languages/python/tasks/fold_gitignore.py"

NO_SHRINK = settings(
    max_examples=60,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)


def _load():
    spec = importlib.util.spec_from_file_location("fold_gitignore", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fold = _load()


def run_in(path: Path) -> int:
    """Run the fold as copier does: as a subprocess, cwd at the destination."""
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)], cwd=str(path), capture_output=True, text=True
    )
    return proc.returncode


def test_every_copy_is_identical():
    """The script must not drift between packages, or one package would fold
    differently from another."""
    copies = sorted(TOOLS.glob("*/*/tasks/fold_gitignore.py"))
    assert len(copies) >= 6
    digests = {
        hashlib.sha256(p.read_bytes()).hexdigest() for p in copies
    }
    assert len(digests) == 1, f"copies have drifted: {[str(p) for p in copies]}"


def test_no_fragment_directory_is_a_no_op(tmp_path):
    assert run_in(tmp_path) == 0
    assert not (tmp_path / ".gitignore").exists()


def test_empty_fragment_directory_writes_no_block(tmp_path):
    (tmp_path / ".gitignore.d").mkdir()
    assert run_in(tmp_path) == 0
    assert "bailiff:" not in (tmp_path / ".gitignore").read_text()


def test_blank_fragment_is_skipped(tmp_path):
    (tmp_path / ".gitignore.d").mkdir()
    (tmp_path / ".gitignore.d/empty").write_text("\n  \n")
    assert run_in(tmp_path) == 0
    assert "bailiff:empty" not in (tmp_path / ".gitignore").read_text()


def test_hand_written_content_survives(tmp_path):
    (tmp_path / ".gitignore").write_text("# mine\nsecrets.env\n!keep.env\n")
    (tmp_path / ".gitignore.d").mkdir()
    (tmp_path / ".gitignore.d/python").write_text("__pycache__/\n")
    assert run_in(tmp_path) == 0
    result = (tmp_path / ".gitignore").read_text()
    assert "secrets.env" in result
    assert "!keep.env" in result
    assert "__pycache__/" in result


def test_edited_fragment_replaces_the_old_block(tmp_path):
    (tmp_path / ".gitignore.d").mkdir()
    fragment = tmp_path / ".gitignore.d/python"
    fragment.write_text("old-pattern\n")
    run_in(tmp_path)
    fragment.write_text("new-pattern\n")
    run_in(tmp_path)
    result = (tmp_path / ".gitignore").read_text()
    assert "new-pattern" in result
    assert "old-pattern" not in result
    assert result.count("# >>> bailiff:python") == 1


def test_truncated_block_is_repaired(tmp_path):
    """A user who deletes the end marker must not cause an append loop."""
    (tmp_path / ".gitignore").write_text("keep\n# >>> bailiff:python\nstale\n")
    (tmp_path / ".gitignore.d").mkdir()
    (tmp_path / ".gitignore.d/python").write_text("fresh\n")
    assert run_in(tmp_path) == 0
    result = (tmp_path / ".gitignore").read_text()
    assert result.count("# >>> bailiff:python") == 1
    assert "fresh" in result
    assert "keep" in result


def test_a_subdirectory_in_the_fragment_dir_is_ignored(tmp_path):
    (tmp_path / ".gitignore.d/nested").mkdir(parents=True)
    (tmp_path / ".gitignore.d/python").write_text("__pycache__/\n")
    assert run_in(tmp_path) == 0
    assert "bailiff:nested" not in (tmp_path / ".gitignore").read_text()


def test_fragments_fold_in_a_stable_order(tmp_path):
    """Two renders in a different order must produce the same file, or the
    .gitignore churns in git history for no reason."""
    def build(names: list[str]) -> str:
        d = tmp_path / ("-".join(names))
        (d / ".gitignore.d").mkdir(parents=True)
        for n in names:
            (d / ".gitignore.d" / n).write_text(f"{n}-pattern\n")
        run_in(d)
        return (d / ".gitignore").read_text()

    assert build(["python", "go", "ts"]) == build(["ts", "go", "python"])


def test_unreadable_fragment_does_not_delete_the_render(tmp_path):
    """cleanup_on_error means a non-zero exit destroys everything rendered, so a
    surprising fragment must not be fatal."""
    (tmp_path / ".gitignore.d").mkdir()
    (tmp_path / ".gitignore.d/binary").write_bytes(b"\xff\xfe\x00not utf-8\n")
    code = run_in(tmp_path)
    assert code == 0, "a bad fragment must not fail the render"


@NO_SHRINK
@given(
    existing=st.text(
        alphabet=st.characters(blacklist_categories=("Cs",)), max_size=200
    ),
    body=st.text(alphabet=st.characters(blacklist_categories=("Cs",)), max_size=200),
)
def test_arbitrary_content_never_loses_user_lines(tmp_path_factory, existing, body):
    dest = tmp_path_factory.mktemp("proj")
    (dest / ".gitignore").write_text(existing, encoding="utf-8")
    (dest / ".gitignore.d").mkdir()
    (dest / ".gitignore.d/pkg").write_text(body, encoding="utf-8")

    assert run_in(dest) == 0
    result = (dest / ".gitignore").read_text(encoding="utf-8")

    # Every pre-existing line that was not part of a bailiff block survives.
    for line in existing.splitlines():
        if "bailiff:" in line:
            continue
        assert line in result.splitlines(), repr(line)


@NO_SHRINK
@given(
    body=st.text(alphabet=st.characters(blacklist_categories=("Cs",)), max_size=200)
)
def test_second_run_is_always_a_fixed_point(tmp_path_factory, body):
    dest = tmp_path_factory.mktemp("proj")
    (dest / ".gitignore.d").mkdir()
    (dest / ".gitignore.d/pkg").write_text(body, encoding="utf-8")

    run_in(dest)
    once = (dest / ".gitignore").read_text(encoding="utf-8")
    run_in(dest)
    assert (dest / ".gitignore").read_text(encoding="utf-8") == once


def test_replace_or_append_is_pure():
    """The helper must not mutate the list it was handed; the caller reassigns
    per fragment and a mutation would compound across fragments."""
    lines = ["keep"]
    original = list(lines)
    fold.replace_or_append(lines, "pkg", "pattern")
    assert lines == original
