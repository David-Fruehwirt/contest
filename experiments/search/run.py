from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,sys
root=Path(__file__).resolve().parent
files=root.parent.parent/'prepared'/'files'
def run(i):
    inp=next(files.glob(f'in_level-3_{i}-*.txt'))
    p=subprocess.run([str(root/'search-v2.exe'),sys.argv[1] if len(sys.argv)>1 else '4'],input=inp.read_bytes(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (root/f'output-{i}.txt').write_bytes(p.stdout)
    (root/f'log-{i}.txt').write_bytes(p.stderr)
    v=subprocess.run([sys.executable,str(root.parent.parent/'checker.py'),str(root/f'output-{i}.txt')],input=inp.read_bytes(),stdout=subprocess.PIPE)
    print(i,v.stdout.decode(),flush=True)
with ThreadPoolExecutor(4) as pool:list(pool.map(run,range(1,5)))
