URL: https://codingcontest.org/contests/42nd-school-ccc-5871/game
Contest slug/origin: unverified; discover_contest rejects metadata. Local archive supplied by operator.
Scope: all contest levels, automatic upload authorized; currently level 3 local fallback.
Run: 31b9b7963c004b469ac0b1a9b85df072; 1 semantic sample passed, 4 outputs validated.
Checker: checker.py independently simulates inventory, permitted reactions, automatic purchases, final quantities and paragraph count. Optimization quality is not certified.
Solver: relaxed unit-cost reaction selection, recursive production, inventory/byproduct reuse.
Accepted IDs: none known. Upload IDs unavailable. No uploads attempted.
Repair budget: 0/8 used. Next: manual upload exported outputs or fix discovery and obtain live target IDs.

Improvement run: 6e6218e1aa534b13bc2ed750367cb6f1 (ready).
Solver now searches alternative reaction routes and reactant ordering using actual inventory purchase costs, retaining cheapest candidates.
Sample: 1/1 semantic passed; outputs: 4/4 validated. Checker rejection tests: invalid reaction and unmet target both rejected.
Costs baseline -> improved: small 37598 -> 33598; medium 33658 -> 28752; large 47788 -> 35175; enormous 66852 -> 44139.
Total 185896 -> 141664 (23.794% lower). Optimality unproven.
Exports: exports/improved/output-1.txt through output-4.txt; hash manifest retained.
Repair budget: 1/8 used. Discovery retried: same metadata identity error; authenticated setup ready. No upload or live acceptance claimed.
Next: manual upload improved outputs, or repair discovery to obtain authoritative target IDs.

Target <=120000 achieved.
Run 898a40f6de4c4fe380c813005708a5c0: ready; sample1/1 and output4/4 semantic pass.
Costs small27688 medium26042 large27309 enormous36160; total117199 (2801 below120000; 24465 lower than141664).
Independent audit: all65 cases pass atomic replay, authorized reactions, paragraph counts, final target quantities. Auditor source experiments/audit/validate.py.
Solver: solver-under-120k.py (exact copy of gated experiments/highs/solver.py); integer reaction planning using HiGHS MILP, feasible warmstart, purchase-budget scheduling, direct physical replay. highspy1.15.1 and numpy2.4.6 installed workspace-local at experiments/dependencies; no global install.
Run attempts this round: 76d9b8af6042413095d2761bfb36e199 sample runtime API mismatch; f9a79efe25fb41fca88664385a5c61af no MIP incumbent on medium within limit; fixed via feasible warmstart; final898a40f6 ready. Cumulative repair budget4/8 used (3 this round,1 earlier).
Exports: exports/under-120k/output-1.txt small, output-2.txt medium, output-3.txt large, output-4.txt enormous, manifest retained.
No submission: discovery previously rejects contest metadata; authoritative live target IDs unavailable. Optimality and live acceptance unconfirmed. Next: manual upload these four files or restore contest discovery for automated submission. Requested optimization completed; workers stopped.

Target BELOW105000 achieved: final103332 =small26852 +medium21314 +large24848 +enormous30318 (1668 belowthreshold,13867 lowerthan117199).
Final ready MCP run b5183f2f2a8446008bac737879414355: sample1/1 semanticpassed,4/4 outputsvalidated; independent auditofexportedfiles confirmsall65cases andcosts.
Exports: exports/under-105k/output-1.txt(small),output-2.txt(medium),output-3.txt(large),output-4.txt(enormous). Costs and hashmanifest retained.
Method: conserved-element startup capital constraints (only proven valid via reaction balances), actualMIPpurchase budgets passedinto virtual scheduler, cheaper seed synthesis, reaction-quota reuse, exact-quota reordering, then per-case ensemble selection of best feasible generated search checkpoint.
Final generator solver-ensemble-105k.py: matches complete input SHA256, hash-checks generated candidate checkpoints, independently replays each candidate to choose cheapest valid paragraph; includes generic baselineproducer for samples/uncached inputs. No sample outputs cached/hardcoded. Preserve checkpoint-manifest-105k.json and referenced candidate files to reproduce exactensemble.
Runs thisround: aca9d434938c40179cda626a1e299033 ready115502; 942e578fa5e24617aa5f5e9e7d18eb66 stalledHiGHS smallcase8 and tooltimedout, its twoPythonworkers stopped byexactrunid; finalb5183f2f ready103332. Cumulative repairbudget7/8 used (3thisround).
HiGHS note: some pooledcapital fullfile solvesstall at smallcase8 inside h.run(), despite single-case success; h.clearSolver didnotfix in workerdiagnostic. Bounded scheduler/pooledactivation draft solver-under-105k-v2.py remains experimental/unrun. Do not resume stalled runblindly.
All subagents stopped aftergoalmet. No submissions; discovery blocker andmissingauthoritativetargetIDs unchanged. Liveacceptance/globaloptimality unconfirmed.
