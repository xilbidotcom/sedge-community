# Troubleshooting

## API unavailable

Run `./scripts/status.sh` from the Community folder. Review `.runtime/api.log`
and `.runtime/web.log`. The Community API uses port 9010, not the main API on
9001. Start both services using `./scripts/start.sh`.

## Port already in use

The launcher refuses to replace another listener. Stop an earlier Community
review with `./scripts/stop.sh`, or choose different ports:

```bash
./scripts/start.sh --api-port 9011 --web-port 5181
```

## Too many records

The count is days × intervals per day × buildings. Reduce the duration, number
of buildings or temporal resolution to stay at or below 50,000 rows.

## The chart did not change

Changing settings only changes the pending configuration. Generate a new dataset
to update the chart. Metadata records the settings used for the displayed result.

## Same data after generating again

This is intentional when the seed and settings are unchanged. Change the seed
for another reproducible realisation. At zero variability the model is
deterministic even across different seeds.

## Main SEDGE is still visible

Open the Community Web port, normally 5180, rather than 5173. The header must say
**Community 1.0.0**. The services use separate source, dependencies and ports.

## Stopping and rebooting

Use `./scripts/stop.sh`. No boot service or restart policy is installed. After
reboot, run `./scripts/start.sh` again when needed. Download results before
closing the browser; there is no saved-run database.
