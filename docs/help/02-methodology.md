# Method and limitations

Community uses simple seeded equations for energy profiles.
No measured datasets, pretrained models or online context providers are used.

## Demand

Households use smooth morning and evening peaks. Offices use a weekday working
period and a lower weekend profile. A reference weekday is normalised to the
configured daily demand. Independent building scales and correlated random
perturbations provide small differences. Negative demand is clipped to zero.

The random perturbation uses a fixed per-step correlation coefficient. Changing
the time resolution changes its effective persistence. This is a simplified
teaching model, not a resolution-invariant stochastic process.

## Solar and temperature

A generic northern-hemisphere seasonal curve changes daylight length and solar
strength. Smooth daylight production is modulated by bounded synthetic cloud
variation. PV is zero outside that daylight window and never exceeds installed
capacity. The temperature curve combines a seasonal term and a daily cycle.

There is no location, solar geometry, roof orientation, irradiance service, HVAC
model or calibration. Temperature is contextual output and does not drive demand.
Buildings share the weather curve; demand variability is independent per building.

## Power and energy

Grid exchange equals demand minus PV. Positive values mean import, negative
values mean export. Energy totals sum each power value multiplied by the interval
in hours. These calculations use the same rounded values exported in CSV and JSON.
The last timestamp is one interval before the end of the requested period.

## Appropriate use

Use the data for teaching, software demonstrations, chart prototyping and basic
pipeline checks. Do not use it for operational control, investment, safety,
forecast accuracy or regulatory claims. Basic numeric bounds are enforced;
this is **not** a full physical-feasibility or plausibility certification.
