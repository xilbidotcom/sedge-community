# Contributing

Contributions should preserve the edition's small, local-first scope. Begin with
a reproducible bug report or a short feature proposal. Large simulation engines,
accounts, queues and advanced research workflows belong outside this edition.

## Local checks

```bash
./scripts/setup.sh
.venv/bin/pytest -q
.venv/bin/ruff check backend tests scripts
npm --prefix web test
npm --prefix web run build
.venv/bin/python scripts/validate_release.py
```

Use British English, meaningful names and short comments explaining non-obvious
behaviour. Keep changes focused, add tests for numerical or API behaviour, and
preserve deterministic generation for fixed inputs and version. Document any
intentional change to generated results. Follow [DEVELOPMENT.md](docs/DEVELOPMENT.md).

## Rights and attribution

Submit only work you have the right to contribute. Intentional contributions
are provided under Apache-2.0 unless explicitly stated otherwise and agreed
with the maintainers. Copyright remains with the respective contributors.
Keep existing notices; add your own truthful copyright notice where appropriate.
Do not copy proprietary code, restricted datasets, credentials or unlicensed
artwork into this repository. Mark substantive changes to existing files in the
pull-request description and retain the change history.

Do not change branding or funding statements without maintainer review.
No copyright assignment or automatic grant of trademark rights is required.

## Reviews and reporting

Describe the problem, approach, tests and limitations in each pull request.
Follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Use the private route in
[SECURITY.md](SECURITY.md) for vulnerabilities, not a public issue.
Do not attach personal, customer or pilot data to reports.
