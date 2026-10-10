import argparse
from pathlib import Path
import pandas as pd

def compare(hours=730):
    if hours<=0: raise ValueError('hours must be positive')
    measured=pd.read_csv('cloud/results/comparison.csv')
    prices=pd.read_csv('cloud/finops_prices.csv')
    frame=measured.merge(prices,on='configuration',validate='one_to_one')
    frame['estimated_monthly_cost_usd']=frame.hourly_price_usd*hours
    frame['operating_hours']=hours
    frame.to_csv('cloud/results/finops.csv',index=False)
    import plotly.express as px
    px.bar(frame,x='configuration',y='estimated_monthly_cost_usd',color='meets_target',title='Hypothetical monthly compute cost').write_html('cloud/results/cost_comparison.html')
    px.bar(frame,x='configuration',y='p95_latency_ms',title='Measured core workload p95 latency').write_html('cloud/results/latency_comparison.html')
    eligible=frame[frame.meets_target.eq(True)].sort_values('estimated_monthly_cost_usd')
    print(frame[['configuration','p95_latency_ms','meets_target','estimated_monthly_cost_usd']].to_string(index=False))
    print('Lowest assumed-cost qualifying configuration: '+str(eligible.iloc[0].configuration) if len(eligible) else 'No configuration met the target.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--hours',type=float,default=730);compare(p.parse_args().hours)
