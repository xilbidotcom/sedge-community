# Copyright 2026 Xilbi Sistemas de Informacion SL
# SPDX-License-Identifier: Apache-2.0
"""Stateless local API. No authentication, database or connection to SEDGE Engine."""

from fastapi import FastAPI
from fastapi.responses import Response

from . import __version__
from .catalogue import SCENARIOS
from .generator import generate, to_csv
from .models import GenerationRequest, GenerationResult

app = FastAPI(
    title="SEDGE Community API",
    version=__version__,
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
    description="Small deterministic energy datasets for learning and prototyping. "
    "Local use only: this edition has no authentication or persistent storage.",
)


@app.get("/api/v1/healthz", tags=["Service"], summary="Check service availability")
def health() -> dict[str, str]:
    return {"status": "ok", "edition": "community", "version": __version__}


@app.get("/api/v1/version", tags=["Service"], summary="Identify this distinct edition")
def version() -> dict[str, str]:
    return {"application": "SEDGE Community", "version": __version__, "licence": "Apache-2.0"}


@app.get("/api/v1/scenarios", tags=["Scenarios"], summary="List the three starter scenarios")
def scenarios() -> list[dict]:
    return SCENARIOS


@app.post(
    "/api/v1/generate",
    response_model=GenerationResult,
    tags=["Generation"],
    summary="Generate a small synthetic dataset",
    description="Synchronous and repeatable for the same configuration and version. "
    "At most 50,000 rows; no file writes. All timestamps are UTC and end-exclusive.",
    responses={422: {"description": "Invalid configuration or row limit exceeded"}},
)
def generate_json(config: GenerationRequest) -> GenerationResult:
    return generate(config)


@app.post(
    "/api/v1/generate.csv",
    tags=["Generation"],
    summary="Generate and download CSV",
    response_class=Response,
    responses={200: {"content": {"text/csv": {}}}, 422: {"description": "Invalid configuration"}},
)
def generate_csv(config: GenerationRequest) -> Response:
    result = generate(config)
    return Response(
        to_csv(result),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{result.dataset_id}.csv"'},
    )
