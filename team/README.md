# CCC Level 3: team optimisation hub

All paths below are relative to `team/`. Minimise total purchase cost (lower is better). The best result per **case** is taken
across all teammates, so improving a single case of a single input already counts.

## Submit your solution

1. Put your output files in `submissions/<your-name>/`. Name each file after its input so
   the level key is in the name:
   `out_level-3_1-small.txt`, `out_level-3_2-medium.txt`, `out_level-3_3-large.txt`,
   `out_level-3_4-enormous.txt` (`output-1.txt` … `output-4.txt` also works).
   Partial or older files are fine: every paragraph is checked on its own, and only
   valid paragraphs can win.
2. Run `python3 ensemble.py` (standard library only), or just push or open a PR, where CI
   runs it for you.
3. Check `LEADERBOARD.md`. `best/out_level-3_*.txt` are the files to upload.

## Files

| file | role |
|---|---|
| `in/` | contest inputs (read-only) |
| `score.py` | judge: simulates each paragraph from an empty inventory, buys missing inputs before each reaction, checks the target. **Read-only, never edit.** |
| `promote.sh` | the only writer of `best/`: replaces a file only if it is valid and strictly cheaper |
| `ensemble.py` | per-case best across `submissions/*/` → `ensemble/` → `promote.sh` → `best/` + `LEADERBOARD.md` |
| `best/` | current best files, the ones to upload |
| `RESULTS.md` | log of every attempt: approach, file, score, valid?, note |

## Solvers (Laurenz)

Python + OR-Tools CP-SAT (`python3 -m venv .venv && .venv/bin/pip install ortools numpy scipy`).
`cases/<input>/<k>.txt` holds the per-case best (first line = cost), and solvers only overwrite it with cheaper results.

- `lb.py` net-balance ILP (weak lower bound); `lb2.py` adds activation order / seed constraints (stronger valid LB)
- `solve_layer.py`, `solve_deep.py`: time-indexed (layered) CP-SAT, exact for any solution it returns
- `solve_macro.py`: layered model where 2-reaction catalytic cycles run serially inside one layer
- `solve_improve.py`: improve-only LNS warm-started from the current per-case best
- `seq_ls.py`: local search directly on the sequence
- `seed_cases.py <in>` pulls `best/` into `cases/`; `merge.py <in>` assembles `cases/` and promotes
