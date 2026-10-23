from pathlib import Path
from collections import Counter
import re,sys,json
root=Path(__file__).resolve().parents[2]
def parse(inp):
    it=iter(x.strip() for x in inp.splitlines() if x.strip());buy={}
    for _ in range(int(next(it))):
        a,b=next(it).split(' -> ');buy[b]=int(a)
    def side(s):
        d=Counter()
        for term in s.split(','):
            n,m=term.split();d[m]+=int(n)
        return d
    reactions={}
    for _ in range(int(next(it))):
        s=next(it);a,b=s.split(' -> ');reactions[s]=side(a),side(b)
    targets=[]
    for _ in range(int(next(it))):
        n,m=next(it).split();targets.append((int(n),m))
    return buy,reactions,targets
def score(block,inp,target):
    buy,rr,_=inp; inv=Counter();cost=0
    for s in block.splitlines():
        a,b=rr[s.strip()]
        for x,k in a.items():
            shortage=max(0,k-inv[x])
            if shortage:
                assert x in buy
                cost+=shortage*buy[x];inv[x]+=shortage
        inv.subtract(a);inv.update(b)
    n,m=target;assert inv[m]>=n
    return cost
out=root/'experiments/search/merged';out.mkdir(exist_ok=True)
for i in range(1,5):
    inp=parse(next((root/'prepared/files').glob(f'in_level-3_{i}-*.txt')).read_text())
    paths=[root/f'exports/improved/output-{i}.txt',root/f'experiments/search/output-{i}.txt',root/f'experiments/search/lp-output-{i}.txt']
    candidates=[re.split(r'\n\s*\n',p.read_text().strip()) for p in paths if p.exists()]
    total=0;blocks=[]
    for j,target in enumerate(inp[2]):
        ranked=[]
        for candidate in candidates:
            try:ranked.append((score(candidate[j],inp,target),candidate[j]))
            except Exception:pass
        value,block=min(ranked);total+=value;blocks.append(block)
    (out/f'output-{i}.txt').write_text('\n\n'.join(blocks)+'\n')
    print(i,total)
