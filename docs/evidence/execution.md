# Actual execution evidence - 10 October 2026

Implemented and verified: Streamlit dashboard, advisory form, analytics/history, farm selection and cloud results view; 3,000 synthetic scenarios; saved Random Forest; six fictional farmers and 30 plots; 90 seeded synthetic demonstration advisories. Manual advisory form submission was tested in an isolated SQLite database.

Final Windows tests: **24 passed in 39.55 seconds**. Docker full-suite tests: **24 passed in 33.70 seconds**. After the final text/documentation packaging changes, the running final container dashboard and measured-results view also passed smoke checks. See tests.txt. AppTest renders all five views; the Cloud Experiments view also rendered successfully after measured CSVs were generated. This is functional testing, not visual browser inspection.

Actual synthetic held-out evaluation: **MAE 1.74366**, **RMSE 2.19596**, **R2 0.99092**; persistence baseline MAE 7.05094. Units for MAE/RMSE are moisture percentage points. 2,400 training and 600 test scenarios, grouped by plot. See model_metrics.json. These results describe the synthetic generator only.

Docker: image built successfully; the full container suite passed all 24 tests and the final packaged container passed dashboard/results smoke checks. The demo container was recreated from the verified image, retaining canewise-data. The final packaged demo mounts cloud/results read-only so measured results display in its Cloud Experiments view. Port 8501 /_stcore/health returned ok; local Streamlit on port 8502 also returned ok. Actual image metadata, container health and startup logs are in docker_image.json, docker_health.txt and docker_logs.txt. PowerShell wraps the stderr startup message as NativeCommandError in the saved logs; the service itself started successfully.

## Experiment 7: actual resource results

Fixed 100-input workload, four workers, five-second warmup, approximately 30-second measured interval per configuration. Each operation validates, predicts, applies rules and writes SQLite. This is core advisory latency, not browser response time. Final sequence ran after builds and verification tests completed; it remains a single run on a shared local machine.

| Config | CPUs | RAM allocation (MB) | p95 (ms) | Throughput (/s) | Errors | Docker CPU mean (%) | Docker RAM peak (MiB) | Target met |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| A | 1 | 512 | 1680.80 | 7.57 | 0 | 91.93 | 220.00 | No |
| B | 2 | 1024 | 1642.39 | 9.44 | 0 | 104.88 | 217.00 | No |
| C | 4 | 2048 | 1745.71 | 6.30 | 0 | 112.95 | 212.90 | No |

Target fixed before testing: p95 <=250 ms, zero errors, throughput >=10/s. **No configuration meets it.** B has the best latency/throughput in this run, but is not a qualifying recommendation. Larger limits did not consistently improve measured performance. Profiling and repeat measurement are required before selecting resources for that target. All configurations ran without workload errors.

Raw evidence: cloud/results/A.json, B.json, C.json; timestamped Docker Stats CSVs, benchmark logs, container logs and docker_info.txt. Comparison: cloud/results/comparison.csv. Four standalone HTML charts summarize CPU, RAM, p95 and throughput. Docker CPU% is relative to one host core and may exceed 100%; Docker memory usage is distinct from process RSS. Process/host metadata are in each JSON. Docker VM reports 12 logical CPUs and ~7.58 GB RAM; Windows baseline reports 12 CPUs and ~15.65 GB RAM.

The Windows Docker exec client stalled after the first workload completed. That initial attempt was interrupted and excluded from final comparisons. The host script now bounds client waits and uses the completed container JSON as evidence. Temporary benchmark containers from the final run were removed.

## Experiment 8: explicit hypothetical cost estimate

Compute estimate = assumed hourly price * 730 hours. Prices are classroom assumptions dated 2026-10-10, not provider quotations or billing. Storage, transfer, tax and other charges excluded.

| Config | Assumed hourly USD | Estimated monthly USD | Qualifies |
|---|---:|---:|---|
| A | 0.025 | 18.25 | No |
| B | 0.050 | 36.50 | No |
| C | 0.100 | 73.00 | No |

See cloud/results/finops.csv, cost_comparison.html and latency_comparison.html. No compliant lowest-cost option can be recommended from this measurement.

## Remaining manual actions

- Supply and review the two reference PDFs; verify assignment-specific requirements and KJS-AGR-01 page 5 layout. Neither PDF was in the supplied attachment folder.
- Execute CloudAnalyst configurations and collect genuine simulator results/screenshots. No simulation results were fabricated.
- Capture dashboard, advisory, Docker and charts screenshots from the real application. Browser runtime reported no available browser; visual QA was not performed.
- Publish to Docker Hub only if wanted, using your account. No image push or real cloud billing was performed.

Technical references: [Streamlit AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest), [Random Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html), [Docker Stats](https://docs.docker.com/reference/cli/docker/container/stats/).
