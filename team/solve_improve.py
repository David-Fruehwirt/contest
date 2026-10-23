"""solve_improve.py <in> <workers> <tl> <slack> [cases]
Improve-only: layer the current per-case best sequence ASAP, hint it into the layered
CP-SAT model (T = depth + slack, reactions = best's ∪ net-LB set) and re-solve."""
import sys, os, heapq
from collections import defaultdict
from lib import Problem, net_ilp, save_case, stem, simulate
from layer import solve_layers


def load_seq(P, path):
    idx = {r[0]: j for j, r in enumerate(P.rx)}
    return [idx[l] for l in open(path).read().split('\n')[1:] if l]


def asap_layers(P, seq):
    """Assign each firing the earliest layer using FIFO units. Returns {(t, j): count}, depth."""
    bought = defaultdict(int); inv = defaultdict(int)
    for j in seq:
        for m, a in P.rx[j][1]:
            if inv[m] < a: bought[m] += a - inv[m]; inv[m] = a
            inv[m] -= a
        for m, a in P.rx[j][2]: inv[m] += a
    units = defaultdict(list)  # m -> heap of [avail_layer, count]
    for m, v in bought.items(): units[m].append([0, v])
    sol = defaultdict(int); depth = 0
    for j in seq:
        L = 0
        for m, a in P.rx[j][1]:
            need = a; q = units[m]
            while need:
                av, c = q[0]; u = min(c, need); need -= u; L = max(L, av)
                if u == c: heapq.heappop(q)
                else: q[0][1] -= u
        for m, a in P.rx[j][2]:
            heapq.heappush(units[m], [L + 1, a])
        sol[L, j] += 1; depth = max(depth, L + 1)
    return dict(sol), depth


if __name__ == '__main__':
    P = Problem(sys.argv[1]); W = int(sys.argv[2]); tl = float(sys.argv[3]); slack = int(sys.argv[4])
    ks = [int(v) for v in sys.argv[5].split(',')] if len(sys.argv) > 5 else range(len(P.targets))
    for k in ks:
        tm, tq = P.targets[k]
        f = f"cases/{stem(sys.argv[1])}/{k}.txt"
        if not os.path.exists(f): print(f"case {k}: no incumbent"); continue
        seq = load_seq(P, f); cur = simulate(P, seq, tm, tq)
        hint, depth = asap_layers(P, seq)
        c, xs, *_ = net_ilp(P, tm, tq, time_limit=10, workers=W)
        rset = set(xs) | set(seq)
        r = solve_layers(P, tm, tq, depth + slack, time_limit=tl, workers=W, rset=rset, hint=hint)
        if r is None: print(f"case {k}: model failed (depth {depth})", flush=True); continue
        new, old = save_case(P, sys.argv[1], k, r[1], f"improve T={depth + slack}")
        print(f"case {k} {tq} {tm}: incumbent {cur} depth {depth} T {depth + slack} -> {new} {r[3]} bound {r[4]:.0f} netLB {c}", flush=True)
