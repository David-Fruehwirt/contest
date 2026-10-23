from pathlib import Path
import subprocess,sys
r=Path(__file__).resolve().parent
s=(r/'diagnostic.py').read_text()
(r/'diagnostic-full.py').write_text(s)
with (r/'diagnostic-full.log').open('w') as log,(r/'diagnostic-full.out').open('w') as out:
 subprocess.run([sys.executable,str(r/'diagnostic-full.py')],input=(r.parents[1]/'prepared/files/in_level-3_1-small.txt').read_bytes(),stderr=log,stdout=out)
