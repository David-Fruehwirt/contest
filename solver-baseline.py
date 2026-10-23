import sys
from collections import defaultdict
lines=iter(x.strip() for x in sys.stdin if x.strip())
prices={}
for _ in range(int(next(lines))):
 a,b=next(lines).split(' -> ');prices[b]=int(a)
def side(s):
 d=defaultdict(int)
 for p in s.split(', '):
  n,m=p.split();d[m]+=int(n)
 return dict(d)
r=[]
for _ in range(int(next(lines))):
 s=next(lines);a,b=s.split(' -> ');r.append((side(a),side(b),s))
cases=[]
for _ in range(int(next(lines))):
 n,m=next(lines).split();cases.append((int(n),m))
cost=dict(prices);choice={m:None for m in prices}
for _ in range(500):
 changed=False
 for i,(a,b,s) in enumerate(r):
  if all(m in cost for m in a):
   c=sum(cost[m]*n for m,n in a.items())
   for m,n in b.items():
    if c/n < cost.get(m,float('inf'))-1e-9:
     cost[m]=c/n;choice[m]=i;changed=True
 if not changed:break
answers=[]
for n,target in cases:
 inv=defaultdict(int);out=[]
 def make(m,qty,stack=()):
  need=qty-inv[m]
  if need<=0:return
  i=choice.get(m)
  if i is None or m in stack:
   assert m in prices
   inv[m]+=need;return
  a,b,s=r[i];times=(need+b[m]-1)//b[m]
  for _ in range(times):
   for x,k in a.items():make(x,k,stack+(m,))
   for x,k in a.items():inv[x]-=k
   for x,k in b.items():inv[x]+=k
   out.append(s)
 make(target,n)
 answers.append('\n'.join(out))
sys.stdout.write('\n\n'.join(answers)+'\n')
