# Basic API

The API is synchronous, stateless and local. It does not require a token or write
files. Do not expose it publicly. Interactive documentation is available at
[/api/docs](/api/docs) and the schema at [/api/openapi.json](/api/openapi.json).

## Routes

- `GET /api/v1/healthz`: availability, edition and version.
- `GET /api/v1/version`: application identity and licence.
- `GET /api/v1/scenarios`: template names, descriptions and defaults.
- `POST /api/v1/generate`: JSON with all rows, configuration and summary.
- `POST /api/v1/generate.csv`: a CSV attachment containing all rows.

## Example

```bash
curl -fsS http://localhost:9010/api/v1/generate \
  -H 'Content-Type: application/json' \
  -d '{"scenario_id":"solar-home","days":2,"seed":42}'
```

The default configuration includes a start date of 2026-06-01, one building,
15-minute intervals, 12 kWh daily demand, 4 kW PV and variability 0.15. Specify
these explicitly when reproducing an example across future releases.

```bash
curl -fsS http://localhost:9010/api/v1/generate.csv \
  -H 'Content-Type: application/json' \
  -d '{"scenario_id":"solar-home","days":2,"seed":42}' \
  -o solar-home.csv
```

## Errors and retries

Invalid fields and scopes return HTTP 422 with field locations and messages.
Unknown routes return 404. Network/server failures should be retried only after
checking the local service. Repeating a valid request with the same seed and
configuration is safe and reproduces its data, although it repeats the work.

The 50,000-row cap is per request, not a multi-user resource quota. Cross-origin
browser access is not enabled; the Web server proxies its own `/api` requests.
