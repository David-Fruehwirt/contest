from pathlib import Path
from collections import Counter
import re
root=Path(__file__).resolve().parents[2]
def side(s):
    d=Counter()
    for z in s.split(', '):
        k,m=z.split();d[m]+=int(k)
    return d
def parse(p):
    it=iter(z.strip() for z in p.read_text().splitlines() if z.strip())
    prices={}
    for _ in range(int(next(it))):
        k,m=next(it).split(' -> ');prices[m]=int(k)
    rs={}
    for _ in range(int(next(it))):
        s=next(it);a,b=s.split(' -> ');rs[s]=(side(a),side(b))
    ts=[]
    for _ in range(int(next(it))):
        k,m=next(it).split();ts.append((int(k),m))
    return prices,rs,ts
def cost(seq,prices,rs,t):
    inv=Counter();c=0
    for s in seq:
        a,b=rs[s]
        for m,k in a.items():
            n=max(0,k-inv[m])
            if n and m not in prices:return 10**15
            c+=n*prices.get(m,0);inv[m]+=n
        inv.subtract(a);inv.update(b)
    return c if inv[t[1]]>=t[0] else 10**15
def prune(seq,rs,t):
    needs=Counter({t[1]:t[0]});out=[]
    for s in reversed(seq):
        a,b=rs[s]
        if any(needs[m]>0 for m in b):
            out.append(s)
            for m,k in b.items():needs[m]=max(0,needs[m]-k)
            needs.update(a)
    return list(reversed(out))
if __name__=='__main__':
    for i,name in enumerate(['small','medium','large','enormous'],1):
        prices,rs,ts=parse(root/f'prepared/files/in_level-3_{i}-{name}.txt')
        blocks=re.split(r'\n\s*\n',(root/f'exports/improved/output-{i}.txt').read_text().strip())
        outs=[];old=0;new=0
        for block,t in zip(blocks,ts):
            seq=block.splitlines();a=cost(seq,prices,rs,t)
            ps=prune(seq,rs,t);b=cost(ps,prices,rs,t)
            assert b<=a,(a,b)
            old+=a;new+=b;outs.append('\n'.join(ps))
        (Path(__file__).parent/f'pruned-{i}.txt').write_text('\n\n'.join(outs)+'\n')
        print(name,old,new)
