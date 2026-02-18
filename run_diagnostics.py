"""
run_diagnostics.py
==================
Validation and diagnostic checks for the framework.

Checks:
    1. Data file integrity
    2. Graph structural properties
    3. Stress model consistency
    4. Result file validation
    5. Convergence verification

Author: Malek Karoui
Course: CS4982 - Winter 2026
"""

import pandas as pd
import networkx as nx

import config
from supplygraph_loader import load_supplygraph, get_graph_summary
from gcsi_loader import GCSIStressModel

logger = config.setup_logging()


def check_data_files():
    """Verify all required data files exist and are valid."""
    print("\n── Data File Checks ──")
    checks = [
        ("Node CSV", config.NODE_CSV),
        ("Edge CSV", config.EDGE_CSV),
        ("GCSI CSV", config.GCSI_CSV),
    ]
    all_ok = True
    for name, path in checks:
        if path.exists():
            df = pd.read_csv(path)
            print(f"  [PASS] {name}: {path} ({len(df)} rows)")
        else:
            print(f"  [FAIL] {name}: {path} NOT FOUND")
            all_ok = False
    return all_ok


def check_graph_structure():
    """Analyze the dependency graph for potential issues."""
    print("\n── Graph Structure Checks ──")
    G = load_supplygraph()
    summary = get_graph_summary(G)

    for k, v in summary.items():
        print(f"  {k}: {v}")

    # Check for isolated nodes
    isolates = list(nx.isolates(G))
    if isolates:
        print(f"  [WARN] {len(isolates)} isolated nodes: {isolates[:5]}...")
    else:
        print("  [PASS] No isolated nodes.")

    # Check for self-loops
    self_loops = list(nx.selfloop_edges(G))
    if self_loops:
        print(f"  [WARN] {len(self_loops)} self-loops found.")
    else:
        print("  [PASS] No self-loops.")

    # Degree distribution
    in_degrees = [d for _, d in G.in_degree()]
    out_degrees = [d for _, d in G.out_degree()]
    print(f"  In-degree  range: [{min(in_degrees)}, {max(in_degrees)}]")
    print(f"  Out-degree range: [{min(out_degrees)}, {max(out_degrees)}]")

    # Top 5 hubs
    print("\n  Top 5 nodes by out-degree (potential cascade sources):")
    top_out = sorted(G.nodes(), key=lambda n: G.out_degree(n), reverse=True)[:5]
    for n in top_out:
        print(f"    {n}: out={G.out_degree(n)}, in={G.in_degree(n)}")

    return G


def check_stress_model():
    """Validate GSCSI stress model consistency."""
    print("\n── Stress Model Checks ──")
    model = GCSIStressModel()
    summary = model.get_summary()

    for k, v in summary.items():
        print(f"  {k}: {v}")

    # Verify ordering: low < medium < high
    m_low = model.get_multiplier("low")
    m_med = model.get_multiplier("medium")
    m_high = model.get_multiplier("high")

    if m_low < m_med < m_high:
        print("  [PASS] Stress ordering: low < medium < high")
    else:
        print(f"  [WARN] Unexpected ordering: low={m_low}, med={m_med}, high={m_high}")


def check_results():
    """Validate that result files exist and contain expected columns."""
    print("\n── Result File Checks ──")
    expected_cols = {"node_id", "stress_level", "raw_fragility", "normalized_fragility", "std"}

    for level in config.STRESS_LEVELS:
        path = config.RESULTS_DIR / f"fragility_{level}.csv"
        if path.exists():
            df = pd.read_csv(path)
            missing = expected_cols - set(df.columns)
            if missing:
                print(f"  [FAIL] {level}: missing columns {missing}")
            else:
                print(f"  [PASS] {level}: {len(df)} nodes, "
                      f"mean={df['normalized_fragility'].mean():.4f}")
        else:
            print(f"  [SKIP] {level}: file not found (run pipeline first)")
