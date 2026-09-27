# Copyright 2026 Xilbi Sistemas de Informacion SL
# SPDX-License-Identifier: Apache-2.0
"""Regression checks for the source-only publication boundary and legal notices."""

import importlib.util
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("release_checks", ROOT / "scripts/validate_release.py")
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


@pytest.fixture
def source(tmp_path):
    for name in checks.source_files(ROOT):
        destination = tmp_path / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, destination)
    return tmp_path


def test_publication_checks_pass():
    assert checks.validate(ROOT) == []


def test_checks_work_without_git(source):
    assert checks.validate(source) == []


def test_reject_runtime_data_and_private_paths(source):
    (source / ".env").write_text("EXAMPLE=not-a-secret\n")
    (source / "output").mkdir()
    (source / "output/sample.db").write_text("test")
    (source / "private.txt").write_text("/" + "home/someone/private/file")
    errors = checks.validate(source)
    assert any("Environment file" in e for e in errors)
    assert any("Excluded file" in e for e in errors)
    assert any("Private path" in e for e in errors)


def test_missing_funding_and_stale_bundled_notice_fail(source):
    (source / "FUNDING.md").write_text("# Incomplete acknowledgement\n")
    errors = checks.validate(source)
    assert any("funding disclaimer missing" in e for e in errors)
    assert any("Bundled notice differs" in e for e in errors)


def test_dependency_lock_change_requires_inventory_refresh(source):
    with (source / "requirements.lock").open("a") as file:
        file.write("# changed\n")
    assert any("inventory is stale" in e for e in checks.validate(source))
