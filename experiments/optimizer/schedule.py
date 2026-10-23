import sys,math,random
from collections import defaultdict,Counter
root='local-levels/level-3/'
def parse(path):
 it=iter(x.strip() for x in open(path) if x.strip());buy={}
 for _ in range(int(next(it))):
  a,b=next(it).split(' -> ');buy[b]=int(a)
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
 return buy,rs,qs
if __name__=='__main__':
 buy,rs,qs=parse(sys.argv[1]);plans=[list(map(float,s.split())) for s in open(sys.argv[2])];rng=random.Random(1);answers=[]
 for case,((need,target),plan) in enumerate(zip(qs,plans)):
  best=1e100;bst=[]
  for trial in range(100):
   counts=[int(math.ceil(x-1e-7)) for x in plan[:len(rs)]];inv=Counter();cost=0;steps=[]
   while sum(counts):
    choices=[]
    for i,n in enumerate(counts):
     if not n:continue
     a,b,s=rs[i]
     if all(inv[m]>=k or m in buy for m,k in a.items()):
      c=sum(max(0,k-inv[m])*buy.get(m,0) for m,k in a.items())
      choices.append((c+rng.random()*[0,10,100,1000][trial%4],i))
    if not choices:break
    _,i=min(choices);a,b,s=rs[i];counts[i]-=1;steps.append(i)
    for m,k in a.items():
     c=max(0,k-inv[m]);cost+=c*buy.get(m,0);inv[m]+=c-k
    inv.update(b)
    if inv[target]>=need:break
   if inv[target]>=need and cost<best:best=cost;bst=steps[:]
  print(case+1,best,len(bst),file=sys.stderr)
  answers.append('\n'.join(rs[i][2] for i in bst))
 open(sys.argv[3],'w').write('\n\n'.join(answers)+'\n')
