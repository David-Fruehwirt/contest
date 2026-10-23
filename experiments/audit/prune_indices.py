"""Backward required-inventory pruning of a valid reaction sequence.

No route choices or cost assumptions are used. A reaction can be removed only
if none of its outputs is required by any retained suffix reaction or target.
"""
from collections import Counter

def prune_indices(steps,reactions,target):
    """reactions=[(Counter(inputs),Counter(outputs)),...], target=(qty,name)."""
    required=Counter({target[1]:target[0]});result=[]
    for j in reversed(steps):
        consumed,produced=reactions[j]
        if not any(required[m]>0 for m in produced):
            continue
        result.append(j)
        for m,n in produced.items():
            required[m]=max(0,required[m]-n)
        required.update(consumed)
    result.reverse()
    return result
