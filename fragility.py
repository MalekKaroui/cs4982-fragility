"""
fragility.py
============
Monte Carlo Cascading Failure Simulation Engine.

Implements the core simulation logic described in the project proposal:
    F(v) = (1/N) * Σ C_i(v)
where C_i(v) is the number of nodes affected in trial i.

The engine supports:
    - Per-node conditional fragility (trigger a specific node)
    - Stress-sensitive propagation (GSCSI multipliers)
    - Edge-weight-based probabilistic propagation
    - Statistical convergence analysis

References:
    Watts (2002). A simple model of global cascades on random networks.
    Motter & Lai (2002). Cascade-based attacks on complex networks.

Author: Malek Karoui
Course: CS4982 - Winter 2026
"""

import random
from collections import deque
from typing import Dict, List, Optional

import numpy as np
import networkx as nx

import config
from gcsi_loader import get_stress_multiplier

logger = config.setup_logging()


def simulate_cascade(
    G: nx.DiGraph,
    seed_node: str,
    stress_multiplier: float = 1.0,
    rng: random.Random = None,
) -> int:
    """
    Simulates a single cascading failure event from a seed node.

    The cascade follows a BFS propagation model:
    for each edge (u, v) where u has failed, v fails with probability
    w(u,v) * stress_multiplier.

    Parameters
    ----------
    G : nx.DiGraph
        The supply chain dependency graph.
    seed_node : str
        The node that initially fails.
    stress_multiplier : float
        Global stress factor applied to all propagation probabilities.
    rng : random.Random, optional
        Random number generator for reproducibility.

    Returns
    -------
    int
        Total number of nodes that failed (including the seed).

    Raises
    ------
    ValueError
        If seed_node is not in the graph.
    """
    if seed_node not in G:
        raise ValueError(f"Node '{seed_node}' not found in graph.")

    if rng is None:
        rng = random.Random()

    failed = {seed_node}
    queue = deque([seed_node])

    while queue:
        u = queue.popleft()
        for v in G.successors(u):
            if v in failed:
                continue

            # Edge propagation probability * stress
            edge_weight = G[u][v].get("weight", 0.5)
            p_propagate = min(edge_weight * stress_multiplier, 1.0)

            if rng.random() < p_propagate:
                failed.add(v)
                queue.append(v)

    return len(failed)


def compute_node_fragility(
    G: nx.DiGraph,
    node_id: str,
    stress_level: str = "medium",
    n_cascades: int = None,
) -> dict:
    """
    Computes the Fragility Index for a single node.

    F(v) = (1/N) * Σ C_i(v)

    Parameters
    ----------
    G : nx.DiGraph
        The dependency graph.
    node_id : str
        The node to evaluate.
    stress_level : str
        One of 'low', 'medium', 'high'.
    n_cascades : int
        Number of Monte Carlo iterations.

    Returns
    -------
    dict
        Contains node_id, stress_level, raw_fragility,
        normalized_fragility, std, min_impact, max_impact.
    """
    if n_cascades is None:
        n_cascades = config.DEFAULT_N_CASCADES

    stress_mult = get_stress_multiplier(stress_level)
    rng = random.Random(config.RANDOM_SEED)
    total_nodes = G.number_of_nodes()

    cascade_sizes = np.empty(n_cascades, dtype=np.float64)

    for i in range(n_cascades):
        # Subtract 1 to exclude the seed node itself
        impact = simulate_cascade(G, node_id, stress_mult, rng) - 1
        cascade_sizes[i] = max(0, impact)

    raw = float(cascade_sizes.mean())
    normalized = raw / max(total_nodes - 1, 1)  # Scale to [0, 1]

    return {
        "node_id": node_id,
        "stress_level": stress_level,
        "raw_fragility": round(raw, 4),
        "normalized_fragility": round(normalized, 6),
        "std": round(float(cascade_sizes.std()), 4),
        "min_impact": int(cascade_sizes.min()),
        "max_impact": int(cascade_sizes.max()),
    }


def compute_fragility_all(
    G: nx.DiGraph,
    stress_level: str = "medium",
    n_cascades: int = None,
) -> List[dict]:
    """
    Computes the Fragility Index for every node in the graph.

    Parameters
    ----------
    G : nx.DiGraph
        The dependency graph.
    stress_level : str
        Stress scenario.
    n_cascades : int
        Monte Carlo iterations per node.

    Returns
    -------
    list of dict
        Fragility results for all nodes.
    """
    if n_cascades is None:
        n_cascades = config.DEFAULT_N_CASCADES

    nodes = list(G.nodes())
    total = len(nodes)
    results = []

    logger.info(
        "Computing fragility for %d nodes | stress=%s | iterations=%d",
        total, stress_level, n_cascades,
    )

    for i, node in enumerate(nodes):
        result = compute_node_fragility(G, node, stress_level, n_cascades)
        results.append(result)

        # Progress logging every 10 nodes
        if (i + 1) % 10 == 0 or (i + 1) == total:
            logger.info("  Progress: %d/%d nodes complete.", i + 1, total)

    return results


def convergence_test(
    G: nx.DiGraph,
    test_node: str = None,
    stress_level: str = "medium",
    sample_sizes: list = None,
) -> List[dict]:
    """
    Tests whether the Monte Carlo estimate converges as N increases.

    This is a key validation step — if the Fragility Index stabilizes
    as we increase iterations, the estimate is reliable.

    Parameters
    ----------
    G : nx.DiGraph
        The dependency graph.
    test_node : str, optional
        Node to test. Defaults to the node with highest out-degree.
    stress_level : str
        Stress scenario.
    sample_sizes : list of int
        Iteration counts to test.

    Returns
    -------
    list of dict
        Each entry contains 'n_cascades', 'mean', 'std'.
    """
    if test_node is None:
        # Pick the node with highest out-degree
        test_node = max(G.nodes(), key=lambda n: G.out_degree(n))

    if sample_sizes is None:
        sample_sizes = config.CONVERGENCE_SAMPLE_SIZES

    logger.info("Running convergence test on node '%s'", test_node)

    results = []
    for n in sample_sizes:
        res = compute_node_fragility(G, test_node, stress_level, n_cascades=n)
        results.append({
            "n_cascades": n,
            "mean": res["raw_fragility"],
            "std": res["std"],
            "normalized": res["normalized_fragility"],
        })
        logger.info("  N=%d → mean=%.3f, std=%.3f", n, res["raw_fragility"], res["std"])

    return results


if __name__ == "__main__":
    from supplygraph_loader import load_supplygraph

    G = load_supplygraph()

    # Quick test: compute fragility for one node
    first_node = list(G.nodes())[0]
    result = compute_node_fragility(G, first_node, "medium", n_cascades=100)
    print(f"\nTest result for '{first_node}':")
    for k, v in result.items():
        print(f"  {k}: {v}")