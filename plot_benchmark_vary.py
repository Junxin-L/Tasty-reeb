import time
import matplotlib.pyplot as plt
from reeb_gen import generate_refined_reeb_graph
from rgcn_solver import solve_rgcn_crossing_sat_local_levels
from rgcn_opsolver import solve_rgcn_optimized
import argparse


def benchmark_varying_param(param_name, param_values, fixed_params, k, num_trials=3):
    avg_solver_times = []
    avg_opsolver_times = []
    for val in param_values:
        solver_times = []
        opsolver_times = []
        for trial in range(num_trials):
            params = fixed_params.copy()
            params[param_name] = val
            V_levels, edges = generate_refined_reeb_graph(
                num_layers=params['num_layers'],
                layer_width=params['layer_width'],
                seed=trial
            )
            V = list(V_levels.keys())
            levels = V_levels

            # Standard solver
            t0 = time.time()
            try:
                solve_rgcn_crossing_sat_local_levels(V, edges, levels, k)
            except Exception:
                pass
            t1 = time.time()
            solver_times.append(t1 - t0)

            # Optimized solver
            t0 = time.time()
            try:
                solve_rgcn_optimized(V, edges, levels, k)
            except Exception:
                pass
            t1 = time.time()
            opsolver_times.append(t1 - t0)

        avg_solver_times.append(sum(solver_times) / num_trials)
        avg_opsolver_times.append(sum(opsolver_times) / num_trials)

    return avg_solver_times, avg_opsolver_times


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Benchmark and plot RGCN solvers with one varying parameter.")
    parser.add_argument('--sweep_param', type=str, required=True, choices=['layer_width', 'num_layers', 'k'],
                        help='Parameter to sweep')
    parser.add_argument('--sweep_start', type=int, required=True, help='Sweep start (inclusive)')
    parser.add_argument('--sweep_end', type=int, required=True, help='Sweep end (inclusive)')
    parser.add_argument('--fixed_layer_width', type=int, default=4, help='Fixed layer_width (if not sweeping)')
    parser.add_argument('--fixed_num_layers', type=int, default=4, help='Fixed num_layers (if not sweeping)')
    parser.add_argument('--fixed_k', type=int, default=0, help='Fixed k (if not sweeping)')
    parser.add_argument('--num_trials', type=int, default=3, help='Number of trials per setting')
    args = parser.parse_args()

    param_name = args.sweep_param
    param_values = list(range(args.sweep_start, args.sweep_end + 1))
    fixed_params = {
        'layer_width': args.fixed_layer_width,
        'num_layers': args.fixed_num_layers
    }
    k = args.fixed_k
    if param_name == 'layer_width':
        fixed_params['num_layers'] = args.fixed_num_layers
    elif param_name == 'num_layers':
        fixed_params['layer_width'] = args.fixed_layer_width
    # If sweeping k, fixed_params stays as is, and k will be set per value below

    avg_solver_times = []
    avg_opsolver_times = []
    if param_name == 'k':
        for val in param_values:
            t1, t2 = benchmark_varying_param(param_name, [val], fixed_params, val, num_trials=args.num_trials)
            avg_solver_times.extend(t1)
            avg_opsolver_times.extend(t2)
    else:
        avg_solver_times, avg_opsolver_times = benchmark_varying_param(
            param_name, param_values, fixed_params, k, num_trials=args.num_trials
        )

    print(f"{param_name:<12} {'avg_solver_time(s)':<20} {'avg_opsolver_time(s)':<22}")
    for v, t1, t2 in zip(param_values, avg_solver_times, avg_opsolver_times):
        print(f"{v:<12} {t1:<20.4f} {t2:<22.4f}")

    plt.plot(param_values, avg_solver_times, marker='o', label='Standard Solver')
    plt.plot(param_values, avg_opsolver_times, marker='s', label='Optimized Solver')
    plt.xlabel(param_name)
    plt.ylabel('Average Time (s)')
    plt.title(f'Benchmark: Vary {param_name}, fixed layer_width={fixed_params["layer_width"]}, num_layers={fixed_params["num_layers"]}, k={k if param_name!="k" else "varied"}')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('benchmark_vary.png')
    # plt.show()  # Removed to avoid displaying the plot interactively 