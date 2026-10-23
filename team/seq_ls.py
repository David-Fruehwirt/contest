"""seq_ls.py <in> <seconds_per_case> [cases]: local search on the per-case best sequence.
Moves: delete a firing, relocate a firing / block, insert a firing of a used reaction.
Accepts equal-cost moves (plateau walk); saves only strict improvements."""
import sys, os, random, time
from lib import Problem, simulate, save_case, stem
from solve_improve import load_seq

P = Problem(sys.argv[1]); secs = float(sys.argv[2])
ks = [int(v) for v in sys.argv[3].split(',')] if len(sys.argv) > 3 else range(len(P.targets))
rng = random.Random(1)
for k in ks:
    tm, tq = P.targets[k]
    f = f"cases/{stem(sys.argv[1])}/{k}.txt"
    if not os.path.exists(f): continue
    seq = load_seq(P, f); cur = simulate(P, seq, tm, tq); start = cur
    pool = sorted(set(seq)); t0 = time.time(); tries = 0
    while time.time() - t0 < secs:
        tries += 1; n = len(seq); r = rng.random(); s = seq
        if r < 0.25:
            i = rng.randrange(n); s = seq[:i] + seq[i + 1:]
        elif r < 0.75:
            i = rng.randrange(n); L = 1 if rng.random() < 0.6 else rng.randint(2, 8)
            blk = seq[i:i + L]; rest = seq[:i] + seq[i + L:]
            p = rng.randrange(len(rest) + 1); s = rest[:p] + blk + rest[p:]
        else:
            p = rng.randrange(n + 1); s = seq[:p] + [rng.choice(pool)] + seq[p:]
        c = simulate(P, s, tm, tq)
        if c is not None and c <= cur:
            seq = s; cur = c
    new, old = save_case(P, sys.argv[1], k, seq, "seq_ls")
    print(f"case {k}: {start} -> {cur} ({tries} tries) saved_prev {old}", flush=True)
