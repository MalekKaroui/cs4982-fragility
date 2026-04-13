import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

from src.kaggle_loader import load_kaggle_supplychain_graph

G = load_kaggle_supplychain_graph()

# color nodes by type
color_map = []
for n, d in G.nodes(data=True):
    t = d.get("node_type", "")
    if t == "supplier":
        color_map.append("red")
    elif t == "sku":
        color_map.append("skyblue")
    elif t == "customer_segment":
        color_map.append("green")
    else:
        color_map.append("gray")

size_map = []
for n, d in G.nodes(data=True):
    t = d.get("node_type", "")
    if t == "supplier":
        size_map.append(500)
    elif t == "sku":
        size_map.append(120)
    elif t == "customer_segment":
        size_map.append(500)
    else:
        size_map.append(150)

plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G, seed=42, k=0.5)

nx.draw_networkx_nodes(G, pos, node_color=color_map, node_size=size_map, alpha=0.85)
nx.draw_networkx_edges(G, pos, alpha=0.25, arrows=True, width=0.6)

# only label important nodes
labels = {}
for n, d in G.nodes(data=True):
    if d.get("node_type") in ["supplier", "customer_segment"]:
        labels[n] = d.get("label", n)

nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)

plt.title("Kaggle Operational Supply Chain Graph\nRed = Suppliers, Blue = SKUs, Green = Customer Segments")
plt.axis("off")
plt.tight_layout()
plt.savefig("kaggle_graph_structure.png", dpi=300)
plt.close()

print("Saved: kaggle_graph_structure.png")