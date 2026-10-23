"""solve_macro.py <in> <workers> <tl> <Tlist as +offsets over minT, e.g. 0,2,4> [cases]
Layered CP-SAT with cycle macros over reactions = net-LB set ∪ incumbent's set."""
import sys, os
from lib import Problem, net_ilp, save_case, stem, simulate
from layer import levels
from layer2 import solve_macro
from macros import find_macros
from solve_improve import load_seq

P = Problem(sys.argv[1]); W = int(sys.argv[2]); tl = float(sys.argv[3])
offs = [int(v) for v in sys.argv[4].split(',')]
ks = [int(v) for v in sys.argv[5].split(',')] if len(sys.argv) > 5 else range(len(P.targets))
for k in ks:
    tm, tq = P.targets[k]
    c, xs, *_ = net_ilp(P, tm, tq, time_limit=10, workers=W)
    rset = set(xs)
    f = f"cases/{stem(sys.argv[1])}/{k}.txt"
    if os.path.exists(f): rset |= set(load_seq(P, f))
    macros = find_macros(P, rset)
    lv, _ = levels(P, sorted(rset))
    for o in offs:
        T = lv[tm] + o
        r = solve_macro(P, tm, tq, T, rset, macros, time_limit=tl, workers=W)
        if r is None: print(f"case {k} T={T}: none", flush=True); continue
        new, old = save_case(P, sys.argv[1], k, r[1], f"macro T={T}")
        print(f"case {k} {tq} {tm} T={T} macros {len(macros)}: model {r[0]} sim {new} {r[2]}"
              f" bound {r[3]:.0f} netLB {c} prev {old}", flush=True)
