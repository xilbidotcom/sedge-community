# GitHub publication and source releases

## Prepared repository

This is the independent **SEDGE Community** repository:
[xilbidotcom/sedge-community](https://github.com/xilbidotcom/sedge-community).
Publish only its source, not the main SEDGE checkout or an enclosing directory.
The public repository has private vulnerability reporting and dependency alerts
enabled. Neither feature exposes the separate main edition.

No remote is required for local work. Account access, destination organisation,
repository visibility and the actual upload are separate publication steps.
Do not publish until the owner explicitly authorises them.

The source licence is Apache-2.0. Retain `LICENSE`, `NOTICE`, `FUNDING.md`,
`BRANDING.md`, `OWNERSHIP.md` and third-party notices. Do not let a repository
creation wizard replace these with a different licence. The npm `private: true`
flag prevents accidental npm publication; it does not make the source proprietary.

## Release checks

```bash
./scripts/setup.sh
.venv/bin/pytest -q
.venv/bin/ruff check backend tests scripts
npm --prefix web test
npm --prefix web run build
.venv/bin/python scripts/validate_release.py
npm --prefix web audit
# Install pip-audit in a separate tooling environment, then:
pip-audit -r requirements.lock --no-deps --disable-pip
```

When dependencies change, install the exact lock files, regenerate notices with
`.venv/bin/python scripts/dependency_inventory.py`, then run
`python3 scripts/sync_legal.py`. Review upstream licence changes before committing.
Dependency audit services receive names and versions, not project source.

After review and a clean local commit:

```bash
./scripts/package.sh
```

The script creates a source folder, ZIP and tar.gz under `dist/`. The folder has
`PACKAGE_MANIFEST.json` (source commit, licence classifications, sizes and hashes)
and `CHECKSUMS.sha256`. A sibling `.sha256` file hashes both archives. Run
`sha256sum -c` on that file from `dist/`, and on `CHECKSUMS.sha256` from inside an
extraction. Validate the extraction with `python3 scripts/validate_release.py`.
The indices document their own non-recursive hash coverage.

Neither archive includes `.git`, environments, `node_modules`, build output,
runtime logs, generated data, private archives or local secrets. Both include
`.github` configuration. Extract the archive before importing source into GitHub;
uploading the ZIP as a release attachment alone does not create a browsable
repository. The existing local repository is also ready for a later normal Git
push, after checking author metadata and authorising the destination.

## GitHub settings after access is granted

1. Create the separate repository under the chosen account or organisation.
2. Enable Issues and retain the supplied issue and pull-request templates.
3. Enable private vulnerability reporting and dependency alerts; see the
   [GitHub private reporting instructions](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository).
4. Check the first Actions run. The supplied workflow has read-only permissions,
   pinned action commits, no deployment step and no repository secrets.
5. Protect the default branch with reviewed changes and successful checks as
   appropriate. Avoid mandatory reviews by nonexistent maintainers.
6. Add the confirmed repository URL to citation/project metadata, then prepare
   the final public release from that reviewed source state.
7. Tag Community releases as `v1.0.0`, then follow semantic versioning independently
   of the main SEDGE product. Never overwrite a published tag.
8. Attach source archives and their checksums to the release. Do not publish
   runtime databases, generated outputs or the main-edition package.

These are the release-maintenance checklist. Check the repository's Actions,
Releases and settings for their current status; local validation does not prove
that a remote workflow or branch protection is in effect. No donation platform
is implied by the funding acknowledgement; there is deliberately no GitHub
sponsorship configuration.
