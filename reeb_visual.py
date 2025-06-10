# rgcn_visualizer.py
import json
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict
from datetime import datetime
import os


def visualize_reeb_graph(V_levels, edges, show_degrees=True, save_path=None):
    """
    Visualize refined Reeb graph and optionally save to file.

    Parameters:
        - V_levels: dict of vertex -> level
        - edges: list of (u,v)
        - show_degrees: bool, whether to annotate node degrees
        - save_path: str, path prefix to save PNG and PDF
    """
    G = nx.DiGraph()
    pos = {}
    layer_nodes = defaultdict(list)
    deg_map = defaultdict(int)

    for v, lvl in V_levels.items():
        layer_nodes[lvl].append(v)

    for u, v in edges:
        deg_map[u] += 1
        deg_map[v] += 1
        G.add_edge(u, v)

    # Assign layout positions
    x_gap = 2
    y_gap = -2
    for lvl, nodes in sorted(layer_nodes.items()):
        nodes = sorted(nodes)
        for i, v in enumerate(nodes):
            pos[v] = (i * x_gap, lvl * y_gap)

    fig, ax = plt.subplots(figsize=(10, 6))

    # Draw graph
    nx.draw_networkx_nodes(G, pos, node_size=500, node_color="skyblue", ax=ax)
    nx.draw_networkx_labels(G, pos, labels={v: str(v) for v in G.nodes()}, font_size=10, ax=ax)

    if show_degrees:
        for v in G.nodes():
            x, y = pos[v]
            ax.text(x, y + 0.4, f"deg={deg_map[v]}", fontsize=8, ha="center", color="darkgreen")

    nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color="black", arrows=False, ax=ax)

    ax.set_title("Refined Reeb Graph")
    ax.set_axis_off()
    plt.tight_layout()

    # Save figure
    if save_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = os.path.splitext(save_path)[0]
        png_path = f"{base}_{timestamp}.png"
        pdf_path = f"{base}_{timestamp}.pdf"
        plt.savefig(png_path)
        plt.savefig(pdf_path)
        print(f"Saved: {png_path}")
        print(f"Saved: {pdf_path}")
    else:
        plt.show()


if __name__ == "__main__":
    with open("rgcn_input.json") as f:
        data = json.load(f)

    V = {int(k): v for k, v in data["V_levels"].items()}
    E = [tuple(e) for e in data["edges"]]

    visualize_reeb_graph(V, E, show_degrees=True, save_path="reeb_graph")
