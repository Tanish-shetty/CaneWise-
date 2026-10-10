import json
from datetime import datetime, timezone
import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from config.settings import DATA, MODEL, FEATURES

def train():
    frame = pd.read_csv(DATA / 'synthetic_agriculture.csv')
    train_idx, test_idx = next(GroupShuffleSplit(n_splits=1, test_size=.2, random_state=42).split(frame, groups=frame.plot_id))
    cats = ['soil_type', 'crop_growth_stage']
    pipeline = Pipeline([('encode', ColumnTransformer([
        ('categorical', OneHotEncoder(handle_unknown='ignore'), cats),
        ('numeric', 'passthrough', [f for f in FEATURES if f not in cats])])),
        ('forest', RandomForestRegressor(n_estimators=100, max_depth=14, min_samples_leaf=2,
                                         random_state=42, n_jobs=1))])
    target = 'next_day_soil_moisture_percent'
    pipeline.fit(frame.iloc[train_idx][FEATURES], frame.iloc[train_idx][target])
    predicted = pipeline.predict(frame.iloc[test_idx][FEATURES])
    actual = frame.iloc[test_idx][target]
    metadata = dict(version='synthetic-rf-v1', trained_at=datetime.now(timezone.utc).isoformat(),
                    sklearn_version=sklearn.__version__, seed=42, train_rows=len(train_idx), test_rows=len(test_idx),
                    train_plots=sorted(frame.iloc[train_idx].plot_id.unique().tolist()),
                    test_plots=sorted(frame.iloc[test_idx].plot_id.unique().tolist()),
                    MAE=float(mean_absolute_error(actual, predicted)),
                    RMSE=float(np.sqrt(mean_squared_error(actual, predicted))), R2=float(r2_score(actual, predicted)),
                    persistence_MAE=float(mean_absolute_error(actual, frame.iloc[test_idx].soil_moisture_percent)))
    joblib.dump({'pipeline': pipeline, 'metadata': metadata}, MODEL)
    (MODEL.parent / 'metrics.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    pd.DataFrame({'plot_id': frame.iloc[test_idx].plot_id, 'actual': actual, 'predicted': predicted}).to_csv(DATA / 'held_out_predictions.csv', index=False)
    pd.DataFrame({'feature': pipeline['encode'].get_feature_names_out(),
                  'importance': pipeline['forest'].feature_importances_}).to_csv(DATA / 'feature_importance.csv', index=False)
    return metadata
