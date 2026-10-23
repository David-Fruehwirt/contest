"""Valid startup-capital cuts for conserved elemental metal pools.

Assumes single-target empty-inventory chemistry. The practical reaction-count
upper bound must be supplied by the caller; these cuts link count to support.
"""
import re
from collections import Counter

def formula(molecule):
    counts=Counter()
    tokens=re.findall(r'([A-Z][a-z]?)([0-9]*)',molecule)
    assert ''.join(e+n for e,n in tokens)==molecule,molecule
    for e,n in tokens:counts[e]+=int(n or 1)
    return counts

def add_capital_constraints(h,x,y,reactions,upper_count=10000):
    """Return mapping (element,demand)->binary variables added to Highs model.

    h: highspy.Highs; x: reaction decision variables; y: molecule->purchase var.
    reactions: [(Counter(inputs),Counter(outputs)), ...].
    """
    import highspy
    names=set(y)|{m for a,b in reactions for m in a|b}
    atoms={m:formula(m) for m in names}
    elements={e for f in atoms.values() for e in f}-set(['C','H','O','N','S','Cl'])
    result={}
    for element in sorted(elements):
        demands=[sum(k*atoms[m][element] for m,k in a.items()) for a,b in reactions]
        yields=[sum(k*atoms[m][element] for m,k in b.items()) for a,b in reactions]
        # Any atom-creating reaction would invalidate this conservation bound.
        if any(b>a for a,b in zip(demands,yields)):continue
        purchases=sum(atoms[m][element]*v for m,v in y.items() if atoms[m][element])
        for demand in sorted(set(demands)-{0}):
            z=h.addVariable(lb=0,ub=1,type=highspy.HighsVarType.kInteger)
            result[element,demand]=z
            h.addConstr(purchases>=demand*z)
            for j,d in enumerate(demands):
                if d==demand:h.addConstr(x[j]<=upper_count*z)
    return result
