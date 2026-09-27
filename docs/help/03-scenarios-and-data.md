# Scenarios and data

## Three starting points

- **Everyday household:** 12 kWh weekday demand, no PV, morning/evening peaks.
- **Home with rooftop PV:** 12 kWh weekday demand and 4 kW PV.
- **Small office:** 48 kWh weekday demand and 6 kW PV; quieter weekends.

Selecting a template loads its defaults while preserving your start date.
The API accepts all settings explicitly; selecting only a scenario ID through
the API does not apply that template's numerical defaults. Retrieve them from
`GET /api/v1/scenarios` or use the JSON examples supplied with the source.

## Columns

- `timestamp`: ISO 8601 UTC timestamp, one per building per interval.
- `building_id`: stable generated identifier, such as `building-001`.
- `load_kw`: non-negative demand in kW.
- `pv_kw`: PV output in kW, between zero and configured capacity.
- `grid_kw`: import-positive, export-negative grid exchange in kW.
- `temperature_c`: illustrative ambient temperature in degrees Celsius.

Rows are ordered by timestamp, then building. The chart sums building power,
whereas the data table and downloads retain each building's rows separately.
Long charts are sampled to keep the view responsive; summaries and downloads
use all rows. The table shows 15 rows per page.

CSV contains the complete row set. JSON additionally includes the configuration,
units, version, deterministic dataset identifier, summary and limitations. The
identifier is derived from the configuration and generator version; it is not
a checksum of the downloaded file and not a stored-run identifier.
