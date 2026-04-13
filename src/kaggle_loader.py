"""
kaggle_loader.py
================
Builds a directed operational supply chain graph from the Kaggle dataset.

Graph design (layered):
  SUP::<Supplier>  ->  SKU::<SKU>  ->  CUST::<Segment>

This is a simplified operational representation to compare against the
dense SupplyGraph benchmark family.

Author: Malek Karoui
Course: CS4982 - Winter 2026
"""

from __future__ import annotations

from typing import Dict, Tuple, Optional
from pathlib import Path
import logging

import pandas as pd
import networkx as nx

from . import config

logger = config.setup_logging()


def _detect_column(df: pd.DataFrame, candidates) -> Optional[str]:
    """Return first matching column name from candidates, else None."""
    for c in candidates:
        if c in df.columns:
            return c
    return None


def load_kaggle_supplychain_graph(csv_path: Optional[str | Path] = None) -> nx.DiGraph:
    """
    Load Kaggle supply-chain operations dataset and transform into a directed graph.

    Returns
    -------
    nx.DiGraph
        Node naming convention:
          - SUP::<supplier>
          - SKU::<sku>
          - CUST::<segment>
    """
    csv_path = Path(csv_path) if csv_path else config.KAGGLE_CSV
    if not csv_path.exists():
        raise FileNotFoundError(f"Kaggle dataset not found: {csv_path}")

    df = pd.read_csv(csv_path)

    # Try to detect columns robustly (Kaggle datasets vary)
    supplier_col = _detect_column(df, ["Supplier name", "supplier", "Supplier", "Supplier Name", "supplier_name"])
    sku_col = _detect_column(df, ["SKU", "sku", "Sku", "Product SKU", "product_sku", "Product"])
    customer_col = _detect_column(df, ["Customer demographics", "customer", "Customer", "Customer Segment", "segment"])

    # If your dataset has exact names from your report, these should resolve:
    # supplier_col = "Supplier name"
    # sku_col = "SKU"
    # customer_col = "Customer demographics"

    if supplier_col is None or sku_col is None or customer_col is None:
        raise ValueError(
            "Could not detect required columns in Kaggle CSV.\n"
            f"Detected: supplier={supplier_col}, sku={sku_col}, customer={customer_col}\n"
            f"Available columns: {list(df.columns)}"
        )

    # Clean strings
    df = df.dropna(subset=[supplier_col, sku_col, customer_col]).copy()
    df[supplier_col] = df[supplier_col].astype(str).str.strip()
    df[sku_col] = df[sku_col].astype(str).str.strip()
    df[customer_col] = df[customer_col].astype(str).str.strip()

    G = nx.DiGraph()

    # Add edges supplier -> sku and sku -> customer
    # Use simple weight=1.0 (or could scale by revenue/quantity if desired)
    for _, row in df.iterrows():
        sup = f"SUP::{row[supplier_col]}"
        sku = f"SKU::{row[sku_col]}"
        cust = f"CUST::{row[customer_col]}"

        G.add_node(sup, layer="supplier")
        G.add_node(sku, layer="sku")
        G.add_node(cust, layer="customer")

        # Dependency edges
        if sup != sku:
            G.add_edge(sup, sku, weight=1.0)
        if sku != cust:
            G.add_edge(sku, cust, weight=1.0)

    logger.info(
        "Kaggle graph built: %d nodes, %d edges (csv=%s)",
        G.number_of_nodes(), G.number_of_edges(), csv_path
    )
    return G


def get_kaggle_graph_summary(G: nx.DiGraph) -> Dict[str, float]:
    """Basic summary for printing/reporting."""
    n = G.number_of_nodes()
    m = G.number_of_edges()
    density = nx.density(G) if n > 1 else 0.0

    suppliers = sum(1 for _, d in G.nodes(data=True) if d.get("layer") == "supplier")
    skus = sum(1 for _, d in G.nodes(data=True) if d.get("layer") == "sku")
    customers = sum(1 for _, d in G.nodes(data=True) if d.get("layer") == "customer")

    return {
        "nodes": n,
        "edges": m,
        "density": round(density, 6),
        "supplier_nodes": suppliers,
        "sku_nodes": skus,
        "customer_nodes": customers,
        "weakly_connected_components": nx.number_weakly_connected_components(G) if n > 0 else 0,
    }