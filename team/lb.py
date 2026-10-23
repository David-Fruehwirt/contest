"""lb.py <in>: net-balance ILP optimum per case (a valid global lower bound)."""
import sys, json, os
from lib import Problem, net_ilp, stem
P = Problem(sys.argv[1]); out = {}
for k, (tm, tq) in enumerate(P.targets):
    cost, xs, bs, st, bd = net_ilp(P, tm, tq, time_limit=20)
    out[k] = cost if st == 'OPTIMAL' else int(bd)
    print(k, tq, tm, cost, st, flush=True)
os.makedirs('lbs', exist_ok=True)
json.dump(out, open(f"lbs/{stem(sys.argv[1])}.json", 'w'))
print("LB total", sum(out.values()))
