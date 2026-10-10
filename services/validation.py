import math
from config.settings import FEATURES, SOILS, STAGES

RANGES = {'soil_moisture_percent': (0, 100), 'temperature_celsius': (5, 50),
          'humidity_percent': (0, 100), 'forecast_rainfall_mm': (0, 150),
          'days_since_last_irrigation': (0, 60)}

def validate(values):
    clean = {}
    for field in FEATURES:
        value = values.get(field)
        if value is None:
            raise ValueError(f'Missing input: {field}')
        if field in RANGES:
            try:
                number = float(value)
            except (ValueError, TypeError):
                raise ValueError(f'{field} must be numeric') from None
            lo, hi = RANGES[field]
            if not math.isfinite(number) or not lo <= number <= hi:
                raise ValueError(f'{field} must be between {lo} and {hi}')
            clean[field] = number
        else:
            options = SOILS if field == 'soil_type' else STAGES
            if value not in options:
                raise ValueError(f'Invalid {field}: choose {options}')
            clean[field] = value
    return clean
