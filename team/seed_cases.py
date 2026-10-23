"""seed_cases.py <in>: split best/out_*.txt into per-case entries (kept only if better)."""
import sys
from lib import Problem, save_case, stem
P = Problem(sys.argv[1]); idx = {r[0]: j for j, r in enumerate(P.rx)}
paras = open(f"best/out_{stem(sys.argv[1])}.txt").read().strip('\n').split('\n\n')
for k, p in enumerate(paras):
    print(k, save_case(P, sys.argv[1], k, [idx[l] for l in p.split('\n') if l], "from best"))
