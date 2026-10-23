# RESULTS
approach | file | score | valid? | note
--- | --- | --- | --- | ---
legacy greedy (prior session) | 0/1/2/3/4 | 136/37598/33658/47788/66852 | yes | seeded best/
net-balance ILP + greedy order | 0-example | LB 66 (case0) vs sim 72 | case1 unorderable | net LB not tight: byproducts of the last firings come too late; cycles get stuck
layered CP-SAT T=6 | 0-example | 136 | yes | both cases OPTIMAL = reference
layered CP-SAT T=10, 30s/case | 1-small | 35400 | yes | all 10 cases OPTIMAL for T=10 (minT=8)
layered CP-SAT, net-LB reaction set, T=2..4x minT, 3 workers, 40s | 1,2 (partial) | small 30156, medium 31764 (5/15 cases new) | yes | deeper T keeps helping; large/enormous killed by OOM (4 parallel jobs)
net-LB gap diagnosis | 1-small case 0 | LB 2048 vs 2432 | - | Ti/TiO2 catalytic cycle needs a 204 Ti seed and runs serially (2 layers per pass); net LB ignores the seed
rolling (g=1,2 units at a time) | 1-small case 0 | 2464 / 2440 | yes | worse than one-shot T=32 (2432) -> dropped
improve LNS (ASAP-layer incumbent as hint, T=depth+8) | 1-small case 0,1 | 2432->2432, 2720->2716 | yes | small gains, bound loose
macro model (2-cycles serial inside one layer) | 1-small case 0,1 | T=14: 2480, 2720 | yes | beats plain at equal T (plain T=16: 2624)
seed per-case store with teammate's exports (under-105k/120k/improved) | 1-4 | 26824/21314/24848/30318 = 103304 | yes | per-case min of ours + teammate; ours wins small cases 0,2 (deep T=32)
