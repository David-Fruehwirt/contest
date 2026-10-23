"""merge.py <in>: assemble best per-case sequences into runs/merged_<stem>.txt, then promote."""
import sys, os, subprocess
from lib import Problem, stem
P = Problem(sys.argv[1]); s = stem(sys.argv[1]); paras = []
for k in range(len(P.targets)):
    f = f"cases/{s}/{k}.txt"
    if not os.path.exists(f): sys.exit(f"missing case {k}")
    paras.append(open(f).read().split('\n', 1)[1].strip('\n'))
out = f"runs/merged_{s}.txt"
open(out, 'w').write('\n\n'.join(paras) + '\n')
subprocess.run(["./promote.sh", sys.argv[1], out])
