# Copyright 2026 Xilbi Sistemas de Informacion SL
# SPDX-License-Identifier: Apache-2.0
"""Check that edition identity, notices and example configurations stay coherent."""

import json
import runpy
import tomllib
from pathlib import Path

from sedge_community import __version__
from sedge_community.models import GenerationRequest

ROOT = Path(__file__).resolve().parents[1]


def test_launcher_version():
    launcher = runpy.run_path(str(ROOT / "scripts/serve.py"))
    assert launcher["version_banner"]() == f"SEDGE Community {__version__}"


def test_versions_and_examples():
    assert ROOT.joinpath("VERSION").read_text().strip() == __version__
    assert tomllib.loads(ROOT.joinpath("pyproject.toml").read_text())["project"]["version"] == __version__
    assert json.loads(ROOT.joinpath("web/package.json").read_text())["version"] == __version__
    for example in ROOT.joinpath("examples").glob("*.json"):
        assert GenerationRequest.model_validate_json(example.read_text()).row_count == 672


def test_licence_and_bundled_notices():
    for name in (
        "LICENSE",
        "NOTICE",
        "BRANDING.md",
        "FUNDING.md",
        "OWNERSHIP.md",
        "THIRD_PARTY_NOTICES.md",
        "THIRD_PARTY_LICENCES.txt",
    ):
        assert ROOT.joinpath(name).read_bytes() == ROOT.joinpath("web/public/legal", name).read_bytes()
    assert "Apache License" in ROOT.joinpath("LICENSE").read_text()
    assert "Version 2.0, January 2004" in ROOT.joinpath("LICENSE").read_text()
    assert len(list(ROOT.joinpath("docs/help").glob("*.md"))) == 5
