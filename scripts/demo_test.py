"""
demo_test.py
PR2 Video Demo - Pipeline Walkthrough
CS4982 - Winter 2026 - Malek Karoui
Shows: Graph Builder, GSCSI Stress Module, Monte Carlo Engine,
       Fragility Pipeline, Convergence Test, Visualization Outputs
Delete after recording.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


import time
import os
import random
import numpy as np
import pandas as pd

from src import config
from src.supplygraph_loader import load_supplygraph, get_graph_summary
from src.fragility import simulate_cascade
from src.gcsi_loader import GCSIStressModel


def show(text):
    print()
    print("=" * 60)
    print(f"  {text}")
    print("=" * 60)
    time.sleep(1.5)


# ──────────────────────────────────────
# STAGE 1: Graph Construction
# PR2 Status: Complete (Week 4)
# ──────────────────────────────────────
show("STAGE 1/7 - Graph Construction [Complete - Week 4]")
print()
print("  Data source: SupplyGraph benchmark dataset")
print(f"  Node CSV: {config.NODE_CSV}")
print(f"  Edge CSV: {config.EDGE_CSV}")
time.sleep(1)

G = load_supplygraph()
s = get_graph_summary(G)

print()
print("  Graph Properties:")
print(f"    Nodes:              {s['nodes']}")
print(f"    Edges:              {s['edges']}")
print(f"    Density:            {s['density']*100:.2f}%")
print(f"    Avg Out-Degree:     {s['avg_out_degree']}")
print(f"    Weakly Connected:   {s['is_weakly_connected']}")
print(f"    Components:         {s['weakly_connected_components']}")

sinks = [n for n in G.nodes() if G.out_degree(n) == 0]
print(f"    Sink Nodes (out=0): {len(sinks)}")
for n in sinks:
    print(f"      - {n}")

top5 = sorted(G.nodes(), key=lambda n: G.out_degree(n), reverse=True)[:5]
print()
print("  Top 5 by out-degree:")
for n in top5:
    print(f"    {n}: {G.out_degree(n)}")

print()
print("  Edge weights normalized to [0.10, 0.65]")
print(f"    Formula: p(e) = 0.10 + (w-wmin)/(wmax-wmin) * 0.55")
time.sleep(2)


# ──────────────────────────────────────
# STAGE 2: GSCSI Stress Module
# PR2 Status: Complete (Week 6)
# ──────────────────────────────────────
show("STAGE 2/7 - GSCSI Stress Module [Complete - Week 6]")

model = GCSIStressModel()
info = model.get_summary()

print()
print("  GSCSI Historical Data:")
print(f"    Data points:  {info['data_points']}")
print(f"    Value range:  [{info['min']:.4f}, {info['max']:.4f}]")
print(f"    Overall mean: {info['mean']:.4f}")
print(f"    33rd pctile:  {info['p33']:.4f}")
print(f"    66th pctile:  {info['p66']:.4f}")

s_low = model.get_multiplier("low")
s_med = model.get_multiplier("medium")
s_high = model.get_multiplier("high")

print()
print("  Derived Stress Multipliers:")
print(f"    Low stress:    {s_low:.4f}x  (below 33rd percentile)")
print(f"    Medium stress: {s_med:.4f}x  (33rd to 66th percentile)")
print(f"    High stress:   {s_high:.4f}x  (above 66th percentile)")
print()
print("  Method: data-driven percentile thresholds (Rehman & Askan 2024)")
time.sleep(2)


# ──────────────────────────────────────
# STAGE 3: Monte Carlo Cascade Engine
# PR2 Status: Complete (Week 5)
# ──────────────────────────────────────
show("STAGE 3/7 - Monte Carlo Cascade Engine [Complete - Week 5]")

target = top5[0]
print()
print(f"  Live cascade demonstration:")
print(f"    Initial failure node: {target}")
print(f"    Out-degree:           {G.out_degree(target)}")
print(f"    Stress level:         medium ({s_med:.4f}x)")
print(f"    Propagation model:    BFS with probabilistic edges")
print()
print("  Running 10 cascades...")
print()
time.sleep(1)

sizes = []
for i in range(10):
    rng = random.Random()
    hit = simulate_cascade(G, target, s_med, rng) - 1
    pct = hit / (G.number_of_nodes() - 1)
    sizes.append(hit)
    print(f"    Trial {i+1:2d}: {hit:2d} / {G.number_of_nodes()-1} nodes failed ({pct:.1%})")
    time.sleep(0.3)

avg = np.mean(sizes)
print()
print(f"  Average cascade size: {avg:.1f} nodes ({avg/(G.number_of_nodes()-1):.1%} of network)")
time.sleep(2)


# ──────────────────────────────────────
# STAGE 4: Fragility Computation Pipeline
# PR2 Status: Complete (Week 8)
# ──────────────────────────────────────
show("STAGE 4/7 - Fragility Pipeline [Complete - Week 8]")

print()
print("  Simulation configuration:")
print(f"    Nodes:              {G.number_of_nodes()}")
print(f"    Iterations/node:    {config.DEFAULT_N_CASCADES}")
print(f"    Stress scenarios:   3 (low, medium, high)")
total = G.number_of_nodes() * config.DEFAULT_N_CASCADES * 3
print(f"    Total simulations:  {total:,}")
print()
print("  Fragility Index: F(v) = (1/N) * sum(C_i(v) / (|V|-1))")
time.sleep(1)

low_df = pd.read_csv(config.RESULTS_DIR / "fragility_low.csv")
med_df = pd.read_csv(config.RESULTS_DIR / "fragility_medium.csv")
high_df = pd.read_csv(config.RESULTS_DIR / "fragility_high.csv")

print()
print("  Results (from pre-computed CSVs):")
print()
print(f"  {'Stress':<10} {'Mean F':>10} {'Max F':>10} {'Min F':>10} {'Std':>10}")
print(f"  {'-'*50}")
for label, df in [("Low", low_df), ("Medium", med_df), ("High", high_df)]:
    m = df["normalized_fragility"]
    print(f"  {label:<10} {m.mean():>10.4f} {m.max():>10.4f} {m.min():>10.4f} {m.std():>10.4f}")

amp = high_df["normalized_fragility"].mean() / low_df["normalized_fragility"].mean()
print()
print(f"  Stress amplification (high/low): {amp:.2f}x")
print("  Network is above cascade threshold (Watts 2002)")
time.sleep(2)


# ──────────────────────────────────────
# STAGE 5: Critical Node Analysis
# PR2 Status: Complete (Week 8)
# ──────────────────────────────────────
show("STAGE 5/7 - Critical Node Identification [Complete - Week 8]")

danger = med_df.nlargest(5, "normalized_fragility")
print()
print("  Top 5 most dangerous nodes (medium stress):")
print()
print(f"  {'Node':<15} {'Out-Deg':>8} {'Fragility':>10} {'Cascade':>10}")
print(f"  {'-'*45}")
for _, r in danger.iterrows():
    node = r["node_id"]
    deg = G.out_degree(node)
    frag = r["normalized_fragility"]
    raw = r["raw_fragility"]
    print(f"  {node:<15} {deg:>8} {frag:>10.4f} {raw:>10.1f}")

print()
print("  These are upstream suppliers and assembly hubs with high")
print("  out-degree, consistent with Buldyrev et al. (2010)")

print()
print("  Safest nodes (F = 0):")
print()
safe = med_df[med_df["normalized_fragility"] == 0]
for _, r in safe.iterrows():
    node = r["node_id"]
    deg = G.out_degree(node)
    print(f"    {node}  (out-degree: {deg}) - sink node")

print()
print(f"  {len(safe)} terminal output nodes with zero cascading risk")
time.sleep(2)


# ──────────────────────────────────────
# STAGE 6: Convergence Validation
# PR2 Status: Complete (Week 8)
# ──────────────────────────────────────
show("STAGE 6/7 - Convergence Test [Complete - Week 8]")

conv = pd.read_csv(config.RESULTS_DIR / "convergence_test.csv")
print()
print("  Testing if N=500 iterations is sufficient:")
print()
print(f"  {'N':>6} {'Mean Cascade':>14} {'Std':>8} {'Fragility':>12} {'Change':>10}")
print(f"  {'-'*54}")

prev = None
for _, r in conv.iterrows():
    n = int(r["n_cascades"])
    mean = r["mean"]
    std = r["std"]
    norm = r["normalized"]

    if prev is not None:
        change = abs(norm - prev) / prev * 100
        print(f"  {n:>6} {mean:>14.3f} {std:>8.4f} {norm:>12.6f} {change:>9.3f}%")
    else:
        print(f"  {n:>6} {mean:>14.3f} {std:>8.4f} {norm:>12.6f} {'--':>10}")
    prev = norm
    time.sleep(0.4)

print()
print("  Result: < 1% change after N=300")
print("  N=500 provides stable estimates (Kroese et al. 2014)")
time.sleep(2)


# ──────────────────────────────────────
# STAGE 7: Outputs
# PR2 Status: Complete (Week 8-9)
# ──────────────────────────────────────
show("STAGE 7/7 - Generated Outputs [Complete - Week 8-9]")

# Figures
figs = []
for root, _, files in os.walk(str(config.FIGURES_DIR)):
    for f in files:
        if f.endswith(".png"):
            figs.append(os.path.relpath(os.path.join(root, f)))

print()
print(f"  Static figures ({len(figs)}):")
for f in sorted(figs):
    print(f"    {f}")

# CSVs
print()
print("  Result files:")
for f in sorted(config.RESULTS_DIR.glob("*.csv")):
    size = f.stat().st_size / 1024
    print(f"    {f.name} ({size:.1f} KB)")

# GitHub
print()
print("  GitHub repository:")
print("    https://github.com/MalekKaroui/cs4982-fragility")
print("    Includes: source code, data, results, README")
time.sleep(2)


# ──────────────────────────────────────
# SUMMARY
# ──────────────────────────────────────
show("PR2 STATUS SUMMARY - Week 9 of 12")

best = danger.iloc[0]
print(f"""
  COMPLETED (85 / 120 hours used = 71%):
    [x] Graph builder              Week 4    12h
    [x] Monte Carlo engine         Week 5    15h
    [x] GSCSI stress module        Week 6    10h
    [x] Fragility pipeline         Week 8    15h
    [x] Convergence test           Week 8     5h
    [x] Visualization suite        Week 8    12h
    [x] Streamlit dashboard        Week 7    10h
    [x] Config + diagnostics       Week 8     3h
    [x] GitHub repo + README       Week 9     1h

  IN PROGRESS:
    [ ] PowerCascade validation    Week 10   7h remaining
    [ ] Ranking stability test     Week 10   planned
    [ ] Degree-fragility corr.     Week 10   planned

  REMAINING:
    [ ] Final report draft         March 22  12h
    [ ] Demo                       March 26   6h
    [ ] Final report               April 13   7h

  KEY RESULTS:
    Graph:         {s['nodes']} nodes, {s['edges']} edges, {s['density']*100:.0f}% density
    Simulations:   {total:,} total cascade runs
    Stress range:  {s_low:.2f}x (low) to {s_high:.2f}x (high)
    Amplification: {amp:.2f}x
    Top threat:    {best['node_id']} (F = {best['normalized_fragility']:.3f})
    Safe nodes:    {len(safe)} sink nodes with F = 0

  NEXT STEP: streamlit run demo_dashboard.py
""")