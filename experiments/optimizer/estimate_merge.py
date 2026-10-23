from pathlib import Path
from schedule import parse
from collections import Counter
P=Path('local-levels/level-3');total=0
for i,n in enumerate(['small','medium','large','enormous'],1):
 inp=list((P/'prepared/files').glob('in_level-3_'+str(i)+'-*'))[0];buy,rs,qs=parse(inp);d={s:(a,b) for a,b,s in rs}
 candidates=list((P/'exports').glob('*/output-'+str(i)+'.txt'))
 candidates+=[P/'experiments/optimizer'/f'{prefix}-{n}.out' for prefix in ['reorder','poolreorder','seedcheap','seedplanned','budget']]
 candidates+=[P/'experiments/search'/f'pool-budget-output-{i}.txt',P/'experiments/search/merged'/f'output-{i}.txt']
 best=[10**20]*len(qs)
 for f in candidates:
  if not f.exists():continue
  blocks=f.read_text().strip().split('\n\n')
  if len(blocks)!=len(qs):continue
  for ci,(block,(num,target)) in enumerate(zip(blocks,qs)):
   inv=Counter();cost=0
   for s in block.splitlines():
    a,b=d[s]
    for m,k in a.items():
     shortage=max(0,k-inv[m])
     if shortage and m not in buy:cost=10**20;break
     cost+=shortage*buy.get(m,0);inv[m]+=shortage-k
    inv.update(b)
   if inv[target]>=num:best[ci]=min(best[ci],cost)
 subtotal=sum(best);total+=subtotal;print(n,subtotal)
print('TOTAL',total)
