from pathlib import Path
source=Path('local-levels/level-3/solver-under-120k.py').read_text()
source=source.replace("h.setOptionValue('time_limit',5.0)","h.setOptionValue('time_limit',float(os.getenv('CHEM_TIME','3')))")
source=source.replace('obj=.00001,type=',"obj=float(os.getenv('CHEM_REACTION_COST','.00001')),type=")
source=source.replace('cons={}', '''# A first firing needs catalyst material purchased or produced elsewhere.
activations={}
for j,(a,b,s) in enumerate(rs):
 catalysts=[(m,k) for m,k in a.items() if b.get(m,0)>=k]
 if catalysts:
  z=h.addVariable(lb=0,ub=1,type=highspy.HighsVarType.kInteger)
  activations[j]=z
  h.addConstr(x[j]<=2000*z)
  for m,k in catalysts:
   available=sum(max(0,bb.get(m,0)-aa.get(m,0))*x[q] for q,(aa,bb,ss) in enumerate(rs) if q!=j)
   if m in y:available+=y[m]
   h.addConstr(available>=k*z)
print('startup constraints',len(activations),file=sys.stderr)
cons={}''')
source=source.replace('h.setSolution(len(inds),inds,vals)', 'inds.extend(v.index for v in activations.values());vals.extend(int(seedcounts[j]>0) for j in activations)\n h.setSolution(len(inds),inds,vals)')
source=source.replace('counts,trials=40','counts,trials=int(os.getenv("CHEM_TRIALS","16"))')
Path('local-levels/level-3/experiments/search/startup.py').write_text(source)
