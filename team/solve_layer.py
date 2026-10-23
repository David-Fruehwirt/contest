"""solve_layer.py <in> <T> [time_limit] [cases e.g. 0,3]: layered ILP per case, store per-case best."""
import sys
from lib import Problem, save_case
from layer import solve_layers, levels
P = Problem(sys.argv[1]); T = int(sys.argv[2])
tl = float(sys.argv[3]) if len(sys.argv) > 3 else 60
ks = [int(v) for v in sys.argv[4].split(',')] if len(sys.argv) > 4 else range(len(P.targets))
for k in ks:
    tm, tq = P.targets[k]
    lv, _ = levels(P, P.relevant(tm))
    r = solve_layers(P, tm, tq, max(T, lv[tm]), time_limit=tl)
    if r is None: print(f"case {k}: no solution T={T}", flush=True); continue
    cost, seq, sol, st, bd = r
    new, old = save_case(P, sys.argv[1], k, seq, f"layer T={T}")
    print(f"case {k} {tq} {tm} minT {lv[tm]} T {T}: model {cost} sim {new} {st} bound {bd:.0f} prev {old}", flush=True)
