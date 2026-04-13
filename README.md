# Operational Fragility Modeling Framework for Industrial Supply Chains
**CS4982 Senior Project — Winter 2026**  
**Author:** Malek Karoui  
**Supervisor:** Professor Chris Baker  
**Institution:** University of New Brunswick (Saint John)

A reproducible Python framework for quantifying **cascading operational fragility** in industrial supply chains using directed dependency graphs, Monte Carlo simulation, and stress scenarios derived from the **World Bank Global Supply Chain Stress Index (GSCSI)**. The project includes a comparative study across network coupling levels, a Kaggle operational case, and an interactive Streamlit dashboard.

---

## Table of Contents
- [Project Summary](#project-summary)
- [Method Overview](#method-overview)
  - [Fragility Index](#fragility-index)
  - [Stress Scenarios (GSCSI)](#stress-scenarios-gscsi)
  - [Cascade Model](#cascade-model)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [How to Run](#how-to-run)
- [Outputs](#outputs)
- [Key Results (Comparative Study)](#key-results-comparative-study)
- [Configuration](#configuration)
- [Data Sources](#data-sources)
- [Reproducibility](#reproducibility)
- [Troubleshooting](#troubleshooting)
- [References](#references)
- [Acknowledgments](#acknowledgments)
- [Contact](#contact)

---

## Project Summary
Modern industrial supply chains behave as **interdependent networks**, not linear supplier lists. A local disruption can propagate through dependency links and trigger **cascading operational failures**. Traditional supplier‑level risk scores fail to capture this systemic behavior.

This project provides an end‑to‑end workflow to:

- Load supply chain datasets from CSV  
- Construct a directed dependency graph (NetworkX)  
- Parameterize low/medium/high stress scenarios using GSCSI percentiles  
- Simulate cascading failures via Monte Carlo  
- Compute a node‑level **Fragility Index**  
- Compare fragility across multiple network structures  
- Explore results interactively via Streamlit  

---

## Method Overview

### Fragility Index
For a node \(v\), fragility is the expected fraction of the network impacted when \(v\) fails:



\[
F(v) = \frac{1}{N} \sum_i \frac{C_i(v)}{|V| - 1}
\]



Where:

- \(C_i(v)\): number of downstream nodes affected in trial \(i\)  
- \(N\): number of Monte Carlo trials (default: 500)  
- \(|V|\): number of nodes  

**Interpretation:**  
A higher fragility score indicates a node capable of triggering large cascades.

---

### Stress Scenarios (GSCSI)
Stress multipliers are derived from GSCSI percentiles:

| Scenario | Percentile |
|---------|------------|
| Low     | ~33rd      |
| Medium  | ~50th      |
| High    | ~66th      |

These multipliers scale propagation probabilities during cascades.

---

### Cascade Model
Cascades propagate using a BFS‑style process:

1. Seed node fails  
2. For each failed node \(u\), each successor \(v\) fails with probability:



\[
p(u,v) = \min(1,\; \text{weight}(u,v) \cdot \text{stress\_multiplier})
\]



Edge weights are min–max normalized into \([0.10, 0.65]\).

---

## Repository Structure
cs4982-fragility/
├── src/
│   ├── config.py
│   ├── supplygraph_loader.py
│   ├── gcsi_loader.py
│   ├── kaggle_loader.py
│   ├── fragility.py
│   ├── visualize.py
│   └── dashboard.py
│
├── scripts/
│   ├── compare_networks.py
│   ├── run_pipeline.py
│   ├── run_diagnostics.py
│   └── run_kaggle_analysis.py
│
├── data/
│   ├── node.csv
│   ├── edge.csv
│   ├── gcsi.csv
│   └── kaggle_supplychain/
│       └── supply_chain_data.csv
│
├── results/
├── figures/
├── run_project.bat
├── requirements.txt
└── README.md

Code

---

## Installation

### Option A — Windows (Recommended)
Automatically creates a virtual environment and installs dependencies:

```
cmd
run_project.bat
```
Option B — Manual Setup
cmd
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Quick Start
Run the comparative study
cmd
```
python scripts\compare_networks.py
```
Launch the dashboard
```
cmd
streamlit run src\dashboard.py
```
How to Run
1) Comparative density study
```
cmd
python scripts\compare_networks.py
```
3) Single-network pipeline
```
cmd
python scripts\run_pipeline.py
```
5) Diagnostics / convergence
```
cmd
python scripts\run_diagnostics.py
```
7) Kaggle operational graph analysis
```
cmd
python scripts\run_kaggle_analysis.py
```
9) Dashboard
```
cmd
streamlit run src\dashboard.py
```
Outputs
results/ (CSV)
Typical files:

network_comparison.csv

fragility_*_low.csv, fragility_*_medium.csv, fragility_*_high.csv

convergence_test.csv

fragility_kaggle_*.csv

kaggle_summary.csv

figures/ (PNG)
Typical folders:

figures/comparison/

figures/heatmaps/

figures/histograms/

figures/topk/

figures/convergence/

Key Results (Comparative Study)
Case	Density	Low Mean F	High Mean F	Amplification
Sparse	0.15	0.1017	0.6254	6.15×
Medium	0.30	0.4114	0.6343	1.54×
Dense	0.45	0.5680	0.6418	1.13×
Original	0.5635	0.6001	0.6435	1.07×

Interpretation:

Sparse networks: robust under low stress but highly stress‑sensitive

Dense networks: inherently fragile even under low stress

Original network: high baseline fragility; stress amplifies it only slightly

Configuration
All parameters are centralized in:
```
src/config.py
```
Key settings:

RANDOM_SEED

DEFAULT_N_CASCADES

WEIGHT_MIN, WEIGHT_MAX

GCSI_LOW_PERCENTILE, GCSI_HIGH_PERCENTILE

Dataset paths

Output directories

Data Sources
SupplyGraph Benchmark (CIOL Research Lab, 2024)

World Bank GSCSI (2024)

Kaggle Supply Chain Operations Dataset (2024)

Reproducibility
Centralized configuration

Fixed random seed

Deterministic density‑variant generation

Explicit CSV + figure outputs

Troubleshooting
If the dashboard shows no data:
```
cmd
python scripts\compare_networks.py
```
or:
```
cmd
python scripts\run_pipeline.py
```
Streamlit layout warnings are cosmetic.

References
Buldyrev, S. et al. (2010). Catastrophic cascade of failures. Nature.

Gao, J. et al. (2016). Universal resilience patterns. Nature.

Helbing, D. (2013). Globally networked risks. Nature.

Motter, A. & Lai, Y.-C. (2002). Cascade-based attacks. PRE.

Watts, D. (2002). Global cascades on random networks. PNAS.

World Bank (2024). Global Supply Chain Stress Index.

SupplyGraph Dataset (2024).

IEEE DataPort (2024). PowerCascade Dataset.

Acknowledgments
CIOL Research Lab — SupplyGraph dataset

World Bank — GSCSI data

Kaggle — operational dataset

Python ecosystem: NetworkX, Pandas, NumPy, Plotly, Streamlit

Contact
Malek Karoui  
malek.karoui@unb.ca
