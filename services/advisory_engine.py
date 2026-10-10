from datetime import date, timedelta
import math
from config.thresholds import *
from services.validation import validate

def advise(values, predicted, today=None):
    v = validate(values)
    if not math.isfinite(predicted) or not 0 <= predicted <= 100:
        raise ValueError('Predicted moisture must be between 0 and 100')
    today = today or date.today()
    current = v['soil_moisture_percent']
    threshold = BASE_MOISTURE[v['soil_type']] + STAGE_OFFSET[v['crop_growth_stage']]
    rain = v['forecast_rainfall_mm']
    if current <= CRITICAL_MOISTURE:
        status, reason, days = 'Irrigation Required', 'Critically low current moisture overrides the rainfall deferral rule.', 0
    elif rain >= RAIN_DEFER_MM:
        status, reason, days = 'Irrigation May Be Deferred Due to Expected Rainfall', 'Forecast rainfall exceeds the illustrative deferral threshold; reassess tomorrow.', 1
    elif min(current, predicted) < threshold:
        status, reason, days = 'Irrigation Required', 'Current or predicted moisture is below the illustrative soil and crop threshold.', 0
    elif min(current, predicted) < threshold + SOON_MARGIN:
        status, reason, days = 'Irrigation Recommended Soon', 'Moisture is within five percentage points of the illustrative threshold.', 1
    else:
        status, reason = 'Irrigation Not Required', 'Current and predicted moisture exceed the illustrative threshold.'
        loss = current - predicted
        days = min(14, max(1, math.ceil((current - threshold) / loss))) if loss > .1 else None
    alerts = []
    if current < threshold: alerts.append(('warning', 'Low soil moisture detected'))
    if v['temperature_celsius'] >= HIGH_TEMPERATURE: alerts.append(('warning', 'High temperature recorded'))
    if rain >= RAIN_DEFER_MM: alerts.append(('info', 'Rainfall expected; reassess after the event'))
    if v['days_since_last_irrigation'] >= OVERDUE_DAYS and current < threshold:
        alerts.append(('warning', 'Irrigation overdue under prototype rules'))
    return dict(status=status, explanation=reason, predicted_moisture=round(predicted, 2),
                threshold=threshold, next_irrigation_date=(today + timedelta(days=days)).isoformat() if days is not None else None,
                date_method='Linear extrapolation of one-day dry-down, capped at 14 days; rainfall deferral means reassess tomorrow. No date when no dry-down is predicted.',
                alerts=alerts)

def duration_hours(area_hectares, water_depth_mm, flow_m3_hour, efficiency):
    if not all(math.isfinite(x) and x > 0 for x in [area_hectares, water_depth_mm, flow_m3_hour, efficiency]) or efficiency > 1:
        raise ValueError('Positive area, depth, flow and efficiency in (0, 1] are required')
    return area_hectares * water_depth_mm * 10 / efficiency / flow_m3_hour
