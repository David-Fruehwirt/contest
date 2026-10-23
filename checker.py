import sys,json,re
from collections import defaultdict,Counter
def check():
 it=iter(x.strip() for x in sys.stdin if x.strip());buy={}
 for _ in range(int(next(it))):
  a,b=next(it).split(' -> ');buy[b]=int(a)
 def side(s):
  d=Counter()
  for t in s.split(','):
   n,m=t.split();d[m]+=int(n)
  return d
 reactions={}
 for _ in range(int(next(it))):
  s=next(it);a,b=s.split(' -> ');reactions[s]=(side(a),side(b))
 targets=[]
 for _ in range(int(next(it))):
  n,m=next(it).split();targets.append((int(n),m))
 text=open(sys.argv[1],encoding='utf-8-sig').read().strip()
 blocks=re.split(r'\n\s*\n',text)
 assert len(blocks)==len(targets),'paragraph count'
 cost=0
 for block,(n,m) in zip(blocks,targets):
  inv=Counter()
  for s in block.splitlines():
   a,b=reactions[s.strip()]
   for x,k in a.items():
    shortage=max(0,k-inv[x])
    if shortage:
     assert x in buy,'unavailable reactant'
     cost+=shortage*buy[x];inv[x]+=shortage
   inv.subtract(a);inv.update(b)
  assert inv[m]>=n,'target missing'
 return cost
try: print(json.dumps({'valid':True,'cost':check()}))
except Exception as e: print(json.dumps({'valid':False,'reason':str(e)}))
