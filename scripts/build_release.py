# Copyright 2026 Xilbi Sistemas de Informacion SL
# SPDX-License-Identifier: Apache-2.0
"""Build a source folder, ZIP, tar.gz, manifest, checksums and validation report.

Only committed Community source is read; no Git history, dependencies, runtime
output or neighbouring repository is copied. Existing releases are never replaced.
Run tests first, then commit and invoke scripts/package.sh. Nothing is uploaded.
"""

import gzip
import io
import json
import subprocess
import tarfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from validate_release import digest, validate

ROOT = Path(__file__).resolve().parents[1]
OWNER = "Xilbi Sistemas de Informacion SL"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def classification(name):
    if name.startswith("web/public/brand/"):
        owner = OWNER
        if name.endswith("eu-funding.png"):
            owner = "European Union"
        elif name.endswith("o-cei-logo.png"):
            owner = "O-CEI project / respective rights holders"
        return {"origin": "brand_artwork", "owner": owner, "licence": "See BRANDING.md"}
    if name.endswith("THIRD_PARTY_LICENCES.txt"):
        return {
            "origin": "third_party_notices",
            "owner": "Respective upstream rights holders",
            "licence": "See individual notices and DEPENDENCY_INVENTORY.json",
        }
    return {"origin": "first_party", "owner": OWNER, "licence": "Apache-2.0"}


def build():
    if git("status", "--porcelain").strip():
        raise SystemExit("Commit intended Community source changes before packaging.")
    errors = validate(ROOT)
    if errors:
        raise SystemExit("\n".join(errors))
    commit = git("rev-parse", "HEAD").decode().strip()
    epoch = int(git("show", "-s", "--format=%ct", "HEAD"))
    version = (ROOT / "VERSION").read_text().strip()
    name = f"sedge-community-{version}-{commit[:7]}"
    output = ROOT / "dist"
    folder = output / name
    archives = [output / f"{name}.tar.gz", output / f"{name}.zip"]
    if folder.exists() or any(path.exists() for path in archives):
        raise SystemExit(f"Release already exists: {name}")
    folder.mkdir(parents=True)
    modes = {}
    with tarfile.open(fileobj=io.BytesIO(git("archive", "--format=tar", "HEAD"))) as source:
        for member in source.getmembers():
            if member.isdir():
                continue
            relative = Path(member.name)
            if not member.isfile() or relative.is_absolute() or ".." in relative.parts:
                raise SystemExit("Non-regular or unsafe archive entry")
            target = folder / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.extractfile(member).read())
            mode = 0o755 if member.mode & 0o111 else 0o644
            target.chmod(mode)
            modes[member.name] = mode
    records = [
        {
            "path": name,
            "sha256": digest(folder / name),
            "size": (folder / name).stat().st_size,
            **classification(name),
        }
        for name in sorted(modes)
    ]
    manifest = {
        "application": "SEDGE Community",
        "version": version,
        "source_commit": commit,
        "source_timestamp": datetime.fromtimestamp(epoch, UTC).isoformat(),
        "source_licence": "Apache-2.0",
        "branding_terms": "BRANDING.md",
        "distribution": "source only",
        "files": records,
        "index_coverage": "This manifest and CHECKSUMS.sha256 are Apache-2.0 generated indices. "
        "The checksum index covers the manifest and payload, but cannot hash itself.",
    }
    (folder / "PACKAGE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    modes["PACKAGE_MANIFEST.json"] = 0o644
    (folder / "CHECKSUMS.sha256").write_text(
        "".join(f"{digest(folder / relative)}  {relative}\n" for relative in sorted(modes))
    )
    modes["CHECKSUMS.sha256"] = 0o644
    errors = validate(folder)
    if errors:
        raise SystemExit("Extracted source validation failed:\n" + "\n".join(errors))
    with (
        archives[0].open("wb") as raw,
        gzip.GzipFile(fileobj=raw, mode="wb", mtime=epoch, filename="") as gz,
        tarfile.open(fileobj=gz, mode="w") as tar,
    ):
        for relative in sorted(modes):
            data = (folder / relative).read_bytes()
            info = tarfile.TarInfo(f"{name}/{relative}")
            info.size, info.mode, info.mtime = len(data), modes[relative], epoch
            tar.addfile(info, io.BytesIO(data))
    with zipfile.ZipFile(archives[1], "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative in sorted(modes):
            info = zipfile.ZipInfo(f"{name}/{relative}", datetime.fromtimestamp(epoch, UTC).timetuple()[:6])
            info.external_attr = (0o100000 | modes[relative]) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, (folder / relative).read_bytes())
    checksum_file = output / f"{name}.sha256"
    checksum_file.write_text("".join(f"{digest(p)}  {p.name}\n" for p in archives))
    report = output / f"{name}-validation.md"
    report.write_text(
        f"# Community source-package validation\n\nVersion: {version}\n\nSource commit: {commit}\n\n"
        f"Source files: {len(records)}; generated integrity indices: 2.\n\n"
        "PASS: required documentation, full funding disclaimer, bundled notices, version coherence, "
        "dependency inventory, internal links and bounded source-hygiene checks.\n\n"
        "PASS: every payload file has an ownership/licence classification and SHA-256; "
        "the manifest is covered by CHECKSUMS.sha256.\n\n"
        "Excluded: Git history, dependencies, build output, local environment files, "
        "runtime logs, generated datasets and internal archives.\n\n"
        "Scope: source-only packaging validation. This does not run a legal review, "
        "live GitHub CI, or a new vulnerability audit. See docs/RELEASE_READINESS.md "
        "for the separately performed checks. No upload is performed by this script.\n\n"
        + "\n".join(f"- {p.name}: {p.stat().st_size} bytes; SHA-256 `{digest(p)}`" for p in archives)
        + "\n"
    )
    print(f"Source folder: {folder}\nManifest: {folder / 'PACKAGE_MANIFEST.json'}")
    for path in (*archives, checksum_file, report):
        print(path)


if __name__ == "__main__":
    build()
