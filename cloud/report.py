"""Summarize measured whole-container RAM and generate comparison charts."""
from pathlib import Path
import re
import pandas as pd
import plotly.express as px

def memory_mib(value):
    number,unit=re.fullmatch(r'([0-9.]+)\s*([A-Za-z]+)',value.strip()).groups()
    return float(number)*{'B':1/1048576,'KiB':1/1024,'MiB':1,'GiB':1024,'kB':1000/1048576,'MB':1000000/1048576,'GB':1000000000/1048576}[unit]

def report():
    root=Path('cloud/results');frame=pd.read_csv(root/'comparison.csv')
    for i,row in frame.iterrows():
        stats=root/f"{row['configuration']}_docker_stats.csv"
        if stats.exists():
            samples=pd.read_csv(stats)
            frame.loc[i,'docker_memory_mib_max']=samples.MemUsage.map(lambda v:memory_mib(v.split('/')[0])).max()
            frame.loc[i,'docker_stats_samples']=len(samples)
    frame.to_csv(root/'comparison.csv',index=False)
    for metric,title in [('p95_latency_ms','Measured core advisory p95 latency (ms)'),('docker_cpu_percent_mean','Measured Docker CPU utilization (% of one host core)'),('docker_memory_mib_max','Measured whole-container RAM peak (MiB)'),('throughput_per_second','Measured throughput (advisories/sec)')]:
        if metric in frame:
            px.bar(frame,x='configuration',y=metric,title=title).write_html(root/f'{metric}.html',include_plotlyjs=True)
    print(frame[['configuration','p95_latency_ms','throughput_per_second','docker_memory_mib_max','meets_target']].to_string(index=False))
if __name__=='__main__': report()
