# Copyright 2026 Xilbi Sistemas de Informacion SL
# SPDX-License-Identifier: Apache-2.0
import csv
import io

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sedge_community.api import app
from sedge_community.generator import generate, to_csv
from sedge_community.models import GenerationRequest

client = TestClient(app)


def test_reproducible_and_seed_sensitive():
    config = GenerationRequest(days=2)
    first = generate(config)
    assert first == generate(config)
    assert first.rows != generate(config.model_copy(update={"seed": 7})).rows


@pytest.mark.parametrize("scenario", ["household", "solar-home", "small-office"])
def test_count_bounds_energy_and_csv(scenario):
    config = GenerationRequest(scenario_id=scenario, days=2, buildings=2)
    result = generate(config)
    assert len(result.rows) == 384
    assert len({(r.timestamp, r.building_id) for r in result.rows}) == 384
    for row in result.rows:
        assert row.load_kw >= 0
        assert 0 <= row.pv_kw <= config.pv_capacity_kw
        assert abs(row.grid_kw - (row.load_kw - row.pv_kw)) < 0.000011
        if int(row.timestamp[11:13]) in (0, 1, 2, 3, 23):
            assert row.pv_kw == 0
    assert result.summary.load_kwh == round(sum(r.load_kw for r in result.rows) * 0.25, 4)
    assert (
        abs(
            result.summary.import_kwh
            - result.summary.export_kwh
            - result.summary.load_kwh
            + result.summary.pv_kwh
        )
        < 0.0003
    )
    exported = list(csv.DictReader(io.StringIO(to_csv(result))))
    assert len(exported) == len(result.rows)
    assert float(exported[0]["load_kw"]) == result.rows[0].load_kw


def test_no_pv_and_weekend_office():
    result = generate(
        GenerationRequest(
            scenario_id="small-office", start_date="2026-06-01", days=7, pv_capacity_kw=0, variability=0
        )
    )
    assert all(r.pv_kw == 0 for r in result.rows)
    weekday = sum(r.load_kw for r in result.rows[:96]) * 0.25
    weekend = sum(r.load_kw for r in result.rows[-96:]) * 0.25
    assert weekday == pytest.approx(12, abs=0.001)
    assert weekend < weekday / 2


@pytest.mark.parametrize(
    "payload",
    [
        {"days": 0},
        {"days": 32},
        {"buildings": 21},
        {"seed": -1},
        {"pv_capacity_kw": -1},
        {"resolution_minutes": 17},
        {"scenario_id": "private"},
        {"variability": float("nan")},
        {"days": 31, "buildings": 20, "resolution_minutes": 5},
        {"users": True},
        {"start_date": "9999-12-31"},
    ],
)
def test_invalid_requests(payload):
    with pytest.raises(ValidationError):
        GenerationRequest(**payload)


def test_api_catalogue_download_and_validation():
    assert client.get("/api/v1/healthz").json()["status"] == "ok"
    assert len(client.get("/api/v1/scenarios").json()) == 3
    request = {"days": 1, "seed": 12}
    result = client.post("/api/v1/generate", json=request)
    assert result.status_code == 200
    assert result.json()["summary"]["rows"] == 96
    response = client.post("/api/v1/generate.csv", json=request)
    assert response.status_code == 200
    assert "attachment" in response.headers["content-disposition"]
    assert len(list(csv.DictReader(io.StringIO(response.text)))) == 96
    assert client.post("/api/v1/generate", json={"days": 32}).status_code == 422
    assert client.get("/api/openapi.json").json()["info"]["version"] == "1.0.0"
    assert client.get("/api/v1/users").status_code == 404
