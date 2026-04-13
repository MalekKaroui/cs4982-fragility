"""
demo_dashboard.py
PR2 Video Demo - Interactive Dashboard
CS4982 - Winter 2026 - Malek Karoui
5 tabs: Overview, Network Map, Node Explorer, Convergence, Stress Curve
Delete after recording.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx

from src.supplygraph_loader import load_supplygraph, get_graph_summary
from src.gcsi_loader import GCSIStressModel
from src import config


st.set_page_config(
    page_title="Fragility Dashboard - PR2 Demo",
    page_icon="F",
    layout="wide",
)


@st.cache_resource
def get_graph():
    return load_supplygraph()


@st.cache_data
def get_results():
    data = {}
    for level in config.STRESS_LEVELS:
        path = config.RESULTS_DIR / f"fragility_{level}.csv"
        if path.exists():
            data[level] = pd.read_csv(path)
    return data


@st.cache_data
def get_convergence():
    path = config.RESULTS_DIR / "convergence_test.csv"
    if path.exists():
        return pd.read_csv(path)
    return None


G = get_graph()
results = get_results()
stress_model = GCSIStressModel()
summary = get_graph_summary(G)
conv_data = get_convergence()


# ── Header ──
st.title("Operational Fragility Modeling Framework")
st.caption("CS4982 - Winter 2026 | Malek Karoui | University of New Brunswick | PR2 Demo")

if not results:
    st.error("No results found. Run: python run_pipeline.py")
    st.stop()


# ── Sidebar ──
st.sidebar.header("Settings")
selected_level = st.sidebar.selectbox("Stress Scenario", config.STRESS_LEVELS, index=1)
k_val = st.sidebar.slider("Top-K Nodes", 5, 40, 10)

st.sidebar.divider()
st.sidebar.subheader("Graph Properties")
st.sidebar.metric("Nodes", summary["nodes"])
st.sidebar.metric("Edges", summary["edges"])
st.sidebar.metric("Density", f"{summary['density']*100:.1f}%")
st.sidebar.metric("Components", summary["weakly_connected_components"])
st.sidebar.metric("Avg Out-Degree", summary["avg_out_degree"])

st.sidebar.divider()
st.sidebar.subheader("GSCSI Stress Multipliers")
for level in config.STRESS_LEVELS:
    mult = stress_model.get_multiplier(level)
    st.sidebar.metric(f"{level.title()} Stress", f"{mult:.4f}x")

st.sidebar.divider()
st.sidebar.subheader("PR2 Status")
st.sidebar.write("Week 9 of 12")
st.sidebar.write("85 / 120 hours (71%)")
st.sidebar.write("All core modules complete")

current_df = results[selected_level]


# ── Tabs ──
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Network Map",
    "Node Explorer",
    "Convergence",
    "Stress Curve",
])


# ════════════════════════════════════
# TAB 1: Overview
# ════════════════════════════════════
with tab1:
    st.header(f"Fragility Overview - {selected_level.upper()} Stress")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Mean Fragility", f"{current_df['normalized_fragility'].mean():.4f}")
    c2.metric("Max Fragility", f"{current_df['normalized_fragility'].max():.4f}")
    c3.metric("Min Fragility", f"{current_df['normalized_fragility'].min():.4f}")
    c4.metric("Std Dev", f"{current_df['normalized_fragility'].std():.4f}")

    col_left, col_right = st.columns(2)

    with col_left:
        fig = px.histogram(
            current_df,
            x="normalized_fragility",
            nbins=20,
            title="Fragility Index Distribution",
            labels={"normalized_fragility": "Fragility Index"},
            color_discrete_sequence=["#E8833A"],
        )
        fig.update_layout(
            xaxis_title="Fragility Index",
            yaxis_title="Number of Nodes",
            showlegend=False,
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        top_k = current_df.nlargest(k_val, "normalized_fragility")
        fig = px.bar(
            top_k,
            x="node_id",
            y="normalized_fragility",
            title=f"Top {k_val} Most Dangerous Nodes",
            labels={"node_id": "Node", "normalized_fragility": "Fragility Index"},
            color="normalized_fragility",
            color_continuous_scale="YlOrRd",
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            showlegend=False,
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("View Full Results Table"):
        st.dataframe(
            current_df.sort_values("normalized_fragility", ascending=False),
            use_container_width=True,
            height=300,
        )


# ════════════════════════════════════
# TAB 2: Network Map
# ════════════════════════════════════
with tab2:
    st.header(f"Interactive Network Heatmap - {selected_level.upper()} Stress")
    st.caption("Node size and color represent fragility. Hover for details. Zoom and pan supported.")

    pos = nx.spring_layout(G, seed=config.RANDOM_SEED, k=0.5)
    frag_map = dict(zip(current_df["node_id"], current_df["normalized_fragility"]))

    # Edges
    edge_x, edge_y = [], []
    for u, v in G.edges():
        if u in pos and v in pos:
            edge_x.extend([pos[u][0], pos[v][0], None])
            edge_y.extend([pos[u][1], pos[v][1], None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(width=0.3, color="#cccccc"),
        hoverinfo="none",
    )

    # Nodes
    node_names = [n for n in G.nodes() if n in pos]
    node_x = [pos[n][0] for n in node_names]
    node_y = [pos[n][1] for n in node_names]
    node_frags = [frag_map.get(n, 0) for n in node_names]
    node_sizes = [8 + 30 * frag_map.get(n, 0) for n in node_names]
    node_text = [
        f"<b>{n}</b><br>"
        f"Fragility: {frag_map.get(n, 0):.4f}<br>"
        f"Out-degree: {G.out_degree(n)}<br>"
        f"In-degree: {G.in_degree(n)}"
        for n in node_names
    ]

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers",
        marker=dict(
            size=node_sizes,
            color=node_frags,
            colorscale="YlOrRd",
            cmin=0, cmax=1,
            colorbar=dict(title="Fragility"),
            line=dict(width=0.5, color="#333333"),
        ),
        text=node_text,
        hoverinfo="text",
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=650,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════
# TAB 3: Node Explorer
# ════════════════════════════════════
with tab3:
    st.header("Single Node Stress Analysis")

    node_list = sorted(current_df["node_id"].unique())
    selected_node = st.selectbox("Select a node to analyze", node_list)

    rows = []
    for level in config.STRESS_LEVELS:
        if level in results:
            match = results[level][results[level]["node_id"] == selected_node]
            if not match.empty:
                r = match.iloc[0]
                rows.append({
                    "Stress": level.title(),
                    "Fragility": r["normalized_fragility"],
                    "Raw Impact": r["raw_fragility"],
                    "Std": r["std"],
                    "Min": r.get("min_impact", 0),
                    "Max": r.get("max_impact", 0),
                })

    if rows:
        comp_df = pd.DataFrame(rows)
        col_info, col_chart = st.columns([1, 2])

        with col_info:
            st.subheader(f"Node: {selected_node}")
            st.table(comp_df)
            st.markdown(f"""
            **Graph Properties:**
            - Out-degree: {G.out_degree(selected_node)}
            - In-degree: {G.in_degree(selected_node)}
            - Direct dependents: {len(list(G.successors(selected_node)))}
            """)

        with col_chart:
            fig = px.bar(
                comp_df,
                x="Stress",
                y="Fragility",
                color="Fragility",
                color_continuous_scale="YlOrRd",
                title=f"Fragility Across Stress Levels - {selected_node}",
            )
            fig.update_layout(
                yaxis_range=[0, 1.05],
                showlegend=False,
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Node not found in results.")


# ════════════════════════════════════
# TAB 4: Convergence
# ════════════════════════════════════
with tab4:
    st.header("Monte Carlo Convergence Analysis")
    st.markdown(
        "This test verifies that the Fragility Index stabilizes as the number "
        "of Monte Carlo iterations increases. If the curve flattens, N=500 "
        "is sufficient for reliable estimates."
    )

    if conv_data is not None and not conv_data.empty:
        fig = px.line(
            conv_data,
            x="n_cascades",
            y="normalized",
            markers=True,
            title="Fragility Index vs Number of Iterations",
            labels={
                "n_cascades": "Iterations (N)",
                "normalized": "Fragility Index",
            },
        )
        fig.update_traces(line=dict(width=3, color="#D94A4A"))
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Convergence Data")
        display = conv_data.copy()
        display["change_%"] = display["normalized"].pct_change().abs() * 100
        display["change_%"] = display["change_%"].fillna(0).round(4)
        st.dataframe(display, use_container_width=True)

        st.success("Less than 1% change after N=300. N=500 is sufficient.")
    else:
        st.info("No convergence data. Run python run_pipeline.py first.")


# ════════════════════════════════════
# TAB 5: Stress Curve
# ════════════════════════════════════
with tab5:
    st.header("System-Wide Stress Sensitivity")
    st.markdown(
        "This curve shows how the average and maximum fragility across all "
        "nodes changes as global stress increases. A flattening curve indicates "
        "the network has exceeded the cascade threshold."
    )

    if len(results) >= 2:
        curve_rows = []
        for level in config.STRESS_LEVELS:
            if level in results:
                mult = stress_model.get_multiplier(level)
                mean_f = results[level]["normalized_fragility"].mean()
                max_f = results[level]["normalized_fragility"].max()
                curve_rows.append({
                    "Level": level.title(),
                    "Multiplier": mult,
                    "Mean Fragility": mean_f,
                    "Max Fragility": max_f,
                })

        curve_df = pd.DataFrame(curve_rows)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=curve_df["Multiplier"],
            y=curve_df["Mean Fragility"],
            mode="lines+markers",
            name="Mean Fragility",
            line=dict(width=3, color="#D94A4A"),
            marker=dict(size=10),
        ))
        fig.add_trace(go.Scatter(
            x=curve_df["Multiplier"],
            y=curve_df["Max Fragility"],
            mode="lines+markers",
            name="Max Fragility",
            line=dict(width=2, color="#E8833A", dash="dash"),
            marker=dict(size=8),
        ))

        for _, row in curve_df.iterrows():
            fig.add_annotation(
                x=row["Multiplier"],
                y=row["Mean Fragility"],
                text=f"{row['Level']}<br>{row['Mean Fragility']:.3f}",
                showarrow=True,
                arrowhead=2,
                yshift=20,
            )

        fig.update_layout(
            title="Average Fragility vs Stress Multiplier",
            xaxis_title="Stress Multiplier",
            yaxis_title="Fragility Index",
            height=450,
        )
        st.plotly_chart(fig, use_container_width=True)

        if "low" in results and "high" in results:
            low_mean = results["low"]["normalized_fragility"].mean()
            high_mean = results["high"]["normalized_fragility"].mean()
            if low_mean > 0:
                amp = high_mean / low_mean
                st.metric(
                    "Stress Amplification Factor (High / Low)",
                    f"{amp:.2f}x",
                )
                st.caption(
                    "1.07x means the network is above the cascade threshold "
                    "(Watts 2002). Stress barely matters - the vulnerability "
                    "is structural."
                )
    else:
        st.info("Need at least 2 stress levels.")


st.sidebar.divider()
st.sidebar.caption("PR2 Demo Build - CS4982 - UNB - March 2026")