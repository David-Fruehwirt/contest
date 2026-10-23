"""Detect 2-reaction catalytic cycles and build macros (fixed short serial sequences)."""
from math import gcd
from collections import defaultdict


def seq_profile(P, seq):
    """net and peak (max prefix deficit) per molecule for a serial sequence of reactions."""
    cur = defaultdict(int); low = defaultdict(int)
    for j in seq:
        for m, a in P.rx[j][1]:
            cur[m] -= a; low[m] = min(low[m], cur[m])
        for m, a in P.rx[j][2]:
            cur[m] += a
    return {m: v for m, v in cur.items() if v}, {m: -v for m, v in low.items() if v}


def find_macros(P, rset, maxmul=4):
    rset = sorted(rset); out = []; seen = set()
    for ia, A in enumerate(rset):
        for B in rset[ia + 1:]:
            nA_, nB_ = P.net[A], P.net[B]
            # cycle signature: some c consumed by A & produced by B, some d produced by A & consumed by B
            cs = [m for m in nA_ if nA_[m] < 0 and nB_.get(m, 0) > 0]
            ds = [m for m in nA_ if nA_[m] > 0 and nB_.get(m, 0) < 0]
            if not cs or not ds: continue
            for p in range(1, maxmul + 1):
                for q in range(1, maxmul + 1):
                    if gcd(p, q) != 1: continue
                    if not all(p * nA_[m] + q * nB_[m] == 0 for m in cs + ds): continue
                    for s in ([A] * p + [B] * q, [B] * q + [A] * p):
                        key = tuple(s)
                        if key in seen: continue
                        seen.add(key)
                        net, peak = seq_profile(P, s)
                        out.append(dict(seq=s, net=net, peak=peak, cat=sorted(set(cs + ds))))
    return out
