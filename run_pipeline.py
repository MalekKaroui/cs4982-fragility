"""
run_pipeline.py
===============
Main execution pipeline for the Fragility Modeling Framework.

Workflow:
    1. Load the SupplyGraph dependency graph
    2. For each stress level (low, medium, high):
       a. Compute Fragility Index for all nodes
       b. Save results to CSV
    3. Run convergence test
    4. Generate static figures

Usage:
    python run_pipeline.py

Author: Malek Karoui
Course: CS4982 - Winter 2026
"""

import time
import pandas as pd

import config
from supplygraph_loader import load_supplygraph, get_graph_summary
from fragility import compute_fragility_all, convergence_test
from visualize import save_all_figures

logger = config.setup_logging()


def main():
    config.ensure_directories()

    print("=" * 60)
    print("  OPERATIONAL FRAGILITY MODELING FRAMEWORK")
    print("  CS4982 — Winter 2026")
    print("=" * 60)

    # ── Step 1: Load Graph ──
    print("\n[1/4] Loading SupplyGraph dataset...")
    t0 = time.time()
    G = load_supplygraph()
    summary = get_graph_summary(G)

    print(f"      Nodes: {summary['nodes']}")
    print(f"      Edges: {summary['edges']}")
    print(f"      Density: {summary['density']}")
    print(f"      Weakly Connected: {summary['is_weakly_connected']}")
    print(f"      Components: {summary['weakly_connected_components']}")
    print(f"      Avg In-Degree: {summary['avg_in_degree']}")
    print(f"      Avg Out-Degree: {summary['avg_out_degree']}")
    print(f"      Loaded in {time.time() - t0:.2f}s")

    # ── Step 2: Compute Fragility ──
    print(f"\n[2/4] Running Monte Carlo simulations ({config.DEFAULT_N_CASCADES} iterations/node)...")

    for level in config.STRESS_LEVELS:
        t1 = time.time()
        print(f"\n      ── {level.upper()} stress scenario ──")

        results = compute_fragility_all(G, stress_level=level, n_cascades=config.DEFAULT_N_CASCADES)
        df = pd.DataFrame(results)

        outfile = config.RESULTS_DIR / f"fragility_{level}.csv"
        df.to_csv(outfile, index=False)

        # Summary statistics
        print(f"      Mean fragility: {df['normalized_fragility'].mean():.4f}")
        print(f"      Max fragility:  {df['normalized_fragility'].max():.4f} ({df.loc[df['normalized_fragility'].idxmax(), 'node_id']})")
        print(f"      Min fragility:  {df['normalized_fragility'].min():.4f}")
        print(f"      Saved: {outfile}")
        print(f"      Time: {time.time() - t1:.2f}s")

    # ── Step 3: Convergence Test ──
    print("\n[3/4] Running convergence test...")
    conv_results = convergence_test(G, stress_level="medium")
    conv_df = pd.DataFrame(conv_results)
    conv_file = config.RESULTS_DIR / "convergence_test.csv"
    conv_df.to_csv(conv_file, index=False)
    print(f"      Saved: {conv_file}")

    # ── Step 4: Generate Figures ──
    print("\n[4/4] Generating static figures...")
    save_all_figures()

    # ── Done ──
    total_time = time.time() - t0
    print("\n" + "=" * 60)
    print(f"  PIPELINE COMPLETE — Total time: {total_time:.1f}s")
    print(f"  Results: {config.RESULTS_DIR}")
    print(f"  Figures: {config.FIGURES_DIR}")
    print(f"  Dashboard: streamlit run dashboard.py")
    print("=" * 60)


if __name__ == "__main__":
    main()