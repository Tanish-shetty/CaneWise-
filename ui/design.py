"""Reusable visual components for the CaneWise interface."""
from html import escape
from datetime import date
import streamlit as st

COLORS = ['#247451', '#4d96ba', '#d9a344', '#8a7eae', '#9ab67f', '#d77c64']
ICONS = {
    'water': '<path d="M12 3C9 8 5 11 5 15a7 7 0 0 0 14 0c0-4-4-7-7-12Z"/><path d="M8 15a4 4 0 0 0 4 4"/>',
    'temperature': '<path d="M9 14V6a3 3 0 0 1 6 0v8a5 5 0 1 1-6 0Z"/><path d="M12 9v9"/>',
    'leaf': '<path d="M20 4C7 2 2 10 6 17s15 2 14-13Z"/><path d="m5 21 11-11"/>',
    'rain': '<path d="M6 14a4 4 0 0 1-1-8 6 6 0 0 1 11-1 4 4 0 1 1 2 9"/><path d="m8 17-1 3m6-3-1 3m6-3-1 3"/>',
}

def icon(kind, size=24):
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[kind]}</svg>'

def css():
    st.markdown('''<style>
    :root {--forest:#184b38;--muted:#748279;--line:#e2e9e1}
    .stApp {background:#f6f8f3;color:#223d30;font-family:"Segoe UI",sans-serif}
    [data-testid="stHeader"] {background:rgba(246,248,243,.94)}
    [data-testid="stMainBlockContainer"] {padding-top:1.8rem;padding-bottom:3rem;max-width:1500px}
    h1,h2,h3 {color:#184b38;letter-spacing:-.035em}
    h1 {font-weight:700!important} h3 {font-size:1.2rem!important}
    [data-testid="stSidebar"] {background:#fff;border-right:1px solid var(--line)}
    [data-testid="stSidebar"] [data-testid="stSidebarContent"] {padding-top:1.3rem}
    [data-testid="stSidebar"] [role="radiogroup"] {gap:5px}
    [data-testid="stSidebar"] label[data-baseweb="radio"] {padding:10px 12px;border-radius:10px;margin:0;transition:background .15s}
    [data-testid="stSidebar"] label[data-baseweb="radio"]:hover {background:#f0f5ec}
    [data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) {background:#e7f2e7;color:#185c3a;font-weight:600}
    [data-testid="stMetric"] {background:#fff;border:1px solid var(--line);border-radius:16px;padding:18px;box-shadow:0 4px 14px #1e422405}
    [data-testid="stMetricLabel"] {color:#718076;font-size:.85rem}
    [data-testid="stMetricValue"] {color:#184b38}
    [data-testid="stPlotlyChart"] {background:white;border:1px solid var(--line);border-radius:18px;overflow:hidden;box-shadow:0 5px 18px #1e422404}
    [data-testid="stForm"] {background:#fff;border:1px solid var(--line);border-radius:18px;padding:24px}
    [data-testid="stExpander"] {background:#fff;border-radius:14px;border-color:var(--line)}
    [data-testid="stVerticalBlockBorderWrapper"]>div {border-color:var(--line)!important;border-radius:16px!important}
    .stButton>button,[data-testid="stFormSubmitButton"] button {background:#236444;color:#fff;border:0;border-radius:10px;font-weight:600;min-height:44px;padding:0 20px}
    .stButton>button:hover,[data-testid="stFormSubmitButton"] button:hover {background:#174d33;color:white}
    [data-testid="stDownloadButton"] button {border-color:#cbdcc8;border-radius:10px;color:#245b3b}
    [data-testid="stAlert"] {border-radius:12px}
    .cw-brand {display:flex;align-items:center;gap:12px;margin-bottom:26px}
    .cw-brand-mark {display:grid;place-items:center;background:#205c3e;color:#def0cf;border-radius:13px;width:45px;height:45px}
    .cw-brand-name {font-size:26px;font-weight:750;letter-spacing:-1px;color:#204f36}
    .cw-brand-sub {font-size:9px;letter-spacing:1.8px;color:#7c8b7d;margin-top:3px}
    .cw-eyebrow {font-size:10px;letter-spacing:2px;font-weight:700;color:#7a8b7a;margin:14px 0 6px;text-transform:uppercase}
    .cw-context {border:1px solid #e3eadf;background:#f6f8f1;border-radius:13px;padding:15px;margin:10px 0 18px}
    .cw-context strong {font-size:14px;color:#285437}.cw-context p {font-size:12px;color:#728170;margin:5px 0 0}
    .cw-header {display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;gap:18px}
    .cw-header h1 {font-size:32px;margin:0;padding:0;font-weight:700;line-height:1.3}
    .cw-header p {color:#63715f;font-size:13px;margin:7px 0 0}
    .cw-badge {display:inline-flex;align-items:center;gap:7px;background:#eef3e7;border:1px solid #dde7d6;border-radius:30px;padding:8px 12px;color:#476448;font-size:11px;white-space:nowrap}
    .cw-dot {height:6px;width:6px;border-radius:50%;background:#73a667;display:inline-block}
    .cw-hero {position:relative;overflow:hidden;background:linear-gradient(110deg,#163e30,#296047);border-radius:22px;padding:30px 34px;color:#fff;display:flex;align-items:center;justify-content:space-between;gap:20px;margin:2px 0 24px}
    .cw-hero h2 {color:#fff;font-size:36px;line-height:1.14;font-weight:650;margin:12px 0;letter-spacing:-1.3px}
    .cw-hero p {color:#c0d6c5;font-size:13px;line-height:1.8;max-width:490px;margin:0}
    .cw-hero .cw-eyebrow {color:#b1caa3;margin:0}
    .cw-hero-tags {display:flex;gap:8px;flex-wrap:wrap;margin-top:18px}
    .cw-hero-tags span {padding:6px 10px;border-radius:7px;border:1px solid #ffffff25;background:#ffffff08;font-size:11px;color:#dceada}
    .cw-metric {background:#fff;border:1px solid var(--line);border-radius:17px;padding:19px 20px;position:relative;min-height:145px;box-sizing:border-box;box-shadow:0 5px 20px #17392204;margin-bottom:8px}
    .cw-metric-top {display:flex;align-items:center;justify-content:space-between;color:#61705f;font-size:12px}
    .cw-metric-icon {height:35px;width:35px;border-radius:11px;display:grid;place-items:center}
    .cw-metric-value {font-size:31px;font-weight:650;color:#254732;letter-spacing:-1px;margin:7px 0 3px;line-height:1.25}
    .cw-metric-unit {font-size:16px;font-weight:400;color:#647461;letter-spacing:0;margin-left:4px}
    .cw-metric-note {font-size:10px;color:#657460}
    .cw-section {display:flex;align-items:center;justify-content:space-between;margin:24px 0 13px}
    .cw-section h3 {font-size:18px!important;font-weight:650;padding:0;margin:0;color:#234831}
    .cw-section span {font-size:11px;color:#66755f}
    .cw-advice {background:#fff;border:1px solid var(--line);border-radius:18px;overflow:hidden;margin-bottom:12px}
    .cw-advice-body {padding:22px 24px}
    .cw-state {display:inline-block;border-radius:7px;padding:5px 9px;font-size:10px;font-weight:700;letter-spacing:.8px;text-transform:uppercase}
    .cw-advice h3 {font-size:23px!important;margin:12px 0 8px;line-height:1.25;letter-spacing:-.5px}
    .cw-advice p {font-size:13px;color:#62735c;line-height:1.7;margin:0}
    .cw-advice-stats {display:grid;grid-template-columns:repeat(3,1fr);background:#fafbf7;border-top:1px solid #e7ede3;padding:18px 24px;gap:15px}
    .cw-advice-stats small {display:block;font-size:10px;color:#60705a;margin-bottom:6px}
    .cw-advice-stats strong {display:block;font-size:17px;font-weight:650;color:#2d5035}
    .cw-details {background:white;border:1px solid var(--line);border-radius:16px;padding:21px}
    .cw-detail-row {display:flex;justify-content:space-between;gap:10px;padding:9px 0;border-bottom:1px solid #edf1e9;font-size:12px;color:#617257}
    .cw-detail-row:last-child {border:0}.cw-detail-row strong {font-weight:600;color:#355337;text-align:right}
    .cw-footer {border-top:1px solid #e1e9dc;margin-top:30px;padding:18px 0;font-size:11px;color:#65745d;display:flex;justify-content:space-between;gap:12px}
    @media(max-width:850px) {.cw-hero-art{display:none}.cw-hero{padding:24px}.cw-hero h2{font-size:29px}.cw-header{align-items:flex-start}.cw-header .cw-badge{display:none}.cw-advice-stats{grid-template-columns:1fr;gap:13px}.cw-metric{padding:14px}.cw-metric-value{font-size:25px}}
    </style>''', unsafe_allow_html=True)

def brand():
    st.sidebar.markdown(f'<div class="cw-brand"><div class="cw-brand-mark">{icon("leaf",28)}</div><div><div class="cw-brand-name">CaneWise<span style="color:#90b180">.</span></div><div class="cw-brand-sub">GROW WITH CONFIDENCE</div></div></div><div class="cw-eyebrow">Workspace</div>',unsafe_allow_html=True)

def header(title, subtitle):
    st.markdown(f'<div class="cw-header"><div><div class="cw-eyebrow">CaneWise / Farm intelligence</div><h1>{escape(title)}</h1><p>{escape(subtitle)}</p></div><span class="cw-badge"><i class="cw-dot"></i>Synthetic demo data</span></div>',unsafe_allow_html=True)

def hero(farmer, plot, variety, stage, scenario_date):
    stalks=''.join(f'<g transform="translate({x} {y})"><path d="M0 38V0" stroke="#b8d99b" stroke-width="3"/><path d="M0 17Q-24 8-19-2Q-3 0 0 17M0 9Q22-1 19-13Q4-9 0 9" fill="#7bab76"/></g>' for x,y in [(68,77),(97,66),(126,55),(150,95),(180,82),(210,70)])
    art=f'<svg class="cw-hero-art" width="270" height="190" viewBox="0 0 280 190" aria-hidden="true"><circle cx="158" cy="88" r="84" fill="#ffffff05"/><circle cx="158" cy="88" r="67" fill="none" stroke="#ffffff0e"/><path d="m28 128 118-63 105 56-119 63Z" fill="#78a267" opacity=".22"/><path d="m38 134 118-62M62 147l118-62M87 160l118-62M110 173l118-62" stroke="#b8d99b" stroke-opacity=".3" stroke-width="2"/>{stalks}<circle cx="46" cy="57" r="23" fill="#2d6a50" stroke="#709a74"/><path d="M46 42c-4 7-9 11-9 17a9 9 0 0 0 18 0c0-6-5-10-9-17Z" fill="#bbdce0"/><circle cx="236" cy="151" r="5" fill="#d1dba7"/></svg>'
    tags=''.join(f'<span>{escape(str(item))}</span>' for item in [plot,variety,stage])
    st.markdown(f'<div class="cw-hero"><div><div class="cw-eyebrow">YOUR FIELD, AT A GLANCE</div><h2>Every drop.<br>A smarter decision.</h2><p>Welcome, {escape(farmer)}. Explore your field conditions and plan irrigation with a clear, explainable advisory.</p><div class="cw-hero-tags">{tags}</div><p style="font-size:10px;margin-top:13px;color:#b9cdb8">Synthetic scenario from {escape(scenario_date)} &middot; Not live sensor readings</p></div>{art}</div>',unsafe_allow_html=True)

def metric(label, value, unit, note, kind='leaf', tone='green'):
    foreground,background={'green':('#347153','#edf5eb'),'blue':('#498ba7','#edf5f8'),'amber':('#b18b3c','#faf4e7')}[tone]
    st.markdown(f'<div class="cw-metric"><div class="cw-metric-top"><span>{escape(label)}</span><span class="cw-metric-icon" style="color:{foreground};background:{background}">{icon(kind,20)}</span></div><div class="cw-metric-value">{escape(str(value))}<span class="cw-metric-unit">{escape(unit)}</span></div><div class="cw-metric-note">{escape(note)}</div></div>',unsafe_allow_html=True)

def section(title, note=''):
    st.markdown(f'<div class="cw-section"><h3>{escape(title)}</h3><span>{escape(note)}</span></div>',unsafe_allow_html=True)

def advice_card(result):
    status=result['status']
    if status=='Irrigation Required': label,color,bg='Action needed','#a56439','#fbefdf'
    elif status=='Irrigation Recommended Soon': label,color,bg='Plan ahead','#9f8032','#fbf5df'
    elif 'Deferred' in status: label,color,bg='Rainfall outlook','#4385a0','#eaf5f8'
    else: label,color,bg='Moisture sufficient','#36734d','#edf5e9'
    when=result['next_irrigation_date']
    when=date.fromisoformat(when).strftime('%d %b %Y') if when else 'Reassess tomorrow'
    stats=[('Next-day prediction',f"{result['predicted_moisture']:.1f}%"),('Illustrative threshold',f"{result['threshold']}%"),('Irrigation / reassessment',when)]
    stats_html=''.join(f'<div><small>{escape(k)}</small><strong>{escape(v)}</strong></div>' for k,v in stats)
    st.markdown(f'<div class="cw-advice"><div class="cw-advice-body"><span class="cw-state" style="color:{color};background:{bg}">{label}</span><h3>{escape(status)}</h3><p>{escape(result["explanation"])}</p></div><div class="cw-advice-stats">{stats_html}</div></div>',unsafe_allow_html=True)

def details(items):
    rows=''.join(f'<div class="cw-detail-row"><span>{escape(str(k))}</span><strong>{escape(str(v))}</strong></div>' for k,v in items)
    st.markdown(f'<div class="cw-details">{rows}</div>',unsafe_allow_html=True)

def plot(fig, height=330):
    fig.update_layout(template='plotly_white',height=height,paper_bgcolor='white',plot_bgcolor='white',
        font=dict(family='Segoe UI, sans-serif',size=11,color='#768573'),
        title=dict(font=dict(size=16,color='#294e36'),x=.06,y=.94),
        margin=dict(l=28,r=24,t=60,b=36),colorway=COLORS,
        legend=dict(orientation='h',y=-.18,x=0,title_text=''),hovermode='x unified')
    fig.update_xaxes(showgrid=False,title_text=None,zeroline=False)
    fig.update_yaxes(gridcolor='#edf1e8',zeroline=False,title_font=dict(size=11))
    st.plotly_chart(fig,width='stretch',config={'displayModeBar':False})

def footer():
    st.markdown('<div class="cw-footer"><span>CaneWise &middot; Smart Sugarcane Irrigation</span><span>Academic prototype &middot; Synthetic predictions &middot; Not field validated</span></div>',unsafe_allow_html=True)
