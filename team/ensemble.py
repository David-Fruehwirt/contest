#!/usr/bin/env python3
"""ensemble.py [--check]: best-of-team per case.

Reads every submissions/<name>/*.txt whose filename contains a level key (1-small,
2-medium, 3-large, 4-enormous; e.g. out_level-3_2-medium.txt or output-2.txt).
Each paragraph is simulated on its own (same rules as score.py), so one broken case
does not discard the rest of a file. The cheapest valid paragraph per case wins.
Writes ensemble/out_level-3_<key>.txt, promotes via promote.sh (best/ only gets
cheaper), and writes LEADERBOARD.md. --check: validate and report only."""
import glob, os, re, subprocess, sys
from collections import defaultdict

LEVELS = ['1-small', '2-medium', '3-large', '4-enormous']
ALIAS = {'1-small': r'(1-small|output-1\b|out-1\b)', '2-medium': r'(2-medium|output-2\b|out-2\b)',
         '3-large': r'(3-large|output-3\b|out-3\b)', '4-enormous': r'(4-enormous|output-4\b|out-4\b)'}


def side(s):
    r = []
    for t in s.split(','):
        a, b = t.strip().split(' ', 1)
        r.append((b.strip(), int(a)))
    return r


def parse_in(path):
    L = open(path).read().split('\n'); i = 0
    M = int(L[i]); i += 1; price = {}
    for _ in range(M):
        c, m = L[i].split('->'); i += 1; price[m.strip()] = int(c)
    while not L[i].strip(): i += 1
    R = int(L[i]); i += 1; rx = {}
    for _ in range(R):
        raw = L[i].strip(); i += 1; l, r = raw.split('->'); rx[raw] = (side(l), side(r))
    while not L[i].strip(): i += 1
    N = int(L[i]); i += 1; T = []
    for _ in range(N):
        a, b = L[i].strip().split(' ', 1); i += 1; T.append((b.strip(), int(a)))
    return price, rx, T


def sim(price, rx, tm, tq, lines):
    inv = defaultdict(int); cost = 0
    for line in lines:
        if line not in rx: return None, f"unknown reaction {line!r}"
        ins, outs = rx[line]
        for m, a in ins:
            if inv[m] < a:
                if m not in price: return None, f"{m} not buyable"
                cost += price[m] * (a - inv[m]); inv[m] = a
            inv[m] -= a
        for m, a in outs: inv[m] += a
    if inv[tm] < tq: return None, f"target {tm} {inv[tm]}<{tq}"
    return cost, None


def main():
    check = '--check' in sys.argv
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs('ensemble', exist_ok=True)
    board = ["# Leaderboard (lower is better)", "",
             "Per-case best across all submissions. `wins` = cases where that submission is strictly cheapest.", ""]
    grand = 0
    for lv in LEVELS:
        inp = f"in/in_level-3_{lv}.txt"
        price, rx, T = parse_in(inp)
        best = [None] * len(T)   # (cost, name, lines)
        subs = {}
        for f in sorted(glob.glob('submissions/*/*.txt')):
            if not re.search(ALIAS[lv], os.path.basename(f)): continue
            name = f.split('/')[1] + '/' + os.path.basename(f)
            paras = open(f).read().replace('\r', '').strip('\n').split('\n\n')
            costs = []
            if len(paras) != len(T):
                print(f"WARN {name}: {len(paras)} paragraphs, expected {len(T)} (using matching prefix)")
            for k, (tm, tq) in enumerate(T):
                if k >= len(paras): costs.append(None); continue
                lines = [l.strip() for l in paras[k].split('\n') if l.strip()]
                c, err = sim(price, rx, tm, tq, lines)
                if err: print(f"INVALID {name} case {k}: {err}")
                costs.append(c)
                if c is not None and (best[k] is None or c < best[k][0]):
                    best[k] = (c, name, lines)
            subs[name] = costs
        missing = [k for k, b in enumerate(best) if b is None]
        total = sum(b[0] for b in best if b)
        board += [f"## {lv}: ensemble {total}" + (f" (MISSING cases {missing})" if missing else ""), "",
                  "| submission | total | valid cases | wins |", "|---|---|---|---|"]
        for name, costs in sorted(subs.items(), key=lambda kv: (None in kv[1], sum(c or 0 for c in kv[1]))):
            ok = [c for c in costs if c is not None]
            wins = sum(1 for k, b in enumerate(best) if b and b[1] == name and
                       all(subs[o][k] is None or subs[o][k] > b[0] for o in subs if o != name))
            tot = sum(ok) if len(ok) == len(T) else f"incomplete ({sum(ok)})"
            board.append(f"| {name} | {tot} | {len(ok)}/{len(T)} | {wins} |")
        board.append("")
        grand += total
        if not missing and not check:
            out = f"ensemble/out_level-3_{lv}.txt"
            open(out, 'w').write('\n\n'.join('\n'.join(b[2]) for b in best) + '\n')
            r = subprocess.run(["./promote.sh", inp, out], capture_output=True, text=True)
            print(r.stdout.strip())
    board.insert(4, f"**Ensemble total: {grand}**\n")
    open('LEADERBOARD.md', 'w').write('\n'.join(board) + '\n')
    print(f"ENSEMBLE TOTAL {grand}")


main()
