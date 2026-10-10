# Experiment 6 - CloudAnalyst
Aim: simulate hypothetical farmer traffic to the irrigation app; assess response and data-center processing time. Tools: CloudAnalyst desktop and Java required by your distribution. No real simulation results are included until that program is run.

Use cloud/cloudanalyst/scenarios.csv. Registered farmers are NOT active sessions. Peak concurrent farmers = 10% registered; off peak = 2%; 12 requests per active user per hour and 2 KB per request. These are classroom assumptions. Peak is 08:00-10:00 in simulator time; document timezone conversion. Run 24 simulated hours.

1. Open CloudAnalyst Configure Simulation. Create one user base UB1 in region 3 (Asia). Enter peak/off-peak active users from the selected scenario, requests/hour 12, request size 2048 bytes and peak interval above. Registered users are recorded in the report only.
2. Define DC1 in region 3: 4 physical machines each 4 processors * 1000 MIPS, 8192 MB RAM, 1 TB storage and 10000 Mbps bandwidth. Time-shared policy, x86/Linux/Xen if these fields are present.
3. Deploy 1, 2 or 4 application VMs from the scenario table. Each VM: 1 CPU, 1000 MIPS, 1024 MB RAM, 100 Mbps bandwidth, 10000 MB storage. Request instruction length: 10000 MI, explicitly hypothetical and not calibrated from wall-clock Python latency.
4. Choose Closest Data Center service broker and Round Robin VM load balancer. Keep network latency/bandwidth matrix at defaults and record the actual defaults. Run all three workloads with 1, 2 and 4 VMs (nine comparisons), holding everything else fixed. Respect host capacities.
5. Save each configuration from the GUI; record simulator version and configuration file. Run simulation, export/screenshot overall response time, DC processing time, per-hour graphs and cost output where available.
6. Compare mean/min/max response and processing times; explain queuing and network differences. Do not equate simulation response time with the measured core benchmark. If displayed, use assumed VM cost $0.05/hour, storage $0.10/GB/month and transfer $0.01/GB; record simulator unit conversion and exclude costs if unsupported.

Actual results: PENDING manual execution. CloudAnalyst versions differ; map GUI field labels and instructor-required settings explicitly. The absent assignment PDF may require changes. Cost and CPU usage must only be reported if the installed simulator actually provides them.

Record the Advanced-tab user grouping and request grouping factors; where supported set both to 1 for this small prototype and hold them fixed across runs. Record the random seed or simulator repeatability settings if available. Region mapping background: [original CloudAnalyst research report](https://www.buyya.com/reports/CloudAnalyst2009.pdf).
