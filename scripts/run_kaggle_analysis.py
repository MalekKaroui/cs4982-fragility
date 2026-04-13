"""
run_kaggle_analysis.py
======================
Runs fragility analysis on the Kaggle supply chain graph.

Author: Malek Karoui
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


import pandas as pd
from src import config
from src.kaggle_loader import load_kaggle_supplychain_graph, get_kaggle_graph_summary
from src.fragility import compute_fragility_all

logger = config.setup_logging()


def main():
    config.ensure_directories()

    print("=" * 60)
    print("  KAGGLE SUPPLY CHAIN FRAGILITY ANALYSIS")
    print("=" * 60)

    G = load_kaggle_supplychain_graph()
    summary = get_kaggle_graph_summary(G)

    print("\nGraph summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    results = []

    for level in config.STRESS_LEVELS:
        print(f"\nRunning {level} stress...")
        fragility_data = compute_fragility_all(G, stress_level=level, n_cascades=config.DEFAULT_N_CASCADES)
        df = pd.DataFrame(fragility_data)

        outfile = config.RESULTS_DIR / f"fragility_kaggle_{level}.csv"
        df.to_csv(outfile, index=False)

        max_row = df.loc[df["normalized_fragility"].idxmax()]

        print(f"  Mean fragility: {df['normalized_fragility'].mean():.4f}")
        print(f"  Max fragility:  {df['normalized_fragility'].max():.4f} ({max_row['node_id']})")
        print(f"  Min fragility:  {df['normalized_fragility'].min():.4f}")
        print(f"  Saved: {outfile}")

        results.append({
            "case": "Kaggle",
            "stress_level": level,
            "nodes": summary["nodes"],
            "edges": summary["edges"],
            "density": summary["density"],
            "mean_fragility": round(df["normalized_fragility"].mean(), 4),
            "max_fragility": round(df["normalized_fragility"].max(), 4),
            "min_fragility": round(df["normalized_fragility"].min(), 4),
            "most_critical_node": max_row["node_id"],
            "zero_fragility_count": int((df["normalized_fragility"] == 0).sum()),
        })

    comparison_file = config.RESULTS_DIR / "kaggle_summary.csv"
    pd.DataFrame(results).to_csv(comparison_file, index=False)
    print(f"\nSaved summary: {comparison_file}")


if __name__ == "__main__":
    main()