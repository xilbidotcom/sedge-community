# Development and edition boundaries

The generator, schema, API, UI and documentation are a separate implementation.
Only the four supplied brand images originate from the main edition. There are no
imports, symlinks, mounted output directories or runtime calls into SEDGE Engine.

## Layout

- `backend/sedge_community/models.py`: validated input and output contracts.
- `generator.py`: pure, seeded, in-memory generation and CSV conversion.
- `catalogue.py`: the API source of truth for three template configurations.
- `api.py`: five synchronous routes plus local OpenAPI documentation.
- `web/src/`: generation workflow, chart, data preview and Help.
- `docs/help/`: canonical Help articles, bundled with Vite.
- `examples/`: three small JSON configurations, not generated datasets.
- `scripts/`: independent setup, review-server lifecycle and source packaging.

## Development servers

```bash
# Terminal 1, repository root
.venv/bin/uvicorn sedge_community.api:app --host 127.0.0.1 --port 9010
# Terminal 2
cd web
npm run dev
```

Vite proxies `/api` to the Community API. The browser uses a relative URL and
never falls back to the main SEDGE API on port 9001. The production review build
uses the same proxy through Vite preview. Vite preview is not a public production
web server. For a shared service, configure a proper reverse proxy and security
controls; there is no public deployment helper in this edition.

Version 1.0.0 belongs to **SEDGE Community**, independently of the main edition.
For future changes update `VERSION`, Python and Web package metadata, UI version
and lock files together. Add generator tests when changing numerical behaviour.

## Source archive

`./scripts/package.sh` packages tracked source into `dist/`, without Git history,
dependencies, caches, server logs or generated outputs. Commit the desired source
state locally first. No remote is configured by these scripts; no push occurs.
The archive includes the licence, notices and brand terms.

## Retained main-edition evidence

This edition does not alter the main repository, operational outputs or frozen
evaluation records. Do not represent Community outputs as equivalent to those
results. No formal project validation is claimed for Community.
