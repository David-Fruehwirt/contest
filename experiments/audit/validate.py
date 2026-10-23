from pathlib import Path
from collections import defaultdict
import sys,re,json

def side(s):
    pairs=[]
    for term in s.split(','):
        number,molecule=term.split()
        assert int(number)>0
        pairs.append((molecule,int(number)))
    return pairs

def validate(input_path,output_path):
    lines=iter(Path(input_path).read_text().split())
    # Independently parse the line-oriented input and retain the authorized reaction texts.
    data=iter(s.strip() for s in Path(input_path).read_text().splitlines() if s.strip())
    prices={}
    for _ in range(int(next(data))):
        p,m=next(data).split(' -> ');prices[m]=int(p)
    reactions={}
    for _ in range(int(next(data))):
        s=next(data);a,b=s.split(' -> ');reactions[s]=(side(a),side(b))
    targets=[]
    for _ in range(int(next(data))):
        n,m=next(data).split();targets.append((m,int(n)))
    blocks=re.split(r'\r?\n\s*\r?\n',Path(output_path).read_text().strip())
    assert len(blocks)==len(targets),(len(blocks),len(targets))
    results=[]
    for block,(target,required) in zip(blocks,targets):
        inventory=defaultdict(int);purchases=defaultdict(int);steps=0
        for reaction in block.splitlines():
            assert reaction.strip() in reactions,('unknown reaction',reaction)
            consumed,produced=reactions[reaction.strip()]
            # Calculate all shortages against the same pre-reaction inventory.
            inputs=defaultdict(int)
            for m,n in consumed:inputs[m]+=n
            for m,n in inputs.items():
                deficit=max(0,n-inventory[m])
                if deficit:
                    assert m in prices,('unbuyable molecule',m)
                    purchases[m]+=deficit;inventory[m]+=deficit
            for m,n in inputs.items():inventory[m]-=n
            for m,n in produced:inventory[m]+=n
            assert min(inventory.values())>=0
            steps+=1
        assert inventory[target]>=required,('missing target',target,inventory[target],required)
        results.append({'target':target,'required':required,'produced':inventory[target],
                        'cost':sum(prices[m]*n for m,n in purchases.items()),'steps':steps})
    return {'valid':True,'cost':sum(c['cost'] for c in results),'cases':results}

if __name__=='__main__':
    try:print(json.dumps(validate(sys.argv[1],sys.argv[2])))
    except Exception as e:print(json.dumps({'valid':False,'reason':repr(e)}));sys.exit(1)
