import sys,os,math,random,json,time
sys.path.insert(0,r'C:/Users/david_bmq3pz5/Documents/CCC/local-levels/level-3/experiments/dependencies')
import highspy
from collections import Counter,defaultdict
rng=random.Random(42)
it=iter(x.strip() for x in sys.stdin if x.strip());prices={}
for _ in range(int(next(it))):
 a,b=next(it).split(' -> ');prices[b]=int(a)
def side(s):
 d=Counter()
 for t in s.split(','):
  n,m=t.split();d[m]+=int(n)
 return d
rs=[]
for _ in range(int(next(it))):
 s=next(it);a,b=s.split(' -> ');rs.append((side(a),side(b),s))
qs=[]
for _ in range(int(next(it))):
 n,m=next(it).split();qs.append((int(n),m))
names=sorted(set(prices)|{m for a,b,s in rs for m in a|b});R=len(rs)
# Feasible base routes used exclusively to seed deadlocked supports.
unit=dict(prices);route={m:-1 for m in prices}
for _ in range(500):
 change=False
 for j,(a,b,s) in enumerate(rs):
  if not all(m in unit for m in a):continue
  c=sum(unit[m]*k for m,k in a.items())
  for m,k in b.items():
   if c/k<unit.get(m,1e100)-1e-9:unit[m]=c/k;route[m]=j;change=True
 if not change:break
h=highspy.Highs();h.setOptionValue('output_flag',False);h.setOptionValue('threads',1);h.setOptionValue('time_limit',float(os.getenv('CHEM_TIME','3')));h.setOptionValue('mip_rel_gap',.005)
x=h.addVariables(R,lb=0,obj=float(os.getenv('CHEM_REACTION_COST','.00001')),type=highspy.HighsVarType.kInteger)
y={m:h.addVariable(lb=0,obj=p,type=highspy.HighsVarType.kInteger) for m,p in prices.items()}
# Proven conserved elemental pools require startup stock before a firing.
import re
atoms={}
for m in names:
 tokens=re.findall(r'([A-Z][a-z]?)([0-9]*)',m)
 assert ''.join(e+q for e,q in tokens)==m,('unparsed formula',m)
 atoms[m]=Counter()
 for e,q in tokens:atoms[m][e]+=int(q or 1)
elements=set().union(*(set(a) for a in atoms.values()))
conserved={e for e in elements if all(sum(k*atoms[m][e] for m,k in a.items())==sum(k*atoms[m][e] for m,k in b.items()) for a,b,s in rs)}
# Only elements absent from every target need explicit capital beyond product demand.
pools=sorted(e for e in conserved if all(atoms[m][e]==0 for _,m in qs))
activations={}
for j,(a,b,s) in enumerate(rs):
 demands={e:sum(k*atoms[m][e] for m,k in a.items()) for e in pools}
 demands={e:q for e,q in demands.items() if q}
 if demands:
  z=h.addVariable(lb=0,ub=1,type=highspy.HighsVarType.kInteger)
  activations[j]=z
  h.addConstr(x[j]<=2000*z)
  for e,q in demands.items():
   capital=sum(atoms[m][e]*v for m,v in y.items() if atoms[m][e])
   h.addConstr(capital>=q*z)
print('capital pools',pools,'activated reactions',len(activations),file=sys.stderr)
cons={}
for m in names:
 expr=sum((b.get(m,0)-a.get(m,0))*x[j] for j,(a,b,s) in enumerate(rs) if b.get(m,0)!=a.get(m,0))
 if m in y:expr+=y[m]
 cons[m]=h.addConstr(expr>=0)

def schedule(counts,purchases,target,need):
 best=(float('inf'),[])
 for trial in range(16):
  remain=counts[:];inv=Counter(purchases);steps=[]
  def fire(j):
   a,b,s=rs[j]
   for m,k in a.items():
    if inv[m]<k:
     if m not in prices:raise ValueError('missing input')
     inv[m]=k
   inv.subtract(a);inv.update(b);steps.append(j)
  def make(m,k,stack):
   if inv[m]>=k:return
   if m in prices:inv[m]=k;return
   if m in stack:raise ValueError('cyclic seed')
   j=route[m];a,b,s=rs[j]
   for _ in range(10000):
    if inv[m]>=k:return
    # Ensure all inputs simultaneously available; producer can consume siblings.
    for rep in range(20):
     if all(inv[v]>=q for v,q in a.items()):break
     for v,q in a.items():
      if inv[v]<q:make(v,q,stack|{m})
    fire(j)
   raise ValueError('seed cap')
  try:
   for step in range(50000):
    if inv[target]>=need:break
    avail=[j for j,c in enumerate(remain) if c and all(inv[m]>=k for m,k in rs[j][0].items())]
    if avail:
     if trial==0:j=avail[0]
     else:j=rng.choice(avail)
    else:
     candidates=[j for j,c in enumerate(remain) if c]
     if not candidates:break
     j=min(candidates,key=lambda j:sum(max(0,k-inv[m])*unit[m] for m,k in rs[j][0].items())*(1+rng.random()*(trial%4)))
     for rep in range(20):
      if all(inv[m]>=k for m,k in rs[j][0].items()):break
      for m,k in rs[j][0].items():
       if inv[m]<k:make(m,k,set())
    remain[j]-=1;fire(j)
   # Independent replay from empty inventory with purchases only at consumption.
   actual=Counter();cost=0
   for j in steps:
    a,b,s=rs[j]
    for m,k in a.items():
     missing=max(0,k-actual[m])
     if missing:
      if m not in prices:raise ValueError('invalid replay')
      cost+=prices[m]*missing;actual[m]+=missing
    actual.subtract(a);actual.update(b)
   if actual[target]>=need and cost<best[0]:best=(cost,steps[:])
  except (ValueError,RecursionError):pass
 return best
def budget_schedule(prices,reactions,target,quotas,trials=40,simplify=True):
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
  def make(m,n,stack):
   if virtual[m]>=n:return
   if m in prices:virtual[m]=n;return
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
    fire(j);counts[j]-=1
   if physical[target[1]]>=target[0] and paid<best[0]:best=(paid,steps[:])
  except (ValueError,RecursionError):pass
 return best


def budget_schedule_capital(prices,reactions,target,quotas,trials=40,simplify=True,purchases=None):
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
 allowance={m:max(0,-bal[m],(purchases or {}).get(m,0)) for m in prices}
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


answers=[]
for case,(need,target) in enumerate(qs):
 h.changeRowBounds(cons[target].index,need,highspy.kHighsInf)
 # Feasible incumbent from basic production protects short MIP time limits.
 initial=Counter();bought=Counter();seed=[]
 def make_seed(m,k,stack):
  if initial[m]>=k:return
  if m in prices and route[m]==-1 or m in stack:
   assert m in prices
   d=k-initial[m];initial[m]+=d;bought[m]+=d;return
  j=route[m];a,b,_=rs[j]
  while initial[m]<k:
   for rep in range(100):
    for v,q in a.items():make_seed(v,q,stack|{m})
    if all(initial[v]>=q for v,q in a.items()):break
   else:raise RuntimeError('seed mismatch')
   initial.subtract(a);initial.update(b);seed.append(j)
 make_seed(target,need,set())
 seedcounts=Counter(seed)
 inds=[v.index for v in x]+[v.index for v in y.values()]
 vals=[seedcounts[j] for j in range(R)]+[bought[m] for m in y]
 inds.extend(v.index for v in activations.values());vals.extend(int(seedcounts[j]>0) for j in activations)
 h.setSolution(len(inds),inds,vals)
 h.run();sol=h.getSolution();info=h.getInfo()
 if not sol.value_valid:raise RuntimeError('no MIP solution')
 counts=[max(0,round(sol.col_value[v.index])) for v in x]
 purchases={m:max(0,round(sol.col_value[v.index])) for m,v in y.items()}
 candidates=[budget_schedule_capital(prices,[(a,b) for a,b,s in rs],(need,target),counts,trials=int(os.getenv("CHEM_TRIALS","24")),purchases=purchases),budget_schedule_capital(prices,[(a,b) for a,b,s in rs],(need,target),counts,trials=16)]
 value,steps=min(candidates,key=lambda v:v[0])
 if os.getenv('CHEM_PLAN'):
  with open(os.getenv('CHEM_PLAN'),'a') as planfile:planfile.write(json.dumps({'case':case+1,'counts':counts,'purchases':purchases})+'\n')
 print(json.dumps({'case':case+1,'bound':info.mip_dual_bound,'model':info.objective_function_value,'cost':value,'steps':len(steps)}),file=sys.stderr)
 assert steps and math.isfinite(value)
 answers.append('\n'.join(rs[j][2] for j in steps))
 h.changeRowBounds(cons[target].index,0,highspy.kHighsInf)
sys.stdout.write('\n\n'.join(answers)+'\n')

