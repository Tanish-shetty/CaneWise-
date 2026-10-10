# Architecture and reduced scope
Browser -> Streamlit -> validation -> saved Random Forest pipeline -> advisory rules -> SQLite.
Streamlit reads CSV synthetic scenarios and test predictions for Plotly analytics. SQLite stores fictional farmers, plots and manual/seeded advisories. No paid APIs, pumps, live weather, real sensors or external authentication.

Core workload -> Docker resource limits -> Docker Stats + latency/error/throughput records -> FinOps assumed-price comparison. CloudAnalyst is a separate hypothetical deployment simulation, not a measurement of this Python model.

Reference review pending: neither PDF was supplied. The prompt is the sole current source for requirements. Page 5 visual conformity and additional experiment-manual requirements cannot be certified.
