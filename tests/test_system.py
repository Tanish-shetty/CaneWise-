from datetime import date
from pathlib import Path
import pytest
from services.validation import validate
from services.advisory_engine import advise, duration_hours
from models.predictor import Predictor
from database.db import initialize, save, history
from config.settings import FEATURES

BASE=dict(soil_moisture_percent=45,temperature_celsius=30,humidity_percent=65,
          forecast_rainfall_mm=0,soil_type='Loamy',crop_growth_stage='Grand growth',days_since_last_irrigation=5)

def test_valid():
    assert set(validate(BASE))==set(FEATURES)

@pytest.mark.parametrize('field,value',[('soil_moisture_percent',-1),('soil_moisture_percent',101),('humidity_percent',101),('forecast_rainfall_mm',-1),('temperature_celsius',float('nan')),('soil_type','Unknown'),('days_since_last_irrigation',None)])
def test_invalid(field,value):
    with pytest.raises(ValueError): validate({**BASE,field:value})

def test_missing():
    with pytest.raises(ValueError): validate({})

@pytest.mark.parametrize('moisture,predicted,rain,status',[(20,15,0,'Irrigation Required'),(70,65,0,'Irrigation Not Required'),(40,38,0,'Irrigation Recommended Soon'),(30,25,30,'Irrigation May Be Deferred Due to Expected Rainfall'),(10,20,30,'Irrigation Required')])
def test_states(moisture,predicted,rain,status):
    result=advise({**BASE,'soil_moisture_percent':moisture,'forecast_rainfall_mm':rain},predicted,date(2026,1,1))
    assert result['status']==status
    assert set(result)=={'status','explanation','predicted_moisture','threshold','next_irrigation_date','date_method','alerts'}
    assert result['explanation']

def test_no_drydown():
    assert advise(BASE,50)['next_irrigation_date'] is None

def test_missing_model(tmp_path):
    with pytest.raises(FileNotFoundError): Predictor(tmp_path/'missing.joblib')

def test_prediction():
    model=Predictor()
    assert 0<=model.predict(BASE)<=100
    assert model.predict(BASE)==model.predict(BASE)
    assert not set(model.metadata['train_plots']) & set(model.metadata['test_plots'])
    assert model.metadata['MAE'] < model.metadata['persistence_MAE']

def test_database(tmp_path):
    db=tmp_path/'test.sqlite';initialize(db)
    result=advise(BASE,40)
    record=save('P01',BASE,result,'test',path=db)
    loaded=history('P01',db)
    assert loaded.iloc[0]['id']==record
    assert loaded.iloc[0]['status']==result['status']
    assert loaded.iloc[0]['soil_moisture_percent']==45

def test_duration():
    assert duration_hours(1,10,25,.8)==5
    with pytest.raises(ValueError): duration_hours(1,10,0,.8)

@pytest.mark.parametrize('page',['Farmer Dashboard','Irrigation Advisory','Analytics & History','Farm & Plots','Cloud Experiments'])
def test_pages(page,tmp_path,monkeypatch):
    # Isolated database: UI tests never append to the demonstration history.
    monkeypatch.setenv('CANEWISE_DB',str(tmp_path/'ui.sqlite'))
    from streamlit.testing.v1 import AppTest
    at=AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'),default_timeout=30).run()
    at.sidebar.radio[0].set_value(page).run()
    assert not at.exception
    if page=='Irrigation Advisory':
        before=len(history())
        at.button[0].click().run()
        assert not at.exception
        assert any('Saved advisory #' in x.value for x in at.caption)
        assert len(history()) == before + 1
