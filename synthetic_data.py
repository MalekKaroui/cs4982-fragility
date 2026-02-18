import random
import networkx as nx


def add_synthetic_node_features(G):
    for n in G.nodes:
        G.nodes[n]["inventory"] = random.randint(10, 100)
        G.nodes[n]["reliability"] = round(random.uniform(0.8, 0.99), 3)
        G.nodes[n]["stress_capacity"] = random.randint(5, 20)


def add_synthetic_edge_features(G):
    for u, v in G.edges:
        G.edges[u, v]["lead_time"] = random.randint(1, 10)
        G.edges[u, v]["capacity"] = random.randint(50, 500)
        G.edges[u, v]["reliability"] = round(random.uniform(0.85, 0.99), 3)
