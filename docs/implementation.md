# Dataset and model decisions
3,000 independent daily scenarios across 30 fictional plots, seed 42. Timestamps are scenario labels; these are not continuous hydrological trajectories. Soil type is fixed per plot. Other environmental values and crop stages vary by scenario.

Current moisture 10-85%, temperature 18-44 Celsius, humidity 25-95%, historical rainfall 0-65 mm, forecast 0-60 mm, irrigation age 0-20 days. Historical rainfall is contextual; forecast drives the synthetic next-day moisture gain. No watering is applied between current and next-day values.

Daily loss = 2 + 0.16(temp-20) + 0.025(70-humidity) + soil loss + stage loss + 0.05 min(days,15). Soil loss: sandy 2, loamy 1, clay 0.4. Stage loss: germination 0.5, tillering 1, grand growth 2, maturity 0. Forecast gain = forecast * soil factor (0.32/0.45/0.50). Add Gaussian noise sigma=1.5 percentage points, clip target to [0,100]. Irrigation label compares target against the same illustrative stage/soil threshold; it is never an input feature.

GroupShuffleSplit with seed 42 holds out six complete plots. OneHotEncoder is fitted only to training rows. Plot identifiers, timestamps, labels and next-day targets are excluded from predictors. Random Forest: 100 trees, depth 14, minimum leaf 2, one worker. Compare MAE with a persistence baseline; metrics describe generalization within this synthetic generator only, not field accuracy.

Thresholds are centralized in config/thresholds.py. Next date extrapolates the one-day moisture loss until the threshold, capped at 14 days. A forecast-based deferral means reassess tomorrow. No dry-down prediction gives no precise date. Pump duration is optional and requires user depth, area, efficiency and measured flow assumptions.

Seeded advisories are saved now with their historical scenario date used for recommendation calculations. created_at means insertion time; synthetic scenario timestamps are not actual sensor collection times. Manual entries are also unvalidated prototype inputs.
