# Operational Fragility Modeling Framework for Industrial Supply Chains

**CS4982 Senior Project — Winter 2026**  
**Author:** Malek Karoui  
**Supervisor:** Professor Chris Baker  
**Institution:** University of New Brunswick (Saint John)

A reproducible Python framework that quantifies **cascading operational fragility** in industrial supply chains using **directed dependency graphs**, **Monte Carlo simulation**, and **stress scenarios** derived from the World Bank **Global Supply Chain Stress Index (GSCSI)**. The project also includes a comparative study across network coupling levels (density variants), an additional Kaggle operational case, and an interactive Streamlit dashboard.

---

## Table of Contents

- [Project Summary](#project-summary)
- [Method Overview](#method-overview)
  - [Fragility Index](#fragility-index)
  - [Stress Scenarios (GSCSI)](#stress-scenarios-gscsi)
  - [Cascade Model](#cascade-model)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [Quick Start (Recommended)](#quick-start-recommended)
- [How to Run](#how-to-run)
  - [Comparative Density Study](#1-comparative-density-study)
  - [Single-Network Pipeline (SupplyGraph)](#2-single-network-pipeline-supplygraph)
  - [Diagnostics / Convergence](#3-diagnostics--convergence)
  - [Kaggle Operational Graph Analysis](#4-kaggle-operational-graph-analysis)
  - [Dashboard](#5-dashboard)
- [Outputs](#outputs)
- [Key Results (Comparative Study)](#key-results-comparative-study)
- [Configuration](#configuration)
- [Data Sources](#data-sources)
- [Reproducibility](#reproducibility)
- [Troubleshooting](#troubleshooting)
- [Citation](#citation)
- [Acknowledgments](#acknowledgments)
- [Contact](#contact)

---

## Project Summary

Modern industrial supply chains behave like **interdependent networks**, not linear supplier chains. A local disruption can propagate through dependency links and trigger **cascading operational failure**. Traditional supplier-by-supplier risk scores do not capture this systemic behavior.

This project provides an end-to-end workflow to:
- Load supply chain datasets from CSV
- Construct a directed dependency graph (NetworkX)
- Parameterize low/medium/high stress scenarios using GSCSI percentiles
- Simulate cascading failures via Monte Carlo methods
- Compute a node-level Fragility Index for every asset
- Visualize and compare fragility across multiple network structures
- Explore results interactively using Streamlit

---

## Method Overview

### Fragility Index

For a node `v`, fragility is estimated as the expected fraction of the network impacted when `v` fails:

```text
F(v) = (1/N) * Σ [ C_i(v) / (|V| - 1) ]
Where:

C_i(v) = number of downstream nodes affected in Monte Carlo trial i
N = number of trials (default: 500)
|V| = number of nodes in the graph
Interpretation: F(v) is the expected fraction of the network disrupted by failure of v.
Stress Scenarios (GSCSI)
Stress multipliers are derived from the empirical GSCSI distribution using percentile regimes:

Low: ~33rd percentile
Medium: ~50th percentile
High: ~66th percentile
These multipliers scale propagation probabilities during cascade simulation.

Cascade Model
Cascades propagate downstream using a breadth-first (BFS) process:

Seed node fails
For each failed node u, each successor v fails with probability:
text

p(u,v) = min(1, weight(u,v) * stress_multiplier)
Edge weights are min–max normalized into a bounded probability range (default [0.10, 0.65]).

Repository Structure
text

cs4982-fragility/
├── src/                        # Core modules (library)
│   ├── config.py               # central parameters + paths
│   ├── supplygraph_loader.py   # SupplyGraph CSV → DiGraph
│   ├── gcsi_loader.py          # GSCSI stress model
│   ├── kaggle_loader.py        # Kaggle CSV → layered DiGraph
│   ├── fragility.py            # Monte Carlo cascade engine
│   ├── visualize.py            # Plotly + Matplotlib figures
│   └── dashboard.py            # Streamlit dashboard
│
├── scripts/                    # Executable entry points
│   ├── compare_networks.py     # sparse/medium/dense/original comparison
│   ├── run_pipeline.py         # single-network pipeline (SupplyGraph)
│   ├── run_diagnostics.py      # convergence / diagnostics
│   └── run_kaggle_analysis.py  # Kaggle operational case
│
├── data/                       # Input datasets
│   ├── node.csv
│   ├── edge.csv
│   ├── gcsi.csv
│   └── kaggle_supplychain/
│       └── supply_chain_data.csv
│
├── results/                    # Generated CSV outputs
├── figures/                    # Generated plots (PNG)
├── run_project.bat             # Windows menu runner (recommended)
├── requirements.txt
└── README.md
Installation
Option A (Windows, recommended): menu runner
The menu runner creates/activates a local virtual environment and installs dependencies automatically.

cmd

run_project.bat
Option B: manual setup
cmd

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
Quick Start (Recommended)
Run the comparative study:
cmd

python scripts\compare_networks.py
Launch the dashboard:
cmd

streamlit run src\dashboard.py
How to Run
1) Comparative density study
Runs Sparse / Medium / Dense / Original variants under low/medium/high stress.

cmd

python scripts\compare_networks.py
2) Single-network pipeline (SupplyGraph)
Runs the baseline pipeline on the original SupplyGraph benchmark.

cmd

python scripts\run_pipeline.py
3) Diagnostics / convergence
Runs validation tests and convergence checks.

cmd

python scripts\run_diagnostics.py
4) Kaggle operational graph analysis
Builds a layered operational graph: Supplier → SKU → Customer segment.

cmd

python scripts\run_kaggle_analysis.py
5) Dashboard
Launch the interactive Streamlit UI:

cmd

streamlit run src\dashboard.py
Outputs
After running the scripts, outputs are written to:

results/ (CSV)
Typical files include:

network_comparison.csv (comparative density study summary)
fragility_*_low.csv, fragility_*_medium.csv, fragility_*_high.csv (node-level fragility per scenario)
convergence_test.csv
fragility_kaggle_low.csv, fragility_kaggle_medium.csv, fragility_kaggle_high.csv
kaggle_summary.csv
figures/ (PNG)
Typical figure folders:

figures/comparison/ (density vs fragility, mean/max fragility, stress amplification)
figures/heatmaps/ (network heatmaps)
figures/histograms/ (fragility distributions)
figures/topk/ (top-k nodes)
figures/convergence/ (convergence plots)
Key Results (Comparative Study)
The comparative study evaluates how structural coupling (density) shapes fragility.

SupplyGraph benchmark (Original):

Nodes: 40
Edges: 879
Density: 0.5635
Mean fragility (example from compare_networks.py):

Case	Density	Low Mean F	High Mean F	Amplification (High/Low)
Sparse	0.15	0.1017	0.6254	6.15×
Medium	0.30	0.4114	0.6343	1.54×
Dense	0.45	0.5680	0.6418	1.13×
Original	0.5635	0.6001	0.6435	1.07×
Interpretation:

Sparse networks can be robust under low stress but highly stress-sensitive.
Dense networks can be inherently fragile even under low stress (topology dominates).
Configuration
All tunable parameters and file paths are centralized in:

src/config.py
Common parameters:

RANDOM_SEED
DEFAULT_N_CASCADES (Monte Carlo trials per node)
WEIGHT_MIN, WEIGHT_MAX (edge propagation probability bounds)
GCSI_LOW_PERCENTILE, GCSI_HIGH_PERCENTILE
output directories (RESULTS_DIR, FIGURES_DIR)
dataset paths (NODE_CSV, EDGE_CSV, GCSI_CSV, KAGGLE_CSV)
Data Sources
SupplyGraph benchmark dataset (CIOL Research Lab, 2024)
Synthetic multi-tier supply chain dependency network (node/edge CSV).

World Bank GSCSI (Global Supply Chain Stress Index, 2024)
Used to derive stress scenario multipliers.

Kaggle Supply Chain Operations dataset (2024)
Used to build an additional sparse operational case graph.

Reproducibility
Centralized configuration in src/config.py
Controlled random seed (default: 42)
Deterministic structure generation for density variants (within scripts)
Explicit CSV and figure outputs saved under results/ and figures/
Troubleshooting
Run everything from the repository root (where src/, scripts/, data/ exist).

If the dashboard shows no data:

cmd

python scripts\compare_networks.py
or:

cmd

python scripts\run_pipeline.py
If you see Streamlit warnings about deprecated layout arguments, they are cosmetic and do not affect correctness.
## References

- Buldyrev, S. et al. (2010). Catastrophic cascade of failures. Nature.
- Gao, J. et al. (2016). Universal resilience patterns. Nature.
- Helbing, D. (2013). Globally networked risks. Nature.
- Motter, A. and Lai, Y.-C. (2002). Cascade-based attacks. Physical Review E.
- Watts, D. (2002). Global cascades on random networks. PNAS.
- World Bank (2024). Global Supply Chain Stress Index.
- SupplyGraph Dataset (2024).
- IEEE DataPort (2024). PowerCascade Dataset.

---
Acknowledgments
CIOL Research Lab — SupplyGraph benchmark dataset
World Bank — GSCSI data
Kaggle — supply chain operations dataset
Python ecosystem: NetworkX, Pandas, NumPy, Plotly, Streamlit
Contact
Malek Karoui
malek.karoui@unb.ca
