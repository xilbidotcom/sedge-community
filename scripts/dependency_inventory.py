# Copyright 2026 Xilbi Sistemas de Informacion SL
# SPDX-License-Identifier: Apache-2.0
"""Regenerate dependency metadata and installed runtime licence notices.

Run in the Community virtual environment after npm ci. No network access or
dependency changes are performed. Upstream licence texts are copied unchanged.
The inventory covers both lock files, including platform-specific npm packages
not installed on this host; full text covers installed Web runtime packages.
"""

import argparse
import hashlib
import json
import re
from importlib.metadata import distribution
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "DEPENDENCY_INVENTORY.json"
NOTICES = ROOT / "THIRD_PARTY_LICENCES.txt"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def licence_files(directory):
    """Find upstream notices, including nested vendored notices, but not dependencies."""
    return sorted(
        path
        for path in directory.rglob("*")
        if path.is_file()
        and "node_modules" not in path.relative_to(directory).parts
        and re.match(r"^(licen[cs]e|copying|notice)([.\-]|$)", path.name, re.IGNORECASE)
    )


def collect():
    components = []
    texts = [
        (
            "SEDGE Community - third-party runtime licence notices\n"
            "Upstream texts below are reproduced unchanged. They apply to the named\n"
            "dependencies, not to first-party Community source. No dependency code\n"
            "is vendored in the source archive. See DEPENDENCY_INVENTORY.json for\n"
            "all locked dependencies, including build/test and platform variants.\n"
        )
    ]
    for line in (ROOT / "requirements.lock").read_text().splitlines():
        name, version = line.split("==")
        dist = distribution(name)
        if dist.version != version:
            raise ValueError(f"Install locked Python dependency: {name}=={version}")
        licence = dist.metadata.get("License-Expression") or dist.metadata.get("License")
        if not licence or len(licence) > 200:
            raise ValueError(f"Review Python licence metadata for {name}")
        components.append({"ecosystem": "pypi", "name": name, "version": version, "licence": licence})
        for item in sorted(dist.files or []):
            if re.match(r"^(licen[cs]e|copying|notice)([.\-]|$)", item.name, re.IGNORECASE):
                path = Path(dist.locate_file(item))
                if path.is_file():
                    texts.append(f"\n{'=' * 72}\n{name} {version} - {item.name}\n{'=' * 72}\n")
                    texts.append(path.read_text())
    lock = json.loads((ROOT / "web/package-lock.json").read_text())
    for relative, package in sorted(lock["packages"].items()):
        if not relative:
            continue
        licence = package.get("license")
        if not licence:
            raise ValueError(f"Review npm licence metadata for {relative}")
        name = relative.split("node_modules/")[-1]
        components.append(
            {
                "ecosystem": "npm",
                "name": name,
                "version": package["version"],
                "licence": licence,
                "lock_path": relative,
                "development_only": package.get("dev", False),
                "optional": package.get("optional", False),
                "integrity": package.get("integrity"),
                "resolved": package.get("resolved"),
            }
        )
        directory = ROOT / "web" / relative
        if not package.get("dev") and directory.is_dir():
            files = licence_files(directory)
            if not files:
                raise ValueError(f"Missing installed npm runtime notices: {name}")
            for path in files:
                texts.append(
                    f"\n{'=' * 72}\n{name} {package['version']} - {path.relative_to(directory)}\n{'=' * 72}\n"
                )
                texts.append(path.read_text())
    inventory = {
        "format": "SEDGE Community dependency inventory 1",
        "scope": "Locked Python and npm dependencies; metadata, not vendored software",
        "lock_sha256": {p: sha(ROOT / p) for p in ("requirements.lock", "web/package-lock.json")},
        "components": components,
    }
    return json.dumps(inventory, indent=2) + "\n", "\n".join(texts) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for path, text in zip((INVENTORY, NOTICES), collect(), strict=True):
        if args.check:
            if not path.exists() or path.read_text() != text:
                raise SystemExit(f"Regenerate {path.name}")
        else:
            path.write_text(text)
            print(f"Updated {path.name}")


if __name__ == "__main__":
    main()
