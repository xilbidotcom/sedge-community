# Third-party software

Community source and documentation: Apache-2.0, Xilbi Sistemas de Informacion SL.
Dependencies retain their licences; their installed distributions contain the
full notices. Lock files record the exact reviewed dependency set.

| Component | Role | Licence |
| --- | --- | --- |
| Python | Runtime | Python Software Foundation |
| FastAPI, Pydantic | HTTP API and validation | MIT |
| Uvicorn, Starlette | ASGI server and framework | BSD-3-Clause |
| HTTPX, HTTPCore | API testing and HTTP transport | BSD-3-Clause |
| certifi | CA certificates in the Python dependency set | MPL-2.0 |
| React, React DOM | Web interface | MIT |
| Vite and React plugin | Build and local review server | MIT |
| Recharts | Time-series chart | MIT |
| react-markdown | Offline Help rendering | MIT |
| Lucide | Interface icons | ISC |

Python transitive dependencies are recorded in `requirements.lock` and Web
dependencies in `web/package-lock.json`. This is a source-only project: no
vendored dependency code, external datasets, trained models or internal
archives are included. Logo terms are documented in `BRANDING.md`.

The complete locked dependency list and declared licence identifiers are in
`DEPENDENCY_INVENTORY.json`, including build/test dependencies and optional npm
platform packages. `THIRD_PARTY_LICENCES.txt` reproduces installed Python and Web
runtime licence notices, including nested charting-library notices. The same
text is available from the application's About page and bundled in Web builds.

Regenerate this inventory after changing dependencies; see `docs/PUBLISHING.md`
in the source package. Upstream package distributions remain
the authority for their own licence scope. These notices do not assert that all
dependencies are Apache-2.0 or that a vulnerability audit is a licence review.
