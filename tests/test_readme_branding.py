# Copyright 2026 Xilbi Sistemas de Informacion SL
# SPDX-License-Identifier: Apache-2.0
"""README contrast wrappers must preserve the exact supplied logo artwork."""

import base64
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NS = {"svg": "http://www.w3.org/2000/svg"}


def test_readme_panels_preserve_artwork_and_have_opaque_backgrounds():
    readme = (ROOT / "README.md").read_text()
    for source in sorted((ROOT / "web/public/brand").glob("*.png")):
        target = ROOT / "docs/assets/brand" / f"{source.stem}.svg"
        assert str(target.relative_to(ROOT)) in readme
        svg = ET.parse(target).getroot()
        background = svg.find("svg:rect", NS)
        assert background.attrib == {"width": svg.get("width"), "height": "112", "fill": "#ffffff"}
        logo = svg.find("svg:image", NS)
        assert logo.get("preserveAspectRatio") == "xMidYMid meet"
        assert base64.b64decode(logo.get("href").split(",", 1)[1]) == source.read_bytes()
        assert svg.find("svg:script", NS) is None


def test_readme_branding_generation_is_current():
    subprocess.run([sys.executable, "scripts/build_readme_branding.py", "--check"], cwd=ROOT, check=True)
