# Third-party software

Community source and documentation: Apache-2.0, Xilbi Sistemas de Informacion SL.
Dependencies retain their licences; their installed distributions contain the
full notices. Lock files record the exact reviewed dependency set.

| Component | Role | Licence |
| --- | --- | --- |
| Python | Runtime | Python Software Foundation |
| FastAPI, Pydantic | HTTP API and validation | MIT |
| Uvicorn, Starlette | ASGI server and framework | BSD-3-Clause |
| React, React DOM | Web interface | MIT |
| Vite and React plugin | Build and local review server | MIT |
| Recharts | Time-series chart | MIT |
| react-markdown | Offline Help rendering | MIT |
| Lucide | Interface icons | ISC |

Python transitive dependencies are recorded in `requirements.lock` and Web
dependencies in `web/package-lock.json`. This is a source-only project: no
vendored dependency code, external datasets, trained models or main-edition
archives are included. Logo terms are documented in `BRANDING.md`.
