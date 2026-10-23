#!/usr/bin/env python3
"""score.py <in> <out> -- simulate each paragraph from an empty inventory.
Before each reaction, missing inputs are bought (only buyable molecules).
At the end the target quantity must be in inventory.
Prints per-case cost and TOTAL, or INVALID + reason (exit code 1)."""
import sys
from collections import defaultdict


def side(s):
    r = []
    for t in s.split(','):
        a, b = t.strip().split(' ', 1)
        if int(a) <= 0:
            raise ValueError("non-positive amount")
        r.append((b.strip(), int(a)))
    return r


def bad(msg):
    print("INVALID", msg)
    sys.exit(1)


def main():
    L = open(sys.argv[1]).read().split('\n')
    i = 0
    M = int(L[i]); i += 1
    price = {}
    for _ in range(M):
        c, m = L[i].split('->'); i += 1
        price[m.strip()] = int(c)
    while not L[i].strip(): i += 1
    R = int(L[i]); i += 1
    rx = {}
    for _ in range(R):
        raw = L[i].strip(); i += 1
        l, r = raw.split('->')
        rx[raw] = (side(l), side(r))
    while not L[i].strip(): i += 1
    N = int(L[i]); i += 1
    T = []
    for _ in range(N):
        a, b = L[i].strip().split(' ', 1); i += 1
        T.append((b.strip(), int(a)))

    text = open(sys.argv[2]).read().replace('\r', '')
    paras = text.strip('\n').split('\n\n')
    if len(paras) != N:
        bad(f"paragraph count {len(paras)} != {N}")
    total = 0
    for k, ((tm, tq), p) in enumerate(zip(T, paras)):
        inv = defaultdict(int)
        cost = 0
        for ln, line in enumerate(p.split('\n')):
            line = line.strip()
            if not line:
                bad(f"case {k}: blank line inside paragraph")
            if line not in rx:
                bad(f"case {k} line {ln}: unknown reaction {line!r}")
            ins, outs = rx[line]
            for m, a in ins:
                if inv[m] < a:
                    if m not in price:
                        bad(f"case {k} line {ln}: need {a - inv[m]} {m}, not buyable")
                    cost += price[m] * (a - inv[m])
                    inv[m] = a
                inv[m] -= a
            for m, a in outs:
                inv[m] += a
        if inv[tm] < tq:
            bad(f"case {k}: target {tm} have {inv[tm]} < {tq}")
        print(f"case {k} {tq} {tm} cost {cost}")
        total += cost
    print("TOTAL", total)


main()
