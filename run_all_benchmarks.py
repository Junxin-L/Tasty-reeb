import subprocess
import sys

# Sweep layer_width
print("\n=== Sweep layer_width (num_layers=4, k=0) ===")
subprocess.run([
    sys.executable, "plot_benchmark_vary.py",
    "--sweep_param", "layer_width",
    "--sweep_start", "4",
    "--sweep_end", "12",
    "--fixed_num_layers", "4",
    "--fixed_k", "0",
    "--num_trials", "10"
])
import os
if os.path.exists("benchmark_vary.png"):
    os.rename("benchmark_vary.png", "benchmark_vary_layer_width.png")
print("Saved plot: benchmark_vary_layer_width.png\n")

# Sweep num_layers
print("\n=== Sweep num_layers (layer_width=4, k=0) ===")
subprocess.run([
    sys.executable, "plot_benchmark_vary.py",
    "--sweep_param", "num_layers",
    "--sweep_start", "4",
    "--sweep_end", "12",
    "--fixed_layer_width", "4",
    "--fixed_k", "0",
    "--num_trials", "10"
])
if os.path.exists("benchmark_vary.png"):
    os.rename("benchmark_vary.png", "benchmark_vary_num_layers.png")
print("Saved plot: benchmark_vary_num_layers.png\n")

# Sweep k
print("\n=== Sweep k (layer_width=4, num_layers=4) ===")
subprocess.run([
    sys.executable, "plot_benchmark_vary.py",
    "--sweep_param", "k",
    "--sweep_start", "0",
    "--sweep_end", "10",
    "--fixed_layer_width", "4",
    "--fixed_num_layers", "4",
    "--num_trials", "10"
])
if os.path.exists("benchmark_vary.png"):
    os.rename("benchmark_vary.png", "benchmark_vary_k.png")
print("Saved plot: benchmark_vary_k.png\n")

print("All sweeps completed!") 