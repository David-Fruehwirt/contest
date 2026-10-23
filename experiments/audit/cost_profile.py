from prune import parse
from collections import Counter
from pathlib import Path
import sys,re,json
root=Path('local-levels/level-3');run=Path('.ccc/runs/898a40f6de4c4fe380c813005708a5c0')
for i,name in enumerate(['small','medium','large','enormous'],1):
    prices,rs,ts=parse(root/f'prepared/files/in_level-3_{i}-{name}.txt')
    blocks=re.split(r'\n\s*\n',(run/f'output-{i}.txt').read_text().strip())
    bought=Counter();leftover=Counter();seqnet=0;case=[]
    for block,t in zip(blocks,ts):
        inv=Counter();bp=Counter()
        for s in block.splitlines():
            a,b=rs[s]
            for m,k in a.items():
                d=max(0,k-inv[m])
                if d:
                    assert m in prices
                    inv[m]+=d;bp[m]+=d
            inv.subtract(a);inv.update(b)
        cost=sum(n*prices[m] for m,n in bp.items())
        waste=sum(inv[m]*prices[m] for m in prices)
        case.append({'cost':cost,'buyable_leftover_value':waste})
        bought.update({m:n*prices[m] for m,n in bp.items()})
        leftover.update({m:inv[m]*prices[m] for m in prices})
    model=[json.loads(s) for s in (run/f'output-{i}.stderr').read_text().splitlines()]
    print(name,'cost',sum(c['cost'] for c in case),'mip-net',sum(c['model'] for c in model),'bound',sum(c['bound'] for c in model))
    print('purchase-top',bought.most_common(12))
    print('leftovers',sum(leftover.values()),leftover.most_common(12))
    print('cases',case)
