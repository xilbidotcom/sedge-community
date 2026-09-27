# Copyright 2026 Xilbi Sistemas de Informacion SL
# SPDX-License-Identifier: Apache-2.0
"""Illustrative seeded load/PV profiles; not a calibrated physical simulation.

Each building has an independent deterministic random stream. Energy summaries
integrate the exported rounded powers, so CSV and JSON have the same totals.
No measured data, fitted models, network requests or file writes are involved.
"""

import csv
import hashlib
import io
import json
import math
import random
from datetime import UTC, datetime, time, timedelta

from . import __version__
from .models import EnergyRow, GenerationRequest, GenerationResult, Summary


def _demand(hour: float, office: bool, weekend: bool) -> float:
    """Dimensionless daily profile; office weekends intentionally use less energy."""
    if office:
        return 0.15 + (0.3 if weekend else 1.6) * math.exp(-(((hour - 13) / 4.5) ** 4))
    return 0.25 + 0.8 * math.exp(-(((hour - 7.5) / 1.6) ** 2)) + 1.35 * math.exp(-(((hour - 19) / 2.5) ** 2))


def generate(config: GenerationRequest) -> GenerationResult:
    """Generate at most MAX_ROWS in memory with non-negative demand and bounded PV.

    The calendar uses UTC throughout and a generic northern-hemisphere seasonal
    shape. Grid power is demand minus PV: positive imports, negative exports.
    """
    start = datetime.combine(config.start_date, time(), tzinfo=UTC)
    steps = 1440 // config.resolution_minutes
    hours = [i * config.resolution_minutes / 60 for i in range(steps)]
    office = config.scenario_id == "small-office"
    normalisation = sum(_demand(h, office, False) for h in hours) / steps * 24
    weather_rng = random.Random(config.seed)
    weather = []
    cloud = 0.85
    for offset in range(config.days * steps):
        stamp = start + timedelta(minutes=offset * config.resolution_minutes)
        seasonal = math.cos(2 * math.pi * (stamp.timetuple().tm_yday - 172) / 365.25)
        daylight_hours = 12 + 3.5 * seasonal
        hour = stamp.hour + stamp.minute / 60
        phase = (hour - (12 - daylight_hours / 2)) / daylight_hours
        sun = math.sin(math.pi * phase) if 0 < phase < 1 else 0
        cloud = max(0.25, min(1.0, 0.9 * cloud + 0.085 + weather_rng.gauss(0, config.variability / 4)))
        pv_fraction = max(0, min(1, sun * (0.75 + 0.2 * seasonal) * cloud))
        temp = 14 + 9 * seasonal + 4 * math.sin(2 * math.pi * (hour - 9) / 24)
        weather.append((stamp, pv_fraction, temp))

    rows = []
    for building in range(config.buildings):
        rng = random.Random(config.seed + 104729 * (building + 1))
        scale = 1 + rng.uniform(-0.12, 0.12) * config.variability / 0.5
        residual = 0.0
        for stamp, pv_fraction, temp in weather:
            residual = 0.75 * residual + rng.gauss(0, config.variability * 0.35)
            profile = _demand(stamp.hour + stamp.minute / 60, office, stamp.weekday() >= 5)
            load = round(max(0, profile * config.daily_load_kwh / normalisation * scale * (1 + residual)), 5)
            pv = round(config.pv_capacity_kw * pv_fraction, 5)
            rows.append(
                EnergyRow(
                    timestamp=stamp.isoformat(),
                    building_id=f"building-{building + 1:03d}",
                    load_kw=load,
                    pv_kw=pv,
                    grid_kw=round(load - pv, 5),
                    temperature_c=round(temp, 2),
                )
            )
    rows.sort(key=lambda row: (row.timestamp, row.building_id))
    dt = config.resolution_minutes / 60
    fingerprint = hashlib.sha256(
        json.dumps(
            {"version": __version__, "config": config.model_dump(mode="json")}, sort_keys=True
        ).encode()
    ).hexdigest()[:16]
    return GenerationResult(
        version=__version__,
        dataset_id=f"community-{fingerprint}",
        configuration=config,
        summary=Summary(
            rows=len(rows),
            buildings=config.buildings,
            load_kwh=round(sum(r.load_kw for r in rows) * dt, 4),
            pv_kwh=round(sum(r.pv_kw for r in rows) * dt, 4),
            import_kwh=round(sum(max(0, r.grid_kw) for r in rows) * dt, 4),
            export_kwh=round(sum(max(0, -r.grid_kw) for r in rows) * dt, 4),
            peak_load_kw=max(r.load_kw for r in rows),
        ),
        units={"load_kw": "kW", "pv_kw": "kW", "grid_kw": "kW", "temperature_c": "degC"},
        methodology="Seeded daily demand profiles and illustrative daylight PV, generic northern hemisphere; UTC.",
        warnings=[
            "Illustrative synthetic data, not calibrated or validated against measured buildings.",
            "No battery, appliance, tariff, weather-service, ML or physical-simulation engine is included.",
        ],
        rows=rows,
    )


def to_csv(result: GenerationResult) -> str:
    """Export every generated row, including a header and explicit column units."""
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(EnergyRow.model_fields), lineterminator="\n")
    writer.writeheader()
    writer.writerows(row.model_dump() for row in result.rows)
    return output.getvalue()
