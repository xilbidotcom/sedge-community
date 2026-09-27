# Copyright 2026 Xilbi Sistemas de Informacion SL
# SPDX-License-Identifier: Apache-2.0
"""Bounded input and explicit output contracts for the Community API."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

MAX_ROWS = 50_000
ScenarioId = Literal["household", "solar-home", "small-office"]


class GenerationRequest(BaseModel):
    """Configure a bounded, UTC, end-exclusive synthetic time series."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    scenario_id: ScenarioId = "solar-home"
    start_date: date = date(2026, 6, 1)
    days: int = Field(default=7, ge=1, le=31)
    resolution_minutes: Literal[5, 15, 30, 60] = 15
    buildings: int = Field(default=1, ge=1, le=20)
    daily_load_kwh: float = Field(default=12, ge=1, le=300)
    pv_capacity_kw: float = Field(default=4, ge=0, le=50)
    variability: float = Field(default=0.15, ge=0, le=0.5)
    seed: int = Field(default=42, ge=0, le=2**32 - 1)

    @property
    def row_count(self) -> int:
        return self.days * (1440 // self.resolution_minutes) * self.buildings

    @model_validator(mode="after")
    def bounded_run(self):
        if self.row_count > MAX_ROWS:
            raise ValueError(f"Requested {self.row_count:,} rows; maximum is {MAX_ROWS:,}. Reduce the scope.")
        if not date(2000, 1, 1) <= self.start_date <= date(2100, 12, 1):
            raise ValueError("start_date must be between 2000-01-01 and 2100-12-01")
        return self


class EnergyRow(BaseModel):
    timestamp: str
    building_id: str
    load_kw: float
    pv_kw: float
    grid_kw: float
    temperature_c: float


class Summary(BaseModel):
    rows: int
    buildings: int
    load_kwh: float
    pv_kwh: float
    import_kwh: float
    export_kwh: float
    peak_load_kw: float


class GenerationResult(BaseModel):
    edition: str = "SEDGE Community"
    version: str
    dataset_id: str
    configuration: GenerationRequest
    summary: Summary
    units: dict[str, str]
    methodology: str
    warnings: list[str]
    rows: list[EnergyRow]
