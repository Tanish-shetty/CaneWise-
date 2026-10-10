# Experiment 7 - Resource right-sizing
Aim: select the smallest resource limit meeting an explicit prototype performance target. Tools: Docker Stats, Python benchmark, SQLite.

```powershell
python -m cloud.right_size --seconds 30
```
This creates isolated A (1 CPU/512 MB), B (2 CPU/1 GB), C (4 CPU/2 GB) containers, verifies Streamlit health, warms up 5 seconds, and performs the same 30-second closed-loop workload with four workers and 100 fixed synthetic inputs. Each operation validates, predicts, generates rules and inserts SQLite. Each container uses a separate benchmark DB. Main Streamlit runs concurrently but browser interaction is not included. Containers are removed afterward; outputs are copied before removal.

Target: successful-operation p95 <=250 ms, zero errors and >=10 operations/sec. This is a classroom demonstration target, not a farmer-facing SLA. Different CPU quotas are local Docker constraints, not equivalent cloud instance measurements. A failed/OOM configuration is not compliant. Measure HTTP/browser interaction separately if your manual requires complete service response time.

Results: cloud/results/comparison.csv, per-configuration JSON, raw Docker Stats CSV, container logs and Docker host info. Process CPU% can exceed 100; Docker CPU% uses host-core convention, not percent of allocated quota. Memory RSS is benchmark-process-only; Docker Stats captures whole container memory including Streamlit. Record host hardware, Docker VM limits and background load. Repeat runs if using results for a stronger comparison.

Charts: python -m cloud.report summarizes whole-container memory from raw Docker Stats and creates CPU, memory, latency and throughput HTML charts. python -m cloud.finops adds assumed cost charts. Smallest passing configuration is the right-sizing candidate, conditional on this workload. Do not infer cost savings or yield improvement beyond the measured workload and price assumptions.
