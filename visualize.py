"""
visualize.py
============
Visualization Suite for the Fragility Modeling Framework.

Generates:
    1. Fragility distribution histograms
    2. Network heatmaps (interactive Plotly + static Matplotlib)
    3. Top-K critical node bar charts
    4. Stress–Fragility sensitivity curves
    5. Convergence plots

Author: Malek Karoui
Course: CS4982 - Winter 2026
"""

import os
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px

from supplygraph_loader import load_supplygraph
import config

logger = config.setup_logging()


# ══════════════════════════════════════════════════
# PLOTLY (Interactive) — Used by Dashboard
# ══════════════════════════════════════════════════

def plotly_network_map(G: nx.DiGraph, fragility_df: pd.DataFrame) -> go.Figure:
    """
    Creates an interactive Plotly network visualization
    colored by normalized fragility.

    Parameters
    ----------
    G : nx.DiGraph
        The supply chain graph.
    fragility_df : pd.DataFrame
        Must contain 'node_id' and 'normalized_fragility' columns.

    Returns
    -------
    go.Figure
        Interactive Plotly figure.
    """
    frag_map = fragility_df.set_index("node_id")["normalized_fragility"].to_dict()
    pos = nx.spring_layout(G, seed=config.NETWORK_LAYOUT_SEED, k=0.15, iterations=60)

    # Edges
    edge_x, edge_y = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.4, color="#aaa"),
        hoverinfo="none",
        mode="lines",
    )

    # Nodes
    node_x, node_y, node_text, node_color, node_size = [], [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        score = frag_map.get(node, 0)
        node_color.append(score)
        # Scale node size by fragility
        node_size.append(8 + score * 30)
        node_text.append(
            f"<b>{node}</b><br>"
            f"Fragility: {score:.4f}<br>"
            f"Out-degree: {G.out_degree(node)}<br>"
            f"In-degree: {G.in_degree(node)}"
        )

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers",
        hoverinfo="text",
        text=node_text,
        marker=dict(
            showscale=True,
            colorscale=config.COLORSCALE,
            color=node_color,
            size=node_size,
            colorbar=dict(title="Fragility Index"),
            line=dict(width=1, color="#333"),
        ),
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode="closest",
            margin=dict(b=0, l=0, r=0, t=0),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        ),
    )
    return fig


def plotly_histogram(df: pd.DataFrame, level: str) -> go.Figure:
    """Interactive histogram of normalized fragility scores."""
    fig = px.histogram(
        df, x="normalized_fragility", nbins=20,
        title=f"Fragility Distribution — {level.upper()} Stress",
        labels={"normalized_fragility": "Normalized Fragility Index"},
        color_discrete_sequence=["#636EFA"],
    )
    fig.update_layout(yaxis_title="Node Count")
    return fig


def plotly_top_k(df: pd.DataFrame, k: int = 10) -> go.Figure:
    """Interactive bar chart of top-K critical nodes."""
    top = df.sort_values("normalized_fragility", ascending=False).head(k)
    fig = px.bar(
        top, x="node_id", y="normalized_fragility",
        title=f"Top {k} Most Critical Nodes",
        color="normalized_fragility",
        color_continuous_scale="Reds",
        labels={
            "node_id": "Node ID",
            "normalized_fragility": "Fragility Index",
        },
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig


def plotly_stress_curve(results: dict) -> go.Figure:
    """
    Plots the stress-fragility sensitivity curve.

    Parameters
    ----------
    results : dict
        Keys are stress levels, values are DataFrames.
    """
    rows = []
    for level, df in results.items():
        rows.append({
            "Stress Level": level,
            "Mean Fragility": df["normalized_fragility"].mean(),
            "Max Fragility": df["normalized_fragility"].max(),
        })
    curve_df = pd.DataFrame(rows)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=curve_df["Stress Level"], y=curve_df["Mean Fragility"],
        mode="lines+markers", name="Mean",
        line=dict(color="#EF553B", width=3),
    ))
    fig.add_trace(go.Scatter(
        x=curve_df["Stress Level"], y=curve_df["Max Fragility"],
        mode="lines+markers", name="Max",
        line=dict(color="#636EFA", width=2, dash="dot"),
    ))
    fig.update_layout(
        title="Stress–Fragility Sensitivity Curve",
        xaxis_title="Stress Level",
        yaxis_title="Fragility Index",
    )
    return fig


def plotly_convergence(convergence_data: list) -> go.Figure:
    """Plots convergence of Monte Carlo estimates."""
    df = pd.DataFrame(convergence_data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["n_cascades"], y=df["mean"],
        mode="lines+markers", name="Mean Impact",
        error_y=dict(type="data", array=df["std"].tolist(), visible=True),
    ))
    fig.update_layout(
        title="Monte Carlo Convergence Test",
        xaxis_title="Number of Iterations (N)",
        yaxis_title="Mean Cascade Size",
    )
    return fig


# ══════════════════════════════════════════════════
# MATPLOTLIB (Static) — Used by run_pipeline for PNGs
# ══════════════════════════════════════════════════

def save_histograms():
    """Saves static histogram PNGs for all stress levels."""
    config.ensure_directories()

    for level in config.STRESS_LEVELS:
        path = config.RESULTS_DIR / f"fragility_{level}.csv"
        if not path.exists():
            logger.warning("No results for %s", level)
            continue

        df = pd.read_csv(path)
        plt.figure(figsize=(8, 5))
        plt.hist(df["normalized_fragility"], bins=20, color="skyblue", edgecolor="black")
        plt.title(f"Fragility Distribution — {level.upper()} Stress")
        plt.xlabel("Normalized Fragility Index")
        plt.ylabel("Node Count")
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()

        out = config.FIGURES_DIR / "histograms" / f"fragility_{level}.png"
        plt.savefig(out, dpi=config.DPI)
        plt.close()
        logger.info("Saved: %s", out)


def save_heatmaps():
    """Saves static network heatmap PNGs."""
    config.ensure_directories()
    G = load_supplygraph()

    path = config.RESULTS_DIR / "fragility_medium.csv"
    if not path.exists():
        logger.warning("No medium results for heatmaps.")
        return

    df = pd.read_csv(path).set_index("node_id")
    frag_map = df["normalized_fragility"].to_dict()
    node_colors = [frag_map.get(n, 0.0) for n in G.nodes]

    layouts = {
        "spring": nx.spring_layout(G, seed=config.NETWORK_LAYOUT_SEED),
        "kamada_kawai": nx.kamada_kawai_layout(G),
        "circular": nx.circular_layout(G),
    }

    for name, pos in layouts.items():
        fig, ax = plt.subplots(figsize=(10, 8))
        nodes = nx.draw_networkx_nodes(
            G, pos, node_color=node_colors, cmap="YlOrRd",
            node_size=100, ax=ax,
        )
        nx.draw_networkx_edges(G, pos, alpha=0.2, width=0.5, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=5, ax=ax)
        fig.colorbar(nodes, ax=ax, label="Normalized Fragility")
        ax.set_title(f"Network Heatmap — {name} layout (medium stress)")
        ax.axis("off")
        plt.tight_layout()

        out = config.FIGURES_DIR / "heatmaps" / f"heatmap_{name}.png"
        plt.savefig(out, dpi=config.DPI)
        plt.close()
        logger.info("Saved: %s", out)


def save_topk(k: int = 10):
    """Saves top-K bar chart PNGs."""
    config.ensure_directories()

    for level in config.STRESS_LEVELS:
        path = config.RESULTS_DIR / f"fragility_{level}.csv"
        if not path.exists():
            continue

        df = pd.read_csv(path)
        topk = df.sort_values("normalized_fragility", ascending=False).head(k)

        plt.figure(figsize=(10, 5))
        plt.bar(topk["node_id"], topk["normalized_fragility"], color="salmon", edgecolor="black")
        plt.xticks(rotation=45, ha="right", fontsize=8)
        plt.ylabel("Normalized Fragility")
        plt.title(f"Top-{k} Most Fragile Nodes — {level.upper()} Stress")
        plt.tight_layout()

        out = config.FIGURES_DIR / "topk" / f"topk_{level}.png"
        plt.savefig(out, dpi=config.DPI)
        plt.close()
        logger.info("Saved: %s", out)


def save_all_figures():
    """Convenience function: generates all static figures."""
    save_histograms()
    save_heatmaps()
    save_topk()


if __name__ == "__main__":
    save_all_figures()