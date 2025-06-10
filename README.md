# Reeb Graph Crossing Number Solver

This project implements and compares different approaches to solve the Reeb Graph Crossing Number (RGCN) problem. It includes both a standard solver and an optimized solver, along with benchmarking tools to compare their performance.

## Overview

The Reeb Graph Crossing Number problem is a graph-theoretical problem that involves finding the minimum number of crossings in a Reeb graph representation. This implementation provides:

- A standard solver using SAT-based approach
- An optimized solver with improved performance
- Tools for generating test cases
- Benchmarking utilities to compare solver performance

## Requirements

- Python 3.9+
- Required Python packages:
  - matplotlib
  - numpy
  - networkx
  - z3-solver

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Solvers

The project provides two main solvers:

1. Standard Solver (`rgcn_solver.py`):
```python
from rgcn_solver import solve_rgcn_crossing_sat_local_levels
result = solve_rgcn_crossing_sat_local_levels(V, edges, levels, k)
```

2. Optimized Solver (`rgcn_opsolver.py`):
```python
from rgcn_opsolver import solve_rgcn_optimized
result = solve_rgcn_optimized(V, edges, levels, k)
```

### Benchmarking

Use the benchmarking script to compare solver performance:

```bash
python plot_benchmark_vary.py --sweep_param [param_name] --sweep_start [start] --sweep_end [end] [other_options]
```

Parameters:
- `--sweep_param`: Parameter to vary ('layer_width', 'num_layers', or 'k')
- `--sweep_start`: Start value for the parameter
- `--sweep_end`: End value for the parameter
- `--fixed_layer_width`: Fixed layer width (default: 4)
- `--fixed_num_layers`: Fixed number of layers (default: 4)
- `--fixed_k`: Fixed k value (default: 0)
- `--num_trials`: Number of trials per setting (default: 3)

Example:
```bash
python plot_benchmark_vary.py --sweep_param layer_width --sweep_start 2 --sweep_end 6 --fixed_num_layers 4
```

### Generating Test Cases

Use the Reeb graph generator to create test cases:

```python
from reeb_gen import generate_refined_reeb_graph
V_levels, edges = generate_refined_reeb_graph(num_layers=4, layer_width=4, seed=42)
```

## Project Structure

- `rgcn_solver.py`: Implementation of the standard solver
- `rgcn_opsolver.py`: Implementation of the optimized solver
- `reeb_gen.py`: Reeb graph generation utilities
- `plot_benchmark_vary.py`: Benchmarking and plotting utilities


