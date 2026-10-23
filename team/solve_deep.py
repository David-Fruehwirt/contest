"""solve_deep.py <in> <workers> <tl> <Tlist e.g. 2,3,4 (x minT)> [cases]
Layered CP-SAT over net-LB reaction set, growing T, warm-started from previous layer solution."""
import sys, json, os
from lib import Problem, net_ilp, save_case, stem
from layer import solve_layers, levels
P = Problem(sys.argv[1]); W = int(sys.argv[2]); tl = float(sys.argv[3])
mults = [float(v) for v in sys.argv[4].split(',')]
ks = [int(v) for v in sys.argv[5].split(',')] if len(sys.argv) > 5 else range(len(P.targets))
lbf = f"lbs/{stem(sys.argv[1])}.json"; lbs = json.load(open(lbf)) if os.path.exists(lbf) else {}
for k in ks:
    tm, tq = P.targets[k]
    c, xs, bs, st, bd = net_ilp(P, tm, tq, time_limit=15, workers=W)
    lbs[str(k)] = c if st == 'OPTIMAL' else int(bd)
    rset = set(xs); lv, _ = levels(P, sorted(rset)); hint = None
    for mu in mults:
        T = int(round(mu * lv[tm]))
        r = solve_layers(P, tm, tq, T, time_limit=tl, workers=W, rset=rset, hint=hint)
        if r is None: print(f"case {k} T={T} none", flush=True); continue
        hint = r[2]
        new, old = save_case(P, sys.argv[1], k, r[1], f"deep T={T}")
        print(f"case {k} {tq} {tm} T={T}: sim {new} {r[3]} rbound {r[4]:.0f} netLB {lbs[str(k)]} prev {old}", flush=True)
os.makedirs('lbs', exist_ok=True)
json.dump(lbs, open(lbf, 'w'))
