# Experiment 8 - FinOps
Aim: compare the three resource configurations using Experiment 7 measurements and explicit cost assumptions.

```powershell
python -m cloud.finops --hours 730
```
cloud/finops_prices.csv contains hypothetical classroom prices dated 2026-10-10: A $0.025/hour, B $0.05/hour, C $0.10/hour. They are NOT cloud-provider quotations or billing records. Monthly compute estimate = hourly price * operation hours. Storage, network, tax, support and free tier are excluded; quote them separately when applicable.

The script joins each resource measurement to its price, preserves target compliance and recommends the lowest assumed-cost compliant option. Outputs: cloud/results/finops.csv, cost_comparison.html and latency_comparison.html. Failed configurations remain ineligible. If a real provider comparison is required, replace assumptions with dated official region/OS/instance-specific quotations; retain source URL and CPU/RAM mapping. Docker limits do not establish provider instance equivalence.

Evidence: measured CSV, cost formula, price source/date, charts, compliant-option reasoning. Actual cloud billing: not performed. Report actual measurements and estimated costs in separate columns.
