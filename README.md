# CaneWise - Smart Sugarcane Irrigation Advisory System

An undergraduate AI and cloud computing prototype: Streamlit dashboard, synthetic agricultural scenarios, Random Forest next-day moisture prediction, explainable irrigation rules and persistent SQLite history. **All farm records and training data are fictional/synthetic. Model predictions are not scientifically validated agricultural advice.**

## Reference and assignment mapping
The supplied master prompt maps KJS-AGR-01 to farmer/plot context, environmental monitoring, irrigation advisory and trends. Cloud experiments 2, 6, 7 and 8 map to containerization, simulation, right-sizing and FinOps. **Neither reference PDF was attached.** The actual assignment manual and page 5 screenshot must be reviewed when supplied; additional requirements may change this implementation. No KIAAR/GBL observations or measured yield/water savings are claimed.

## Problem and objectives
Show how a student-sized application can turn soil moisture, temperature, humidity, forecast rainfall, soil and sugarcane stage into a transparent irrigation advisory; preserve decisions and demonstrate the deployment/resource/cost tradeoffs of the same application.

## Features and stack
Python 3.11+, Streamlit, Pandas/NumPy, scikit-learn, Joblib, Plotly and SQLite. Farmer dashboard; fictional farm/plot selection; validated advisory form; four advisory states; next-date estimation; optional assumption-driven irrigation duration; low-moisture, heat, forecast rain and overdue alerts; filtered scenario/history charts and CSV export; held-out prediction metrics and feature importance; cloud procedures and measured-results display.

## Folder structure
```text
app.py                      Streamlit application (five sidebar views)
config/                     Portable paths and illustrative thresholds
services/                   Synthetic generator, validation, rules
database/db.py              SQLite schema, seed records and history
models/                     Training, prediction, model artifact and metrics
data/                       Dataset, held-out predictions, feature importance, SQLite
scripts/                    Setup and standalone dataset generation
cloud/                      Benchmark, Docker right-sizing, FinOps
  cloudanalyst/             Reproducible hypothetical scenario table
  results/                  Actual generated measurements and charts
tests/                      Unit and Streamlit integration tests
docs/                       Architecture, implementation, reports and demo
Dockerfile, .dockerignore   Non-root container with health check
```

## Architecture and methodology
Browser -> Streamlit -> validation -> saved ML pipeline -> configurable advisory rules -> SQLite. Analytics use synthetic CSV and saved history. See [architecture](docs/architecture.md) and [data/model assumptions](docs/implementation.md).

Dataset: 3,000 independent daily scenarios across 30 plots, fixed seed 42. Transparent temperature/humidity/soil/stage loss and forecast infiltration rules generate the next-day target with Gaussian noise. Scenarios are not a continuous physical simulation. A grouped split holds out six entire plots. Categories are encoded inside the fitted pipeline, preventing preprocessing leakage. Targets, irrigation labels, IDs and timestamps are excluded from prediction inputs. Metrics and persistence-baseline MAE are written to models/metrics.json after actual training. High synthetic R2 demonstrates learning this generator, not real-world accuracy.

## Windows installation and local execution
From the repository root in PowerShell:
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m scripts.setup
.\.venv\Scripts\python.exe -m streamlit run app.py
```
If Python 3.11 is not installed, use `python -m venv .venv` with an installed Python >=3.11. Open http://localhost:8501. Using the venv executable avoids PowerShell activation-policy changes. Setup is idempotent: it generates missing assets, retrains if the sklearn version differs, and seeds history only if empty. No model training happens during normal form submissions.

Regenerate/retrain deliberately:
```powershell
python -m scripts.generate_dataset
python -c "from models.train_model import train; print(train())"
```
Restart Streamlit after retraining so its cached predictor reloads. Use a trusted locally generated Joblib model; package versions must match. Docker retrains inside its own environment to avoid host/container sklearn incompatibility. Runtime database can be redirected with `$env:CANEWISE_DB = 'data/my-demo.sqlite'`.

## Docker and cloud experiments
```powershell
docker build -t sugarcane-irrigation .
docker run -d --name canewise-demo -p 8501:8501 -v canewise-data:/app/data sugarcane-irrigation
docker ps
docker logs canewise-demo
```
See [Experiment 2](docs/experiment_2.md) for health verification, actual screenshots and optional Docker Hub publication; [Experiment 6](docs/experiment_6.md) for CloudAnalyst configuration; [Experiment 7](docs/experiment_7.md) for resource monitoring; [Experiment 8](docs/experiment_8.md) for cost estimates.

```powershell
python -m cloud.benchmark --seconds 30
python -m cloud.right_size --seconds 30
python -m cloud.report
python -m cloud.finops --hours 730
```
Right-sizing assumes a built `sugarcane-irrigation` image and running Docker Desktop. Its temporary benchmark containers are removed after evidence collection. Results measure core inference/rules/database latency, not complete browser response latency. Docker Stats additionally measures whole-container resources. Configuration A/B/C target: p95 <=250 ms, zero errors and >=10 operations/sec. Local Docker resource caps are not calibrated cloud instance performance. FinOps uses explicitly hypothetical dated prices; no real provider billing is claimed. Raw measurements, errors and target compliance are preserved. CloudAnalyst requires manual GUI simulation; no screenshots or simulator outputs are fabricated.

## Tests
```powershell
python -m pytest -q
```
Tests cover validation boundaries/missing values, low/high moisture, rain deferral and critical override, output structure, missing model, repeatable predictions, disjoint plot groups, persistence baseline, duration assumptions, SQLite retrieval, all Streamlit views and saved form submission.

## Evidence, report and demonstration
[Report template](docs/report_template.md), [five-minute demo](docs/demo.md), and docs/evidence/execution.md record verified results and outstanding actions. Actual test/model/container evidence should be shown separately from hypothetical assumptions. Capture screenshots from your real local browser, Docker and CloudAnalyst runs.

## Limitations and future scope
Synthetic generator and illustrative thresholds cannot establish agronomic reliability. Forecast is manually entered; no live sensors/weather, authentication, actuator control, alerts outside the app or field-calibrated water requirement exists. Scenario plots are independent rather than longitudinal. Next dates extrapolate only one day and ignore future uncertainty. Future work: supplied-PDF alignment, expert-calibrated soil/crop thresholds, real sensor/weather data with consent, field validation, temporal evaluation and genuine browser load testing.
