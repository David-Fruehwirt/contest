from collections import Counter
import random,time

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

if __name__=='__main__':
 from pathlib import Path
 import sys
 from schedule import parse
 prices,rs,qs=parse(sys.argv[1]);lookup={s:j for j,(a,b,s) in enumerate(rs)};reactions=[(a,b) for a,b,s in rs];out=[];total=0
 blocks=Path(sys.argv[2]).read_text().strip().split('\n\n')
 for case,(block,t) in enumerate(zip(blocks,qs)):
  value,steps=reorder([lookup[s] for s in block.splitlines()],reactions,prices,t,trials=100,max_seconds=.5)
  total+=value;out.append('\n'.join(rs[j][2] for j in steps));print(case+1,value,file=sys.stderr)
 Path(sys.argv[3]).write_text('\n\n'.join(out)+'\n');print('TOTAL',total,file=sys.stderr)
