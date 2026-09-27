# Community 1.0.0 publication readiness

The source is prepared for a separate GitHub repository. Publication itself is
not performed by the setup, validation or packaging scripts.

## Included

- Apache-2.0 licence text, copyright/ownership scope and NOTICE.
- EU/O-CEI funding acknowledgement and complete responsibility disclaimer in
  the README, NOTICE, funding document, application footer and About page.
- Branding terms identifying the four supplied logo assets separately from
  the source licence; no third-party logo is relicensed by this repository.
- Exact dependency locks, machine-readable dependency/licence inventory and
  upstream runtime licence texts, also bundled with the Web application.
- First-use, API, methodology, limitations, development and publication guides.
- Contribution, conduct, support and private-security-reporting guidance.
- Citation metadata, changelog, issue templates and pull-request checklist.
- Read-only, commit-pinned GitHub Actions checks and Dependabot configuration.
- Source-only ZIP/tar.gz, per-file manifest and SHA-256 integrity indices.

## Verification scope

Local verification completed for this preparation:

| Check | Result |
| --- | --- |
| Python tests, including release-policy regressions | 24 passed |
| Web tests, including complete funding and legal links | 5 passed |
| Ruff | Passed |
| Production Web build | Passed; advisory about bundle size |
| Python dependency audit | No known vulnerabilities reported |
| npm audit | No known vulnerabilities reported |
| GitHub configuration YAML | Five files parsed successfully |
| Application funding and About view | Verified in the local browser |
| Tracked PNG metadata | No text or EXIF chunks found |

The backend TestClient emits an upstream deprecation warning. These checks are
point-in-time results, not a promise that future advisories will remain empty.
The generated package validation report records source identity and checksums;
commands are in [PUBLISHING.md](PUBLISHING.md). Initial browser workflows are
described in [VERIFICATION.md](VERIFICATION.md).

## Privacy and publication boundary

First-party source and release files use organisation attribution, not personal
developer names, email addresses or machine-specific directory names. The new
Community repository uses organisation-only author/committer metadata and a
non-deliverable `.invalid` email identifier; no personal Git identity is needed
to import the source archive. Archives contain no Git history or local metadata.

Required upstream copyright notices retain their original authors and licence
text. Corporate names, funding bodies and product marks are also retained.
These are attribution, not project-team personal profiles. Do not remove required
upstream notices in an attempt to anonymise dependencies.

An external release policy checks source/package names and text for restricted
development references and project-specific personal identifiers. The detection
vocabulary is not distributed with either edition. Historical main-edition
archives and frozen evaluation records are not part of the Community release.

GitHub Actions and account-side settings can only be verified after publication.
Automated source and advisory scans do not certify legal compliance, absence of
all vulnerabilities, or permission beyond the stated source and artwork terms.
The owner retains the final decision on destination, visibility and publication.

No scientific-validation results from the separate SEDGE Engine are claimed.
Only illustrative, seeded synthetic generation is provided. The main edition,
its licence, private outputs and internal archives are outside this package.
