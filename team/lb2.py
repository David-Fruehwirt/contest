"""lb2.py <in> [workers] [tl]: net-balance ILP + activation order (valid lower bound).
Any real sequence induces first-appearance times: a used reaction's inputs must each be
bought (b>0) or produced by a used reaction activated strictly earlier."""
import sys, json, os
from collections import defaultdict
from ortools.sat.python import cp_model
from lib import Problem, stem


def act_lb(P, tm, tq, workers=4, tl=60):
    rset = P.relevant(tm); md = cp_model.CpModel(); UB = 10000; L = len(P.mols) + 1
    x = {j: md.NewIntVar(0, UB, f"x{j}") for j in rset}
    u = {j: md.NewBoolVar(f"u{j}") for j in rset}
    lr = {j: md.NewIntVar(1, L, f"lr{j}") for j in rset}
    mols = {m for j in rset for m, _ in P.rx[j][1] + P.rx[j][2]} | {tm}
    b = {m: md.NewIntVar(0, UB, f"b{m}") for m in P.price if m in mols}
    lm = {m: md.NewIntVar(0, L, f"lm{m}") for m in mols}
    a = {m: md.NewBoolVar(f"a{m}") for m in mols}
    bal = defaultdict(list); prod = defaultdict(list)
    for j in rset:
        md.Add(x[j] <= UB * u[j]); md.Add(x[j] >= u[j])
        for m, v in P.net[j].items(): bal[m].append(v * x[j])
        for m, _ in P.rx[j][1]:
            md.AddImplication(u[j], a[m])
            md.Add(lm[m] < lr[j]).OnlyEnforceIf(u[j])
        for m, _ in P.rx[j][2]: prod[m].append(j)
    for m in mols:
        md.Add(sum(bal[m]) + (b[m] if m in b else 0) >= (tq if m == tm else 0))
        opts = []
        if m in b:
            s = md.NewBoolVar(f"s{m}"); md.Add(b[m] >= 1).OnlyEnforceIf(s)
            md.Add(lm[m] == 0).OnlyEnforceIf(s); opts.append(s)
        for j in prod[m]:
            e = md.NewBoolVar(f"e{m}_{j}"); md.AddImplication(e, u[j])
            md.Add(lr[j] < lm[m]).OnlyEnforceIf(e); opts.append(e)
        md.AddBoolOr(opts).OnlyEnforceIf(a[m]) if opts else md.Add(a[m] == 0)
    md.Add(a[tm] == 1)
    md.Minimize(sum(P.price[m] * v for m, v in b.items()))
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = tl; s.parameters.num_workers = workers
    st = s.Solve(md)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return int(s.BestObjectiveBound() + 0.999), s.StatusName(st), None, None
    return (int(s.BestObjectiveBound() + 0.999), s.StatusName(st),
            {m: s.Value(v) for m, v in b.items() if s.Value(v)}, {j: s.Value(x[j]) for j in rset if s.Value(x[j])})


if __name__ == '__main__':
    P = Problem(sys.argv[1]); W = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    tl = float(sys.argv[3]) if len(sys.argv) > 3 else 60
    lbf = f"lbs/{stem(sys.argv[1])}_act.json"; out = {}
    for k, (tm, tq) in enumerate(P.targets):
        bd, st, bs, xs = act_lb(P, tm, tq, W, tl); out[k] = bd
        print(k, tq, tm, bd, st, flush=True)
    os.makedirs('lbs', exist_ok=True); json.dump(out, open(lbf, 'w'))
    print("ACT LB total", sum(out.values()))
