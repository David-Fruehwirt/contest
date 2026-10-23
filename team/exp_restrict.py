import sys, time
from lib import Problem, net_ilp, save_case
from layer import solve_layers
P = Problem(sys.argv[1]); k = int(sys.argv[2]); tm, tq = P.targets[k]
c, xs, bs, st, bd = net_ilp(P, tm, tq, time_limit=10)
print("netLB", c, "used", len(xs))
for T in [int(v) for v in sys.argv[3].split(',')]:
    t0 = time.time()
    r = solve_layers(P, tm, tq, T, time_limit=float(sys.argv[4]), rset=set(xs))
    if r is None: print(T, "none"); continue
    new, old = save_case(P, sys.argv[1], k, r[1], f"layer-restricted T={T}")
    print(f"T={T} model {r[0]} sim {new} {r[3]} bound {r[4]:.0f} prev {old} {time.time()-t0:.0f}s", flush=True)
