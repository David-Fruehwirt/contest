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
h=highspy.Highs();h.setOptionValue('output_flag',False);h.setOptionValue('threads',1);h.setOptionValue('time_limit',5.0);h.setOptionValue('mip_rel_gap',.005)
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

def budget_schedule(prices,reactions,target,quotas,trials=40,simplify=True,purchases=None):
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


def cheap_schedule(prices,reactions,target,quotas,trials=40,simplify=True,purchases=None):
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


def reorder(steps,reactions,prices,target,trials=100,max_seconds=8):
 """Return (purchase cost, reaction indices), preserving the input as fallback.
 reactions = [(Counter inputs, Counter outputs),...]; target=(quantity,molecule).
 Only reorders/truncates the input reaction multiset; never adds reactions.
 """
 started=time.monotonic();rng=random.Random(331)
 support=list(dict.fromkeys(steps));local={j:i for i,j in enumerate(support)}
 mols=set(prices)
 for j in support:
  a,b=reactions[j];mols.update(a);mols.update(b)
 names=list(mols);ids={m:i for i,m in enumerate(names)};K=len(names)
 p=[prices.get(m,-1) for m in names];ti=ids[target[1]];need=target[0]
 ar=[[(ids[m],k) for m,k in reactions[j][0].items()] for j in support]
 br=[[(ids[m],k) for m,k in reactions[j][1].items()] for j in support]
 adj=[set() for _ in range(K)]
 for j,a in enumerate(ar):
  for m,k in a:adj[m].add(j)
 cnt0=[0]*len(support);bal=[0]*K
 for j in steps:cnt0[local[j]]+=1
 for j,count in enumerate(cnt0):
  for m,k in ar[j]:bal[m]-=k*count
  for m,k in br[j]:bal[m]+=k*count
 allow=[max(0,-v) if p[m]>=0 else 0 for m,v in enumerate(bal)]
 original=list(steps);best=original;bst=0;iv=[0]*K
 for old in original:
  j=local[old]
  for m,k in ar[j]:
   d=max(0,k-iv[m])
   if d and p[m]<0:return float('inf'),original
   bst+=d*max(0,p[m]);iv[m]+=d-k
  for m,k in br[j]:iv[m]+=k
 if iv[ti]<need:return float('inf'),original
 noises=[0,3,10,30,100,300,1000]
 for tr in range(trials):
  if tr and time.monotonic()-started>max_seconds:break
  counts=cnt0[:];virt=allow[:];phys=[0]*K;cost=0;seq=[]
  ready={j for j,a in enumerate(ar) if all(virt[m]>=k for m,k in a)}
  priorities=[rng.random() for _ in support]
  for step in range(len(original)):
   at=-1;bs=1e100
   if ready:
    for j in ready:
     d=sum(max(0,k-phys[m])*max(0,p[m]) for m,k in ar[j])
     v=d+rng.random()*noises[tr%7]
     if tr%11==0:v=rng.random()*1000
     if tr%13==0:v=priorities[j]*1000
     if v<bs:bs=v;at=j
   else:
    for j,a in enumerate(ar):
     if not counts[j] or any(virt[m]<k and p[m]<0 for m,k in a):continue
     d=sum(max(0,k-virt[m])*max(0,p[m]) for m,k in a)
     actual=sum(max(0,k-phys[m])*max(0,p[m]) for m,k in a)
     v=d*1000+actual+rng.random()*noises[tr%7]
     if v<bs:bs=v;at=j
   if at<0:break
   changed=set()
   for m,k in ar[at]:
    virt[m]=max(virt[m],k)-k
    d=max(0,k-phys[m]);cost+=d*max(0,p[m]);phys[m]+=d-k;changed.add(m)
   for m,k in br[at]:virt[m]+=k;phys[m]+=k;changed.add(m)
   counts[at]-=1;seq.append(support[at])
   if cost>=bst:break
   if phys[ti]>=need:bst=cost;best=seq[:];break
   affected={at}
   for m in changed:affected.update(adj[m])
   for j in affected:
    if counts[j] and all(virt[m]>=k for m,k in ar[j]):ready.add(j)
    else:ready.discard(j)
 return bst,best


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
 value,steps=budget_schedule(prices,[(a,b) for a,b,s in rs],(need,target),counts,trials=40,purchases=purchases)
 alternative,altsteps=cheap_schedule(prices,[(a,b) for a,b,s in rs],(need,target),counts,trials=40,purchases=purchases)
 if alternative<value:value,steps=alternative,altsteps
 if steps:value,steps=reorder(steps,[(a,b) for a,b,s in rs],prices,(need,target),trials=100,max_seconds=.5)
 print(json.dumps({'case':case+1,'bound':info.mip_dual_bound,'model':info.objective_function_value,'cost':value,'steps':len(steps)}),file=sys.stderr)
 assert steps and math.isfinite(value)
 answers.append('\n'.join(rs[j][2] for j in steps))
 h.changeRowBounds(cons[target].index,0,highspy.kHighsInf)
sys.stdout.write('\n\n'.join(answers)+'\n')

