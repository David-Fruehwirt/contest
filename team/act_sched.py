"""act_sched.py <in> <workers> <tl> <restarts> [cases]: activation ILP (net balance + seed
order) -> randomized serial scheduling of its counts; keep the cheapest simulated sequence."""
import sys, random
from lib import Problem, schedule, simulate, save_case
from lb2 import act_lb

P = Problem(sys.argv[1]); W = int(sys.argv[2]); tl = float(sys.argv[3]); R = int(sys.argv[4])
ks = [int(v) for v in sys.argv[5].split(',')] if len(sys.argv) > 5 else range(len(P.targets))
for k in ks:
    tm, tq = P.targets[k]
    bd, st, bs, xs = act_lb(P, tm, tq, W, tl)
    if xs is None: print(f"case {k}: no ILP solution ({st})", flush=True); continue
    plan = sum(P.price[m] * v for m, v in bs.items())
    best = None
    for it in range(R):
        seq = schedule(P, xs, bs, rng=random.Random(it) if it else None)
        c = simulate(P, seq, tm, tq) if seq else None
        if c is not None and (best is None or c < best[0]): best = (c, seq)
    if best is None: print(f"case {k}: unschedulable, plan {plan} lb {bd}", flush=True); continue
    new, old = save_case(P, sys.argv[1], k, best[1], "act_sched")
    print(f"case {k} {tq} {tm}: actLB {bd} ({st}) plan {plan} sim {best[0]} prev {old}", flush=True)
