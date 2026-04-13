"""
supplygraph_loader.py
=====================
Dependency Graph Construction and Preprocessing Module.

Loads node.csv + edge.csv, maps indices to node names, normalizes edge weights,
and constructs a NetworkX DiGraph.

Author: Malek Karoui
Course: CS4982 - Winter 2026
"""

from typing import Dict

import numpy as np
import pandas as pd
import networkx as nx

from . import config

logger = config.setup_logging()


def _load_node_mapping(path=None) -> Dict[int, str]:
    """
    Reads node.csv and creates a mapping from row index to node name.
    Expects a column named 'Node'.
    """
    csv_path = path or config.NODE_CSV

    if not csv_path.exists():
        raise FileNotFoundError(f"Node file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    if df.empty:
        raise ValueError("Node CSV is empty.")
    if "Node" not in df.columns:
        raise ValueError("Node CSV must contain a 'Node' column.")

    mapping = df["Node"].to_dict()
    logger.info("Loaded %d node names from %s", len(mapping), csv_path)
    return mapping


def _load_edges(path=None) -> pd.DataFrame:
    """
    Reads edge.csv and normalizes the Storage Location column into propagation weights.
    Expects columns: node1, node2, Storage Location
    """
    csv_path = path or config.EDGE_CSV

    if not csv_path.exists():
        raise FileNotFoundError(f"Edge file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    required_cols = {"Storage Location", "node1", "node2"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Edge CSV must contain columns: {required_cols}")

    sl = df["Storage Location"]
    sl_min, sl_max = sl.min(), sl.max()

    if sl_max == sl_min:
        df["weight"] = (config.WEIGHT_MIN + config.WEIGHT_MAX) / 2
    else:
        normalized = (sl - sl_min) / (sl_max - sl_min)
        df["weight"] = config.WEIGHT_MIN + normalized * (config.WEIGHT_MAX - config.WEIGHT_MIN)

    logger.info(
        "Loaded %d edges, weight range [%.3f, %.3f]",
        len(df), df["weight"].min(), df["weight"].max(),
    )
    return df


def load_supplygraph() -> nx.DiGraph:
    """Construct the full directed dependency graph."""
    config.ensure_directories()

    id_to_name = _load_node_mapping()
    edges_df = _load_edges()

    G = nx.DiGraph()

    # Add nodes with baseline failure probabilities
    rng = np.random.default_rng(config.RANDOM_SEED)
    for idx, name in id_to_name.items():
        prob = rng.uniform(config.BASE_FAIL_PROB_MIN, config.BASE_FAIL_PROB_MAX)
        G.add_node(name, label=name, failure_prob=round(float(prob), 4))

    # Add edges using the index-to-name mapping
    skipped = 0
    for _, row in edges_df.iterrows():
        try:
            src = id_to_name.get(int(row["node1"]))
            tgt = id_to_name.get(int(row["node2"]))

            if src and tgt:
                w = round(float(row["weight"]), 4)
                if G.has_edge(src, tgt):
                    existing = G[src][tgt]["weight"]
                    G[src][tgt]["weight"] = max(existing, w)
                else:
                    G.add_edge(src, tgt, weight=w)
            else:
                skipped += 1
        except (ValueError, KeyError):
            skipped += 1

    if skipped > 0:
        logger.warning("Skipped %d edges (unmapped indices).", skipped)

    logger.info("Graph constructed: %d nodes, %d edges.", G.number_of_nodes(), G.number_of_edges())
    return G


def get_graph_summary(G: nx.DiGraph) -> dict:
    """
    Returns a summary dictionary of graph properties.

    Backward-compatible keys expected by scripts (e.g., run_pipeline.py):
    - is_weakly_connected
    - weakly_connected_components
    - avg_in_degree / avg_out_degree
    """
    n = G.number_of_nodes()
    m = G.number_of_edges()

    # nx.is_weakly_connected throws on empty graphs
    is_wcc = nx.is_weakly_connected(G) if n > 0 else False
    num_wcc = nx.number_weakly_connected_components(G) if n > 0 else 0

    avg_in = sum(d for _, d in G.in_degree()) / max(n, 1)
    avg_out = sum(d for _, d in G.out_degree()) / max(n, 1)

    return {
        "nodes": n,
        "edges": m,
        "density": round(nx.density(G), 4),
        "is_weakly_connected": is_wcc,
        "weakly_connected_components": num_wcc,
        "avg_in_degree": round(avg_in, 2),
        "avg_out_degree": round(avg_out, 2),
        "sink_nodes": sum(1 for v in G.nodes if G.out_degree(v) == 0),
        "source_nodes": sum(1 for v in G.nodes if G.in_degree(v) == 0),
    }