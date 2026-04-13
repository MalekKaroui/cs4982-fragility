# Operational Fragility Modeling Framework for Industrial Supply Chains

**CS4982 Senior Project - Winter 2026**

**Author:** Malek Karoui

**Supervisor:** Professor Baker

**University of New Brunswick**

---

## Overview

This framework quantifies systemic fragility in industrial supply chains using Monte Carlo cascading failure simulations on directed dependency graphs. It integrates the World Bank Global Supply Chain Stress Index (GSCSI) to model low-, medium-, and high-stress scenarios.

The primary output is a **Fragility Index F(v)** that measures the expected downstream disruption when a specific node fails.

```
F(v) = (1/N) * SUM( C_i(v) )
```

Where C_i(v) is the number of nodes affected in simulation trial i, and N is the total number of Monte Carlo iterations.

---

## Architecture

```
Public Data (CSVs)
       |
       v
+--------------------+
|   Graph Builder    |  <-- node.csv + edge.csv (SupplyGraph 2024)
|   (NetworkX)       |
+--------+-----------+
         |
         v
+--------------------+     +--------------------+
|   Monte Carlo      | <-- |   GSCSI Stress     |  <-- gcsi.csv
|   Simulation       |     |   Model            |
|   Engine           |     +--------------------+
+--------+-----------+
         |
         v
+--------------------+
|   Fragility Index  |
|   Computation      |
+--------+-----------+
         |
         v
+--------------------+
|   Visualization    |  --> Plotly + Matplotlib
|   Dashboard        |  --> Streamlit
+--------------------+
```

---

## Key Results

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

### Most Critical Nodes

| Node | Role | Fragility |
|------|------|-----------|
| ATN02K12P | Assembly Terminal Node | 97.4% |
| SOS005L04P | Solvent Supplier | 97.4% |
| SOS500M24P | Solvent Supplier | 97.4% |
| POP002L09P | Polymer Provider | 97.4% |
| SOS003L04P | Solvent Supplier | 97.4% |

### Isolated Nodes (Zero Fragility)

| Node | Role |
|------|------|
| SO0001L12P | End-of-chain Solvent Output |
| SO0500M24P | End-of-chain Solvent Output |
| MAP1K25P | Final Assembly Part |
| EEA500G12P | Final Electronic Assembly |
| EEA200G24P | Final Electronic Assembly |

---

## Project Structure

```
cs4982-fragility/
|-- data/
|   |-- node.csv
|   |-- edge.csv
|   |-- gcsi.csv
|-- results/
|-- figures/
|-- config.py
|-- supplygraph_loader.py
|-- gcsi_loader.py
|-- fragility.py
|-- visualize.py
|-- run_pipeline.py
|-- run_diagnostics.py
|-- dashboard.py
|-- run_project.bat
|-- requirements.txt
|-- README.md
```

---

## Module Descriptions

| Module | Purpose |
|--------|--------|
| config.py | Central configuration with all paths and parameters |
| supplygraph_loader.py | Reads CSVs, maps indices to names, builds NetworkX DiGraph |
| gcsi_loader.py | Loads GSCSI data, computes percentile thresholds |
| fragility.py | Monte Carlo engine for cascading failure simulation |
| visualize.py | Interactive Plotly charts and static Matplotlib PNGs |
| run_pipeline.py | Full simulation workflow |
| run_diagnostics.py | Data and graph validation |
| dashboard.py | Streamlit web dashboard with 5 tabs |

---

## Dashboard Tabs

| Tab | Description |
|-----|------------|
| Overview | Summary metrics, histogram, top-K critical nodes |
| Network Map | Interactive graph colored by fragility |
| Node Explorer | Per-node stress sensitivity analysis |
| Convergence | Monte Carlo convergence verification |
| Stress Curve | System-wide stress amplification |

---

## Data Sources

| Dataset | Description |
|---------|------------|
| SupplyGraph (2024) | 40-node synthetic supply chain network |
| World Bank GSCSI | Monthly stress index values |
| PowerCascade (IEEE) | Cascading failure validation data |

---

## Quick Start

```bash
git clone git@github.com:MalekKaroui/cs4982-fragility.git
cd cs4982-fragility
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run_diagnostics.py
python run_pipeline.py
streamlit run dashboard.py
```

---

## Simulation Parameters

| Parameter | Value | Description |
|-----------|-------|------------|
| RANDOM_SEED | 42 | Reproducibility seed |
| DEFAULT_N_CASCADES | 500 | Iterations per node |
| WEIGHT_MIN | 0.10 | Min propagation probability |
| WEIGHT_MAX | 0.65 | Max propagation probability |
| GCSI_LOW_PERCENTILE | 33 | Low stress threshold |
| GCSI_HIGH_PERCENTILE | 66 | High stress threshold |

---

## Theoretical Foundation

- **Percolation Theory** - Probabilistic failure propagation through networks
- **Watts (2002)** - Global cascades above critical connectivity thresholds
- **Motter and Lai (2002)** - Cascade-based attacks on complex networks
- **Helbing (2013)** - Globally networked risks and systemic collapse
- **Gao et al. (2016)** - Universal resilience patterns in complex networks

---

## Key Findings

1. **Hypercritical Density:** At 56% density, any failure cascades to 60-97% of the network
2. **Structural Vulnerability:** 1.07x amplification shows risk is topology-driven
3. **Critical vs Safe:** 5 upstream nodes cause total collapse, 5 end nodes cause zero damage
4. **Recommendation:** Reduce edge density below cascade threshold for resilience

---

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

**Malek Karoui** - University of New Brunswick - malek.karoui@unb.ca
