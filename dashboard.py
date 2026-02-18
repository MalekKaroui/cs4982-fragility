"""
dashboard.py
============
Interactive Streamlit Dashboard for the Fragility Modeling Framework.

Tabs:
    1. Overview — Histograms, Top-K charts, summary statistics
    2. Network Map — Interactive Plotly graph visualization
    3. Node Explorer — Per-node stress sensitivity analysis
    4. Convergence — Monte Carlo convergence verification
    5. Stress Curve — System-wide stress sensitivity

Usage:
    streamlit run dashboard.py

Author: Malek Karoui
Course: CS4982 - Winter 2026
"""

import os
import pandas as pd
import streamlit as st

import config
from supplygraph_loader import load_supplygraph, get_graph_summary
from gcsi_loader import GCSIStressModel
import visualize

# ── Page Config ──
st.set_page_config(
    page_title="Supply Chain Fragility Dashboard",
    page_icon="🏭",
    layout="wide",
)


# ── Data Loading (Cached) ──
@st.cache_data
def load_results():
    """Load precomputed fragility results from CSV files."""
    data = {}
    for level in config.STRESS_LEVELS:
        path = config.RESULTS_DIR / f"fragility_{level}.csv"
        if path.exists():
            data[level] = pd.read_csv(path)
    return data


@st.cache_resource
def load_graph():
    """Load and cache the dependency graph."""
    return load_supplygraph()


@st.cache_data
def load_convergence():
    """Load convergence test results."""
    path = config.RESULTS_DIR / "convergence_test.csv"
    if path.exists():
        return pd.read_csv(path)
    return None


# ── Load Everything ──
results = load_results()
G = load_graph()
stress_model = GCSIStressModel()
graph_summary = get_graph_summary(G)
conv_data = load_convergence()

# ── Header ──
st.title("🏭 Operational Fragility Modeling Framework")
st.caption("CS4982 — Winter 2026 | Malek Karoui | University of New Brunswick")

if not results:
    st.error(
        "⚠️ No results found. Please run the pipeline first:\n\n"
        "```\npython run_pipeline.py\n```"
    )
    st.stop()

# ── Sidebar ──
st.sidebar.header("⚙️ Configuration")
selected_level = st.sidebar.selectbox("Stress Scenario", config.STRESS_LEVELS, index=1)
k_val = st.sidebar.slider("Top-K Critical Nodes", 5, 41, config.TOP_K_DEFAULT)

st.sidebar.divider()
st.sidebar.subheader("📊 Graph Properties")
for key, val in graph_summary.items():
    st.sidebar.metric(key.replace("_", " ").title(), val)

st.sidebar.divider()
st.sidebar.subheader("📈 GSCSI Stress Model")
stress_summary = stress_model.get_summary()
for level in config.STRESS_LEVELS:
    mult = stress_model.get_multiplier(level)
    st.sidebar.metric(f"{level.title()} Multiplier", f"{mult:.3f}x")

# ── Current Data ──
current_df = results[selected_level]

# ══════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "🌐 Network Map",
    "🔍 Node Explorer",
    "📉 Convergence",
    "📈 Stress Curve",
])

# ── TAB 1: Overview ──
with tab1:
    st.header(f"Fragility Overview — {selected_level.upper()} Stress")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Mean Fragility", f"{current_df['normalized_fragility'].mean():.4f}")
    col2.metric("Max Fragility", f"{current_df['normalized_fragility'].max():.4f}")
    col3.metric("Min Fragility", f"{current_df['normalized_fragility'].min():.4f}")
    col4.metric("Std Dev", f"{current_df['normalized_fragility'].std():.4f}")

    # Charts
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(
            visualize.plotly_histogram(current_df, selected_level),
            use_container_width=True,
        )
    with chart_col2:
        st.plotly_chart(
            visualize.plotly_top_k(current_df, k_val),
            use_container_width=True,
        )

    # Raw data table
    with st.expander("📋 View Full Results Table"):
        st.dataframe(
            current_df.sort_values("normalized_fragility", ascending=False),
            use_container_width=True,
            height=300,
        )

# ── TAB 2: Network Map ──
with tab2:
    st.header(f"Interactive Network Heatmap — {selected_level.upper()} Stress")
    st.caption("Node size and color represent fragility. Hover for details. Zoom and pan supported.")

    fig = visualize.plotly_network_map(G, current_df)
    st.plotly_chart(fig, use_container_width=True, height=700)

# ── TAB 3: Node Explorer ──
with tab3:
    st.header("Single Node Analysis")

    node_list = sorted(current_df["node_id"].unique())
    selected_node = st.selectbox("Select a node", node_list)

    # Gather data across all stress levels
    comparison_rows = []
    for level in config.STRESS_LEVELS:
        if level in results:
            row = results[level][results[level]["node_id"] == selected_node]
            if not row.empty:
                r = row.iloc[0]
                comparison_rows.append({
                    "Stress Level": level,
                    "Normalized Fragility": r["normalized_fragility"],
                    "Raw Impact (Nodes)": r["raw_fragility"],
                    "Std Dev": r["std"],
                    "Min Impact": r.get("min_impact", "N/A"),
                    "Max Impact": r.get("max_impact", "N/A"),
                })

    if comparison_rows:
        comp_df = pd.DataFrame(comparison_rows)

        col_table, col_chart = st.columns([1, 2])

        with col_table:
            st.subheader(f"Profile: `{selected_node}`")
            st.table(comp_df)

            # Graph metrics for this node
            st.markdown("**Graph Properties:**")
            st.write(f"- Out-degree: {G.out_degree(selected_node)}")
            st.write(f"- In-degree: {G.in_degree(selected_node)}")
            successors = list(G.successors(selected_node))
            st.write(f"- Direct dependents: {len(successors)}")

        with col_chart:
            import plotly.express as px

            fig = px.line(
                comp_df,
                x="Stress Level",
                y="Normalized Fragility",
                markers=True,
                title=f"Stress Sensitivity — {selected_node}",
            )
            fig.update_traces(line=dict(width=3))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Node not found in results.")

# ── TAB 4: Convergence ──
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
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📋 Convergence Data"):
            st.dataframe(conv_data)
    else:
        st.info("No convergence data found. Run `python run_pipeline.py` to generate it.")

# ── TAB 5: Stress Curve ──
with tab5:
    st.header("System-Wide Stress Sensitivity")
    st.markdown(
        """
        This curve shows how the **average** and **maximum** fragility
        across all nodes changes as global stress increases.
        A steep rise indicates the network is highly sensitive to stress.
        """
    )

    if len(results) >= 2:
        fig = visualize.plotly_stress_curve(results)
        st.plotly_chart(fig, use_container_width=True)

        # Amplification factor
        if "low" in results and "high" in results:
            low_mean = results["low"]["normalized_fragility"].mean()
            high_mean = results["high"]["normalized_fragility"].mean()
            if low_mean > 0:
                amp = high_mean / low_mean
                st.metric(
                    "Stress Amplification Factor (High / Low)",
                    f"{amp:.2f}x",
                    help="How much worse fragility gets from low to high stress.",
                )
    else:
        st.info("Need results for at least 2 stress levels.")

# ── Footer ──
st.sidebar.divider()
st.sidebar.caption("Built for CS4982 — University of New Brunswick")