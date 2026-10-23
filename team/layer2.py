"""Layered CP-SAT with cycle macros. A macro M (fixed serial sequence, net n, peak p) fired
k times in layer t needs start-of-layer stock (-n)^+ * k + (p - (-n)^+) * z  (z = [k > 0]),
since the seed part is borrowed and returned within the serial chain. Its net n*k becomes
available from layer t+1. Plain reactions as in layer.py. Every solution expands to a valid
sequence: within a layer all firings draw on disjoint shares of the start-of-layer stock."""
from collections import defaultdict
from ortools.sat.python import cp_model
from layer import levels, dist_to


def solve_macro(P, tm, tq, T, rset, macros, time_limit=60, workers=12, hint=None, xub=300,
                log=False):
    rset = sorted(rset)
    _, rl = levels(P, rset)
    dr = dist_to(P, rset, tm)
    md = cp_model.CpModel()
    x = {}
    for j in rset:
        for t in range(rl[j], T - dr[j]):
            x[t, j] = md.NewIntVar(0, xub, f"x{t}_{j}")
    mk, mz = {}, {}
    for i, M in enumerate(macros):
        lo = max(rl[j] for j in M['seq']); hi = T - min(dr[j] for j in M['seq'])
        for t in range(lo, hi):
            mk[t, i] = md.NewIntVar(0, xub, f"k{t}_{i}")
            mz[t, i] = md.NewBoolVar(f"z{t}_{i}")
            md.Add(mk[t, i] <= xub * mz[t, i])
            md.Add(mk[t, i] >= mz[t, i])
    used = {m for j in rset for m, _ in P.rx[j][1] + P.rx[j][2]} | {tm}
    b = {m: md.NewIntVar(0, 20000, f"b{m}") for m in P.price if m in used}
    cons = defaultdict(lambda: defaultdict(list))
    netl = defaultdict(lambda: defaultdict(list))
    for (t, j), v in x.items():
        for m, a in P.rx[j][1]: cons[t][m].append(a * v)
        for m, a in P.net[j].items(): netl[t][m].append(a * v)
    for (t, i), k in mk.items():
        M = macros[i]; z = mz[t, i]
        for m, p in M['peak'].items():
            neg = max(0, -M['net'].get(m, 0))
            cons[t][m].append(neg * k)
            if p - neg: cons[t][m].append((p - neg) * z)
        for m, n in M['net'].items(): netl[t][m].append(n * k)
    for m in used:
        run = [b[m]] if m in b else []
        for t in range(T):
            if cons[t][m]:
                md.Add(sum(run) - sum(cons[t][m]) >= 0)
            run = run + netl[t][m]
        if m == tm:
            md.Add(sum(run) >= tq)
    md.Minimize(1000 * sum(P.price[m] * v for m, v in b.items())
                + sum(x.values()) + sum(len(macros[i]['seq']) * k for (t, i), k in mk.items()))
    if hint:
        for (t, j), v in x.items():
            md.AddHint(v, hint.get((t, j), 0))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = time_limit
    s.parameters.num_workers = workers
    s.parameters.log_search_progress = log
    st = s.Solve(md)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return None
    seq = []
    for t in range(T):
        for j in rset:
            if (t, j) in x: seq += [j] * s.Value(x[t, j])
        for i, M in enumerate(macros):
            if (t, i) in mk: seq += M['seq'] * s.Value(mk[t, i])
    cost = sum(P.price[m] * s.Value(v) for m, v in b.items())
    return cost, seq, s.StatusName(st), s.BestObjectiveBound() / 1000.0
