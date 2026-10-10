from html import escape
import pandas as pd
import plotly.express as px
import streamlit as st
from config.settings import DATA, MODEL, SOILS, STAGES, FEATURES
from database.db import initialize, plots, history, save
from models.predictor import Predictor
from services.advisory_engine import advise, duration_hours
from ui import design as ui

st.set_page_config(page_title="CaneWise | Irrigation advisory", page_icon="\U0001f331", layout="wide")
ui.css()
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
ui.brand()
page = st.sidebar.radio('Navigation', ['Farmer Dashboard', 'Irrigation Advisory', 'Analytics & History', 'Farm & Plots', 'Cloud Experiments'], label_visibility='collapsed')
farmer = st.sidebar.selectbox('Farmer', farm.farmer_name.unique())
options = farm[farm.farmer_name == farmer]
plot = st.sidebar.selectbox('Plot', options.plot_id)
selected = options[options.plot_id == plot].iloc[0]
st.sidebar.markdown(f'<div class="cw-context"><strong>{escape(plot)} &middot; {selected.area_hectares} hectares</strong><p>{escape(selected.soil_type)} soil &middot; {escape(selected.irrigation_method)} irrigation</p></div>', unsafe_allow_html=True)
st.sidebar.caption('SYNTHETIC DATA / ACADEMIC PROTOTYPE')
st.sidebar.caption('Predictions and illustrative thresholds are not field validated.')
subtitles = {'Farmer Dashboard': 'A clearer view of your crop, water and field conditions.', 'Irrigation Advisory': 'Turn field measurements into an explainable irrigation plan.', 'Analytics & History': 'Explore field patterns and the decisions behind them.', 'Farm & Plots': 'Your farmers, fields and cultivation details in one place.', 'Cloud Experiments': 'Explore deployment, performance and resource decisions.'}
ui.header('Farm overview' if page == 'Farmer Dashboard' else page, subtitles[page])
observations = dataset().query('plot_id == @plot').copy()
latest = observations.iloc[-1].to_dict()
values = {f: latest[f] for f in FEATURES}

def result_card(result, show_alerts=True):
    ui.advice_card(result)
    with st.expander('How this advisory is estimated'):
        st.caption(result['date_method'])
        st.caption('This prototype uses a synthetic-data model and illustrative thresholds.')
    if show_alerts:
        for level, message in result['alerts']: getattr(st, level)(message)

if page == 'Farmer Dashboard':
    ui.hero(farmer,plot,selected.variety,latest['crop_growth_stage'],latest['timestamp'][:10])
    specs=[('Soil moisture',f"{latest['soil_moisture_percent']:.1f}",'%', 'Current synthetic measurement','water','blue'),
           ('Temperature',f"{latest['temperature_celsius']:.1f}",'C','Ambient field temperature','temperature','amber'),
           ('Humidity',f"{latest['humidity_percent']:.1f}",'%', 'Relative air humidity','leaf','green'),
           ('Expected rainfall',f"{latest['forecast_rainfall_mm']:.1f}",'mm', 'Entered forecast scenario','rain','blue')]
    for col,spec in zip(st.columns(4,gap='medium'),specs):
        with col: ui.metric(*spec)
    left,right=st.columns([2.1,1],gap='large')
    result=advise(values,model.predict(values))
    with left:
        ui.section('Your irrigation outlook','Prediction + explainable rules')
        result_card(result,show_alerts=False)
    with right:
        ui.section('Field signals','Prototype alerts')
        if result['alerts']:
            for level,message in result['alerts']: getattr(st,level)(message)
        else: st.success('No alerts triggered by this scenario.')
        ui.details([('Variety',selected.variety),('Growth stage',latest['crop_growth_stage']),('Soil',selected.soil_type),('Area',f'{selected.area_hectares} ha')])
    ui.section('Field conditions','Independent synthetic scenarios')
    a,b=st.columns([1.35,1],gap='medium')
    with a:
        chart=px.area(observations,x='timestamp',y='soil_moisture_percent',title='Soil moisture',color_discrete_sequence=['#448466'])
        chart.update_traces(line_width=2,fillcolor='rgba(68,132,102,.09)')
        chart.add_hline(y=result['threshold'],line_dash='dot',line_color='#d8ae60',annotation_text='Illustrative threshold',annotation_position='bottom right')
        chart.update_yaxes(title_text='Moisture (%)',range=[0,100])
        ui.plot(chart)
    with b:
        chart=px.bar(observations.tail(20),x='timestamp',y=['rainfall_mm','forecast_rainfall_mm'],title='Rainfall outlook',barmode='group',color_discrete_sequence=['#6ea5b5','#c1d8e0'],labels={'value':'Rainfall (mm)'})
        chart.for_each_trace(lambda trace:trace.update(name={'rainfall_mm':'Scenario rainfall','forecast_rainfall_mm':'Forecast rainfall'}.get(trace.name,trace.name)))
        ui.plot(chart)
    records=history(plot)
    if not records.empty:
        ui.section('Recent advisories',f'{len(records)} saved records for {plot}')
        st.dataframe(records[['created_at','status','predicted_moisture','next_irrigation_date','source']].tail(5).iloc[::-1].rename(columns={'created_at':'Saved at','status':'Recommendation','predicted_moisture':'Predicted moisture (%)','next_irrigation_date':'Irrigation / reassessment','source':'Data source'}),hide_index=True,width='stretch')
        ui.plot(px.scatter(records,x='created_at',y='predicted_moisture',color='status',title='Advisory history',color_discrete_sequence=ui.COLORS),300)

elif page == 'Irrigation Advisory':
    ui.section('Build your irrigation plan',f'{plot} / {selected.soil_type} soil')
    st.caption('Enter your measurements below. Predictions use a synthetic-data model.')
    with st.form('advisory'):
        a,b = st.columns(2,gap='large')
        a.subheader('Field measurements')
        a.caption('Moisture, temperature and air conditions')
        b.subheader('Crop & rainfall')
        b.caption('Forecast and cultivation context')
        entered = dict(soil_moisture_percent=a.slider('Soil moisture (%)',0.,100.,35.),
            temperature_celsius=a.number_input('Temperature (Celsius)',5.,50.,30.),
            humidity_percent=a.slider('Humidity (%)',0.,100.,65.),
            forecast_rainfall_mm=b.number_input('Expected rainfall (mm)',0.,150.,0.),
            soil_type=b.selectbox('Soil type',SOILS,index=SOILS.index(selected.soil_type)),
            crop_growth_stage=b.selectbox('Growth stage',STAGES,index=2),
            days_since_last_irrigation=b.number_input('Days since irrigation',0,60,5))
        submit = st.form_submit_button('Generate Advisory',type='primary',width='stretch')
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
        st.caption('User-supplied assumptions: volume = hectares * depth (mm) * 10 / efficiency; hours = volume / flow. No agronomic depth recommendation is implied.')
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
        summary=st.columns(4)
        for col,field,label,unit in zip(summary,['soil_moisture_percent','temperature_celsius','humidity_percent','rainfall_mm'],['Average moisture','Average temperature','Average humidity','Total scenario rainfall'],['%','C','%','mm']):
            value=filtered[field].sum() if field=='rainfall_mm' else filtered[field].mean()
            col.metric(label,f'{value:.1f} {unit}')
        with st.expander('Detailed summary statistics'):
            st.dataframe(filtered[['soil_moisture_percent','temperature_celsius','humidity_percent','rainfall_mm']].describe(),width='stretch')
        chart_columns=st.columns(2,gap='medium')
        for index,(field,label) in enumerate([('soil_moisture_percent','Moisture (%)'),('temperature_celsius','Temperature (Celsius)'),('humidity_percent','Humidity (%)'),('rainfall_mm','Rainfall (mm)')]):
            with chart_columns[index%2]:
                ui.plot(px.line(filtered,x='timestamp',y=field,title=label,color_discrete_sequence=[ui.COLORS[index]]),280)
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
    ui.plot(chart,400)
    importance=pd.read_csv(DATA/'feature_importance.csv').sort_values('importance')
    ui.plot(px.bar(importance,x='importance',y='feature',orientation='h',title='What influences the prediction?',color_discrete_sequence=['#65946b']),420)

elif page == 'Farm & Plots':
    st.info('Fictional demo farmers and plots. Growth stage is a scenario attribute, not inferred from planting date.')
    farm_metrics=st.columns(3)
    farm_metrics[0].metric('Demo farmers',farm.farmer_id.nunique())
    farm_metrics[1].metric('Registered plots',len(farm))
    farm_metrics[2].metric('Total area',f'{farm.area_hectares.sum():.1f} ha')
    ui.section('Farm directory','Fictional demonstration records')
    st.dataframe(farm,hide_index=True,width='stretch')
    st.download_button('Export farm records',farm.to_csv(index=False),'sample_farmers.csv','text/csv')

else:
    ui.section('Four experiments, one application','Procedures & actual measurements')
    for col,number,title in zip(st.columns(4),['02','06','07','08'],['Containerization','Cloud simulation','Resource sizing','FinOps']):
        with col: ui.metric(title,number,'','Connected to the irrigation application')
    for title,filename in [('2 | Docker containerization','experiment_2.md'),('6 | CloudAnalyst workload simulation','experiment_6.md'),('7 | Resource right-sizing','experiment_7.md'),('8 | FinOps cost comparison','experiment_8.md')]:
        with st.expander(title): st.markdown((DATA.parent/'docs'/filename).read_text(encoding='utf-8'))
    results=DATA.parent/'cloud'/'results'/'comparison.csv'
    if results.exists():
        measured=pd.read_csv(results)
        st.dataframe(measured,width='stretch')
        ui.plot(px.bar(measured,x='configuration',y='p95_latency_ms',title='Measured core advisory latency (ms)',color='configuration',color_discrete_sequence=ui.COLORS))
    else: st.info('Docker resource comparisons have not been executed yet.')
    costs=DATA.parent/'cloud'/'results'/'finops.csv'
    if costs.exists(): st.dataframe(pd.read_csv(costs),width='stretch')

ui.footer()
