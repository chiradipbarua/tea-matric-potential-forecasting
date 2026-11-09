# Input schemas and units

No study records are included in this repository; the schemas below describe the expected inputs.

## Point metrics

Provide equally sized finite arrays `observed`, `predicted` and optionally `persistence`, in kPa, on identical eligible endpoints for one horizon, partition and target definition. Bias is prediction minus observation. Within10/Within15 and coverage are proportions; multiply by 100 only for percentage reporting. R² uses the evaluated observed mean. MSE skill uses the supplied persistence prediction.

## Interval scores

Provide ordered q0.1/q0.5/q0.9 predictions and observations in kPa. Use only validation observations to estimate expansion. One central 80% interval and the median define WIS; this is not full-distribution CRPS. Statistical validity of calibration requires assumptions beyond calculating its finite rank.

## Alert metrics

Binary observed/predicted labels must refer to the same confirmed new-onset population. Currently dry origins are excluded by the caller. Sustained-run confirmation and missing-hour handling must be applied before scoring. Confusion counts concern warning origins, not unique episodes. Both touched plot-days and 24-hour issuance exposure may be reported; these denominators differ.

## Coverage figure CSV

Required columns: `model`, `block_hours`, `horizon_h`, `interval`, `metric`, `value`, `lower`, `upper`. Accepted model for this manuscript layout: `Chronos-2 LoRA`; intervals `raw`/`validation_expanded`; metrics `coverage`/`width`. Supply one row per 24/48/72-h horizon, interval and metric for 72-h blocks. Coverage values/bounds are proportions. Width values/bounds are kPa. The code draws existing estimates and intervals; it does not regenerate their bootstrap samples.

## Alert F1 figure CSV

Required columns: `model`, `block_hours`, `metric`, `rule`, `setting`, `horizon_h`, `value`, `lower`, `upper`. Models: `Chronos-2`, `Chronos-2 LoRA`; metric `F1`; rule `q10_path`; setting `default`; block_hours `72`. Supply one row per model and horizon. F1 and its bounds are dimensionless.

## Joint block difference dataframe

Columns: `origin_timestamp` (hourly timestamp with one consistent timezone), `plot_id`, `observed`, `predicted`, `reference` (kPa). Each origin/plot key must be unique. Supply one common eligible horizon/split population. Blocks are drawn on a dense hourly calendar and shared across both plots. Missing calendar hours are not interpolated. A positive difference means higher MAE for `predicted` than `reference`.

## Revision GPU runner

The runner expects `training_windows.npz`, `evaluation_origins.csv`, `eligible_endpoint_reference.csv` and `sensor_installation_confirmed.json` in the input directory (see `revision_gpu/README.md`).
