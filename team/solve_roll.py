"""solve_roll.py <in> <g> <T> <tl> [cases]: make the target g units at a time, carrying leftovers."""
import sys
from collections import defaultdict
from lib import Problem, net_ilp, save_case, simulate
from layer import solve_layers, levels
P = Problem(sys.argv[1]); g = int(sys.argv[2]); T = int(sys.argv[3]); tl = float(sys.argv[4])
ks = [int(v) for v in sys.argv[5].split(',')] if len(sys.argv) > 5 else range(len(P.targets))
for k in ks:
    tm, tq = P.targets[k]
    c, xs, bs, st, bd = net_ilp(P, tm, tq, time_limit=10)
    rset = set(xs)
    lv, _ = levels(P, sorted(rset)); TT = max(T, lv[tm])
    inv = defaultdict(int); seq = []; made = 0
    while made < tq:
        step = min(g, tq - made)
        r = solve_layers(P, tm, made + step, TT, time_limit=tl, rset=rset, init=dict(inv))
        if r is None: print("fail"); break
        for j in r[1]:
            for m, a in P.rx[j][1]: inv[m] = max(inv[m], a); inv[m] -= a
            for m, a in P.rx[j][2]: inv[m] += a
        seq += r[1]; made = inv[tm]
    new, old = save_case(P, sys.argv[1], k, seq, f"roll g={g} T={TT}")
    print(f"case {k} {tq} {tm}: netLB {c} roll {new} prev {old}", flush=True)
