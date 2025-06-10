# from pysat.formula import IDPool, CNF
# from pysat.card import CardEnc
# from pysat.solvers import Solver
# import itertools
# from collections import defaultdict


# def solve_rgcn_crossing_sat_local_levels(V, edges, levels, k, extract_solution=False):
#     pool = IDPool()
#     cnf = CNF()

#     # Step 1: assign local positions per level
#     level_groups = defaultdict(list)
#     for v in V:
#         level_groups[levels[v]].append(v)

#     position_ranges = {}  # vertex -> (start, end) position
#     pos_counter = 1
#     for lvl in sorted(level_groups):
#         nodes = level_groups[lvl]
#         for v in nodes:
#             position_ranges[v] = (pos_counter, pos_counter + len(nodes) - 1)
#         pos_counter += len(nodes)

#     # Step 2: position variables
#     pos_var = lambda v, i: pool.id(f"p_{v}_{i}")
#     for v in V:
#         start, end = position_ranges[v]
#         # Each node must occupy one position
#         cnf.append([pos_var(v, i) for i in range(start, end + 1)])
#         # No two positions at once
#         for i, j in itertools.combinations(range(start, end + 1), 2):
#             cnf.append([-pos_var(v, i), -pos_var(v, j)])

#     # Step 3: ensure positions are unique per slot
#     for lvl in sorted(level_groups):
#         positions = set()
#         for v in level_groups[lvl]:
#             start, end = position_ranges[v]
#             for i in range(start, end + 1):
#                 positions.add(i)
#         for i in positions:
#             for u, v in itertools.combinations(level_groups[lvl], 2):
#                 cnf.append([-pos_var(u, i), -pos_var(v, i)])

#     # Step 4: crossing constraints
#     crossing_vars = []
#     for (u1, v1), (u2, v2) in itertools.combinations(edges, 2):
#         if {levels[u1], levels[v1]} != {levels[u2], levels[v2]}:
#             continue

#         x = pool.id(f"c_{u1}_{v1}_{u2}_{v2}")
#         crossing_vars.append(x)

#         for i1, i2, i3, i4 in itertools.permutations(range(1, pos_counter), 4):
#             if not (i1 < i2 < i3 < i4):
#                 continue
#             cnf.append([-pos_var(u1, i1), -pos_var(u2, i2),
#                         -pos_var(v1, i3), -pos_var(v2, i4), x])
#             cnf.append([-pos_var(u2, i1), -pos_var(u1, i2),
#                         -pos_var(v2, i3), -pos_var(v1, i4), x])

#     # Step 5: crossing number bound
#     card = CardEnc.atmost(lits=crossing_vars, bound=k, vpool=pool, encoding=1)
#     cnf.extend(card.clauses)

#     # Step 6: solve
#     with Solver(bootstrap_with=cnf.clauses) as solver:
#         if not solver.solve():
#             return False

#         model = solver.get_model()
#         if not extract_solution:
#             return True

#         pos_assignment = {}
#         for v in V:
#             for i in range(*position_ranges[v]):
#                 if pos_var(v, i) in model:
#                     pos_assignment[v] = i
#                     break

#         return pos_assignment

from pysat.formula import CNF, IDPool
from pysat.card import CardEnc
from pysat.solvers import Solver
import itertools

def solve_rgcn_optimized(V, edges, levels, k, extract_solution=False):
    pool = IDPool()
    cnf = CNF()

    # Step 1: Assign slot ranges for each level
    level_to_nodes = {}
    for v in V:
        level_to_nodes.setdefault(levels[v], []).append(v)
    level_slots = {}
    current = 1
    for lvl, nodes in sorted(level_to_nodes.items()):
        level_slots[lvl] = (current, current + len(nodes) - 1)
        current += len(nodes)

    # Step 2: Position variables
    pos_var = lambda v, i: pool.id(f"p_{v}_{i}")

    for lvl, nodes in level_to_nodes.items():
        slots = level_slots[lvl]
        for v in nodes:
            cnf.append([pos_var(v, i) for i in range(slots[0], slots[1]+1)])
            for i, j in itertools.combinations(range(slots[0], slots[1]+1), 2):
                cnf.append([-pos_var(v, i), -pos_var(v, j)])
        for i in range(slots[0], slots[1]+1):
            cnf.append([pos_var(v, i) for v in nodes])
            for u, v in itertools.combinations(nodes, 2):
                cnf.append([-pos_var(u, i), -pos_var(v, i)])

    # Step 3: Crossing variables (optimized)
    crossing_vars = []
    for (u1, v1), (u2, v2) in itertools.combinations(edges, 2):
        if levels[u1] != levels[u2] or levels[v1] != levels[v2]:
            continue  # not same level, skip

        cvar = pool.id(f"c_{u1}_{v1}_{u2}_{v2}")
        crossing_vars.append(cvar)

        # For each pair of positions a<b<c<d (slot ranges)
        for i1 in range(1, current):
            for i2 in range(i1 + 1, current):
                for i3 in range(i2 + 1, current):
                    for i4 in range(i3 + 1, current):
                        # crossing case 1
                        cnf.append([-pos_var(u1, i1), -pos_var(u2, i2),
                                    -pos_var(v1, i3), -pos_var(v2, i4), cvar])
                        # crossing case 2
                        cnf.append([-pos_var(u2, i1), -pos_var(u1, i2),
                                    -pos_var(v2, i3), -pos_var(v1, i4), cvar])

    # Step 4: Total crossing count at most k
    card = CardEnc.atmost(lits=crossing_vars, bound=k, vpool=pool, encoding=1)
    cnf.extend(card.clauses)

    # Step 5: Solve
    with Solver(bootstrap_with=cnf.clauses) as solver:
        sat = solver.solve()
        if not sat:
            return False
        if not extract_solution:
            return True

        model = solver.get_model()
        assignment = {}
        for v in V:
            for i in range(1, current):
                if pos_var(v, i) in model:
                    assignment[v] = i
                    break
        return assignment

if __name__ == '__main__':
    # Define test cases
    tests = [
        {
            "name": "Test A: Non-crossing 3 edges",
            "V": list(range(6)),
            "edges": [(0, 3), (1, 4), (2, 5)],
            "levels": {0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1},
            "k": 0,
            "expect_sat": True
        },
        {
            "name": "Test B: cross",
            "V": list(range(4)),
            "edges": [(0, 3), (0, 2), (1, 2), (1, 3)],
            "levels": {0: 0, 1: 0, 2: 1, 3: 1},
            "k": 0,
            "expect_sat": False
        },
        {
            "name": "Test B': 1 cross",
            "V": list(range(4)),
            "edges": [(0, 3), (0, 2), (1, 2), (1, 3)],
            "levels": {0: 0, 1: 0, 2: 1, 3: 1},
            "k": 1,
            "expect_sat": True
        },
        {
            "name": "Test C: Partial crossings allowed",
            "V": list(range(6)),
            "edges": [(0, 3), (0, 5), (1, 4), (1, 5), (2, 3), (2, 5)],
            "levels": {0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1},
            "k": 1,
            "expect_sat": True
        },
        {
            "name": "Test C': 3 crosses",
            "V": list(range(6)),
            "edges": [(0, 3), (0, 5), (1, 4), (1, 5), (2, 3), (2, 5), (3, 4)],
            "levels": {0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1},
            "k": 0,
            "expect_sat": False
        },
    ]

    results = []
    for test in tests:
        res = solve_rgcn_optimized(
            test["V"], test["edges"], test["levels"], test["k"])
        passed = res == test["expect_sat"]
        results.append({
            "Test": test["name"],
            "Expected": test["expect_sat"],
            "Result": res,
            "Status": "✅ PASSED" if passed else "❌ FAILED"
        })

    for r in results:
        print(r)
