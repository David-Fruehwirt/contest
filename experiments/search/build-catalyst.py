from pathlib import Path
p=Path('local-levels/level-3/solver-under-120k.py')
s=p.read_text()
s=s.replace("h.setOptionValue('time_limit',5.0)","h.setOptionValue('time_limit',float(os.getenv('CHEM_TIME','3')))")
s=s.replace('obj=.00001,type=',"obj=float(os.getenv('CHEM_REACTION_COST','.00001')),type=")
s=s.replace('cons={}', '''# Molecules with no net-positive production require shop catalyst startup.
no_producer={m for m in prices if all(b.get(m,0)<=a.get(m,0) for a,b,s in rs)}
activations={}
for j,(a,b,s) in enumerate(rs):
 catalysts=[(m,k) for m,k in a.items() if m in no_producer and b.get(m,0)>=k]
 if catalysts:
  z=h.addVariable(lb=0,ub=1,type=highspy.HighsVarType.kInteger)
  activations[j]=z
  h.addConstr(x[j]<=1000*z)
  for m,k in catalysts:h.addConstr(y[m]>=k*z)
print('startup bounds',len(activations),sorted(no_producer),file=sys.stderr)
cons={}''')
s=s.replace('h.setSolution(len(inds),inds,vals)', 'inds.extend(v.index for v in activations.values());vals.extend(int(seedcounts[j]>0) for j in activations)\n h.setSolution(len(inds),inds,vals)')
s=s.replace('counts,trials=40','counts,trials=int(os.getenv("CHEM_TRIALS","16"))')
Path('local-levels/level-3/experiments/search/catalyst.py').write_text(s)
