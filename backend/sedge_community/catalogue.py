# Copyright 2026 Xilbi Sistemas de Informacion SL
# SPDX-License-Identifier: Apache-2.0
"""Small, inspectable starter scenarios; no external or private data."""

SCENARIOS = [
    {
        "id": "household",
        "name": "Everyday household",
        "category": "Residential",
        "description": "Morning and evening demand peaks with a quieter daytime period.",
        "defaults": {
            "scenario_id": "household",
            "days": 7,
            "resolution_minutes": 15,
            "buildings": 1,
            "daily_load_kwh": 12,
            "pv_capacity_kw": 0,
            "variability": 0.15,
            "seed": 42,
        },
    },
    {
        "id": "solar-home",
        "name": "Home with rooftop PV",
        "category": "Residential + solar",
        "description": "Household demand and daylight solar production, with signed grid exchange.",
        "defaults": {
            "scenario_id": "solar-home",
            "days": 7,
            "resolution_minutes": 15,
            "buildings": 1,
            "daily_load_kwh": 12,
            "pv_capacity_kw": 4,
            "variability": 0.15,
            "seed": 42,
        },
    },
    {
        "id": "small-office",
        "name": "Small office",
        "category": "Commercial",
        "description": "Weekday working-hour demand with reduced weekend activity.",
        "defaults": {
            "scenario_id": "small-office",
            "days": 7,
            "resolution_minutes": 15,
            "buildings": 1,
            "daily_load_kwh": 48,
            "pv_capacity_kw": 6,
            "variability": 0.1,
            "seed": 42,
        },
    },
]
