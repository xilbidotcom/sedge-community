# Getting started

SEDGE Community creates small, illustrative energy time series. No login is
required; download results before closing the page because runs are not saved.

## Your first dataset

1. Open **Generate** and choose a template, or select one from **Scenarios**.
2. Set the start date, duration, interval and number of buildings.
3. Set daily demand and PV capacity per building. Zero PV means no solar output.
4. Choose a seed and press **Generate dataset**.
5. Inspect **Chart**, **Data** and **Metadata**, then download CSV or JSON.

The default is a seven-day solar-home example: 672 quarter-hour rows for one
building. Settings can be reset using the circular-arrow button.

## Controls

- Duration: 1–31 complete days; all timestamps use UTC, not local civil time.
- Interval: 5, 15, 30 or 60 minutes.
- Buildings: 1–20; total records must not exceed 50,000.
- Daily demand: 1–300 kWh per building, a typical weekday reference, not an exact
  daily target when random variability or office weekends are active.
- PV capacity: 0–50 kW per building.
- Variability: 0–50%, the intensity of random profile perturbations, **not** a
  percentage of anomalous records or a measured prediction error.
- Seed: an integer from 0 to 4,294,967,295. Same settings and version reproduce
  the same numerical dataset.

## Keeping results

Only the latest result is retained in browser memory. Changing settings does not
change the existing result until you generate again. Download buttons always
export the displayed result, not the pending settings. Reloading or closing the
page discards it. The API does not store results.
