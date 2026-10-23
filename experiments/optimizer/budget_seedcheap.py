"""Construct reaction schedules from integer reaction quotas with purchase budgets.
schedule(prices, reactions, target, quotas, trials=40) returns (cost, reaction_indices).
reactions = [(Counter(inputs), Counter(outputs)), ...]; target=(quantity,molecule).
"""
from collections import Counter
import random,math

def schedule(prices,reactions,target,quotas,trials=40,simplify=True):
 rng=random.Random(157);unit=dict(prices);base={m:-1 for m in prices}
 for _ in range(500):
  changed=False
  for j,(a,b) in enumerate(reactions):
   if all(m in unit for m in a):
    cost=sum(unit[m]*k for m,k in a.items())
    for m,k in b.items():
     if cost/k<unit.get(m,1e50)-1e-8:unit[m]=cost/k;base[m]=j;changed=True
  if not changed:break
 count0=[max(0,math.ceil(x-1e-6)) for x in quotas];bal=Counter()
 for count,(a,b) in zip(count0,reactions):
  for m,k in a.items():bal[m]-=count*k
  for m,k in b.items():bal[m]+=count*k
 if simplify:
  bal[target[1]]-=target[0]
  while True:
   choices=[]
   for j,(count,(a,b)) in enumerate(zip(count0,reactions)):
    if not count:continue
    net=Counter(b);net.subtract(a)
    if any(m not in prices and bal[m]-k<0 for m,k in net.items()):continue
    delta=sum((max(0,-bal[m]+k)-max(0,-bal[m]))*prices[m] for m,k in net.items() if m in prices)
    if delta<=0:choices.append((delta+rng.random()*.1,j,net))
   if not choices:break
   _,j,net=min(choices);count0[j]-=1;bal.subtract(net)
  bal[target[1]]+=target[0]
 allowance={m:max(0,-bal[m]) for m in prices}
 best=(10**30,None)
 for trial in range(trials):
  counts=count0[:];virtual=Counter(allowance);physical=Counter();steps=[];paid=0
  def fire(j):
   nonlocal paid
   a,b=reactions[j]
   if not all(virtual[m]>=k for m,k in a.items()):raise ValueError('virtual unavailable')
   for m,k in a.items():
    d=max(0,k-physical[m])
    if d and m not in prices:raise ValueError('physical unavailable')
    paid+=d*prices.get(m,0);physical[m]+=d-k;virtual[m]-=k
   physical.update(b);virtual.update(b);steps.append(j)
   if counts[j]>0:counts[j]-=1
  def make(m,n,stack):
   if virtual[m]>=n:return
   if m in prices and (base[m]==-1 or m in stack):virtual[m]=n;return
   if m in stack:raise ValueError('base cycle')
   j=base[m];a,b=reactions[j]
   while virtual[m]<n:
    for _ in range(100):
     for x,k in a.items():make(x,k,stack|{m})
     if all(virtual[x]>=k for x,k in a.items()):break
    else:raise ValueError('dependency consumes sibling')
    fire(j)
    if len(steps)>10000:raise ValueError('long')
  try:
   for _ in range(20000):
    if physical[target[1]]>=target[0]:break
    choices=[]
    for j,n in enumerate(counts):
     if n and all(virtual[m]>=k for m,k in reactions[j][0].items()):
      # Small random priorities explore ordering, with expensive purchases delayed.
      p=sum(max(0,k-physical[m])*prices.get(m,0) for m,k in reactions[j][0].items())
      choices.append((p+rng.random()*[0,10,100,1000][trial%4],j))
    if choices:_,j=min(choices)
    else:
     remain=[j for j,n in enumerate(counts) if n]
     if not remain:raise ValueError('quota target missing')
     # Prefer cheap shop seeds before manufacturing extra molecules.
     scores=[]
     for j in remain:
      ds=[(m,max(0,k-virtual[m])) for m,k in reactions[j][0].items()]
      c=sum(d*unit.get(m,1e20) for m,d in ds)
      scores.append((c+rng.random()*[0,10,100,1000][trial%4],j))
     _,j=min(scores)
     for _ in range(100):
      for m,k in reactions[j][0].items():make(m,k,set())
      if all(virtual[m]>=k for m,k in reactions[j][0].items()):break
     else:raise ValueError('quota consume sibling')
    fire(j)
   if physical[target[1]]>=target[0] and paid<best[0]:best=(paid,steps[:])
  except (ValueError,RecursionError):pass
 return best

if __name__=='__main__':
 import sys
 from pathlib import Path
 from schedule import parse
 prices,rs,targets=parse(sys.argv[1]);reactions=[(a,b) for a,b,s in rs];plans=[[float(x) for x in s.split()][:len(rs)] for s in Path(sys.argv[2]).read_text().splitlines()];answers=[];total=0
 for c,(t,q) in enumerate(zip(targets,plans)):
  value,steps=schedule(prices,reactions,t,q)
  print(c+1,value,len(steps or []),file=sys.stderr)
  assert steps is not None
  answers.append('\n'.join(rs[j][2] for j in steps));total+=value
 Path(sys.argv[3]).write_text('\n\n'.join(answers)+'\n');print('TOTAL',total,file=sys.stderr)
