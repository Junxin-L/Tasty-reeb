# rgcn_input_generator.py
import json
import random
from collections import defaultdict

def generate_refined_reeb_graph(num_layers=5, layer_width=5, seed=42):
    random.seed(seed)
    V_levels = {}      # vertex_id -> level
    edges = []         # list of (u, v)

    # Step 1: create vertices
    vertex_id = 0
    layers = []
    for level in range(num_layers):
        layer = []
        for _ in range(layer_width):
            V_levels[vertex_id] = level
            layer.append(vertex_id)
            vertex_id += 1
        layers.append(layer)

    # Step 2: connect layers with valid degree constraints
    degree_down = defaultdict(int)
    degree_up = defaultdict(int)
    degree_total = defaultdict(int)

    for l in range(num_layers - 1):
        upper = layers[l]
        lower = layers[l + 1]

        candidates = [(u, v) for u in upper for v in lower]
        random.shuffle(candidates)

        for u, v in candidates:
            if degree_down[u] >= 2 or degree_up[v] >= 2:
                continue
            if degree_total[u] >= 3 or degree_total[v] >= 3:
                continue
            # Add edge if valid
            edges.append((u, v))
            degree_down[u] += 1
            degree_up[v] += 1
            degree_total[u] += 1
            degree_total[v] += 1

    return V_levels, edges


def save_input(V_levels, edges, filename="rgcn_input.json"):
    with open(filename, "w") as f:
        json.dump({
            "V_levels": {str(k): v for k, v in V_levels.items()},
            "edges": edges
        }, f, indent=2)


if __name__ == "__main__":
    V, E = generate_refined_reeb_graph()
    save_input(V, E)
    print(f"Generated refined Reeb graph with {len(V)} vertices and {len(E)} edges.")
