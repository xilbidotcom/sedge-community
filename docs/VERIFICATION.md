# Community edition verification

This records verification of Community 1.0.0, not the capabilities or KPI results
of the separate SEDGE Engine. The generator is illustrative and uncalibrated.

## Automated checks

- Backend: 19 tests passed, covering seeded reproducibility, all three scenarios,
  row limits, demand/PV bounds, signed grid balance, energy totals, CSV output,
  request validation, API discovery and edition metadata.
- Python static checks: Ruff passed for the backend, tests and launcher.
- Web: three tests passed for estimates, exports, chart aggregation and errors.
- Production Web build and fresh dependency setup completed successfully.
- All five shell entry points passed Bash syntax validation.

The backend test dependency emits a TestClient deprecation warning; the Web
builder emits an advisory about the initial bundle size. Neither is a failed
test. No claim is made about penetration testing or production readiness.

## Browser review

The local production preview was checked on desktop and at a 375-pixel mobile
viewport. The SEDGE, XILBI, O-CEI and EU assets loaded. No browser console errors
were observed during the review.

Verified workflows include generation, chart display, paginated data, metadata,
scenario selection, reset, row-limit blocking, Help navigation and search.
CSV and JSON downloads were opened and checked. The default seven-day solar-home
example produced 672 records with seed 42; the browser CSV and API CSV contained
identical records. The JSON contained the same 672 records and configuration.

## Runtime isolation

The Community Web and API run on loopback ports 5180 and 9010. Start, stop and
restart were exercised; a duplicate start was rejected without stopping the
existing instance. No boot service is installed. The launcher does not manage
the main SEDGE services or their ports.

Only approved branding images were reused. The Community implementation has
its own source repository, dependencies, examples and tests. No main-edition
source modules, database, trained models, generated datasets, D3 materials or
internal archives are required or included. The main repository's pre-existing
branding edits were left unchanged.

## Source archive

Run `./scripts/package.sh` from a clean committed Community checkout. It archives
tracked source only and writes a SHA-256 checksum alongside the archive.
Dependency directories, runtime logs, downloaded output and build products are
ignored and must not be added to the repository. Source is Apache-2.0; names and
logos retain the separate terms documented in `BRANDING.md`.
