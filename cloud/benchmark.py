"""Fixed-duration core advisory workload; excludes browser/WebSocket latency."""
import argparse, json, platform, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import Thread, Event
import numpy as np
import pandas as pd
import psutil
from config.settings import DATA, FEATURES
from models.predictor import Predictor
from services.advisory_engine import advise
from database.db import initialize, save

def run(seconds=30, workers=4, output=Path('cloud/results/local.json')):
    model=Predictor()
    inputs=pd.read_csv(DATA/'synthetic_agriculture.csv').head(100).to_dict('records')
    output.parent.mkdir(parents=True,exist_ok=True)
    db=output.parent/'benchmark.sqlite'
    initialize(db)
    process=psutil.Process(); samples=[]; stop=Event()
    def monitor():
        process.cpu_percent(None)
        while not stop.wait(.5): samples.append((process.cpu_percent(None),process.memory_info().rss/1024**2))
    thread=Thread(target=monitor,daemon=True); thread.start()
    deadline=time.perf_counter()+seconds
    def workload(worker):
        latencies=[]; errors=0; i=worker
        while time.perf_counter()<deadline:
            row=inputs[i%len(inputs)]; values={f:row[f] for f in FEATURES}; start=time.perf_counter()
            try:
                result=advise(values,model.predict(values))
                save(row['plot_id'],values,result,model.metadata['version'],source='benchmark',path=db)
                latencies.append((time.perf_counter()-start)*1000)
            except Exception: errors+=1
            i+=workers
        return latencies,errors
    start=time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as pool: results=list(pool.map(workload,range(workers)))
    elapsed=time.perf_counter()-start; stop.set(); thread.join()
    latencies=[v for r,_ in results for v in r]; errors=sum(e for _,e in results)
    count=len(latencies)+errors
    report=dict(workload='validate + RF inference + rules + SQLite insert; not HTTP response time',
        seconds=elapsed, workers=workers, attempts=count, errors=errors,
        error_rate=errors/count if count else 1, throughput_per_second=len(latencies)/elapsed,
        p95_latency_ms=float(np.percentile(latencies,95)) if latencies else None,
        mean_latency_ms=float(np.mean(latencies)) if latencies else None,
        process_cpu_percent_mean=float(np.mean([x[0] for x in samples])) if samples else None,
        process_rss_mb_max=max([x[1] for x in samples],default=None),
        platform=platform.platform(),python=platform.python_version(),host_logical_cpus=psutil.cpu_count(),
        host_memory_gb=round(psutil.virtual_memory().total/1024**3,2),model_version=model.metadata['version'])
    output.write_text(json.dumps(report,indent=2),encoding='utf-8'); print(json.dumps(report,indent=2))
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--seconds',type=int,default=30); p.add_argument('--workers',type=int,default=4); p.add_argument('--output',type=Path,default=Path('cloud/results/local.json')); a=p.parse_args()
    if a.seconds<1 or a.workers<1: p.error('positive duration and workers required')
    run(a.seconds,a.workers,a.output)
