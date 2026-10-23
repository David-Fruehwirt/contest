from pathlib import Path
from collections import Counter
import sys,re,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'dependencies'))
import highspy
from prune import parse
from capital_constraints import add_capital_constraints,formula
root=Path('local-levels/level-3');run=Path('.ccc/runs/898a40f6de4c4fe380c813005708a5c0')
i=int(sys.argv[1]);name=['small','medium','large','enormous'][i-1]
prices,rs,ts=parse(root/f'prepared/files/in_level-3_{i}-{name}.txt');texts=list(rs);ri={s:j for j,s in enumerate(texts)};reactions=list(rs.values());R=len(texts)
h=highspy.Highs();h.setOptionValue('output_flag',False);h.setOptionValue('threads',1);h.setOptionValue('time_limit',float(sys.argv[2]) if len(sys.argv)>2 else 1)
x=h.addVariables(R,lb=0,obj=0,type=highspy.HighsVarType.kInteger)
y={m:h.addVariable(lb=0,obj=p,type=highspy.HighsVarType.kInteger) for m,p in prices.items()}
names=set(prices)|{m for a,b in reactions for m in a|b};cons={}
for m in names:
    expr=sum((b[m]-a[m])*x[j] for j,(a,b) in enumerate(reactions) if b[m]!=a[m])
    if m in y:expr+=y[m]
    cons[m]=h.addConstr(expr>=0)
zs=add_capital_constraints(h,x,y,reactions)
blocks=re.split(r'\n\s*\n',(run/f'output-{i}.txt').read_text().strip());results=[]
for case,((need,target),block) in enumerate(zip(ts,blocks)):
    h.changeRowBounds(cons[target].index,need,highspy.kHighsInf)
    inv=Counter();purchases=Counter();counts=Counter(ri[s] for s in block.splitlines())
    for s in block.splitlines():
        a,b=rs[s]
        for m,k in a.items():
            d=max(0,k-inv[m]);purchases[m]+=d;inv[m]+=d
        inv.subtract(a);inv.update(b)
    zvalues={}
    for (e,d),v in zs.items():
        active=any(counts[j] and sum(k*formula(m)[e] for m,k in a.items())==d for j,(a,b) in enumerate(reactions))
        zvalues[e,d]=int(active)
    inds=[v.index for v in x]+[v.index for v in y.values()]+[v.index for v in zs.values()]
    vals=[counts[j] for j in range(R)]+[purchases[m] for m in y]+[zvalues[k] for k in zs]
    h.setSolution(len(inds),inds,vals);h.run();info=h.getInfo()
    result={'case':case+1,'target':target,'need':need,'bound':info.mip_dual_bound,'incumbent':info.objective_function_value,'actual':sum(prices[m]*purchases[m] for m in prices)}
    results.append(result);print(json.dumps(result),flush=True)
    h.changeRowBounds(cons[target].index,0,highspy.kHighsInf)
Path(__file__).with_name(f'capital-bounds-{i}.json').write_text(json.dumps(results))
