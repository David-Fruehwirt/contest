import random
from collections import defaultdict
from ortools.sat.python import cp_model


def side(s):
    r = []
    for t in s.split(','):
        a, b = t.strip().split(' ', 1)
        r.append((b.strip(), int(a)))
    return r


class Problem:
    def __init__(self, path):
        L = open(path).read().split('\n')
        i = 0
        M = int(L[i]); i += 1
        self.price = {}
        for _ in range(M):
            c, m = L[i].split('->'); i += 1
            self.price[m.strip()] = int(c)
        while not L[i].strip(): i += 1
        R = int(L[i]); i += 1
        self.rx = []  # (raw, ins, outs)
        for _ in range(R):
            raw = L[i].strip(); i += 1
            l, r = raw.split('->')
            self.rx.append((raw, side(l), side(r)))
        while not L[i].strip(): i += 1
        N = int(L[i]); i += 1
        self.targets = []
        for _ in range(N):
            a, b = L[i].strip().split(' ', 1); i += 1
            self.targets.append((b.strip(), int(a)))
        self.mols = sorted(set(self.price) | {m for _, a, b in self.rx for m, _ in a + b}
                           | {t for t, _ in self.targets})
        # net effect per reaction
        self.net = []
        for _, ins, outs in self.rx:
            d = defaultdict(int)
            for m, a in ins: d[m] -= a
            for m, a in outs: d[m] += a
            self.net.append(dict(d))

    def relevant(self, tm):
        """Reactions that can contribute to making tm (backward closure over producers)."""
        need = {tm}; rel = set(); changed = True
        while changed:
            changed = False
            for j, (_, ins, outs) in enumerate(self.rx):
                if j in rel: continue
                if any(m in need for m, _ in outs):
                    rel.add(j); changed = True
                    for m, _ in ins: need.add(m)
        return sorted(rel)


def net_ilp(P, tm, tq, time_limit=30, workers=12, rset=None, extra=None):
    """Lower bound: min sum p*b s.t. b + sum x*net >= demand. Returns (cost, x dict, b dict, status)."""
    rset = P.relevant(tm) if rset is None else rset
    md = cp_model.CpModel()
    UB = 10000
    x = {j: md.NewIntVar(0, UB, f"x{j}") for j in rset}
    b = {m: md.NewIntVar(0, UB, f"b{m}") for m in P.price}
    bal = defaultdict(list)
    for j in rset:
        for m, a in P.net[j].items():
            bal[m].append(a * x[j])
    for m in set(bal) | {tm}:
        md.Add(sum(bal[m]) + (b[m] if m in b else 0) >= (tq if m == tm else 0))
    if extra: extra(md, x, b)
    md.Minimize(sum(P.price[m] * b[m] for m in b) * 1000 + sum(x.values()))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = time_limit
    s.parameters.num_workers = workers
    st = s.Solve(md)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    xs = {j: s.Value(x[j]) for j in rset if s.Value(x[j])}
    bs = {m: s.Value(b[m]) for m in b if s.Value(b[m])}
    cost = sum(P.price[m] * v for m, v in bs.items())
    bound = s.BestObjectiveBound() / 1000.0
    return cost, xs, bs, s.StatusName(st), bound


def simulate(P, seq, tm, tq):
    inv = defaultdict(int); cost = 0
    for j in seq:
        _, ins, outs = P.rx[j]
        for m, a in ins:
            if inv[m] < a:
                if m not in P.price: return None
                cost += P.price[m] * (a - inv[m]); inv[m] = a
            inv[m] -= a
        for m, a in outs: inv[m] += a
    if inv[tm] < tq: return None
    return cost


def schedule(P, xs, bs, rng=None, prio=None):
    """Order counts xs given upfront stock bs. Fire fireable reactions; if stuck, buy the
    cheapest missing inputs. Returns sequence of reaction indices."""
    cnt = dict(xs); inv = defaultdict(int, bs); seq = []
    order = sorted(cnt, key=lambda j: (prio[j] if prio else 0, rng.random() if rng else j))
    rem = sum(cnt.values())
    while rem:
        fired = False
        for j in order:
            if cnt[j] and all(inv[m] >= a for m, a in P.rx[j][1]):
                for m, a in P.rx[j][1]: inv[m] -= a
                for m, a in P.rx[j][2]: inv[m] += a
                cnt[j] -= 1; rem -= 1; seq.append(j); fired = True
                break
        if fired: continue
        best = None
        for j in order:
            if cnt[j] and all(inv[m] >= a or m in P.price for m, a in P.rx[j][1]):
                c = sum(P.price[m] * (a - inv[m]) for m, a in P.rx[j][1] if inv[m] < a)
                if best is None or c < best[0]: best = (c, j)
        if best is None: return None
        for m, a in P.rx[best[1]][1]:
            if inv[m] < a: inv[m] = a
    return seq


def write_out(P, seqs, path):
    with open(path, 'w') as f:
        f.write('\n\n'.join('\n'.join(P.rx[j][0] for j in s) for s in seqs) + '\n')


def stem(path):
    import os
    return os.path.basename(path)[len('in_'):-len('.txt')]


def save_case(P, inpath, k, seq, note=''):
    """Keep per-case best in cases/<stem>/<k>.txt (first line: cost). Returns (new, old)."""
    import os
    tm, tq = P.targets[k]
    c = simulate(P, seq, tm, tq)
    if c is None: return None, None
    d = f"cases/{stem(inpath)}"; os.makedirs(d, exist_ok=True)
    f = f"{d}/{k}.txt"; old = None
    if os.path.exists(f):
        old = int(open(f).readline().split()[0])
        if c >= old: return c, old
    with open(f, 'w') as fh:
        fh.write(f"{c} {note}\n" + '\n'.join(P.rx[j][0] for j in seq) + '\n')
    return c, old
