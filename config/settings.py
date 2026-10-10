import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
MODEL = ROOT / 'models' / 'irrigation_model.joblib'
DB = Path(os.environ.get('CANEWISE_DB', str(ROOT / 'data' / 'canewise.sqlite')))
FEATURES = ['soil_moisture_percent', 'temperature_celsius', 'humidity_percent',
            'forecast_rainfall_mm', 'soil_type', 'crop_growth_stage', 'days_since_last_irrigation']
SOILS = ['Sandy', 'Loamy', 'Clay']
STAGES = ['Germination', 'Tillering', 'Grand growth', 'Maturity']
