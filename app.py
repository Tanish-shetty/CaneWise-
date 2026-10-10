import json
import pandas as pd
import plotly.express as px
import streamlit as st
from config.settings import DATA, MODEL, SOILS, STAGES, FEATURES
from database.db import initialize, plots, history, save
from models.predictor import Predictor
from services.advisory_engine import advise, duration_hours

st.set_page_config(page_title="CaneWise | Irrigation advisory", page_icon="\U0001f331", layout="wide")
st.markdown("""<style>
.stApp {background:#f5f8f4} h1,h2,h3 {color:#184c36}
[data-testid="stSidebar"] {background:#e6efe6}
[data-testid="stMetric"] {background:white;border:1px solid #d9e6dc;border-radius:12px;padding:16px}
.stButton>button {background:#205d41;color:white;border-radius:8px}
</style>""", unsafe_allow_html=True)
if not MODEL.exists() or not (DATA / 'synthetic_agriculture.csv').exists():
    st.error('Project assets missing. Run python -m scripts.setup before launching.')
    st.stop()
initialize()
@st.cache_resource
def predictor():
    return Predictor()
@st.cache_data
def dataset():
    return pd.read_csv(DATA / 'synthetic_agriculture.csv')
try:
    model = predictor()
except (FileNotFoundError, ValueError, KeyError) as exc:
    st.error(str(exc)); st.stop()
farm = plots()
st.sidebar.title('\U0001f331 CaneWise')
st.sidebar.caption('SMART SUGARCANE IRRIGATION')
page = st.sidebar.radio('Navigation', ['Farmer Dashboard', 'Irrigation Advisory', 'Analytics & History', 'Farm & Plots', 'Cloud Experiments'])
farmer = st.sidebar.selectbox('Farmer', farm.farmer_name.unique())
options = farm[farm.farmer_name == farmer]
plot = st.sidebar.selectbox('Plot', options.plot_id)
selected = options[options.plot_id == plot].iloc[0]
st.sidebar.caption(f"{selected.area_hectares} ha | {selected.soil_type} | {selected.irrigation_method}")
st.sidebar.info('Academic prototype | Synthetic data. Predictions and thresholds are not field validated.')
st.title(page)
st.caption('Smart Sugarcane Irrigation Advisory System Using AI and Cloud Computing')
observations = dataset().query('plot_id == @plot').copy()
latest = observations.iloc[-1].to_dict()
values = {f: latest[f] for f in FEATURES}

def result_card(result):
    status = result['status']
    if status == 'Irrigation Required': st.error(status)
    elif status == 'Irrigation Recommended Soon': st.warning(status)
    elif 'Deferred' in status: st.info(status)
    else: st.success(status)
    st.write(result['explanation'])
    a,b,c = st.columns(3)
    a.metric('Predicted next-day moisture', f"{result['predicted_moisture']:.1f}%")
    b.metric('Illustrative threshold', f"{result['threshold']}%")
    c.metric('Next irrigation / reassessment', result['next_irrigation_date'] or 'Reassess tomorrow')
    st.caption(result['date_method'])
    for level, message in result['alerts']: getattr(st, level)(message)

if page == 'Farmer Dashboard':
    st.subheader(f'{farmer} | {plot}')
    st.caption(f"{selected.variety} | {latest['crop_growth_stage']} | planted {selected.planting_date}")
    st.info(f"Latest synthetic scenario: {latest['timestamp'][:10]}. Values are demonstration scenarios, not live sensor readings.")
    cols = st.columns(4)
    for col, name, value in zip(cols, ['Soil moisture','Temperature','Humidity','Expected rainfall'],
        [f"{latest['soil_moisture_percent']:.1f}%", f"{latest['temperature_celsius']:.1f} C", f"{latest['humidity_percent']:.1f}%", f"{latest['forecast_rainfall_mm']:.1f} mm"]): col.metric(name,value)
    result_card(advise(values, model.predict(values)))
    a,b = st.columns(2)
    a.plotly_chart(px.line(observations, x='timestamp', y='soil_moisture_percent', title='Synthetic moisture scenarios', color_discrete_sequence=['#287b55']), width='stretch')
    b.plotly_chart(px.bar(observations.tail(20), x='timestamp', y=['rainfall_mm','forecast_rainfall_mm'], title='Rainfall scenarios (mm)'), width='stretch')
    records = history(plot)
    if not records.empty:
        st.plotly_chart(px.scatter(records, x='created_at', y='predicted_moisture', color='status', title='Saved advisory history'), width='stretch')

elif page == 'Irrigation Advisory':
    st.write('Enter measurements for the selected plot. Recommendations use a synthetic-data model and illustrative rules.')
    with st.form('advisory'):
        a,b = st.columns(2)
        entered = dict(soil_moisture_percent=a.slider('Soil moisture (%)',0.,100.,35.),
            temperature_celsius=a.number_input('Temperature (Celsius)',5.,50.,30.),
            humidity_percent=a.slider('Humidity (%)',0.,100.,65.),
            forecast_rainfall_mm=b.number_input('Expected rainfall (mm)',0.,150.,0.),
            soil_type=b.selectbox('Soil type',SOILS,index=SOILS.index(selected.soil_type)),
            crop_growth_stage=b.selectbox('Growth stage',STAGES,index=2),
            days_since_last_irrigation=b.number_input('Days since irrigation',0,60,5))
        submit = st.form_submit_button('Generate Advisory')
    if submit:
        try:
            result = advise(entered, model.predict(entered))
            record_id = save(plot, entered, result, model.metadata['version'])
            st.session_state['last_advisory'] = (plot, result, record_id)
        except (ValueError, OSError) as exc: st.error(str(exc))
    if 'last_advisory' in st.session_state and st.session_state.last_advisory[0] == plot:
        _,result,record_id = st.session_state.last_advisory
        result_card(result)
        st.caption(f'Saved advisory #{record_id}')
    with st.expander('Optional irrigation duration calculator'):
        st.caption('User-supplied assumptions: volume = hectares | depth (mm) | 10 / efficiency; hours = volume / flow. No agronomic depth recommendation is implied.')
        area=st.number_input('Area (ha)',.01,1000.,float(selected.area_hectares))
        depth=st.number_input('Assumed application depth (mm)',.1,200.,10.)
        flow=st.number_input('Measured flow (m3/hour)',.1,10000.,30.)
        efficiency=st.slider('Assumed application efficiency',.1,1.,.8)
        st.metric('Calculated duration under your assumptions', f'{duration_hours(area,depth,flow,efficiency):.2f} hours')

elif page == 'Analytics & History':
    from datetime import date
    chosen=st.date_input('Synthetic scenario date range', value=(pd.Timestamp(observations.timestamp.min()).date(),pd.Timestamp(observations.timestamp.max()).date()))
    filtered=observations
    if len(chosen)==2:
        dates=pd.to_datetime(observations.timestamp).dt.date
        filtered=observations[(dates>=chosen[0])&(dates<=chosen[1])]
    if filtered.empty: st.info('No scenarios in this range.')
    else:
        st.dataframe(filtered[['soil_moisture_percent','temperature_celsius','humidity_percent','rainfall_mm']].describe(), width='stretch')
        for field,label in [('soil_moisture_percent','Moisture (%)'),('temperature_celsius','Temperature (Celsius)'),('humidity_percent','Humidity (%)'),('rainfall_mm','Rainfall (mm)')]:
            st.plotly_chart(px.line(filtered,x='timestamp',y=field,title=label),width='stretch')
    st.subheader('Saved advisory records')
    records=history(plot)
    if not records.empty:
        date_range=st.date_input('Advisory creation date range',value=(pd.to_datetime(records.created_at).min().date(),pd.to_datetime(records.created_at).max().date()))
        if len(date_range)==2:
            dates=pd.to_datetime(records.created_at).dt.date
            records=records[(dates>=date_range[0])&(dates<=date_range[1])]
        st.dataframe(records,width='stretch')
        st.download_button('Export advisories as CSV',records.to_csv(index=False),'advisories.csv','text/csv')
    else: st.info('No saved advisories for this plot.')
    st.subheader('Held-out synthetic model evaluation')
    cols=st.columns(3)
    for col,key in zip(cols,['MAE','RMSE','R2']): col.metric(key,f'{model.metadata[key]:.3f}')
    st.caption(f"{model.metadata['version']} | trained {model.metadata['trained_at']} | entire plots held out. These scores measure fit to the synthetic generator only.")
    test=pd.read_csv(DATA/'held_out_predictions.csv')
    chart=px.scatter(test,x='actual',y='predicted',color='plot_id',title='Actual synthetic target vs predicted moisture (%)')
    chart.add_shape(type='line',x0=0,y0=0,x1=100,y1=100,line=dict(dash='dash',color='gray'))
    st.plotly_chart(chart,width='stretch')
    importance=pd.read_csv(DATA/'feature_importance.csv').sort_values('importance')
    st.plotly_chart(px.bar(importance,x='importance',y='feature',orientation='h',title='Encoded feature importance'),width='stretch')

elif page == 'Farm & Plots':
    st.info('Fictional demo farmers and plots. Growth stage is a scenario attribute, not inferred from planting date.')
    st.dataframe(farm,width='stretch')
    st.download_button('Export farm records',farm.to_csv(index=False),'sample_farmers.csv','text/csv')

else:
    st.subheader('Four experiments, one application')
    for title,filename in [('2 | Docker containerization','experiment_2.md'),('6 | CloudAnalyst workload simulation','experiment_6.md'),('7 | Resource right-sizing','experiment_7.md'),('8 | FinOps cost comparison','experiment_8.md')]:
        with st.expander(title): st.markdown((DATA.parent/'docs'/filename).read_text(encoding='utf-8'))
    results=DATA.parent/'cloud'/'results'/'comparison.csv'
    if results.exists():
        measured=pd.read_csv(results)
        st.dataframe(measured,width='stretch')
        st.plotly_chart(px.bar(measured,x='configuration',y='p95_latency_ms',title='Measured core advisory latency (not browser latency)'),width='stretch')
    else: st.info('Docker resource comparisons have not been executed yet.')
    costs=DATA.parent/'cloud'/'results'/'finops.csv'
    if costs.exists(): st.dataframe(pd.read_csv(costs),width='stretch')
