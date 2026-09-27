# Copyright 2026 Xilbi Sistemas de Informacion SL
# SPDX-License-Identifier: Apache-2.0
"""Bundle canonical legal documents without maintaining separate edited copies."""

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGAL_FILES = (
    "LICENSE",
    "NOTICE",
    "BRANDING.md",
    "FUNDING.md",
    "OWNERSHIP.md",
    "THIRD_PARTY_NOTICES.md",
    "THIRD_PARTY_LICENCES.txt",
)


def sync(check=False):
    """Copy exact source bytes, or fail if a production-facing notice is stale."""
    for name in LEGAL_FILES:
        source = ROOT / name
        target = ROOT / "web/public/legal" / name
        if check:
            if not target.exists() or target.read_bytes() != source.read_bytes():
                raise ValueError(f"Bundled notice is missing or stale: {name}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    sync(parser.parse_args().check)
