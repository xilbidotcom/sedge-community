# Development guide

SEDGE Community combines a synchronous Python API with a React interface.
Generation is seeded, bounded and performed in memory; no database or worker
queue is required.

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

Vite proxies `/api` to the Community API on port 9010. The browser uses a relative URL.
The production review build
uses the same proxy through Vite preview. Vite preview is not a public production
web server. For a shared service, configure a proper reverse proxy and security
controls; there is no public deployment helper in this edition.

For future changes update `VERSION`, Python and Web package metadata, UI version
and lock files together. Add generator tests when changing numerical behaviour.

## Source archive

`./scripts/package.sh` packages tracked source into `dist/`, without Git history,
dependencies, caches, server logs or generated outputs. Commit the desired source
state locally first. No remote is configured by these scripts; no push occurs.
The archive includes the licence, notices and brand terms.

## Documentation style

Describe the product, its limits and the procedure the reader needs. Keep
implementation history and cross-repository copying narratives out of user
guides, notices and About text. State licence scope directly; retain technical
methodology and verification records where they help readers assess results.
