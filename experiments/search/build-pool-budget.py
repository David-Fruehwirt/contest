from pathlib import Path
s=Path('local-levels/level-3/experiments/search/pool.py').read_text()
helper=Path('local-levels/level-3/experiments/optimizer/budget_seedcheap.py').read_text()
helper=helper[helper.index('def schedule('):helper.index("if __name__=='__main__':")]
helper=helper.replace('def schedule(prices,reactions,target,quotas,trials=40,simplify=True):','def budget_schedule_capital(prices,reactions,target,quotas,trials=40,simplify=True,purchases=None):')
helper=helper.replace('allowance={m:max(0,-bal[m]) for m in prices}','allowance={m:max(0,-bal[m],(purchases or {}).get(m,0)) for m in prices}')
s=s.replace('answers=[]\nfor case',helper+'\nanswers=[]\nfor case')
new='''candidates=[budget_schedule_capital(prices,[(a,b) for a,b,s in rs],(need,target),counts,trials=int(os.getenv("CHEM_TRIALS","24")),purchases=purchases),budget_schedule_capital(prices,[(a,b) for a,b,s in rs],(need,target),counts,trials=16)]
 value,steps=min(candidates,key=lambda v:v[0])
 if os.getenv('CHEM_PLAN'):
  with open(os.getenv('CHEM_PLAN'),'a') as planfile:planfile.write(json.dumps({'case':case+1,'counts':counts,'purchases':purchases})+'\\n')'''
s=s.replace('value,steps=budget_schedule(prices,[(a,b) for a,b,s in rs],(need,target),counts,trials=int(os.getenv("CHEM_TRIALS","24")))',new)
Path('local-levels/level-3/experiments/search/pool-budget.py').write_text(s)
