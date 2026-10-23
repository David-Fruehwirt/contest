import pathlib,subprocess,json
root=pathlib.Path('local-levels/level-3')
checker=str(root/'checker.py');example=root/'prepared/files/in_level-3_0-example.txt'
for name,text in [('invalid-reaction','nonsense\n\nnonsense\n'),('missing-target','1 C, 1 O2 -> 1 CO2\n\n1 C, 1 O2 -> 1 CO2\n')]:
 p=root/(name+'.txt');p.write_text(text)
 result=subprocess.run(['.venv/Scripts/python.exe',checker,str(p)],input=example.read_bytes(),capture_output=True)
 obj=json.loads(result.stdout);assert obj['valid'] is False;print(name,obj)
for i,kind in enumerate(['small','medium','large','enormous'],1):
 inp=root/f'prepared/files/in_level-3_{i}-{kind}.txt';out=root/f'exports/improved/output-{i}.txt'
 result=subprocess.run(['.venv/Scripts/python.exe',checker,str(out)],input=inp.read_bytes(),capture_output=True)
 print(kind,json.loads(result.stdout))

