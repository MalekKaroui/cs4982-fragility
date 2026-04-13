"""
dashboard.py
============
Interactive Streamlit Dashboard for the Fragility Modeling Framework.

Run:
    streamlit run src/dashboard.py

Author: Malek Karoui
Course: CS4982 - Winter 2026
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# -------------------------------------------------------------------
# Make imports work when Streamlit runs this file as a standalone script
# -------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src import config
from src.supplygraph_loader import load_supplygraph, get_graph_summary
from src.gcsi_loader import GCSIStressModel
from src import visualize


# -----------------------
# Streamlit Page Config
# -----------------------
st.set_page_config(
    page_title="Supply Chain Fragility Dashboard",
    page_icon="🏭",
    layout="wide",
)

# Ensure output folders exist (safe)
try:
    config.ensure_directories()
except Exception:
    pass


# -----------------------
# Cached Loaders
# -----------------------
@st.cache_data(show_spinner=False)
def load_results():
    """
    Load precomputed fragility results from CSV files.

    Priority per stress level:
      1) results/fragility_{level}.csv
      2) results/fragility_original_{level}.csv
    """
    data = {}

    for level in getattr(config, "STRESS_LEVELS", ["low", "medium", "high"]):
        level = str(level).lower()

        primary = config.RESULTS_DIR / f"fragility_{level}.csv"
        fallback = config.RESULTS_DIR / f"fragility_original_{level}.csv"

        if primary.exists():
            df = pd.read_csv(primary)
            df["__source_file__"] = primary.name
            data[level] = df
        elif fallback.exists():
            df = pd.read_csv(fallback)
            df["__source_file__"] = fallback.name
            data[level] = df

    return data


@st.cache_resource(show_spinner=False)
def load_graph():
    """Load and cache the dependency graph."""
    return load_supplygraph()


@st.cache_data(show_spinner=False)
def load_convergence():
    """Load convergence test results."""
    path = config.RESULTS_DIR / "convergence_test.csv"
    if path.exists():
        return pd.read_csv(path)
    return None


# -----------------------
# Load Data
# -----------------------
results = load_results()
G = load_graph()
stress_model = GCSIStressModel()
graph_summary = get_graph_summary(G)
conv_data = load_convergence()

# -----------------------
# Header
# -----------------------
st.title("🏭 Operational Fragility Modeling Framework")
st.caption("CS4982 — Winter 2026 | Malek Karoui | University of New Brunswick")

if not results:
    st.error(
        "No fragility results found in the results/ folder.\n\n"
        "Generate results using one of these commands:\n\n"
        "• `python scripts/run_pipeline.py`  (generates fragility_low/medium/high)\n"
        "• `python scripts/compare_networks.py` (generates fragility_original_* and variants)\n"
    )
    st.stop()

# -----------------------
# Sidebar
# -----------------------
st.sidebar.header("Configuration")

stress_levels = list(results.keys())
default_index = stress_levels.index("medium") if "medium" in stress_levels else 0

selected_level = st.sidebar.selectbox("Stress Scenario", stress_levels, index=default_index)

k_default = getattr(config, "TOP_K_DEFAULT", 10)
k_val = st.sidebar.slider("Top-K Critical Nodes", 5, max(10, min(50, G.number_of_nodes())), int(k_default))

st.sidebar.divider()
st.sidebar.subheader("Graph Properties")
for key, val in graph_summary.items():
    st.sidebar.metric(key.replace("_", " ").title(), val)

st.sidebar.divider()
st.sidebar.subheader("GSCSI Stress Model")
stress_summary = stress_model.get_summary()
for level in ["low", "medium", "high"]:
    try:
        mult = stress_model.get_multiplier(level)
        st.sidebar.metric(f"{level.title()} Multiplier", f"{mult:.3f}x")
    except Exception:
        pass

# Current results DF
current_df = results[selected_level].copy()

# Basic validation
required_cols = {"node_id", "normalized_fragility", "raw_fragility"}
missing = required_cols - set(current_df.columns)
if missing:
    st.error(
        "Results file is missing required columns.\n\n"
        f"Missing: {sorted(missing)}\n\n"
        f"Loaded file: {current_df.get('__source_file__', pd.Series(['unknown'])).iloc[0] if '__source_file__' in current_df.columns else 'unknown'}"
    )
    st.stop()

# -----------------------
# Tabs
# -----------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Overview", "Network Map", "Node Explorer", "Convergence", "Stress Curve"]
)

# -----------------------
# TAB 1: Overview
# -----------------------
with tab1:
    st.header(f"Fragility Overview — {selected_level.upper()} Stress")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Mean Fragility", f"{current_df['normalized_fragility'].mean():.4f}")
    col2.metric("Max Fragility", f"{current_df['normalized_fragility'].max():.4f}")
    col3.metric("Min Fragility", f"{current_df['normalized_fragility'].min():.4f}")
    col4.metric("Std Dev", f"{current_df['normalized_fragility'].std():.4f}")

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(
            visualize.plotly_histogram(current_df, selected_level),
            width="stretch",
        )
    with chart_col2:
        st.plotly_chart(
            visualize.plotly_top_k(current_df, k_val),
            width="stretch",
        )

    with st.expander("View Full Results Table"):
        st.dataframe(
            current_df.sort_values("normalized_fragility", ascending=False),
            width="stretch",
            height=350,
        )

    if "__source_file__" in current_df.columns:
        st.caption(f"Loaded results from: `{current_df['__source_file__'].iloc[0]}`")

# -----------------------
# TAB 2: Network Map
# -----------------------
with tab2:
    st.header(f"Interactive Network Heatmap — {selected_level.upper()} Stress")
    st.caption("Node size and color represent fragility. Hover for details. Zoom and pan supported.")

    fig = visualize.plotly_network_map(G, current_df)
    st.plotly_chart(fig, width="stretch")

# -----------------------
# TAB 3: Node Explorer
# -----------------------
with tab3:
    st.header("Single Node Analysis")

    node_list = sorted(current_df["node_id"].astype(str).unique())
    selected_node = st.selectbox("Select a node", node_list)

    comparison_rows = []
    for level, df in results.items():
        df2 = df[df["node_id"].astype(str) == str(selected_node)]
        if not df2.empty:
            r = df2.iloc[0]
            comparison_rows.append(
                {
                    "Stress Level": level,
                    "Normalized Fragility": float(r["normalized_fragility"]),
                    "Raw Impact (Nodes)": float(r["raw_fragility"]),
                    "Std Dev": float(r.get("std", 0.0)),
                    "Min Impact": r.get("min_impact", "N/A"),
                    "Max Impact": r.get("max_impact", "N/A"),
                }
            )

    if comparison_rows:
        comp_df = pd.DataFrame(comparison_rows)

        col_table, col_chart = st.columns([1, 2])

        with col_table:
            st.subheader(f"Profile: `{selected_node}`")
            st.table(comp_df)

            st.markdown("**Graph Properties:**")
            if selected_node in G:
                st.write(f"- Out-degree: {G.out_degree(selected_node)}")
                st.write(f"- In-degree: {G.in_degree(selected_node)}")
                successors = list(G.successors(selected_node))
                st.write(f"- Direct dependents: {len(successors)}")
            else:
                st.warning("Selected node not found in graph (label mismatch).")

        with col_chart:
            import plotly.express as px

            fig = px.line(
                comp_df.sort_values("Stress Level"),
                x="Stress Level",
                y="Normalized Fragility",
                markers=True,
                title=f"Stress Sensitivity — {selected_node}",
            )
            fig.update_traces(line=dict(width=3))
            st.plotly_chart(fig, width="stretch")
    else:
        st.warning("Node not found in results across stress levels.")

# -----------------------
# TAB 4: Convergence
# -----------------------
with tab4:
    st.header("Monte Carlo Convergence Analysis")
    st.markdown(
        """
This test verifies that the Fragility Index stabilizes as the number
of Monte Carlo iterations increases. A flat curve at higher N values
indicates convergence and reliable estimates.
"""
    )

    if conv_data is not None and not conv_data.empty:
        fig = visualize.plotly_convergence(conv_data.to_dict("records"))
        st.plotly_chart(fig, width="stretch")

        with st.expander("Convergence Data"):
            st.dataframe(conv_data, width="stretch")
    else:
        st.info("No convergence data found. Run: `python scripts/run_pipeline.py` to generate it.")

# -----------------------
# TAB 5: Stress Curve
# -----------------------
with tab5:
    st.header("System-Wide Stress Sensitivity")
    st.markdown(
        """
This curve shows how the average and maximum fragility across all nodes changes as global stress increases.
A steep rise indicates the network is highly sensitive to stress.
"""
    )

    if len(results) >= 2:
        fig = visualize.plotly_stress_curve(results)
        st.plotly_chart(fig, width="stretch")

        if "low" in results and "high" in results:
            low_mean = results["low"]["normalized_fragility"].mean()
            high_mean = results["high"]["normalized_fragility"].mean()
            if low_mean > 0:
                amp = high_mean / low_mean
                st.metric("Stress Amplification Factor (High / Low)", f"{amp:.2f}x")
    else:
        st.info("Need results for at least 2 stress levels.")

# Footer
st.sidebar.divider()
st.sidebar.caption("Built for CS4982 — University of New Brunswick")