from pathlib import Path
import subprocess,sys
r=Path(__file__).resolve().parent
inp=(r.parents[1]/'prepared/files/in_level-3_1-small.txt').read_text()
lines=[x.strip() for x in inp.splitlines() if x.strip()]
m=int(lines[0]);rn=int(lines[m+1]);end=m+2+rn
(r/'case8.in').write_text('\n'.join(lines[:end]+['1',lines[end+8]])+'\n')
s=(r/'pool-budget.py').read_text()
s=s.replace('make_seed(target,need,set())', "print('BEFORE SEED',file=sys.stderr,flush=True)\n make_seed(target,need,set())\n print('AFTER SEED',file=sys.stderr,flush=True)")
s=s.replace('h.run();sol=h.getSolution();info=h.getInfo()',"print('BEFORE MIP',file=sys.stderr,flush=True)\n h.run();sol=h.getSolution();info=h.getInfo()\n print('AFTER MIP',info.objective_function_value,file=sys.stderr,flush=True)")
s=s.replace('candidates=[budget_schedule_capital',"print('BEFORE SCHEDULE',file=sys.stderr,flush=True)\n candidates=[budget_schedule_capital")
s=s.replace('value,steps=min(candidates',"print('AFTER SCHEDULE',file=sys.stderr,flush=True)\n value,steps=min(candidates")
s=s.replace('for trial in range(trials):',"for trial in range(trials):\n  print('TRIAL',trial,file=sys.stderr,flush=True)")
(r/'diagnostic.py').write_text(s)
with (r/'diagnostic.log').open('w') as log,(r/'diagnostic.out').open('w') as out:
 subprocess.run([sys.executable,str(r/'diagnostic.py')],input=(r/'case8.in').read_bytes(),stderr=log,stdout=out)
