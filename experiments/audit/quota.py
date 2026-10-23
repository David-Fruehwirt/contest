from prune import parse,cost,prune
from pathlib import Path
from collections import Counter,defaultdict
import sys,math,random
rng=random.Random(131)
prices,rs,targets=parse(Path(sys.argv[1]));texts=list(rs);reactions=[rs[s] for s in texts];R=len(texts)
plans=[list(map(float,s.split()))[:R] for s in Path(sys.argv[2]).read_text().splitlines()]
unit=dict(prices);base={m:-1 for m in prices};opts=defaultdict(list)
for i,(a,b) in enumerate(reactions):
    for m in b:opts[m].append(i)
for _ in range(200):
    changed=False
    for i,(a,b) in enumerate(reactions):
        if all(m in unit for m in a):
            c=sum(unit[m]*k for m,k in a.items())
            for m,k in b.items():
                if c/k<unit.get(m,1e50)-1e-8:unit[m]=c/k;base[m]=i;changed=True
    if not changed:break
net=[]
for a,b in reactions:
    v=Counter(b);v.subtract(a);net.append(v)
def balances(counts,t):
    bal=Counter({t[1]:-t[0]})
    for n,v in zip(counts,net):
        if n:
            for m,k in v.items():bal[m]+=n*k
    return bal
def objective(bal):return sum(max(0,-bal[m])*p for m,p in prices.items())
def repair(counts,t):
    bal=balances(counts,t)
    for _ in range(2000):
        deficit=[m for m,k in bal.items() if k<0 and m not in prices]
        if not deficit:return True
        m=max(deficit,key=lambda x:-bal[x]*unit.get(x,1e20));j=base[m]
        if j==-1:return False
        n=math.ceil(-bal[m]/net[j][m]);counts[j]+=n
        for x,k in net[j].items():bal[x]+=n*k
    return False
def simplify(counts,t):
    bal=balances(counts,t);value=objective(bal)
    for _ in range(4000):
        candidates=[]
        for j,n in enumerate(counts):
            if not n:continue
            if any(m not in prices and bal[m]-k<0 for m,k in net[j].items()):continue
            delta=sum((max(0,-bal[m]+k)-max(0,-bal[m]))*prices[m] for m,k in net[j].items() if m in prices)
            if delta<=0:candidates.append((delta+rng.random()*.1,j))
        if not candidates:break
        _,j=min(candidates);counts[j]-=1
        for m,k in net[j].items():bal[m]-=k
    return objective(bal)
def schedule(counts,t,trial):
    counts=counts[:];inv=Counter();steps=[];paid=0
    def fire(j):
        nonlocal paid
        a,b=reactions[j]
        for m,k in a.items():
            d=max(0,k-inv[m])
            if d and m not in prices:raise ValueError('unavailable')
            paid+=d*prices.get(m,0);inv[m]+=d-k
        inv.update(b);steps.append(j)
    def make(m,n,stack):
        nonlocal paid
        if inv[m]>=n:return
        if m in prices:
            d=n-inv[m];paid+=d*prices[m];inv[m]+=d;return
        if m in stack:raise ValueError('cycle')
        j=base[m];a,b=reactions[j]
        while inv[m]<n:
            for x,k in a.items():make(x,k,stack|{m})
            fire(j)
            if len(steps)>20000:raise ValueError('too long')
    for _ in range(20000):
        if inv[t[1]]>=t[0]:return paid,[texts[j] for j in steps]
        choices=[]
        for j,n in enumerate(counts):
            if not n:continue
            a,b=reactions[j]
            if all(inv[m]>=k or m in prices for m,k in a.items()):
                p=sum(max(0,k-inv[m])*prices.get(m,0) for m,k in a.items())
                choices.append((p+rng.random()*[0,3,10,100][trial%4],j))
        if not choices:
            remain=[j for j,n in enumerate(counts) if n]
            if not remain:break
            j=min(remain,key=lambda j:sum(max(0,k-inv[m])*unit[m] for m,k in reactions[j][0].items()))
            for m,k in reactions[j][0].items():
                if m not in prices:make(m,k,set())
        else:_,j=min(choices)
        fire(j);counts[j]-=1
    raise ValueError('target missing')
answers=[];total=0
for c,(plan,t) in enumerate(zip(plans,targets)):
    bst=10**20;seq=None;lb=0
    for trial in range(40):
        counts=[max(0,math.ceil(v-1e-6)) for v in plan]
        assert repair(counts,t)
        lb=simplify(counts,t)
        try:value,ss=schedule(counts,t,trial)
        except (ValueError,RecursionError):continue
        pp=prune(ss,rs,t);value=cost(pp,prices,rs,t)
        if value<bst:bst,seq=value,pp
    assert seq is not None
    total+=bst;answers.append('\n'.join(seq));print(c+1,'net',lb,'actual',bst,file=sys.stderr)
Path(sys.argv[3]).write_text('\n\n'.join(answers)+'\n');print('TOTAL',total,file=sys.stderr)
