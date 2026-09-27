# Copyright 2026 Xilbi Sistemas de Informacion SL
# SPDX-License-Identifier: Apache-2.0
"""Check source publication hygiene, notices, links, versions and package hashes.

Works without installed dependencies and without Git in an extracted archive.
This is a bounded automated check, not a legal opinion or exhaustive secret scan.
Exit 1 on any finding; no files are modified.
"""

import argparse
import hashlib
import json
import re
import subprocess
import tomllib
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "README.md",
    "LICENSE",
    "NOTICE",
    "FUNDING.md",
    "OWNERSHIP.md",
    "BRANDING.md",
    "THIRD_PARTY_NOTICES.md",
    "THIRD_PARTY_LICENCES.txt",
    "DEPENDENCY_INVENTORY.json",
    "SECURITY.md",
    "SUPPORT.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "CHANGELOG.md",
    "CITATION.cff",
    "VERSION",
    "docs/PUBLISHING.md",
    "docs/RELEASE_READINESS.md",
    ".github/workflows/ci.yml",
    ".github/dependabot.yml",
    "scripts/setup.sh",
    "scripts/start.sh",
    "scripts/stop.sh",
    "scripts/package.sh",
)
LEGAL = (
    "LICENSE",
    "NOTICE",
    "BRANDING.md",
    "FUNDING.md",
    "OWNERSHIP.md",
    "THIRD_PARTY_NOTICES.md",
    "THIRD_PARTY_LICENCES.txt",
)
BLOCKED_PARTS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".runtime",
    ".pytest_cache",
    ".ruff_cache",
    "out",
    "output",
    "SEDGE_INTERNAL_ARCHIVE",
}
BLOCKED_SUFFIXES = {".db", ".sqlite", ".sqlite3", ".parquet", ".ckpt", ".pt", ".pth", ".pem", ".key", ".log"}
DISCLAIMER = (
    "Funded by the European Union through the O-CEI project. Views and opinions "
    "expressed are however those of the author(s) only and do not necessarily "
    "reflect those of the European Union or European Commission. Neither the "
    "European Union nor the granting authority can be held responsible for them."
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_files(root):
    if (root / ".git").exists():
        result = subprocess.check_output(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=root
        )
        return sorted({x.decode() for x in result.split(b"\0") if x})
    return sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file() or p.is_symlink())


def validate(root):
    errors = []
    files = source_files(root)
    for name in REQUIRED:
        if name not in files:
            errors.append(f"Missing required file: {name}")
    if errors:
        return errors
    version = (root / "VERSION").read_text().strip()
    if not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", version):
        errors.append("VERSION must be a stable semantic version")
    package = json.loads((root / "web/package.json").read_text())
    lock = json.loads((root / "web/package-lock.json").read_text())
    python = tomllib.loads((root / "pyproject.toml").read_text())["project"]
    versions = [python["version"], package["version"], lock["version"], lock["packages"][""]["version"]]
    for name, pattern in (
        ("backend/sedge_community/__init__.py", r'__version__ = "([^\"]+)"'),
        ("CITATION.cff", r"(?m)^version: (.+)$"),
    ):
        match = re.search(pattern, (root / name).read_text())
        versions.append(match.group(1) if match else "missing")
    if any(v != version for v in versions):
        errors.append(f"Version mismatch: canonical {version}, components {versions}")
    if python["license"] != "Apache-2.0" or package["license"] != "Apache-2.0":
        errors.append("First-party metadata must identify Apache-2.0")
    if "Version 2.0, January 2004" not in (root / "LICENSE").read_text():
        errors.append("Apache-2.0 licence text missing")
    for name in ("README.md", "NOTICE", "FUNDING.md"):
        if DISCLAIMER not in " ".join((root / name).read_text().split()):
            errors.append(f"Full funding disclaimer missing from {name}")
    js = (root / "web/src/legal.js").read_text()
    if DISCLAIMER not in "".join(re.findall(r'"([^\"]*)"', js)):
        errors.append("Web funding disclaimer differs")
    for name in LEGAL:
        target = root / "web/public/legal" / name
        if not target.exists() or target.read_bytes() != (root / name).read_bytes():
            errors.append(f"Bundled notice differs: {name}")
    inventory = json.loads((root / "DEPENDENCY_INVENTORY.json").read_text())
    for name, expected in inventory["lock_sha256"].items():
        if digest(root / name) != expected:
            errors.append(f"Dependency inventory is stale: {name}")
    if any(not p.get("licence") for p in inventory["components"]):
        errors.append("Unclassified dependency licence")
    for name in files:
        path = root / name
        if path.is_symlink() or not path.is_file():
            errors.append(f"Non-regular source file: {name}")
            continue
        if BLOCKED_PARTS.intersection(path.relative_to(root).parts) or path.suffix in BLOCKED_SUFFIXES:
            errors.append(f"Excluded file in source: {name}")
        if path.name.startswith(".env") and path.name != ".env.example":
            errors.append(f"Environment file in source: {name}")
        if path.stat().st_size > 2_000_000:
            errors.append(f"Oversized file needs review: {name}")
        if path.suffix == ".png":
            continue
        text = path.read_text(encoding="utf-8")
        # Detect common credential formats without printing a matching secret.
        patterns = [
            r"-----BEGIN [A-Z ]*PRIVATE " + "KEY-----",
            r"gh[pousr]_" + r"[A-Za-z0-9]{30,}",
            r"AKIA" + r"[A-Z0-9]{16}",
            r"/" + r"home/[^\s/]+/",
            r"/media/" + r"[^\s/]+/",
        ]
        if any(re.search(pattern, text) for pattern in patterns):
            errors.append(f"Private path or credential-like content: {name}")
        if path.suffix == ".md":
            for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
                link = unquote(link.split("#")[0].split("?")[0])
                if not link or re.match(r"[a-z]+:", link):
                    continue
                if link in {"/api/docs", "/api/openapi.json"}:
                    continue
                if not (path.parent / link).exists():
                    errors.append(f"Broken local link: {name}: {link}")
    manifest_path = root / "PACKAGE_MANIFEST.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        if manifest["version"] != version:
            errors.append("Manifest version mismatch")
        indexed = {item["path"] for item in manifest["files"]}
        if set(files) != indexed | {"PACKAGE_MANIFEST.json", "CHECKSUMS.sha256"}:
            errors.append("Manifest does not cover exactly the archive payload")
        for item in manifest["files"]:
            path = root / item["path"]
            if not path.is_file() or digest(path) != item["sha256"]:
                errors.append(f"Manifest checksum mismatch: {item['path']}")
            if not all(item.get(k) for k in ("origin", "owner", "licence")):
                errors.append(f"Ownership classification missing: {item['path']}")
        checksums = root / "CHECKSUMS.sha256"
        seen = set()
        if checksums.exists():
            for line in checksums.read_text().splitlines():
                expected, name = line.split("  ", 1)
                if name not in indexed | {"PACKAGE_MANIFEST.json"}:
                    errors.append("Unexpected checksum entry")
                    continue
                seen.add(name)
                if not (root / name).is_file() or digest(root / name) != expected:
                    errors.append(f"Checksum mismatch: {name}")
        if seen != indexed | {"PACKAGE_MANIFEST.json"}:
            errors.append("Checksum index incomplete")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    for error in errors:
        print(f"FAIL {error}")
    if errors:
        raise SystemExit(1)
    print("PASS: required files, funding, licences, versions, dependency inventory, links and source hygiene")
    if (args.root / "PACKAGE_MANIFEST.json").exists():
        print("PASS: archive ownership inventory and checksums")


if __name__ == "__main__":
    main()
