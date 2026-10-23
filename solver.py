import sys,random,math,time
from collections import defaultdict
rng=random.Random(5871)
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
cost=dict(prices);base={m:-1 for m in prices};opts=defaultdict(list)
for m in prices:opts[m].append(-1)
for i,(a,b,s) in enumerate(r):
 for m in b:opts[m].append(i)
for _ in range(500):
 changed=False
 for i,(a,b,s) in enumerate(r):
  if all(m in cost for m in a):
   c=sum(cost[m]*n for m,n in a.items())
   for m,n in b.items():
    if c/n < cost.get(m,float('inf'))-1e-9:
     cost[m]=c/n;base[m]=i;changed=True
 if not changed:break
# Mutations are biased toward economical routes but include every feasible option.
weights={}
for m,options in opts.items():
 w=[]
 for i in options:
  c=prices[m] if i==-1 else sum(cost.get(x,1e9)*k for x,k in r[i][0].items())/r[i][1][m]
  w.append(1/(1+c/max(cost.get(m,1),.01))**2)
 weights[m]=w

def evaluate(policy,target,n,order,collect=False):
 inv=defaultdict(int);spent=0;steps=[];used=set();counter=0
 def make(m,qty,stack):
  nonlocal spent,counter
  need=qty-inv[m]
  if need<=0:return
  used.add(m);i=policy.get(m,-1)
  if i==-1 or m in stack:
   if m not in prices:raise ValueError()
   inv[m]+=need;spent+=need*prices[m];return
  a,b,s=r[i];times=(need+b[m]-1)//b[m]
  if times>20000:raise ValueError()
  items=list(a.items())
  if order:items.sort(key=lambda x:order.get(x[0],0))
  for _ in range(times):
   for x,k in items:
    make(x,k,stack|{m});inv[x]-=k
   for x,k in b.items():inv[x]+=k
   counter+=1
   if counter>20000:raise ValueError()
   if collect:steps.append(i)
  if inv[m]<qty:raise ValueError()
 try:
  make(target,n,set())
  return spent,used,steps
 except (ValueError,RecursionError):return float('inf'),used,[]
answers=[]
start=time.monotonic()
for case,(n,target) in enumerate(cases):
 best=dict(base);bestorder={};score,used,_=evaluate(best,target,n,{})
 original=score
 # Search production choices against actual inventory costs, preserving the best.
 for iteration in range(1400):
  if time.monotonic()-start>100*(case+1)/len(cases):break
  policy=dict(best);order=dict(bestorder)
  mutable=[m for m in used if len(opts[m])>1]
  if not mutable:break
  count=1 if iteration%5 else rng.randint(2,min(6,len(mutable))+1)
  for _ in range(count):
   m=rng.choice(mutable)
   policy[m]=rng.choices(opts[m],weights[m])[0]
  if iteration%4==0:
   for m in rng.sample(list(cost),min(12,len(cost))):order[m]=rng.random()
  value,newused,_=evaluate(policy,target,n,order)
  if value<score or value==score and rng.random()<.07:
   score,best,bestorder,used=value,policy,order,newused
 _,_,steps=evaluate(best,target,n,bestorder,True)
 assert steps and score<float('inf')
 answers.append('\n'.join(r[i][2] for i in steps))
 print(f'case {case+1}: {original} -> {score}',file=sys.stderr)
sys.stdout.write('\n\n'.join(answers)+'\n')
