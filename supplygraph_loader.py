"""
supplygraph_loader.py
=====================
Dependency Graph Construction and Preprocessing Module.

Loads the SupplyGraph benchmark dataset (node.csv + edge.csv),
maps integer indices to named assets, normalizes edge weights,
and constructs a NetworkX DiGraph.

Design Reference:
    Section 3.1 of the project proposal — G = (V, E) where
    V = operational assets, E = dependency relationships.

Author: Malek Karoui
Course: CS4982 - Winter 2026
"""

from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
import networkx as nx

import config

logger = config.setup_logging()


def _load_node_mapping(path: str = None) -> Dict[int, str]:
    """
    Reads node.csv and creates a mapping from row index to node name.

    Parameters
    ----------
    path : str, optional
        Path to node CSV file.

    Returns
    -------
    dict
        Mapping {integer_index: node_name_string}.

    Raises
    ------
    FileNotFoundError
        If the node CSV does not exist.
    ValueError
        If the CSV is empty or missing the 'Node' column.
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


def _load_edges(path: str = None) -> pd.DataFrame:
    """
    Reads edge.csv and normalizes the Storage Location column
    into propagation weights.

    Parameters
    ----------
    path : str, optional
        Path to edge CSV file.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns [node1, node2, weight].
    """
    csv_path = path or config.EDGE_CSV

    if not csv_path.exists():
        raise FileNotFoundError(f"Edge file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    required_cols = {"Storage Location", "node1", "node2"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Edge CSV must contain columns: {required_cols}")

    # Normalize Storage Location → propagation weight
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
    """
    Constructs the full directed dependency graph.

    This is the primary public function of this module.
    It loads nodes and edges, maps integer indices to string names,
    and returns a NetworkX DiGraph with node/edge attributes.

    Returns
    -------
    nx.DiGraph
        Directed graph with attributes:
        - Node: 'label', 'failure_prob'
        - Edge: 'weight' (propagation probability)

    Example
    -------
    >>> G = load_supplygraph()
    >>> G.number_of_nodes()
    41
    """
    id_to_name = _load_node_mapping()
    edges_df = _load_edges()

    G = nx.DiGraph()

    # Add nodes with baseline failure probabilities
    rng = np.random.default_rng(config.RANDOM_SEED)
    for idx, name in id_to_name.items():
        prob = rng.uniform(config.BASE_FAIL_PROB_MIN, config.BASE_FAIL_PROB_MAX)
        G.add_node(name, label=name, failure_prob=round(prob, 4))

    # Add edges using the index-to-name mapping
    skipped = 0
    for _, row in edges_df.iterrows():
        try:
            src = id_to_name.get(int(row["node1"]))
            tgt = id_to_name.get(int(row["node2"]))

            if src and tgt:
                # If edge already exists, keep the higher weight
                if G.has_edge(src, tgt):
                    existing = G[src][tgt]["weight"]
                    G[src][tgt]["weight"] = max(existing, row["weight"])
                else:
                    G.add_edge(src, tgt, weight=round(row["weight"], 4))
            else:
                skipped += 1
        except (ValueError, KeyError):
            skipped += 1

    if skipped > 0:
        logger.warning("Skipped %d edges (unmapped indices).", skipped)

    logger.info(
        "Graph constructed: %d nodes, %d edges.",
        G.number_of_nodes(), G.number_of_edges(),
    )
    return G


def get_graph_summary(G: nx.DiGraph) -> dict:
    """
    Returns a summary dictionary of graph properties.

    Useful for diagnostics and the dashboard sidebar.
    """
    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "density": round(nx.density(G), 4),
        "is_weakly_connected": nx.is_weakly_connected(G),
        "weakly_connected_components": nx.number_weakly_connected_components(G),
        "avg_in_degree": round(
            sum(d for _, d in G.in_degree()) / max(G.number_of_nodes(), 1), 2
        ),
        "avg_out_degree": round(
            sum(d for _, d in G.out_degree()) / max(G.number_of_nodes(), 1), 2
        ),
    }


if __name__ == "__main__":
    G = load_supplygraph()
    summary = get_graph_summary(G)
    for k, v in summary.items():
        print(f"  {k}: {v}")