"""Time-indexed (layered) ILP: in layer t each firing consumes only stock present at the
start of layer t (bought upfront + produced in layers < t). Any feasible solution maps to
a valid sequence (layer by layer), so the objective is an exact upper bound; with enough
layers it is the true optimum."""
from collections import defaultdict
from ortools.sat.python import cp_model

INF = 10 ** 9


def levels(P, rset):
    lv = {m: (0 if m in P.price else INF) for m in P.mols}
    changed = True
    while changed:
        changed = False
        for j in rset:
            l = max(lv[m] for m, _ in P.rx[j][1]) + 1
            if l < INF:
                for m, _ in P.rx[j][2]:
                    if l < lv[m]: lv[m] = l; changed = True
    rl = {j: max(lv[m] for m, _ in P.rx[j][1]) for j in rset}
    return lv, rl


def dist_to(P, rset, tm):
    d = defaultdict(lambda: INF); d[tm] = 0
    changed = True
    while changed:
        changed = False
        for j in rset:
            dr = min(d[m] for m, _ in P.rx[j][2])
            if dr < INF:
                for m, _ in P.rx[j][1]:
                    if dr + 1 < d[m]: d[m] = dr + 1; changed = True
    return {j: min(d[m] for m, _ in P.rx[j][2]) for j in rset}


def solve_layers(P, tm, tq, T, time_limit=60, workers=12, hint=None, xub=300, log=False, rset=None, init=None, leftover_w=None):
    rset = P.relevant(tm) if rset is None else sorted(rset)
    _, rl = levels(P, rset)
    dr = dist_to(P, rset, tm)
    md = cp_model.CpModel()
    x = {}
    for j in rset:
        for t in range(rl[j], T - dr[j]):
            x[t, j] = md.NewIntVar(0, xub, f"x{t}_{j}")
    if not x: return None
    used = {m for j in rset for m, _ in P.rx[j][1] + P.rx[j][2]} | {tm}
    b = {m: md.NewIntVar(0, 20000, f"b{m}") for m in P.price if m in used}
    cons = defaultdict(lambda: defaultdict(list))   # t -> m -> terms consumed in layer t
    netl = defaultdict(lambda: defaultdict(list))   # t -> m -> net terms of layer t
    for (t, j), v in x.items():
        for m, a in P.rx[j][1]: cons[t][m].append(a * v)
        for m, a in P.net[j].items(): netl[t][m].append(a * v)
    # stock before layer t = b + sum_{s<t} net_s ; must cover consumption in layer t
    for m in used:
        run = [b[m]] if m in b else []
        if init and init.get(m): run = run + [init[m]]
        for t in range(T):
            if cons[t][m]:
                md.Add(sum(run) - sum(cons[t][m]) >= 0)
            run = run + netl[t][m]
        if m == tm:
            md.Add(sum(run) >= tq)
    obj = 1000 * sum(P.price[m] * v for m, v in b.items()) + sum(x.values())
    if leftover_w:
        # reward leftover stock that later rounds can reuse (weights in cost units * 1000)
        for m, w in leftover_w.items():
            if m in used and m != tm:
                fin = md.NewIntVar(0, 20000, f"f{m}")
                tot = (b[m] if m in b else 0) + (init.get(m, 0) if init else 0) + sum(sum(netl[t][m]) for t in range(T))
                md.Add(fin <= tot)
                obj = obj - int(w) * fin
    md.Minimize(obj)
    if hint:
        for (t, j), v in x.items():
            md.AddHint(v, hint.get((t, j), 0))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = time_limit
    s.parameters.num_workers = workers
    s.parameters.log_search_progress = log
    st = s.Solve(md)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return None
    sol = {(t, j): s.Value(v) for (t, j), v in x.items() if s.Value(v)}
    seq = []
    for t in range(T):
        for j in rset:
            seq += [j] * sol.get((t, j), 0)
    cost = sum(P.price[m] * s.Value(v) for m, v in b.items())
    return cost, seq, sol, s.StatusName(st), s.BestObjectiveBound() / 1000.0
