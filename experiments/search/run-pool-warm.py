from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,sys,os
root=Path(__file__).resolve().parent
files=root.parent.parent/'prepared'/'files'
def run(i):
    inp=next(files.glob(f'in_level-3_{i}-*.txt'))
    plan=root/f'pool-warm-plan-{i}.jsonl';plan.write_text('')
    p=subprocess.run([sys.executable,str(root/'pool-warm.py')],input=inp.read_bytes(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=dict(os.environ,CHEM_TIME='3',CHEM_PLAN=str(plan)))
    (root/f'pool-warm-output-{i}.txt').write_bytes(p.stdout)
    (root/f'pool-warm-log-{i}.txt').write_bytes(p.stderr)
    v=subprocess.run([sys.executable,str(root.parent.parent/'checker.py'),str(root/f'pool-warm-output-{i}.txt')],input=inp.read_bytes(),stdout=subprocess.PIPE)
    print(i,v.stdout.decode(),flush=True)
with ThreadPoolExecutor(4) as pool:list(pool.map(run,range(1,5)))
