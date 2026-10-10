"""Deterministic independent synthetic scenarios, not field observations."""
import numpy as np
import pandas as pd
from config.settings import DATA, SOILS, STAGES
from config.thresholds import BASE_MOISTURE, STAGE_OFFSET
from services.validation import validate

def generate(seed=42, rows=3000):
    rng = np.random.default_rng(seed)
    records = []
    for i in range(rows):
        soil = SOILS[(i % 30) % 3]
        stage = STAGES[int(rng.integers(4))]
        moisture = float(rng.uniform(10, 85))
        temp = float(rng.uniform(18, 44))
        humidity = float(rng.uniform(25, 95))
        rain = float(rng.uniform(5, 65)) if rng.random() < .22 else 0.
        forecast = float(rng.uniform(5, 60)) if rng.random() < .25 else 0.
        days = int(rng.integers(0, 21))
        # Simplified daily dry-down and forecast infiltration; no irrigation applied.
        loss = 2 + .16 * (temp - 20) + .025 * (70 - humidity)
        loss += {'Sandy': 2, 'Loamy': 1, 'Clay': .4}[soil]
        loss += {'Germination': .5, 'Tillering': 1, 'Grand growth': 2, 'Maturity': 0}[stage]
        loss += min(days, 15) * .05
        gain = forecast * {'Sandy': .32, 'Loamy': .45, 'Clay': .5}[soil]
        next_moisture = np.clip(moisture - loss + gain + rng.normal(0, 1.5), 0, 100)
        record = dict(plot_id=f'P{i % 30 + 1:02}',
                      timestamp=(pd.Timestamp('2026-01-01') + pd.Timedelta(days=i // 30)).isoformat(),
                      soil_moisture_percent=round(moisture, 3), temperature_celsius=round(temp, 3),
                      humidity_percent=round(humidity, 3), rainfall_mm=round(rain, 3),
                      forecast_rainfall_mm=round(forecast, 3), soil_type=soil,
                      crop_growth_stage=stage, days_since_last_irrigation=days,
                      irrigation_method=['Drip', 'Furrow'][i % 2],
                      irrigation_required=int(next_moisture < BASE_MOISTURE[soil] + STAGE_OFFSET[stage]),
                      next_day_soil_moisture_percent=round(float(next_moisture), 3),
                      data_source='synthetic')
        validate(record)
        records.append(record)
    frame = pd.DataFrame(records)
    assert frame.next_day_soil_moisture_percent.between(0, 100).all()
    DATA.mkdir(exist_ok=True)
    frame.to_csv(DATA / 'synthetic_agriculture.csv', index=False)
    return frame
