from pathlib import Path
s=Path('local-levels/level-3/experiments/search/pool-budget.py').read_text()
s=s.replace('h.run();sol=h.getSolution();info=h.getInfo()', '''# First solve with continuous support flags to obtain a good net-flow plan.
 for v in activations.values():h.changeColIntegrality(v.index,highspy.HighsVarType.kContinuous)
 h.setOptionValue('time_limit',.7);h.run();relaxed=h.getSolution()
 if relaxed.value_valid:
  warmcounts=[max(0,round(relaxed.col_value[v.index])) for v in x]
  warmbuy={m:max(0,round(relaxed.col_value[v.index])) for m,v in y.items()}
  for e in pools:
   required=max((sum(k*atoms[m][e] for m,k in rs[j][0].items()) for j,c in enumerate(warmcounts) if c),default=0)
   held=sum(atoms[m][e]*q for m,q in warmbuy.items())
   if held<required:
    carrier=min((m for m in y if atoms[m][e]),key=lambda m:prices[m]/atoms[m][e])
    warmbuy[carrier]+=math.ceil((required-held)/atoms[carrier][e])
  vals=[warmcounts[j] for j in range(R)]+[warmbuy[m] for m in y]+[int(warmcounts[j]>0) for j in activations]
 for v in activations.values():h.changeColIntegrality(v.index,highspy.HighsVarType.kInteger)
 h.setSolution(len(inds),inds,vals)
 h.setOptionValue('time_limit',float(os.getenv('CHEM_TIME','3')))
 h.run();sol=h.getSolution();info=h.getInfo()''')
s=s.replace('physical.update(b);virtual.update(b);steps.append(j)', "physical.update(b);virtual.update(b);steps.append(j)\n   if paid>=best[0] or len(steps)>3000:raise ValueError('search bound')")
Path('local-levels/level-3/experiments/search/pool-warm.py').write_text(s)
