# Operational Fragility Modeling Framework for Industrial Supply Chains

**CS4982 Senior Project — Winter 2026**  
**Author:** Malek Karoui  
**Supervisor:** Professor Chris Baker  
**University of New Brunswick (Saint John)**

---

## Overview

Industrial supply chains increasingly behave like **interdependent networks** rather than linear chains. This project provides a reproducible framework to quantify **cascading operational fragility** using:

- **Directed dependency graphs** (NetworkX)
- **Monte Carlo cascading-failure simulation** (BFS propagation)
- **Stress scenarios** derived from the World Bank **Global Supply Chain Stress Index (GSCSI)**
- Node-level **Fragility Index** scoring
- A comparative study across multiple network coupling levels (density variants)
- An interactive **Streamlit dashboard** for exploration

The primary output is a **Fragility Index** \(F(v)\): the expected fraction of the network disrupted when node \(v\) fails.

\[
F(v) = \frac{1}{N}\sum_{i=1}^{N}\frac{C_i(v)}{|V|-1}
\]

Where:
- \(C_i(v)\) is the number of downstream nodes affected in simulation trial \(i\)
- \(N\) is the number of Monte Carlo trials (default: 500)
- \(|V|\) is the number of nodes in the graph

---

## Repository Structure

```text
cs4982-fragility/
├── src/                        # Core modules (library)
│   ├── config.py               # paths + parameters
│   ├── supplygraph_loader.py   # SupplyGraph CSV → DiGraph
│   ├── gcsi_loader.py          # GSCSI stress model
│   ├── kaggle_loader.py        # Kaggle CSV → layered DiGraph
│   ├── fragility.py            # Monte Carlo cascade engine
│   ├── visualize.py            # Plotly + Matplotlib figures
│   └── dashboard.py            # Streamlit dashboard
│
├── scripts/                    # Executable entry points
│   ├── compare_networks.py     # 4-case comparative study (density variants)
│   ├── run_pipeline.py         # single-network pipeline (SupplyGraph)
│   ├── run_diagnostics.py      # convergence / diagnostics
│   └── run_kaggle_analysis.py  # Kaggle operational graph analysis
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
├── run_project.bat             # Windows menu runner
├── requirements.txt
└── README.md
Quick Start (Windows)
Option 1 — Menu runner (recommended)
cmd

run_project.bat
Option 2 — Manual commands
cmd

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

python scripts\compare_networks.py
streamlit run src\dashboard.py
How to Run
1) Comparative density study (recommended)
Runs Sparse / Medium / Dense / Original network variants under low/medium/high stress.

Bash

python scripts/compare_networks.py
Outputs:

results/network_comparison.csv
figures/comparison/*.png
per-case fragility CSVs in results/
2) Single benchmark pipeline (SupplyGraph only)
Bash

python scripts/run_pipeline.py
Outputs:

fragility CSVs under results/
figures under figures/ (depending on pipeline configuration)
3) Kaggle operational supply chain analysis
Builds a layered operational graph: Supplier → SKU → Customer segment.

Bash

python scripts/run_kaggle_analysis.py
Outputs:

results/fragility_kaggle_low.csv
results/fragility_kaggle_medium.csv
results/fragility_kaggle_high.csv
results/kaggle_summary.csv
4) Diagnostics / convergence test
Bash

python scripts/run_diagnostics.py
Outputs:

results/convergence_test.csv
5) Streamlit dashboard
Bash

streamlit run src/dashboard.py
The dashboard reads results from results/ and provides:

Overview (distribution + top-k nodes)
Network heatmap (interactive Plotly)
Node Explorer (stress sensitivity per node)
Convergence (if available)
Stress curve (system-wide)
Method Summary
Graph + propagation model
Nodes represent supply-chain assets (anonymized SupplyGraph labels)
Directed edges represent dependency links (failure propagates downstream)
Each edge has a probability weight derived from min–max normalization into:
[
0.10
,
0.65
]
[0.10,0.65]
Stress scenarios (GSCSI)
Low / medium / high stress multipliers are derived from percentiles of the GSCSI distribution (33rd/50th/66th). These multipliers scale edge propagation probabilities.

Monte Carlo simulation
For each seed node and stress level, the cascade simulation runs 
N
N trials (default 500) to estimate expected downstream impact.

Core Results (from compare_networks.py)
SupplyGraph benchmark (Original)
Nodes: 40
Edges: 879
Density: 0.5635
Comparative findings (mean fragility)
The comparative study evaluates structural coupling by controlled edge removal (density variants):

Case	Density	Low Mean F	High Mean F	Amplification
Sparse	0.15	0.1017	0.6254	6.15×
Medium	0.30	0.4114	0.6343	1.54×
Dense	0.45	0.5680	0.6418	1.13×
Original	0.5635	0.6001	0.6435	1.07×
Key interpretation:

Sparse networks are relatively safe under calm conditions but highly stress-sensitive.
Dense networks are structurally fragile even under low stress (stress adds little additional fragility).
Data Sources
SupplyGraph benchmark dataset (CIOL Research Lab, 2024)
Synthetic multi-tier supply chain dependency graph (node.csv + edge.csv)

World Bank GSCSI (Global Supply Chain Stress Index, 2024)
Used to derive stress scenario multipliers from empirical percentiles

Kaggle Supply Chain Operations dataset (2024)
Used to build a sparse operational graph (Supplier → SKU → Customer segment)

Configuration
All paths and parameters are centralized in:

src/config.py
Key parameters:

RANDOM_SEED = 42
DEFAULT_N_CASCADES = 500
WEIGHT_MIN = 0.10
WEIGHT_MAX = 0.65
GCSI_LOW_PERCENTILE = 33
GCSI_HIGH_PERCENTILE = 66
Troubleshooting
Run all commands from the project root (where src/, scripts/, data/ exist).
If the dashboard shows no results, run:
Bash

python scripts/compare_networks.py
or
Bash

python scripts/run_pipeline.py
If Streamlit warns about deprecated use_container_width, it is safe to ignore (cosmetic).
(You can replace use_container_width=True with width="stretch".)
Suggested Citation
bibtex

@misc{karoui2026fragility,
  author  = {Malek Karoui},
  title   = {Operational Fragility Modeling Framework for Industrial Supply Chains},
  year    = {2026},
  note    = {CS4982 Senior Project, University of New Brunswick}
}
Contact: malek.karoui@unb.ca
