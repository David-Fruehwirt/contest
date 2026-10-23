from pathlib import Path
source=Path('local-levels/level-3/solver-under-120k.py').read_text()
source=source.replace("h.setOptionValue('time_limit',5.0)","h.setOptionValue('time_limit',float(os.getenv('CHEM_TIME','3')))")
source=source.replace('obj=.00001,type=',"obj=float(os.getenv('CHEM_REACTION_COST','.00001')),type=")
source=source.replace('cons={}', '''# Proven conserved elemental pools require startup stock before a firing.
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
cons={}''')
source=source.replace('h.setSolution(len(inds),inds,vals)', 'inds.extend(v.index for v in activations.values());vals.extend(int(seedcounts[j]>0) for j in activations)\n h.setSolution(len(inds),inds,vals)')
source=source.replace('counts,trials=40','counts,trials=int(os.getenv("CHEM_TRIALS","24"))')
Path('local-levels/level-3/experiments/search/pool.py').write_text(source)
