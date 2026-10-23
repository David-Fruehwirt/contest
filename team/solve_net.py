"""Net-balance ILP (lower bound) + randomized greedy scheduling.
usage: solve_net.py <in> <out> [restarts]"""
import sys, random
from lib import Problem, net_ilp, schedule, simulate, write_out

P = Problem(sys.argv[1])
restarts = int(sys.argv[3]) if len(sys.argv) > 3 else 50
seqs = []; tot = 0; tlb = 0
for k, (tm, tq) in enumerate(P.targets):
    cost, xs, bs, st, bound = net_ilp(P, tm, tq)
    best = None
    for it in range(restarts):
        seq = schedule(P, xs, bs, rng=random.Random(it) if it else None)
        c = simulate(P, seq, tm, tq) if seq else None
        if c is not None and (best is None or c < best[0]): best = (c, seq)
    print(f"case {k} {tq} {tm}: lb {cost} ({st}, bound {bound:.0f}) sim {best[0]} gap {best[0]-cost}"
          f" firings {sum(xs.values())}", file=sys.stderr)
    seqs.append(best[1]); tot += best[0]; tlb += cost
print(f"TOTAL sim {tot} lb {tlb}", file=sys.stderr)
write_out(P, seqs, sys.argv[2])
