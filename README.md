\# Operational Fragility Modeling Framework for Industrial Supply Chains



\*\*CS4982 Senior Project — Winter 2026\*\*

\*\*Author:\*\* Malek Karoui

\*\*Supervisor:\*\* Professor Baker

\*\*University of New Brunswick\*\*



---



\## Overview



This framework quantifies systemic fragility in industrial supply chains using Monte Carlo cascading failure simulations on directed dependency graphs. It integrates the World Bank Global Supply Chain Stress Index (GSCSI) to model low-, medium-, and high-stress scenarios.



The primary output is a \*\*Fragility Index F(v)\*\* — the expected downstream disruption when a specific node fails:

F(v) = (1/N) × Σ C\_i(v)



text





where `C\_i(v)` is the number of nodes affected in simulation trial `i`, and `N` is the total number of Monte Carlo iterations.



---



\## Architecture

Public Data (CSVs)

│

▼

┌──────────────────┐

│ Graph Builder │ ◄── node.csv + edge.csv (SupplyGraph 2024)

│ (NetworkX) │

└────────┬─────────┘

│

▼

┌──────────────────┐ ┌──────────────────┐

│ Monte Carlo │ ◄───│ GSCSI Stress │ ◄── gcsi.csv (World Bank)

│ Simulation │ │ Model │

│ Engine │ └──────────────────┘

└────────┬─────────┘

│

▼

┌──────────────────┐

│ Fragility Index │

│ Computation │

└────────┬─────────┘

│

▼

┌──────────────────┐

│ Visualization │ ──► Plotly (Interactive) + Matplotlib (Static PNGs)

│ Dashboard │ ──► Streamlit Web Interface

└──────────────────┘



text





---



\## Key Results



| Metric | Value |

|--------|-------|

| Total Nodes | 40 |

| Total Edges | 879 |

| Graph Density | 56.35% |

| Monte Carlo Iterations | 500 per node |

| Low Stress Avg Fragility | 60.0% |

| Medium Stress Avg Fragility | 63.7% |

| High Stress Avg Fragility | 64.4% |

| Stress Amplification Factor | 1.07x |



\### Most Critical Nodes (Cascade Sources)



| Node | Role | Fragility (Medium Stress) |

|------|------|--------------------------|

| ATN02K12P | Assembly Terminal Node | 97.4% |

| SOS005L04P | Solvent Supplier | 97.4% |

| SOS500M24P | Solvent Supplier | 97.4% |

| POP002L09P | Polymer Provider | 97.4% |

| SOS003L04P | Solvent Supplier | 97.4% |



\### Isolated Nodes (Zero Fragility)



| Node | Role |

|------|------|

| SO0001L12P | End-of-chain Solvent Output |

| SO0500M24P | End-of-chain Solvent Output |

| MAP1K25P | Final Assembly Part |

| EEA500G12P | Final Electronic Assembly |

| EEA200G24P | Final Electronic Assembly |



---



\## Project Structure

cs4982-fragility/

├── data/

│ ├── node.csv # 40-node SupplyGraph dataset

│ ├── edge.csv # 879 directed dependency edges

│ └── gcsi.csv # World Bank GSCSI monthly values

├── results/ # Generated simulation results

│ ├── fragility\_low.csv

│ ├── fragility\_medium.csv

│ ├── fragility\_high.csv

│ └── convergence\_test.csv

├── figures/ # Generated static figures

│ ├── histograms/

│ ├── heatmaps/

│ └── topk/

├── config.py # Central configuration and parameters

├── supplygraph\_loader.py # Graph construction from CSVs

├── gcsi\_loader.py # GSCSI stress integration module

├── fragility.py # Monte Carlo cascading failure engine

├── visualize.py # Plotly + Matplotlib visualization suite

├── run\_pipeline.py # Full simulation pipeline

├── run\_diagnostics.py # Data and graph validation checks

├── dashboard.py # Streamlit interactive dashboard

├── run\_project.bat # One-click Windows launcher

├── requirements.txt # Python dependencies

└── README.md



text





---



\## Module Descriptions



| Module | Purpose |

|--------|---------|

| `config.py` | Central configuration — all paths, parameters, and constants |

| `supplygraph\_loader.py` | Reads node/edge CSVs, maps integer indices to asset names, builds NetworkX DiGraph |

| `gcsi\_loader.py` | Loads GSCSI data, computes percentile thresholds, provides stress multipliers |

| `fragility.py` | Monte Carlo engine — simulates cascading failures, computes Fragility Index |

| `visualize.py` | Generates interactive Plotly charts and static Matplotlib PNGs |

| `run\_pipeline.py` | Orchestrates full workflow: load → simulate → save → visualize |

| `run\_diagnostics.py` | Validates data integrity, graph structure, and stress model consistency |

| `dashboard.py` | Streamlit web dashboard with 5 interactive tabs |



---



\## Dashboard Tabs



| Tab | Description |

|-----|-------------|

| \*\*Overview\*\* | Summary metrics, fragility histogram, top-K critical nodes |

| \*\*Network Map\*\* | Interactive Plotly graph colored by fragility (hover for details) |

| \*\*Node Explorer\*\* | Per-node stress sensitivity analysis across all scenarios |

| \*\*Convergence\*\* | Monte Carlo convergence verification (stability proof) |

| \*\*Stress Curve\*\* | System-wide stress amplification analysis |



---



\## Data Sources



| Dataset | Description | Source |

|---------|-------------|--------|

| SupplyGraph (2024) | 40-node synthetic supply chain network | \[SupplyGraph Benchmark](https://github.com/SupplyGraph) |

| World Bank GSCSI | Monthly Global Supply Chain Stress Index | \[World Bank](https://www.worldbank.org) |

| PowerCascade | Cascading failure validation sequences | \[IEEE DataPort](https://ieee-dataport.org) |



---



\## Quick Start



\### Prerequisites



\- Python 3.10+

\- pip



\### Installation



```bash

\# Clone the repository

git clone git@github.com:MalekKaroui/cs4982-fragility.git

cd cs4982-fragility



\# Create virtual environment

python -m venv venv



\# Activate (Windows)

venv\\Scripts\\activate



\# Install dependencies

pip install -r requirements.txt

Run

Bash



\# Step 1: Validate data and graph

python run\_diagnostics.py



\# Step 2: Run Monte Carlo simulations

python run\_pipeline.py



\# Step 3: Launch interactive dashboard

streamlit run dashboard.py

Or simply double-click run\_project.bat on Windows.



Simulation Parameters

Parameter	Value	Description

RANDOM\_SEED	42	Reproducibility seed

DEFAULT\_N\_CASCADES	500	Monte Carlo iterations per node

WEIGHT\_MIN	0.10	Minimum edge propagation probability

WEIGHT\_MAX	0.65	Maximum edge propagation probability

BASE\_FAIL\_PROB\_MIN	0.03	Minimum node failure probability

BASE\_FAIL\_PROB\_MAX	0.12	Maximum node failure probability

GCSI\_LOW\_PERCENTILE	33	Low stress threshold

GCSI\_HIGH\_PERCENTILE	66	High stress threshold

All parameters are configurable in config.py.



Theoretical Foundation

The cascading failure model is inspired by:



Percolation Theory — Failures propagate through network edges with probabilistic weights

Watts (2002) — Global cascades on random networks occur above a critical connectivity threshold

Motter \& Lai (2002) — Cascade-based attacks exploit network topology to maximize disruption

Helbing (2013) — Globally networked risks amplify local failures into systemic collapse

Gao et al. (2016) — Universal resilience patterns in complex networks

Key Findings

Hypercritical Density: At 56% edge density, the network is above the percolation threshold. Any single node failure cascades to 60-97% of the network.



Structural Vulnerability: The small stress amplification factor (1.07x) reveals that vulnerability is primarily structural, not stress-driven. The network topology itself is the risk.



Critical vs Safe Nodes: Five upstream suppliers cause near-total collapse. Five end-of-chain products have zero downstream impact. This asymmetry identifies exactly where to invest in redundancy.



Resilience Recommendation: Reducing unnecessary dependencies (lowering density below the cascade threshold) would improve resilience more than preparing for external stress events.



References

Buldyrev, S. et al. (2010). Catastrophic cascade of failures in interdependent networks. Nature.

Gao, J., Barzel, B., \& Barabási, A.-L. (2016). Universal resilience patterns in complex networks. Nature.

Helbing, D. (2013). Globally networked risks and how to respond. Nature.

Li, M. et al. (2021). Structural properties of supply chain networks. PNAS.

Motter, A. \& Lai, Y.-C. (2002). Cascade-based attacks on complex networks. Physical Review E.

Watts, D. (2002). A simple model of global cascades on random networks. PNAS.

Zhao, K. et al. (2020). Quantifying supply chain resilience. Reliability Engineering \& System Safety.

World Bank (2024). Global Supply Chain Stress Index.

SupplyGraph Dataset (2024).

IEEE DataPort (2024). PowerCascade Dataset.

License

This project was developed for CS4982 at the University of New Brunswick. For academic use only.



Author

Malek Karoui

University of New Brunswick

malek.karoui@unb.ca

