import time
import argparse
from reeb_gen import generate_refined_reeb_graph
from rgcn_solver import solve_rgcn_crossing_sat_local_levels
from rgcn_opsolver import solve_rgcn_optimized
import concurrent.futures


def run_with_timeout(func, args=(), kwargs=None, timeout=30):
    if kwargs is None:
        kwargs = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            result = future.result(timeout=timeout)
            return result, future._end_time - future._start_time if hasattr(future, '_end_time') and hasattr(future, '_start_time') else None
        except concurrent.futures.TimeoutError:
            return 'TIMEOUT', timeout


def run_benchmark(num_layers, layer_width, k, num_trials, seed_start=0, timeout=30):
    results = []
    for trial in range(num_trials):
        seed = seed_start + trial
        V_levels, edges = generate_refined_reeb_graph(num_layers=num_layers, layer_width=layer_width, seed=seed)
        V = list(V_levels.keys())
        levels = V_levels

        # Standard solver
        t0 = time.time()
        res1 = solve_rgcn_crossing_sat_local_levels(V, edges, levels, k)
        t1 = time.time()
        time1 = t1 - t0

        # Optimized solver
        t0 = time.time()
        res2 = solve_rgcn_optimized(V, edges, levels, k)
        t1 = time.time()
        time2 = t1 - t0

        results.append({
            'trial': trial,
            'seed': seed,
            'n': len(V),
            'm': len(edges),
            'k': k,
            'solver_result': res1,
            'solver_time': time1,
            'opsolver_result': res2,
            'opsolver_time': time2
        })
    return results


def print_results_table(results):
    print(f"{'trial':<5} {'n':<4} {'m':<4} {'k':<3} {'solver_time(s)':<16} {'opsolver_time(s)':<18} {'solver_result':<14} {'opsolver_result':<16}")
    for r in results:
        print(f"{r['trial']:<5} {r['n']:<4} {r['m']:<4} {r['k']:<3} {r['solver_time']:<16.4f} {r['opsolver_time']:<18.4f} {str(r['solver_result']):<14} {str(r['opsolver_result']):<16}")


def main():
    parser = argparse.ArgumentParser(description="Benchmark RGCN solvers on random Reeb graphs.")
    parser.add_argument('--num_layers', type=int, default=5, help='Number of layers in Reeb graph')
    parser.add_argument('--layer_width', type=int, default=5, help='Number of vertices per layer')
    parser.add_argument('-k', type=int, default=0, help='Crossing number bound')
    parser.add_argument('--num_trials', type=int, default=5, help='Number of random graphs to test')
    parser.add_argument('--seed_start', type=int, default=0, help='Starting seed for random generation')
    args = parser.parse_args()

    results = run_benchmark(args.num_layers, args.layer_width, args.k, args.num_trials, args.seed_start)
    print_results_table(results)

if __name__ == '__main__':
    main() 