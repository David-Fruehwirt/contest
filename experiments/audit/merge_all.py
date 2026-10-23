from pathlib import Path
from validate import validate
import re,json
root=Path('local-levels/level-3');run=Path('.ccc/runs/898a40f6de4c4fe380c813005708a5c0');total=0
outdir=Path(__file__).parent/'merged';outdir.mkdir(exist_ok=True)
for i,name in enumerate(['small','medium','large','enormous'],1):
    inp=root/f'prepared/files/in_level-3_{i}-{name}.txt'
    candidates=[run/f'output-{i}.txt',root/f'exports/improved/output-{i}.txt']
    candidates+=list((root/'experiments/optimizer').glob(f'*{name}*.out'))
    candidates+=list((root/'experiments/search').glob(f'*output-{i}.txt'))
    best=None;used=[]
    for path in candidates:
        try:r=validate(inp,path)
        except Exception:continue
        b=re.split(r'\n\s*\n',path.read_text().strip())
        if best is None:best=[(c['cost'],s,str(path)) for c,s in zip(r['cases'],b)]
        else:
            for case,(c,s) in enumerate(zip(r['cases'],b)):
                if c['cost']<best[case][0]:best[case]=(c['cost'],s,str(path))
    out=outdir/f'output-{i}.txt';out.write_text('\n\n'.join(s for c,s,p in best)+'\n')
    score=sum(c for c,s,p in best);total+=score
    print(name,score,[(c,Path(p).name) for c,s,p in best])
    assert validate(inp,out)['cost']==score
print('TOTAL',total)
