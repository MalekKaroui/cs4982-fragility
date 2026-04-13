"""
compare_networks.py
===================
Multi-Network Comparative Fragility Analysis.

Creates 4 supply chain network cases with different density levels
and compares fragility across all cases and stress scenarios.

This addresses the requirement to analyze more than one supply chain
structure and demonstrate how the framework can compare industrial
supply chain configurations.

Cases:
    Case 1 - Sparse:  ~15% density (loosely coupled supply chain)
    Case 2 - Medium:  ~30% density (moderately coupled supply chain)
    Case 3 - Dense:   ~45% density (tightly coupled supply chain)
    Case 4 - Original: ~56% density (benchmark SupplyGraph network)

Author: Malek Karoui
Course: CS4982 - Winter 2026
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


import random
import time
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src import config
from src.supplygraph_loader import load_supplygraph, get_graph_summary
from src.fragility import compute_fragility_all
from src.gcsi_loader import GCSIStressModel

logger = config.setup_logging()


def create_sparse_variant(G_original, target_density=0.15, seed=42):
    """
    Creates a sparse supply chain variant by randomly removing edges.
    
    This represents a loosely coupled industrial supply chain where
    suppliers have fewer interdependencies, such as a decentralized
    manufacturing network with independent supplier tiers.
    
    Parameters
    ----------
    G_original : nx.DiGraph
        The original benchmark graph.
    target_density : float
        Target edge density (0 to 1).
    seed : int
        Random seed for reproducibility.
    
    Returns
    -------
    nx.DiGraph
        A sparser copy of the original graph.
    """
    rng = random.Random(seed)
    G = G_original.copy()
    
    edges = list(G.edges())
    n_nodes = G.number_of_nodes()
    max_edges = n_nodes * (n_nodes - 1)
    target_edges = int(target_density * max_edges)
    
    # Shuffle and remove edges until we hit target
    rng.shuffle(edges)
    
    while G.number_of_edges() > target_edges and edges:
        edge = edges.pop()
        G.remove_edge(*edge)
    
    logger.info(
        "Sparse variant: %d nodes, %d edges, density %.4f",
        G.number_of_nodes(), G.number_of_edges(), nx.density(G)
    )
    return G


def create_medium_variant(G_original, target_density=0.30, seed=123):
    """
    Creates a medium-density supply chain variant.
    
    This represents a moderately coupled industrial supply chain,
    such as a regional automotive parts network where suppliers
    share some but not all dependencies.
    """
    rng = random.Random(seed)
    G = G_original.copy()
    
    edges = list(G.edges())
    n_nodes = G.number_of_nodes()
    max_edges = n_nodes * (n_nodes - 1)
    target_edges = int(target_density * max_edges)
    
    rng.shuffle(edges)
    
    while G.number_of_edges() > target_edges and edges:
        edge = edges.pop()
        G.remove_edge(*edge)
    
    logger.info(
        "Medium variant: %d nodes, %d edges, density %.4f",
        G.number_of_nodes(), G.number_of_edges(), nx.density(G)
    )
    return G


def create_dense_variant(G_original, target_density=0.45, seed=256):
    """
    Creates a dense supply chain variant.
    
    This represents a tightly coupled industrial supply chain,
    such as a centralized electronics manufacturing network
    where most suppliers depend on shared components.
    """
    rng = random.Random(seed)
    G = G_original.copy()
    
    edges = list(G.edges())
    n_nodes = G.number_of_nodes()
    max_edges = n_nodes * (n_nodes - 1)
    target_edges = int(target_density * max_edges)
    
    rng.shuffle(edges)
    
    while G.number_of_edges() > target_edges and edges:
        edge = edges.pop()
        G.remove_edge(*edge)
    
    logger.info(
        "Dense variant: %d nodes, %d edges, density %.4f",
        G.number_of_nodes(), G.number_of_edges(), nx.density(G)
    )
    return G


def analyze_case(G, case_name, n_cascades=500):
    """
    Runs full fragility analysis on one network case across all
    stress scenarios.
    
    Parameters
    ----------
    G : nx.DiGraph
        The supply chain graph for this case.
    case_name : str
        Label for the case (e.g., "Sparse", "Medium").
    n_cascades : int
        Monte Carlo iterations per node.
    
    Returns
    -------
    list of dict
        Comparison results for this case.
    """
    results = []
    summary = get_graph_summary(G)
    
    for level in config.STRESS_LEVELS:
        print(f"      Running {case_name} - {level} stress...")
        
        fragility_data = compute_fragility_all(G, stress_level=level, n_cascades=n_cascades)
        df = pd.DataFrame(fragility_data)
        
        # Save per-case results
        outfile = config.RESULTS_DIR / f"fragility_{case_name.lower()}_{level}.csv"
        df.to_csv(outfile, index=False)
        
        # Find most critical node
        max_row = df.loc[df["normalized_fragility"].idxmax()]
        
        results.append({
            "case": case_name,
            "stress_level": level,
            "nodes": summary["nodes"],
            "edges": summary["edges"],
            "density": summary["density"],
            "mean_fragility": round(df["normalized_fragility"].mean(), 4),
            "max_fragility": round(df["normalized_fragility"].max(), 4),
            "min_fragility": round(df["normalized_fragility"].min(), 4),
            "std_fragility": round(df["normalized_fragility"].std(), 4),
            "most_critical_node": max_row["node_id"],
            "zero_fragility_count": int((df["normalized_fragility"] == 0).sum()),
        })
    
    return results


def plot_comparison(comparison_df):
    """
    Generates comparison visualizations across all 4 cases.
    """
    config.ensure_directories()
    comparison_dir = config.FIGURES_DIR / "comparison"
    comparison_dir.mkdir(parents=True, exist_ok=True)
    
    # ── Plot 1: Mean Fragility by Case and Stress ──
    fig, ax = plt.subplots(figsize=(10, 6))
    
    cases = comparison_df["case"].unique()
    stress_levels = ["low", "medium", "high"]
    x = np.arange(len(cases))
    width = 0.25
    
    for i, level in enumerate(stress_levels):
        subset = comparison_df[comparison_df["stress_level"] == level]
        # Ensure order matches cases
        values = []
        for case in cases:
            row = subset[subset["case"] == case]
            if not row.empty:
                values.append(row.iloc[0]["mean_fragility"])
            else:
                values.append(0)
        
        ax.bar(x + i * width, values, width, label=f"{level.title()} Stress")
    
    ax.set_xlabel("Supply Chain Configuration", fontsize=12)
    ax.set_ylabel("Mean Fragility Index", fontsize=12)
    ax.set_title("Comparative Fragility Analysis Across Supply Chain Structures", fontsize=14)
    ax.set_xticks(x + width)
    ax.set_xticklabels(cases)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(comparison_dir / "mean_fragility_comparison.png", dpi=300)
    plt.close()
    logger.info("Saved: mean_fragility_comparison.png")
    
    # ── Plot 2: Max Fragility by Case ──
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for i, level in enumerate(stress_levels):
        subset = comparison_df[comparison_df["stress_level"] == level]
        values = []
        for case in cases:
            row = subset[subset["case"] == case]
            if not row.empty:
                values.append(row.iloc[0]["max_fragility"])
            else:
                values.append(0)
        
        ax.bar(x + i * width, values, width, label=f"{level.title()} Stress")
    
    ax.set_xlabel("Supply Chain Configuration", fontsize=12)
    ax.set_ylabel("Max Fragility Index", fontsize=12)
    ax.set_title("Maximum Node Fragility Across Supply Chain Structures", fontsize=14)
    ax.set_xticks(x + width)
    ax.set_xticklabels(cases)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(comparison_dir / "max_fragility_comparison.png", dpi=300)
    plt.close()
    logger.info("Saved: max_fragility_comparison.png")
    
    # ── Plot 3: Density vs Mean Fragility ──
    fig, ax = plt.subplots(figsize=(8, 6))
    
    medium_data = comparison_df[comparison_df["stress_level"] == "medium"]
    ax.scatter(medium_data["density"], medium_data["mean_fragility"], s=200, c="red", zorder=5)
    
    for _, row in medium_data.iterrows():
        ax.annotate(
            row["case"],
            (row["density"], row["mean_fragility"]),
            textcoords="offset points",
            xytext=(10, 10),
            fontsize=11,
        )
    
    ax.plot(
        medium_data["density"].values,
        medium_data["mean_fragility"].values,
        "--", color="gray", alpha=0.5
    )
    
    ax.set_xlabel("Network Density", fontsize=12)
    ax.set_ylabel("Mean Fragility Index (Medium Stress)", fontsize=12)
    ax.set_title("Relationship Between Network Density and Systemic Fragility", fontsize=14)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(comparison_dir / "density_vs_fragility.png", dpi=300)
    plt.close()
    logger.info("Saved: density_vs_fragility.png")
    
    # ── Plot 4: Stress Amplification by Case ──
    fig, ax = plt.subplots(figsize=(8, 6))
    
    amplification = []
    case_names = []
    for case in cases:
        case_data = comparison_df[comparison_df["case"] == case]
        low_row = case_data[case_data["stress_level"] == "low"]
        high_row = case_data[case_data["stress_level"] == "high"]
        
        if not low_row.empty and not high_row.empty:
            low_val = low_row.iloc[0]["mean_fragility"]
            high_val = high_row.iloc[0]["mean_fragility"]
            
            if low_val > 0:
                amp = high_val / low_val
            else:
                amp = 0
            
            amplification.append(amp)
            case_names.append(case)
    
    ax.bar(case_names, amplification, color=["#2ecc71", "#3498db", "#e74c3c", "#9b59b6"])
    ax.set_xlabel("Supply Chain Configuration", fontsize=12)
    ax.set_ylabel("Stress Amplification Factor (High / Low)", fontsize=12)
    ax.set_title("Stress Sensitivity Across Supply Chain Structures", fontsize=14)
    ax.axhline(y=1.0, color="gray", linestyle="--", alpha=0.5, label="No amplification")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(comparison_dir / "stress_amplification_comparison.png", dpi=300)
    plt.close()
    logger.info("Saved: stress_amplification_comparison.png")


def main():
    config.ensure_directories()
    
    print("=" * 60)
    print("  MULTI-NETWORK COMPARATIVE FRAGILITY ANALYSIS")
    print("  CS4982 - Winter 2026")
    print("=" * 60)
    
    # ── Load original graph ──
    print("\n[1/6] Loading original SupplyGraph network...")
    t0 = time.time()
    G_original = load_supplygraph()
    original_summary = get_graph_summary(G_original)
    print(f"      Original: {original_summary['nodes']} nodes, "
          f"{original_summary['edges']} edges, "
          f"density {original_summary['density']}")
    
    # ── Create variants ──
    print("\n[2/6] Creating network variants...")
    
    G_sparse = create_sparse_variant(G_original, target_density=0.15)
    G_medium = create_medium_variant(G_original, target_density=0.30)
    G_dense = create_dense_variant(G_original, target_density=0.45)
    
    sparse_summary = get_graph_summary(G_sparse)
    medium_summary = get_graph_summary(G_medium)
    dense_summary = get_graph_summary(G_dense)
    
    print(f"      Sparse:   {sparse_summary['nodes']} nodes, "
          f"{sparse_summary['edges']} edges, "
          f"density {sparse_summary['density']}")
    print(f"      Medium:   {medium_summary['nodes']} nodes, "
          f"{medium_summary['edges']} edges, "
          f"density {medium_summary['density']}")
    print(f"      Dense:    {dense_summary['nodes']} nodes, "
          f"{dense_summary['edges']} edges, "
          f"density {dense_summary['density']}")
    print(f"      Original: {original_summary['nodes']} nodes, "
          f"{original_summary['edges']} edges, "
          f"density {original_summary['density']}")
    
    # ── Run analysis on each case ──
    cases = [
        (G_sparse, "Sparse"),
        (G_medium, "Medium"),
        (G_dense, "Dense"),
        (G_original, "Original"),
    ]
    
    all_results = []
    
    for i, (G, name) in enumerate(cases, start=3):
        print(f"\n[{i}/6] Analyzing {name} network...")
        case_results = analyze_case(G, name, n_cascades=config.DEFAULT_N_CASCADES)
        all_results.extend(case_results)
    
    # ── Save comparison table ──
    comparison_df = pd.DataFrame(all_results)
    comparison_file = config.RESULTS_DIR / "network_comparison.csv"
    comparison_df.to_csv(comparison_file, index=False)
    print(f"\n      Saved comparison: {comparison_file}")
    
    # ── Print summary table ──
    print("\n" + "=" * 90)
    print("  COMPARATIVE RESULTS SUMMARY")
    print("=" * 90)
    print(f"{'Case':<12} {'Stress':<8} {'Nodes':>6} {'Edges':>6} "
          f"{'Density':>8} {'Mean F':>8} {'Max F':>8} {'Min F':>8} "
          f"{'Zeros':>6} {'Top Node':<15}")
    print("-" * 90)
    
    for _, row in comparison_df.iterrows():
        print(f"{row['case']:<12} {row['stress_level']:<8} "
              f"{row['nodes']:>6} {row['edges']:>6} "
              f"{row['density']:>8.4f} {row['mean_fragility']:>8.4f} "
              f"{row['max_fragility']:>8.4f} {row['min_fragility']:>8.4f} "
              f"{row['zero_fragility_count']:>6} {row['most_critical_node']:<15}")
    
    # ── Compute amplification factors ──
    print("\n" + "=" * 60)
    print("  STRESS AMPLIFICATION FACTORS")
    print("=" * 60)
    
    for case_name in ["Sparse", "Medium", "Dense", "Original"]:
        case_data = comparison_df[comparison_df["case"] == case_name]
        low_row = case_data[case_data["stress_level"] == "low"]
        high_row = case_data[case_data["stress_level"] == "high"]
        
        if not low_row.empty and not high_row.empty:
            low_val = low_row.iloc[0]["mean_fragility"]
            high_val = high_row.iloc[0]["mean_fragility"]
            
            if low_val > 0:
                amp = high_val / low_val
                print(f"  {case_name:<12} High/Low = {high_val:.4f} / {low_val:.4f} = {amp:.2f}x")
            else:
                print(f"  {case_name:<12} Low fragility is zero, cannot compute amplification")
    
    # ── Generate comparison plots ──
    print("\n[6/6] Generating comparison figures...")
    plot_comparison(comparison_df)
    
    # ── Done ──
    total_time = time.time() - t0
    print("\n" + "=" * 60)
    print(f"  COMPARISON COMPLETE - Total time: {total_time:.1f}s")
    print(f"  Results: {config.RESULTS_DIR}")
    print(f"  Figures: {config.FIGURES_DIR / 'comparison'}")
    print("=" * 60)


if __name__ == "__main__":
    main()