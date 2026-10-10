import joblib
import pandas as pd
from config.settings import MODEL, FEATURES
from services.validation import validate

class Predictor:
    def __init__(self, path=MODEL):
        if not path.exists():
            raise FileNotFoundError('Model missing. Run python -m scripts.setup first.')
        artifact = joblib.load(path)
        self.pipeline = artifact['pipeline']
        self.metadata = artifact['metadata']

    def predict(self, values):
        clean = validate(values)
        return float(self.pipeline.predict(pd.DataFrame([clean], columns=FEATURES))[0])
