from pathlib import Path
from schedule import parse
from collections import Counter
P=Path('local-levels/level-3')
for i,n in enumerate(['1-small','2-medium','3-large','4-enormous'],1):
 buy,rs,qs=parse(P/'prepared/files'/('in_level-3_'+n+'.txt'));d={s:(a,b) for a,b,s in rs};blocks=(P/'exports/under-120k'/('output-'+str(i)+'.txt')).read_text().strip().split('\n\n');net=0
 for ci,block in enumerate(blocks,1):
  bal=Counter();inv=Counter();cost=0
  for s in block.splitlines():
   a,b=d[s];bal.subtract(a);bal.update(b)
   for m,k in a.items():
    need=max(0,k-inv[m]);cost+=need*buy.get(m,0);inv[m]+=need-k
   inv.update(b)
  nc=sum(max(0,-bal[m])*p for m,p in buy.items());net+=nc
  print(i,ci,'net',nc,'actual',cost,'overhead',cost-nc)
 print('FILE',i,net)
