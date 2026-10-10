import argparse, json, subprocess, time
from pathlib import Path
import pandas as pd

CONFIGS=[('A',1,'512m',512),('B',2,'1g',1024),('C',4,'2g',2048)]

def docker(*args): return subprocess.check_output(['docker',*args],text=True,timeout=120)

def run(seconds=30):
    root=Path('cloud/results');root.mkdir(parents=True,exist_ok=True);reports=[]
    (root/'docker_info.txt').write_text(docker('info'),encoding='utf-8')
    for label,cpus,memory,mb in CONFIGS:
        name=f'canewise-bench-{label.lower()}'
        docker('run','-d','--name',name,'--cpus',str(cpus),'--memory',memory,'sugarcane-irrigation')
        try:
            # Readiness: confirm the actual Streamlit health endpoint.
            for attempt in range(60):
                check=subprocess.run(['docker','exec',name,'python','-c',"import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')"],capture_output=True)
                if check.returncode==0: break
                time.sleep(1)
            else: raise RuntimeError(f'{name} did not become ready')
            docker('exec',name,'python','-m','cloud.benchmark','--seconds','5','--output','/tmp/warmup.json')
            task=subprocess.Popen(['docker','exec',name,'python','-m','cloud.benchmark','--seconds',str(seconds),'--output','/tmp/benchmark.json'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            stats=[]
            client_deadline=time.monotonic()+seconds+60
            while task.poll() is None and time.monotonic()<client_deadline:
                sample=json.loads(docker('stats','--no-stream','--format','{{json .}}',name))
                sample['sampled_at_utc']=pd.Timestamp.now(tz='UTC').isoformat()
                stats.append(sample)
            if task.poll() is None:
                task.terminate()
            stdout,stderr=task.communicate(timeout=15)
            (root/f'{label}_benchmark.log').write_text(stdout+stderr,encoding='utf-8')
            # The container JSON is authoritative if the Windows exec client fails after completion.
            report=json.loads(docker('exec',name,'cat','/tmp/benchmark.json'))
            pd.DataFrame(stats).to_csv(root/f'{label}_docker_stats.csv',index=False)
            report.update(configuration=label,cpu_allocation=cpus,memory_allocation_mb=mb,
                          docker_cpu_percent_mean=sum(float(s['CPUPerc'].strip('%')) for s in stats)/len(stats) if stats else None)
            report['meets_target']=report['p95_latency_ms'] is not None and report['p95_latency_ms']<=250 and report['error_rate']==0 and report['throughput_per_second']>=10
            reports.append(report)
            (root/f'{label}.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
            (root/f'{label}_container.log').write_text(docker('logs',name),encoding='utf-8')
        except Exception as exc:
            reports.append(dict(configuration=label,cpu_allocation=cpus,memory_allocation_mb=mb,meets_target=False,p95_latency_ms=None,error_rate=1,throughput_per_second=0,failure=str(exc)))
        finally: docker('rm','-f',name)
    pd.DataFrame(reports).to_csv(root/'comparison.csv',index=False)
    print(pd.DataFrame(reports).to_string(index=False))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seconds',type=int,default=30);run(p.parse_args().seconds)
