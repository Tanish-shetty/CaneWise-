from config.settings import DATA, MODEL
from services.data_generator import generate
from models.train_model import train
from database.db import initialize, history, save, plots
from models.predictor import Predictor
from services.advisory_engine import advise
from config.settings import FEATURES

def setup():
    if not (DATA / 'synthetic_agriculture.csv').exists():
        generate()
    import json
    import sklearn
    metadata = MODEL.parent / "metrics.json"
    version_matches = metadata.exists() and json.loads(metadata.read_text())["sklearn_version"] == sklearn.__version__
    if not MODEL.exists() or not version_matches:
        print(train())
    initialize()
    plots().to_csv(DATA / "sample_farmers.csv", index=False)
    if history().empty:
        import pandas as pd
        from datetime import date
        frame = pd.read_csv(DATA / 'synthetic_agriculture.csv').tail(90)
        predictor = Predictor()
        for row in frame.to_dict('records'):
            values = {f: row[f] for f in FEATURES}
            result = advise(values, predictor.predict(values), date.fromisoformat(row['timestamp'][:10]))
            save(row['plot_id'], values, result, predictor.metadata['version'], source='synthetic seeded demonstration')
    print('Dataset, model and SQLite ready.')

if __name__ == '__main__':
    setup()
